from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from .evaluate_markdown import evaluate
from .xlsx_to_markdown import convert_workbook


def _report_markdown(stem: str, loops: list[dict], final_path: Path) -> str:
    lines = [f"# Conversion evaluation: {stem}", ""]
    for r in loops:
        ev = r["evaluation"]
        lines += [
            f"## Loop {r['loop']}", "",
            f"- Fidelity mode: {r['fidelity']}/5",
            f"- Score: **{ev['score']:.2f}/100**",
            f"- Result: **{'PASS' if ev['passed'] else 'RETRY'}**",
            f"- Worksheet coverage: {ev['sheet_coverage']:.2f}%",
            f"- Cell coverage: {ev['cell_coverage']:.2f}% ({ev['covered_cells']}/{ev['total_cells']})",
            f"- Formula coverage: {ev['formula_coverage']:.2f}%",
            f"- Structure score: {ev['structure_score']:.2f}%",
            f"- Layout score: {ev['layout_score']:.2f}%",
            "",
        ]
        if ev["issues"]:
            lines.append("### Problems detected")
            lines += [f"- {x}" for x in ev["issues"]]
            lines.append("")
        if ev["recommendations"]:
            lines.append("### Changes for next loop")
            lines += [f"- {x}" for x in ev["recommendations"]]
            lines.append("")
    final = loops[-1]["evaluation"]
    lines += [
        "## Final result", "",
        f"- Final Markdown: `{final_path.as_posix()}`",
        f"- Loops executed: {len(loops)}",
        f"- Final score: **{final['score']:.2f}/100**",
        f"- Final status: **{'PASS' if final['passed'] else 'BEST EFFORT / REVIEW REQUIRED'}**",
        "",
    ]
    return "\n".join(lines)


def run_quality_loop(xlsx: Path, output_dir: Path, report_dir: Path, threshold: float = 90.0, max_loops: int = 5):
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    stem = xlsx.stem
    loop_results = []
    final_candidate = None

    for loop in range(1, max_loops + 1):
        fidelity = min(loop, 5)
        candidate = report_dir / f"{stem}.pass{loop}.md"
        candidate.write_text(convert_workbook(xlsx, fidelity=fidelity), encoding="utf-8")
        ev = evaluate(xlsx, candidate, threshold=threshold)
        payload = {"loop": loop, "fidelity": fidelity, "candidate": str(candidate), "evaluation": ev.to_dict()}
        loop_results.append(payload)
        (report_dir / f"{stem}.pass{loop}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        print(f"Loop {loop}: score={ev.score:.2f} status={'PASS' if ev.passed else 'RETRY'} cell={ev.cell_coverage:.2f}% layout={ev.layout_score:.2f}%")
        for issue in ev.issues:
            print(f"  issue: {issue}")
        final_candidate = candidate
        if ev.passed:
            break

    final_path = output_dir / f"{stem}.md"
    shutil.copyfile(final_candidate, final_path)
    summary = _report_markdown(stem, loop_results, final_path)
    summary_path = report_dir / f"{stem}.evaluation.md"
    summary_path.write_text(summary, encoding="utf-8")
    json_path = report_dir / f"{stem}.evaluation.json"
    json_path.write_text(json.dumps({"source": str(xlsx), "final": str(final_path), "loops": loop_results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return final_path, summary_path, loop_results


def main() -> int:
    p = argparse.ArgumentParser(description="Convert XLSX to Markdown and evaluate/retry up to five times.")
    p.add_argument("xlsx")
    p.add_argument("--output-dir", default="output")
    p.add_argument("--report-dir", default="reports")
    p.add_argument("--threshold", type=float, default=90.0)
    p.add_argument("--max-loops", type=int, default=5, choices=range(1, 6))
    args = p.parse_args()
    final, summary, loops = run_quality_loop(Path(args.xlsx), Path(args.output_dir), Path(args.report_dir), args.threshold, args.max_loops)
    print(f"Final: {final}")
    print(f"Report: {summary}")
    print(f"Loops: {len(loops)}")
    return 0 if loops[-1]["evaluation"]["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
