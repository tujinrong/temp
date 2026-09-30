"""Final gate: independent content checks AND actual Mermaid validation.

Both reports must describe the exact bytes of the current Markdown. A stale
report, missing renderer, unknown expected diagram count or failed diagram
cannot be offset by a good content score.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from .mermaid_validate import validate


def combine(markdown: str | Path, acceptance: dict, mermaid: dict) -> dict:
    digest=hashlib.sha256(Path(markdown).read_bytes()).hexdigest()
    checks=acceptance.get('checks',[])
    reasons=[]
    if acceptance.get('markdown_sha256')!=digest or mermaid.get('markdown_sha256')!=digest:
        reasons.append('Report fingerprint does not match the current Markdown.')
    if not checks or not all(c.get('passed') is True for c in checks):
        reasons.append('Independent content checks are missing or failed.')
    if mermaid.get('expected_count') is None:
        reasons.append('Expected diagram count is not specified independently.')
    if mermaid.get('diagram_count')!=mermaid.get('expected_count'):
        reasons.append('Diagram count differs from the reviewed expectation.')
    if len(mermaid.get('diagrams',[])) != mermaid.get('diagram_count'):
        reasons.append('Per-diagram results are missing.')
    runtime_required=bool(mermaid.get('expected_count'))
    blocked=runtime_required and mermaid.get('runtime_status')!='EXECUTED'
    if not mermaid.get('passed') or blocked:
        reasons.append('Mermaid gate did not pass; parsing alone is insufficient.')
    if runtime_required and any(len(d.get('profiles',[]))!=2 or
        not all(p.get('passed') is True for p in d['profiles']) for d in mermaid.get('diagrams',[])):
        reasons.append('Not all diagrams completed both render profiles.')
    return {'status':'BLOCKED' if blocked else ('FAIL' if reasons else 'PASS'),
            'passed':not reasons and not blocked, 'markdown_sha256':digest,
            'reasons':reasons, 'content_checks':checks, 'mermaid':mermaid,
            'scope':'Content acceptance plus Mermaid legality/renderability; not proof of business correctness.'}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('markdown',type=Path)
    p.add_argument('--acceptance-json',type=Path,required=True)
    p.add_argument('--expected-count',type=int,required=True)
    g=p.add_mutually_exclusive_group()
    g.add_argument('--asset-map',type=Path);g.add_argument('--bundle',type=Path)
    p.add_argument('--version',default='unidentified')
    p.add_argument('--browser-path');p.add_argument('--artifacts',type=Path)
    p.add_argument('--json',type=Path,required=True)
    a=p.parse_args()
    if a.json.resolve() in (a.markdown.resolve(),a.acceptance_json.resolve()):
        p.error('Output JSON must not overwrite the Markdown or acceptance report.')
    try:
        acceptance=json.loads(a.acceptance_json.read_text(encoding='utf-8'))
        result=validate(a.markdown,asset_map=a.asset_map,bundle=a.bundle,version=a.version,
                        browser_path=a.browser_path,expected_count=a.expected_count,artifacts=a.artifacts)
        data=combine(a.markdown,acceptance,result)
    except (OSError,ValueError) as exc:
        data={'status':'BLOCKED','passed':False,'error':str(exc)}
    a.json.parent.mkdir(parents=True,exist_ok=True)
    a.json.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(data['status'],a.json)
    return 0 if data['passed'] else (2 if data['status']=='BLOCKED' else 1)

if __name__=='__main__':
    raise SystemExit(main())
