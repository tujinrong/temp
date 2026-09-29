"""Reproducible source-contract evaluation of up to five repair revisions.

The legacy score is diagnostic only. A PASS requires every acceptance check.
This is a deterministic strategy loop, not an autonomous code-writing agent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .evaluate_markdown import evaluate
from .semantic_repair import convert
from .spec_review import review, source_fingerprint
from .xlsx_to_markdown import convert_workbook

STRATEGIES = {
    1: 'Repository baseline (unmodified renderer)',
    2: 'Repair prose, domain organization and repeated metadata',
    3: 'Resolve supported counts; distinguish unspecified defaults',
    4: 'Preserve flow conditions and expose inference/source gaps',
    5: 'Recheck unresolved findings; no claim of a new automatic repair',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(xlsx: Path, contract: Path, output: Path, report_dir: Path, max_loops=5):
    if not 1 <= max_loops <= 5:
        raise ValueError('max_loops must be 1..5')
    source_before = sha(xlsx)
    contract_data = json.loads(contract.read_text(encoding='utf-8'))
    if source_fingerprint(xlsx) != contract_data['source_content_sha256']:
        raise ValueError('Unknown source contract: review the new workbook before scoring it.')
    report_dir.mkdir(parents=True, exist_ok=True)
    history = []
    last_issues = []
    for loop in range(1, max_loops + 1):
        candidate = report_dir / f'loop{loop}.md'
        text = convert_workbook(xlsx, fidelity=1) if loop == 1 else convert(xlsx, revision=loop)
        candidate.write_text(text, encoding='utf-8')
        acceptance = review(xlsx, candidate, contract)
        legacy = evaluate(xlsx, candidate).to_dict()
        payload = {
            'loop': loop, 'strategy': STRATEGIES[loop], 'candidate': str(candidate),
            'sha256': sha(candidate), 'responding_to': last_issues,
            'legacy_evaluation': legacy, 'acceptance': acceptance,
        }
        history.append(payload)
        (report_dir / f'loop{loop}.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        last_issues = [c['id'] for c in acceptance['checks'] if not c['passed']]
        print(f"Loop {loop}: {acceptance['passed_checks']}/{acceptance['total_checks']} checks; "
              f"{acceptance['status']}; legacy score={legacy['score']:.2f}")
        for check in acceptance['checks']:
            if not check['passed']:
                print(f"  {check['id']}: {check['check']}")
        if acceptance['passed']:
            break
        if loop > 1 and history[-2]['sha256'] == payload['sha256']:
            payload['no_progress'] = True
            break
    best = max(history, key=lambda entry: (entry['acceptance']['passed'], entry['acceptance']['passed_checks'], -entry['loop']))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(Path(best['candidate']).read_text(encoding='utf-8'), encoding='utf-8')
    if sha(xlsx) != source_before:
        raise RuntimeError('Source workbook changed during execution.')
    summary = {'source': str(xlsx), 'source_sha256': source_before,
               'source_content_sha256': source_fingerprint(xlsx),
               'contract': str(contract), 'contract_sha256': sha(contract),
               'final': str(output), 'selected_loop': best['loop'],
               'status': 'ACCEPTANCE_CHECKS_PASS' if best['acceptance']['passed'] else 'REVIEW_REQUIRED',
               'source_unchanged': True, 'loops': history}
    (report_dir / 'evaluation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Executed specification evolution loop', '',
             'The same 25 workbook-specific acceptance checks were applied to every candidate. '
             'The old heuristic score is shown for comparison, not as a measure of AI understanding.', '',
             '| Loop | Strategy | Legacy score | Acceptance checks | Outcome |', '|---|---|---:|---:|---|']
    for item in history:
        ev = item['acceptance']
        lines.append(f"| {item['loop']} | {item['strategy']} | {item['legacy_evaluation']['score']:.2f} | {ev['passed_checks']}/{ev['total_checks']} | {ev['status']} |")
    for item in history:
        lines += ['', f"## Loop {item['loop']}", '', f"Candidate SHA-256: `{item['sha256']}`", '']
        failures = [c for c in item['acceptance']['checks'] if not c['passed']]
        lines += [f"- {c['id']}: {c['check']}. {c['evidence_or_repair']}" for c in failures] or ['All checks passed.']
    lines += ['', '## Final result', '',
              f"Selected loop: {best['loop']}. Status: **{summary['status']}**.", '',
              'The source workbook was not modified. Unspecified interface behavior and uncertain diagram '
              'connections remain explicit review questions, not invented requirements.', '',
              '**Scope:** This run uses the synthetic Japanese login specification. '
              'A new workbook requires its own reviewed source contract. Passing these checks is not proof '
              'of visual fidelity, Mermaid browser rendering, LLM task accuracy, or general conversion accuracy.', '',
              f"Source SHA-256: `{source_before}`", '',
              f"Contract SHA-256: `{summary['contract_sha256']}`", '']
    (report_dir / 'evaluation.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xlsx', type=Path)
    parser.add_argument('--contract', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=Path('output/japanese_program_spec_test.md'))
    parser.add_argument('--report-dir', type=Path, default=Path('reports/evolution'))
    parser.add_argument('--max-loops', type=int, default=5, choices=range(1, 6))
    args = parser.parse_args()
    result = run(args.xlsx, args.contract, args.output, args.report_dir, args.max_loops)
    raise SystemExit(0 if result['status'] == 'ACCEPTANCE_CHECKS_PASS' else 2)


if __name__ == '__main__':
    main()
