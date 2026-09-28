from __future__ import annotations

import argparse
import html
from pathlib import Path
import re

from openpyxl.utils.cell import range_boundaries

from .xlsx_spec import WorkbookInfo, SheetInfo, CellInfo, effective_columns, load_xlsx


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def md_code(text: str) -> str:
    return text.replace("`", "\\`")


def _cell_lookup(sheet: SheetInfo) -> dict[tuple[int, int], CellInfo]:
    return {(c.row, c.col): c for c in sheet.cells}


def _merge_anchors(sheet: SheetInfo) -> dict[tuple[int, int], tuple[int, int, str]]:
    result = {}
    for rng in sheet.merged_ranges:
        min_col, min_row, max_col, max_row = range_boundaries(rng)
        result[(min_row, min_col)] = (max_row, max_col, rng)
    return result


def _first_nonempty_in_rows(sheet: SheetInfo, first: int, last: int) -> list[CellInfo]:
    return [c for c in sheet.nonempty if first <= c.row <= last]


def _render_header(sheet: SheetInfo) -> str:
    if not sheet.header_rows:
        return ""
    cells = _first_nonempty_in_rows(sheet, 1, sheet.header_rows)
    if not cells:
        return ""
    lines = ["### Sheet header", "", "| Cell | Value |", "|---|---|"]
    for c in cells:
        if c.merged_range and c.coordinate != c.merged_range.split(":")[0]:
            continue
        lines.append(f"| `{c.coordinate}` | {esc(c.text)} |")
    return "\n".join(lines) + "\n\n"


def _render_cover(sheet: SheetInfo) -> str:
    cells = [c for c in sheet.nonempty if not (c.merged_range and c.coordinate != c.merged_range.split(":")[0])]
    cells.sort(key=lambda c: (c.row, c.col))
    if not cells:
        return "_Empty cover sheet._\n"
    title = next((c.text for c in cells if c.bold and len(c.text) >= 3), None) or cells[0].text
    lines = [f"# {title}", "", "| Item | Value |", "|---|---|"]
    # Pair labels and values by row, a common cover-page pattern.
    by_row: dict[int, list[CellInfo]] = {}
    for c in cells:
        by_row.setdefault(c.row, []).append(c)
    used = set()
    for row, items in sorted(by_row.items()):
        items.sort(key=lambda c: c.col)
        if len(items) >= 2:
            label = items[0].text
            value = " / ".join(x.text for x in items[1:] if x.text)
            lines.append(f"| {esc(label)} | {esc(value)} |")
            used.update(x.coordinate for x in items)
    for c in cells:
        if c.coordinate not in used and c.text != title:
            lines.append(f"| `{c.coordinate}` | {esc(c.text)} |")
    return "\n".join(lines) + "\n"


def _rectangular_region(sheet: SheetInfo, start_row: int) -> tuple[list[int], list[int]]:
    rows = sorted({c.row for c in sheet.nonempty if c.row >= start_row})
    cols = effective_columns(sheet)
    # Only keep columns that actually have data in body to avoid wide visual-grid sheets.
    body_cols = [col for col in cols if any(c.col == col and c.row >= start_row and c.text for c in sheet.nonempty)]
    return rows, body_cols


