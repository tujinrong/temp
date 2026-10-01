"""Verified, immutable local checkpoints for publication through a GitHub adapter.

Only already-scoped artifacts belong in snapshots. This module never executes
workbook content and never changes GitHub refs. Publish the returned artifacts and
manifest together on main using the connected GitHub tools; download them to
resume. ZIP and ordinary-file snapshots are supported. Stage compatibility includes input, rule and code fingerprints.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
import zipfile

SCHEMA = 1
MAX_EXPANDED = 64 * 1024 * 1024


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_name(name: str) -> str:
    p = PurePosixPath(name)
    if not name or '\\' in name or p.is_absolute() or '..' in p.parts or str(p) != name:
        raise ValueError('Unsafe relative artifact path: ' + name)
    return name


def fingerprints(paths: dict[str, Path]) -> dict[str, str]:
    return {name: digest(Path(path).read_bytes()) for name, path in sorted(paths.items())}


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save(directory: Path, stage: str, dependencies: dict[str, str],
         artifacts: dict[str, bytes], *, next_action: str) -> dict:
    """Create a stage ZIP and manifest. A published stage is never overwritten."""
    directory = Path(directory)
    if not artifacts or not stage or not dependencies:
        raise ValueError('Stage, dependencies and artifacts are required.')
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / 'state.json').exists() or (directory / 'artifacts.zip').exists():
        raise FileExistsError('Use a new stage/attempt directory.')
    if sum(len(data) for data in artifacts.values()) > MAX_EXPANDED:
        raise ValueError('Checkpoint exceeds expanded-size limit.')
    for name in artifacts:
        safe_name(name)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(artifacts.items()):
            z.writestr(name, data)
    packed = buf.getvalue()
    state = {'schema': SCHEMA, 'stage': stage, 'status': 'CHECKPOINT_ONLY',
             'dependencies': dependencies, 'next_action': next_action,
             'archive_sha256': digest(packed),
             'artifacts': {k: {'sha256': digest(v), 'bytes': len(v)} for k, v in sorted(artifacts.items())}}
    atomic_write(directory / 'artifacts.zip', packed)
    atomic_write(directory / 'state.json', (json.dumps(state, ensure_ascii=False, indent=2) + '\n').encode())
    return state


def save_files(directory: Path, stage: str, dependencies: dict[str, str],
               artifacts: dict[str, bytes], *, next_action: str) -> dict:
    """Plain-file alternative for text-only GitHub upload adapters."""
    directory = Path(directory)
    if not stage or not dependencies or not artifacts:
        raise ValueError('Stage, dependencies and artifacts are required.')
    if sum(map(len, artifacts.values())) > MAX_EXPANDED:
        raise ValueError('Checkpoint exceeds expanded-size limit.')
    if (directory / 'state.json').exists():
        raise FileExistsError('Use a new stage/attempt directory.')
    for name in artifacts:
        safe_name(name)
        if name == 'state.json' or (directory / name).exists():
            raise FileExistsError('Reserved or existing artifact: ' + name)
        if not (directory / name).resolve().is_relative_to(directory.resolve()):
            raise ValueError('Artifact would follow an external symlink.')
    state = {'schema': SCHEMA, 'storage': 'files', 'stage': stage,
             'status': 'CHECKPOINT_ONLY', 'dependencies': dependencies,
             'next_action': next_action,
             'artifacts': {k: {'sha256': digest(v), 'bytes': len(v)}
                           for k, v in sorted(artifacts.items())}}
    for name, raw in artifacts.items():
        atomic_write(directory / name, raw)
    atomic_write(directory / 'state.json', (json.dumps(state, ensure_ascii=False, indent=2) + '\n').encode())
    return state


def verify(directory: Path, dependencies: dict[str, str]) -> tuple[dict, dict[str, bytes]]:
    directory = Path(directory)
    state = json.loads((directory / 'state.json').read_text(encoding='utf-8'))
    if state.get('schema') != SCHEMA or state.get('dependencies') != dependencies:
        raise ValueError('Input, rules or stage code changed; do not reuse this stage.')
    if state.get('storage') == 'files':
        entries = state.get('artifacts', {})
        if not entries or sum(v['bytes'] for v in entries.values()) > MAX_EXPANDED:
            raise ValueError('Invalid plain-file checkpoint size or inventory.')
        data = {}
        for name, expected in entries.items():
            safe_name(name)
            path = directory / name
            if name == 'state.json' or not path.resolve().is_relative_to(directory.resolve()):
                raise ValueError('Unsafe plain-file artifact.')
            if path.stat().st_size != expected['bytes']:
                raise ValueError('Artifact size mismatch: ' + name)
            payload = path.read_bytes()
            if digest(payload) != expected['sha256']:
                raise ValueError('Artifact fingerprint mismatch: ' + name)
            data[name] = payload
        return state, data
    if state.get('storage', 'zip') != 'zip':
        raise ValueError('Unsupported checkpoint storage mode.')
    raw = (directory / 'artifacts.zip').read_bytes()
    if digest(raw) != state['archive_sha256']:
        raise ValueError('Archive fingerprint mismatch.')
    data = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != set(state['artifacts']):
            raise ValueError('Archive entry inventory mismatch.')
        if sum(i.file_size for i in z.infolist()) > MAX_EXPANDED:
            raise ValueError('Archive expansion limit exceeded.')
        for name in names:
            safe_name(name)
            payload = z.read(name)
            expected = state['artifacts'][name]
            if digest(payload) != expected['sha256'] or len(payload) != expected['bytes']:
                raise ValueError('Artifact mismatch: ' + name)
            data[name] = payload
    return state, data


def restore(directory: Path, destination: Path, dependencies: dict[str, str]) -> dict:
    state, artifacts = verify(directory, dependencies)
    destination = Path(destination).resolve()
    # Validate every target before writing any restored file.
    for name, raw in artifacts.items():
        target = destination / name
        if not target.resolve().is_relative_to(destination):
            raise ValueError('Restore would follow an external symlink.')
        if target.exists() and target.read_bytes() != raw:
            raise FileExistsError('Refuse to overwrite a newer/different artifact: ' + name)
    for name, raw in artifacts.items():
        atomic_write(destination / name, raw)
    return state


def cleanup(directory: Path, final_files: dict[str, Path], receipt: dict) -> None:
    """Local cleanup only after caller supplies a verified main read-back receipt.

