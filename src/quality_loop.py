from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from .evaluate_markdown import evaluate
from .xlsx_to_markdown import convert_workbook

STRATEGIES = {
    1: 'semantic-baseline',
    2: 'analysis-index',
    3: 'requirements-explicit',
    4: 'traceability-enhanced',
    5: 'semantic-recovery',
}


def _report_markdown(stem: str, loops: list[dict], final_path: Path) -> str:
    lines = [
        f'# AI-readable specification evaluation: {stem}',
        '',
        '> Goal: produce a human-written Markdown specification optimized for AI understanding and analysis, not an Excel-shaped transcription.',
        '',
    ]
    for r in loops:
        ev = r['evaluation']
        lines += [
            f"## Loop {r['loop']}", '',
            f"Strategy: {r['strategy']}",
            f"Score: **{ev['score']:.2f}/100**",
            f"Result: **{'PASS' if ev['passed'] else 'RETRY'}**",
            f"Sheet traceability: {ev['sheet_coverage']:.2f}%",
            f"Meaningful content coverage: {ev['content_coverage']:.2f}% ({ev['covered_values']}/{ev['total_values']})",
            f"Metadata score: {ev['metadata_score']:.2f}%",
            f"Specification structure: {ev['structure_score']:.2f}%",
            f"Requirement explicitness: {ev['requirement_score']:.2f}%",
            f"AI readability: {ev['ai_readability_score']:.2f}%",
            f"Spreadsheet-artifact penalty: {ev['spreadsheet_artifact_penalty']:.2f}%",
            '',
        ]
        if ev['issues']:
            lines += ['### Problems detected', ''] + [f'- {x}' for x in ev['issues']] + ['']
        if ev['recommendations']:
            lines += ['### Changes for next loop', ''] + [f'- {x}' for x in ev['recommendations']] + ['']

    final = loops[-1]['evaluation']
    lines += [
        '## Final result', '',
        f'Final Markdown: {final_path.as_posix()}',
        f'Loops executed: {len(loops)}',
        f"Final score: **{final['score']:.2f}/100**",
        f"Final status: **{'PASS' if final['passed'] else 'BEST EFFORT / REVIEW REQUIRED'}**",
        '',
    ]
    return '\n'.join(lines)


def run_quality_loop(
    xlsx: Path,
    output_dir: Path,
    report_dir: Path,
    threshold: float = 88.0,
    max_loops: int = 5,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    stem = xlsx.stem
    loop_results = []
    final_candidate = None

    for loop in range(1, max_loops + 1):
        candidate = report_dir / f'{stem}.pass{loop}.md'
        candidate.write_text(convert_workbook(xlsx, fidelity=loop), encoding='utf-8')
        ev = evaluate(xlsx, candidate, threshold=threshold)
        payload = {
            'loop': loop,
            'strategy': STRATEGIES[loop],
            'candidate': str(candidate),
            'evaluation': ev.to_dict(),
        }
        loop_results.append(payload)
        (report_dir / f'{stem}.pass{loop}.json').write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )

        print(
            f"Loop {loop} [{STRATEGIES[loop]}]: "
            f"score={ev.score:.2f} "
            f"status={'PASS' if ev.passed else 'RETRY'} "
            f"content={ev.content_coverage:.2f}% "
            f"ai={ev.ai_readability_score:.2f}%"
        )
        for issue in ev.issues:
            print(f'  issue: {issue}')

        final_candidate = candidate
        if ev.passed:
            break

    final_path = output_dir / f'{stem}.md'
    shutil.copyfile(final_candidate, final_path)

    summary_path = report_dir / f'{stem}.evaluation.md'
    summary_path.write_text(
        _report_markdown(stem, loop_results, final_path),
        encoding='utf-8',
    )
    (report_dir / f'{stem}.evaluation.json').write_text(
        json.dumps(
            {'source': str(xlsx), 'final': str(final_path), 'loops': loop_results},
            ensure_ascii=False,
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    return final_path, summary_path, loop_results


def main():
    p = argparse.ArgumentParser(
        description='Convert XLSX to AI-readable Markdown and evaluate/retry up to five semantic passes.'
    )
    p.add_argument('xlsx')
    p.add_argument('--output-dir', default='output')
    p.add_argument('--report-dir', default='reports')
    p.add_argument('--threshold', type=float, default=88.0)
    p.add_argument('--max-loops', type=int, default=5, choices=range(1, 6))
    a = p.parse_args()

    final, summary, loops = run_quality_loop(
        Path(a.xlsx),
        Path(a.output_dir),
        Path(a.report_dir),
        a.threshold,
        a.max_loops,
    )
    print(f'Final: {final}')
    print(f'Report: {summary}')
    print(f'Loops: {len(loops)}')
    raise SystemExit(0 if loops[-1]['evaluation']['passed'] else 2)


if __name__ == '__main__':
    main()