def _render_table(sheet: SheetInfo, start_row: int = 1) -> str:
    rows, cols = _rectangular_region(sheet, start_row)
    if not rows or not cols:
        return "_No data._\n"
    lookup = _cell_lookup(sheet)
    anchors = _merge_anchors(sheet)

    # Choose first body row as header when it looks label-like; otherwise use coordinates.
    first = rows[0]
    first_values = [lookup[(first, c)].text for c in cols]
    header_score = sum(bool(x) for x in first_values)
    use_first_as_header = header_score >= max(1, len(cols) // 2)
    headers = first_values if use_first_as_header else [f"Col {c}" for c in cols]
    data_rows = rows[1:] if use_first_as_header else rows

    lines = ["| " + " | ".join(esc(x) for x in headers) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in data_rows:
        values = []
        for c in cols:
            cell = lookup[(r, c)]
            text = cell.text
            # Empty members of merged regions intentionally remain empty; anchor holds text.
            values.append(esc(text))
        if any(v for v in values):
            lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def _render_list(sheet: SheetInfo, start_row: int) -> str:
    anchors = [
        c for c in sheet.nonempty
        if c.row >= start_row and not (c.merged_range and c.coordinate != c.merged_range.split(":")[0])
    ]
    by_row: dict[int, list[CellInfo]] = {}
    for c in anchors:
        by_row.setdefault(c.row, []).append(c)
    rows = sorted(by_row)
    lines: list[str] = []
    i = 0
    while i < len(rows):
        r = rows[i]
        items = sorted(by_row[r], key=lambda c: c.col)
        if len(items) == 1:
            c = items[0]
            if c.bold or (c.merged_range and range_boundaries(c.merged_range)[2] - range_boundaries(c.merged_range)[0] + 1 >= max(3, sheet.max_col // 2)):
                lines += [f"### {c.text}", ""]
            else:
                lines += [c.text, ""]
            i += 1
            continue
        if len(items) == 2:
            lines.append(f"- **{items[0].text}**: {items[1].text}")
            i += 1
            continue
        # Table group: consecutive rows with at least three logical merged anchors.
        group = [r]
        j = i + 1
        while j < len(rows) and len(by_row[rows[j]]) >= 3:
            group.append(rows[j])
            j += 1
        table_rows = [[c.text for c in sorted(by_row[rr], key=lambda c: c.col)] for rr in group]
        width = max(len(x) for x in table_rows)
        table_rows = [x + [""] * (width - len(x)) for x in table_rows]
        lines.append("| " + " | ".join(esc(x) for x in table_rows[0]) + " |")
        lines.append("| " + " | ".join("---" for _ in range(width)) + " |")
        for vals in table_rows[1:]:
            lines.append("| " + " | ".join(esc(x) for x in vals) + " |")
        lines.append("")
        i = j
    return "\n".join(lines).rstrip() + "\n"

def _flow_nodes(sheet: SheetInfo, start_row: int) -> list[CellInfo]:
    candidates = []
    for c in sheet.nonempty:
        if c.row < start_row:
            continue
        if c.merged_range and c.coordinate != c.merged_range.split(":")[0]:
            continue
        t = c.text.strip()
        if not t or len(t) > 160:
            continue
        # Prefer merged, bordered or bold cells: common visual boxes in Japanese specs.
        if c.merged_range or c.border or c.bold or any(x in t for x in ("開始", "終了", "判定", "処理", "入力", "出力", "確認")):
            candidates.append(c)
    return sorted(candidates, key=lambda c: (c.row, c.col))


def _render_flow(sheet: SheetInfo, start_row: int) -> str:
    nodes = [
        c for c in _flow_nodes(sheet, start_row)
        if c.text.strip() not in {sheet.name, "処理フロー", "フロー", "Process Flow"}
        and not c.text.strip().startswith(("補足:", "補足：", "Note:", "NOTE:"))
    ]
    if len(nodes) < 2:
        return _render_table(sheet, start_row)
    lines = ["```mermaid", "flowchart TD"]
    ids = []
    for i, c in enumerate(nodes, 1):
        nid = f"N{i}"
        ids.append(nid)
        label = c.text.replace('"', "'").replace("\n", " ")
        is_decision = any(w in label for w in ("?", "？", "判定", "確認", "有無", "場合"))
        if is_decision:
            lines.append(f'    {nid}{{"{label}"}}')
        elif any(w in label for w in ("開始", "終了", "Start", "End")):
            lines.append(f'    {nid}(["{label}"])')
        else:
            lines.append(f'    {nid}["{label}"]')

    i = 0
    while i < len(nodes) - 1:
        cur = nodes[i]
        label = cur.text
        is_decision = any(w in label for w in ("?", "？", "判定", "確認", "有無", "場合"))
        if is_decision and i + 2 < len(nodes) and nodes[i + 1].row == nodes[i + 2].row:
            left_i, right_i = i + 1, i + 2
            left, right = nodes[left_i], nodes[right_i]
            # left/right labels follow the common Japanese spec convention.
            lines.append(f"    {ids[i]} -->|いいえ| {ids[left_i]}")
            lines.append(f"    {ids[i]} -->|はい| {ids[right_i]}")
            if i + 3 < len(nodes):
                join_id = ids[i + 3]
                lines.append(f"    {ids[left_i]} --> {join_id}")
                lines.append(f"    {ids[right_i]} --> {join_id}")
                i += 3
            else:
                i += 2
        else:
            lines.append(f"    {ids[i]} --> {ids[i + 1]}")
            i += 1
    lines += ["```", "", "> Flow connections are inferred from the cell layout. Decision labels use the common left=いいえ / right=はい convention when two branches appear on the same row.", ""]
    notes = [c.text for c in sheet.nonempty if c.row >= start_row and c.text.strip().startswith(("補足:", "補足：", "Note:", "NOTE:"))]
    for note in notes:
        lines.append(f"> {esc(note)}")
    if notes:
        lines.append("")
    return "\n".join(lines)


def _render_article(sheet: SheetInfo, start_row: int) -> str:
    anchors = [
        c for c in sheet.nonempty
        if c.row >= start_row and not (c.merged_range and c.coordinate != c.merged_range.split(":")[0])
    ]
    by_row: dict[int, list[CellInfo]] = {}
    for c in anchors:
        by_row.setdefault(c.row, []).append(c)
    rows = sorted(by_row)
    lines: list[str] = []
    i = 0
    heading_re = re.compile(r"^\s*\d+(?:\.\d+)*[\.．\s]")
    while i < len(rows):
        r = rows[i]
        items = sorted(by_row[r], key=lambda c: c.col)
        if len(items) == 1 and (heading_re.search(items[0].text) or (items[0].bold and items[0].merged_range)):
            lines += [f"### {items[0].text.strip()}", ""]
            i += 1
            continue
        if len(items) == 1:
            t = items[0].text.strip()
            if t.startswith(("・", "- ", "※", "○")):
                lines.append(f"- {t.lstrip('・※○- ').strip()}")
            else:
                lines += [t, ""]
            i += 1
            continue
        # Multiple anchors on a row usually indicate a definition/message table.
        group = [r]
        width = len(items)
        j = i + 1
        while j < len(rows):
            nxt = sorted(by_row[rows[j]], key=lambda c: c.col)
            if len(nxt) < 2 or heading_re.search(nxt[0].text):
                break
            group.append(rows[j])
            j += 1
        table_rows = [[c.text for c in sorted(by_row[rr], key=lambda c: c.col)] for rr in group]
        maxw = max(len(x) for x in table_rows)
        table_rows = [x + [""] * (maxw - len(x)) for x in table_rows]
        lines.append("| " + " | ".join(esc(x) for x in table_rows[0]) + " |")
        lines.append("| " + " | ".join("---" for _ in range(maxw)) + " |")
        for rowvals in table_rows[1:]:
            lines.append("| " + " | ".join(esc(x) for x in rowvals) + " |")
        lines.append("")
        i = j
    return "\n".join(lines).rstrip() + "\n"

def _looks_like_form(sheet: SheetInfo) -> bool:
    body = " ".join(c.text.lower() for c in sheet.nonempty[:120])
    return sheet.kind == "screen" or sum(k in body for k in ("項目名", "入力", "必須", "桁数", "型", "表示", "画面")) >= 2


def _render_form(sheet: SheetInfo, start_row: int) -> str:
    # HTML table is intentionally used for screen/form design because Markdown tables
    # cannot express colspan well and Japanese specs frequently use merged grid cells.
    lookup = _cell_lookup(sheet)
    anchors = _merge_anchors(sheet)
    covered: set[tuple[int, int]] = set()
    cols = [c for c in range(1, sheet.max_col + 1) if c not in sheet.hidden_cols]
    rows = [r for r in range(start_row, sheet.max_row + 1) if r not in sheet.hidden_rows]
    if len(cols) > 40:
        cols = effective_columns(sheet, narrow_threshold=3.0)
    lines = ['<table class="excel-form">']
    for r in rows:
        vals = []
        for c in cols:
            if (r, c) in covered:
                continue
            cell = lookup[(r, c)]
            attrs = []
            if (r, c) in anchors:
                max_row, max_col, _ = anchors[(r, c)]
                colspan = sum(1 for x in cols if c <= x <= max_col)
                rowspan = max_row - r + 1
                if colspan > 1:
                    attrs.append(f'colspan="{colspan}"')
                if rowspan > 1:
                    attrs.append(f'rowspan="{rowspan}"')
                for rr in range(r, max_row + 1):
                    for cc in range(c, max_col + 1):
                        if (rr, cc) != (r, c):
                            covered.add((rr, cc))
            width = sheet.column_widths.get(c, 13.0)
            if width <= 3.0:
                attrs.append('data-grid-width="narrow"')
            tag = "th" if cell.bold else "td"
            vals.append(f"<{tag} {' '.join(attrs)}>{html.escape(cell.text).replace(chr(10), '<br>')}</{tag}>")
        if vals and any(lookup[(r, c)].text for c in cols):
            lines.append("  <tr>" + "".join(vals) + "</tr>")
    lines.append("</table>")
    return "\n".join(lines) + "\n"


def _render_semantic(sheet: SheetInfo) -> str:
    start = sheet.header_rows + 1 if sheet.header_rows else 1
    out = []
    if sheet.header_rows:
        out.append(_render_header(sheet))
    if sheet.kind == "cover":
        out.append(_render_cover(sheet))
    elif sheet.kind == "flow":
        out.append(_render_flow(sheet, start))
    elif sheet.kind == "article":
        out.append(_render_article(sheet, start))
    elif sheet.kind == "list":
        out.append(_render_list(sheet, start))
    elif _looks_like_form(sheet):
        out.append(_render_form(sheet, start))
    else:
        out.append(_render_table(sheet, start))
    return "\n".join(out)


def _source_grid(sheet: SheetInfo, include_style: bool = False, include_formula: bool = False) -> str:
    lines = ["### Source grid", "", "| Cell | Value |" + (" Formula |" if include_formula else "") + (" Layout |" if include_style else ""),
             "|---|---|" + ("---|" if include_formula else "") + ("---|" if include_style else "")]
    for c in sheet.nonempty:
        if c.merged_range and c.coordinate != c.merged_range.split(":")[0] and not c.text:
            continue
        row = f"| `{c.coordinate}` | {esc(c.text)} |"
        if include_formula:
            row += f" {esc(c.formula or '')} |"
        if include_style:
            bits = []
            if c.merged_range: bits.append(f"merge={c.merged_range}")
            if c.bold: bits.append("bold")
            if c.border: bits.append("border")
            if c.number_format and c.number_format != "General": bits.append(f"format={md_code(c.number_format)}")
            width = sheet.column_widths.get(c.col, 13.0)
            if width <= 3.0: bits.append(f"col_width={width:g}")
            row += f" {esc('; '.join(bits))} |"
        lines.append(row)
    return "\n".join(lines) + "\n"


def convert_workbook(path: str | Path, fidelity: int = 1) -> str:
    info = load_xlsx(path)
    lines = [f"# {info.title}", "", f"> Converted from `{Path(path).name}`. Fidelity level: {fidelity}/5.", ""]
    for sheet in info.sheets:
        lines += [f"## {sheet.name}", "", f"<!-- sheet-kind: {sheet.kind}; rows: {sheet.max_row}; columns: {sheet.max_col} -->", ""]
        lines.append(_render_semantic(sheet))
        if fidelity == 2 and sheet.kind in {"flow", "screen"}:
            lines.append(_source_grid(sheet, include_style=False, include_formula=False))
        if fidelity >= 3:
            lines.append(_source_grid(sheet, include_style=False, include_formula=False))
        if fidelity >= 4:
            lines.append("### Workbook layout metadata\n")
            lines.append(f"- Merged ranges: {', '.join(sheet.merged_ranges) if sheet.merged_ranges else 'none'}")
            narrow = [f"{c}={w:g}" for c, w in sheet.column_widths.items() if w <= 3.0]
            lines.append(f"- Narrow grid columns (width ≤ 3): {', '.join(narrow) if narrow else 'none'}")
            lines.append(f"- Charts: {sheet.charts}; images: {sheet.images}\n")
            lines.append(_source_grid(sheet, include_style=True, include_formula=True))
        if fidelity >= 5:
            lines.append("### Audit inventory\n")
            lines.append("This inventory is intentionally verbose so every non-empty source cell and formula can be audited.\n")
            for c in sheet.nonempty:
                formula = f"; formula={md_code(c.formula)}" if c.formula else ""
                merge = f"; merge={c.merged_range}" if c.merged_range else ""
                lines.append(f"- `{sheet.name}!{c.coordinate}` = {esc(c.text)}{formula}{merge}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Convert .xlsx program specifications to Markdown.")
    p.add_argument("xlsx", help="Input .xlsx file")
    p.add_argument("-o", "--output", help="Output Markdown path")
    p.add_argument("--fidelity", type=int, choices=range(1, 6), default=1)
    args = p.parse_args()
    output = Path(args.output) if args.output else Path("output") / (Path(args.xlsx).stem + ".md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(convert_workbook(args.xlsx, args.fidelity), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