The GitHub adapter must independently verify receipt fields. Deleting the
published ZIP/state on main is a separate, non-force Git commit, never a rewrite.
"""
    if receipt.get('branch') != 'main' or receipt.get('verified') is not True or not receipt.get('commit'):
        raise ValueError('A verified main delivery receipt is required.')
    actual = fingerprints(final_files)
    if not actual or actual != receipt.get('files'):
        raise ValueError('Final outputs differ from the verified delivery receipt.')
    directory = Path(directory)
    state_path = directory / 'state.json'
    if not state_path.exists():
        return
    state = json.loads(state_path.read_text(encoding='utf-8'))
    verify(directory, state['dependencies'])
    names = list(state['artifacts']) if state.get('storage') == 'files' else ['artifacts.zip']
    for name in names:
        (directory / safe_name(name)).unlink()
    state_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['verify', 'restore'])
    parser.add_argument('checkpoint', type=Path)
    parser.add_argument('--dependencies', type=Path, required=True,
                        help='JSON fingerprints recomputed from current source/rules/code, not copied blindly.')
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    deps = json.loads(args.dependencies.read_text(encoding='utf-8'))
    if args.action == 'restore':
        if not args.destination:
            parser.error('--destination is required for restore')
        state = restore(args.checkpoint, args.destination, deps)
    else:
        state, _ = verify(args.checkpoint, deps)
    print(state['stage'], state['next_action'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
