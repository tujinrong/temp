from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import html
import json
from pathlib import Path
import re
import unicodedata

from .xlsx_spec import WorkbookInfo, load_xlsx


def norm(s: str) -> str:
    s = html.unescape(s)
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\\|", "|").replace("\\`", "`")
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


@dataclass
class Evaluation:
    score: float
    passed: bool
    threshold: float
    sheet_coverage: float
    cell_coverage: float
    formula_coverage: float
    structure_score: float
    layout_score: float
    covered_cells: int
    total_cells: int
    issues: list[str]
    recommendations: list[str]

    def to_dict(self):
        return asdict(self)


def evaluate(xlsx: str | Path, markdown: str | Path, threshold: float = 90.0) -> Evaluation:
    info = load_xlsx(xlsx)
    md = Path(markdown).read_text(encoding="utf-8")
    nmd = norm(md)
    issues: list[str] = []
    recs: list[str] = []

    nonempty_sheets = [s for s in info.sheets if s.nonempty]
    sheet_hits = sum(1 for s in nonempty_sheets if norm(s.name) in nmd)
    sheet_cov = sheet_hits / len(nonempty_sheets) if nonempty_sheets else 1.0
    if sheet_cov < 1:
        issues.append(f"Missing {len(nonempty_sheets)-sheet_hits} worksheet name(s) in Markdown.")
        recs.append("Include an explicit section for every non-empty worksheet.")

    cells = []
    for s in nonempty_sheets:
        for c in s.nonempty:
            if c.text or c.formula:
                cells.append((s, c))
    covered = 0
    missing_examples = []
    for s, c in cells:
        txt = norm(c.text)
        formula = norm(c.formula or "")
        hit = (txt and txt in nmd) or (formula and formula in nmd)
        if hit:
            covered += 1
        elif len(missing_examples) < 12:
            missing_examples.append(f"{s.name}!{c.coordinate}={c.text or c.formula}")
    cell_cov = covered / len(cells) if cells else 1.0
    if cell_cov < 0.95:
        issues.append(f"Cell-value coverage is {cell_cov:.1%}; examples: " + "; ".join(missing_examples[:6]))
        recs.append("Add a source-grid/audit appendix for source values that semantic rendering omits.")

    formulas = [(s, c) for s, c in cells if c.formula]
    formula_hits = sum(1 for _, c in formulas if norm(c.formula or "") in nmd)
    formula_cov = formula_hits / len(formulas) if formulas else 1.0
    if formulas and formula_cov < 0.9:
        issues.append(f"Formula coverage is {formula_cov:.1%} ({formula_hits}/{len(formulas)}).")
        recs.append("Include original formulas in a technical appendix.")

    structure_parts = []
    structure_parts.append(1.0 if re.search(r"^#\s+", md, re.M) else 0.0)
    structure_parts.append(1.0 if re.search(r"^##\s+", md, re.M) else 0.0)
    flow_sheets = [s for s in nonempty_sheets if s.kind == "flow"]
    if flow_sheets:
        structure_parts.append(1.0 if "```mermaid" in md else 0.4 if "|" in md else 0.0)
    screen_sheets = [s for s in nonempty_sheets if s.kind == "screen"]
    if screen_sheets:
        structure_parts.append(1.0 if "<table" in md.lower() or "<form" in md.lower() else 0.5 if "|" in md else 0.0)
    structure = sum(structure_parts) / len(structure_parts)
    if structure < 0.85:
        issues.append("Semantic Markdown structure is weak for one or more sheet types.")
        recs.append("Use Mermaid for flow sheets and HTML/Markdown tables for screen or form specifications.")

    merge_count = sum(len(s.merged_ranges) for s in nonempty_sheets)
    narrow_count = sum(sum(1 for w in s.column_widths.values() if w <= 3.0) for s in nonempty_sheets)
    layout_components = []
    if merge_count:
        merge_tokens = sum(1 for s in nonempty_sheets for rng in s.merged_ranges if norm(rng) in nmd)
        layout_components.append(min(1.0, merge_tokens / max(1, merge_count)))
    if narrow_count:
        layout_components.append(1.0 if "narrow grid" in nmd or "col_width=" in nmd or "data-grid-width" in nmd else 0.5)
    layout = sum(layout_components) / len(layout_components) if layout_components else 1.0
    if layout < 0.7:
        issues.append("Merged-cell or narrow-grid layout information is underrepresented.")
        recs.append("Preserve merged ranges and width≈2 layout-grid information in HTML or metadata.")

    score = 100 * (0.15 * sheet_cov + 0.55 * cell_cov + 0.10 * formula_cov + 0.12 * structure + 0.08 * layout)
    score = round(score, 2)
    return Evaluation(
        score=score,
        passed=score >= threshold and sheet_cov == 1.0 and cell_cov >= 0.90,
        threshold=threshold,
        sheet_coverage=round(100 * sheet_cov, 2),
        cell_coverage=round(100 * cell_cov, 2),
        formula_coverage=round(100 * formula_cov, 2),
        structure_score=round(100 * structure, 2),
        layout_score=round(100 * layout, 2),
        covered_cells=covered,
        total_cells=len(cells),
        issues=issues,
        recommendations=recs,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Evaluate Excel-to-Markdown conversion fidelity.")
    p.add_argument("xlsx")
    p.add_argument("markdown")
    p.add_argument("--threshold", type=float, default=90.0)
    p.add_argument("--json", dest="json_path")
    args = p.parse_args()
    result = evaluate(args.xlsx, args.markdown, args.threshold)
    data = result.to_dict()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
