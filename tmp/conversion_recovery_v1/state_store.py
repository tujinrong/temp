"""Local immutable stage snapshots. GitHub read-back receipts are explicit, not inferred.
No converters or repository rules are imported, patched, or executed here.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Mapping


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    key = PurePosixPath(relative)
    if not relative or key.is_absolute() or any(x in ('..', '.') for x in key.parts) or '\\' in relative:
        raise ValueError('Unsafe artifact path')
    root = root.resolve()
    target = (root / key).resolve()
    if target == root or root not in target.parents:
        raise ValueError('Artifact escapes the run directory')
    return target


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.writing')
    try:
        with temporary.open('w', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def save_stage(run: Path, stage: str, dependencies: Mapping[str, str], artifacts: Mapping[str, Path]) -> Path:
    """Snapshot one bounded stage. The caller must serialize writers to a run."""
    if not re.fullmatch(r'[a-z0-9_-]{1,64}', stage) or not dependencies or not artifacts:
        raise ValueError('Stage, dependencies and actual artifacts are required')
    # Read all inputs before changing the manifest. A missing source cannot replace good state.
    payload = {name: path.read_bytes() for name, path in artifacts.items()}
    hashes = {name: {'sha256': digest(data), 'bytes': len(data)} for name, data in payload.items()}
    key = digest(json.dumps({'dependencies': dict(dependencies), 'artifacts': hashes}, sort_keys=True).encode())
    folder = safe_path(run, f'snapshots/{stage}/{key}')
    targets = {name: safe_path(folder, name) for name in payload}
    for name, data in payload.items():
        target = targets[name]; target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != data:
            raise ValueError('Immutable snapshot was altered')
        target.write_bytes(data)
        if digest(target.read_bytes()) != hashes[name]['sha256']:
            raise OSError('Snapshot verification failed')
    manifest = safe_path(run, f'{stage}.json')
    atomic_json(manifest, {'schema': 1, 'stage': stage, 'dependencies': dict(dependencies),
        'snapshot': f'snapshots/{stage}/{key}', 'artifacts': hashes, 'durability': 'LOCAL_ONLY'})
    return manifest


def validate_stage(run: Path, manifest: Path, dependencies: Mapping[str, str]) -> dict:
    """Fail closed: no missing/corrupt/stale stage is reusable."""
    try:
        record = json.loads(manifest.read_text(encoding='utf-8'))
        if record.get('schema') != 1 or record.get('dependencies') != dict(dependencies):
            raise ValueError('Schema or dependency fingerprints changed')
        if not record.get('artifacts'):
            raise ValueError('No artifact payloads')
        folder = safe_path(run, record['snapshot'])
        for name, expected in record['artifacts'].items():
            data = safe_path(folder, name).read_bytes()
            if digest(data) != expected['sha256'] or len(data) != expected['bytes']:
                raise ValueError('Artifact fingerprint mismatch: ' + name)
        return {'action': 'REUSE', 'durability': record.get('durability', 'LOCAL_ONLY'), 'record': record}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'action': 'RERUN_STAGE', 'reason': str(exc)}


def acknowledge_readback(run: Path, manifest: Path, dependencies: Mapping[str, str],
                         commit: str, retrieved: Mapping[str, bytes]) -> dict:
    """Call only with bytes actually re-read from the acknowledged remote commit."""
    checked = validate_stage(run, manifest, dependencies)
    if checked['action'] != 'REUSE' or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Unverified local stage or invalid commit')
    record = checked['record']
    if set(retrieved) != set(record['artifacts']):
        raise ValueError('Incomplete remote read-back')
    for name, data in retrieved.items():
        if digest(data) != record['artifacts'][name]['sha256']:
            raise ValueError('Remote artifact differs: ' + name)
    receipt = {'commit': commit, 'artifacts': record['artifacts'], 'status': 'READBACK_VERIFIED'}
    atomic_json(manifest.with_suffix('.receipt.json'), receipt)
    return receipt
