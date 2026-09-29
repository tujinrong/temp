from __future__ import annotations

import argparse
import html
from pathlib import Path
import re
import unicodedata

from openpyxl.utils.cell import range_boundaries

from .xlsx_spec import SheetInfo, CellInfo, load_xlsx

META_KEYS = {
    '文書名','システム名','機能id','機能名','機能名称','画面名','画面名称','処理名','api名',
    '版','版数','バージョン','作成者','担当者','作成日','更新日','承認者','文書種別',
    'document name','system name','function id','function name','author','creator','date','version','document type'
}
REQ_TERMS = (
    '必須','以内','以上','以下','禁止','しない','とする','場合','遷移する','表示する','記録する',
    'ロックする','呼び出す','返却する','送信する','保存する','削除する','更新する','取得する',
    '成功時','失敗時','してください','required','must','shall','when','if ','error'
)


def esc(text: str) -> str:
    return str(text).replace('\\','\\\\').replace('|','\\|').replace('\n','<br>')


def norm(text: str) -> str:
    text = unicodedata.normalize('NFKC', str(text or '')).lower()
    return re.sub(r'\s+',' ',text).strip()


def anchors(sheet: SheetInfo, start_row: int = 1) -> list[CellInfo]:
    return [
        c for c in sheet.nonempty
        if c.row >= start_row and not (
            c.merged_range and c.coordinate != c.merged_range.split(':')[0]
        )
    ]


def rows(sheet: SheetInfo, start_row: int = 1) -> dict[int, list[CellInfo]]:
    out = {}
    for c in anchors(sheet, start_row):
        out.setdefault(c.row, []).append(c)
    for values in out.values():
        values.sort(key=lambda c: c.col)
    return out


def lookup(sheet: SheetInfo) -> dict[tuple[int, int], CellInfo]:
    return {(c.row, c.col): c for c in sheet.cells}


def metadata_pairs(sheet: SheetInfo, max_row: int) -> list[tuple[str, str]]:
    result = []
    seen = set()
    for r, items in sorted(rows(sheet).items()):
        if r > max_row:
            continue
        for i, cell in enumerate(items[:-1]):
            if norm(cell.text) in META_KEYS:
                value = items[i + 1].text.strip()
                if value and norm(value) not in META_KEYS:
                    key = (norm(cell.text), norm(value))
                    if key not in seen:
                        seen.add(key)
                        result.append((cell.text.strip(), value))
    return result


def render_header(sheet: SheetInfo) -> str:
    pairs = metadata_pairs(sheet, max(4, sheet.header_rows))
    if not pairs:
        return ''
    return '\n'.join(f'> **{k}:** {v}  ' for k, v in pairs).rstrip() + '\n\n'


def render_cover(sheet: SheetInfo) -> str:
    by_row = rows(sheet)
    rev_start = next(
        (r for r, items in by_row.items() if any('改訂履歴' in c.text for c in items)),
        None,
    )
    pairs = metadata_pairs(sheet, (rev_start - 1) if rev_start else min(sheet.max_row, 16))
    lines = ['## 文書情報', '', '| 項目 | 内容 |', '|---|---|']
    lines += [f'| {esc(k)} | {esc(v)} |' for k, v in pairs]

    if rev_start:
        table = []
        for r in sorted(x for x in by_row if x > rev_start):
            vals = [c.text.strip() for c in by_row[r] if c.text.strip()]
            if len(vals) >= 2:
                table.append(vals)
        if table:
            width = max(len(x) for x in table)
            table = [x + [''] * (width - len(x)) for x in table]
            lines += ['', '## 改訂履歴', '',
                      '| ' + ' | '.join(esc(x) for x in table[0]) + ' |',
                      '| ' + ' | '.join('---' for _ in range(width)) + ' |']
            lines += ['| ' + ' | '.join(esc(x) for x in xrow) + ' |' for xrow in table[1:]]
    return '\n'.join(lines).rstrip() + '\n'


def render_list(sheet: SheetInfo, start_row: int) -> str:
    by_row = rows(sheet, start_row)
    ordered = sorted(by_row)
    lines = []
    i = 0

    while i < len(ordered):
        r = ordered[i]
        items = by_row[r]

        if len(items) == 1:
            c = items[0]
            wide_merge = False
            if c.merged_range:
                a, _, b, _ = range_boundaries(c.merged_range)
                wide_merge = (b - a + 1) >= max(3, sheet.max_col // 2)
            if c.bold or wide_merge:
                lines += [f'### {c.text.strip()}', '']
            elif c.text.strip():
                lines += [c.text.strip(), '']
            i += 1
            continue

        if len(items) == 2:
            key = items[0].text.strip()
            value = items[1].text.strip()
            if value.startswith('='):
                value = 'calculated in source workbook'
            lines.append(f'- **{key}**: {value}')
            i += 1
            continue

        group = [r]
        j = i + 1
        while j < len(ordered) and len(by_row[ordered[j]]) >= 3:
            group.append(ordered[j])
            j += 1

        table = [[c.text.strip() for c in by_row[rr]] for rr in group]
        width = max(len(x) for x in table)
        table = [x + [''] * (width - len(x)) for x in table]
        lines += [
            '| ' + ' | '.join(esc(x) for x in table[0]) + ' |',
            '| ' + ' | '.join('---' for _ in range(width)) + ' |',
        ]
        lines += ['| ' + ' | '.join(esc(x) for x in vals) + ' |' for vals in table[1:]]
        lines.append('')
        i = j

    return '\n'.join(lines).rstrip() + '\n'


def flow_nodes(sheet: SheetInfo, start_row: int) -> list[CellInfo]:
    result = []
    for c in anchors(sheet, start_row):
        t = c.text.strip()
        if not t or len(t) > 160 or t in {sheet.name, '処理フロー', 'フロー', 'Process Flow'}:
            continue
        if t.startswith(('補足:', '補足：', 'Note:', 'NOTE:')):
            continue
        if c.merged_range or c.border or c.bold or any(
            x in t for x in ('開始','終了','判定','処理','入力','出力','確認')
        ):
            result.append(c)
    return sorted(result, key=lambda c: (c.row, c.col))


def render_flow(sheet: SheetInfo, start_row: int) -> str:
    nodes = flow_nodes(sheet, start_row)
    if len(nodes) < 2:
        return render_list(sheet, start_row)

    fence = chr(96) * 3
    lines = ['### 処理フロー', '', fence + 'mermaid', 'flowchart TD']
    ids = []
    for i, c in enumerate(nodes, 1):
        nid = f'N{i}'
        ids.append(nid)
        label = c.text.replace('"', "'").replace('\n', ' ')
        if any(w in label for w in ('?','？','判定','確認','有無','場合')):
            lines.append(f'    {nid}{{"{label}"}}')
        elif any(w in label for w in ('開始','終了','Start','End')):
            lines.append(f'    {nid}(["{label}"])')
        else:
            lines.append(f'    {nid}["{label}"]')

    i = 0
    while i < len(nodes) - 1:
        decision = any(w in nodes[i].text for w in ('?','？','判定','確認','有無','場合'))
        if decision and i + 2 < len(nodes) and nodes[i + 1].row == nodes[i + 2].row:
            lines.append(f'    {ids[i]} -->|いいえ| {ids[i + 1]}')
            lines.append(f'    {ids[i]} -->|はい| {ids[i + 2]}')
            if i + 3 < len(nodes):
                lines.append(f'    {ids[i + 1]} --> {ids[i + 3]}')
                lines.append(f'    {ids[i + 2]} --> {ids[i + 3]}')
                i += 3
            else:
                i += 2
        else:
            lines.append(f'    {ids[i]} --> {ids[i + 1]}')
            i += 1

    lines += [fence, '']
    for c in anchors(sheet, start_row):
        if c.text.strip().startswith(('補足:', '補足：', 'Note:', 'NOTE:')):
            lines.append(f'- {c.text.strip()}')
    lines.append('')
    return '\n'.join(lines)


def find_field_table(sheet: SheetInfo, start_row: int):
    by_row = rows(sheet, start_row)
    cells = lookup(sheet)

    for r in sorted(by_row):
        header_cells = by_row[r]
        labels = [norm(c.text) for c in header_cells]
        if '項目名' in labels and ('項目id' in labels or '種別' in labels):
            cols = [c.col for c in header_cells]
            headers = [c.text.strip() for c in header_cells]
            data = []
            rr = r + 1
            while rr <= sheet.max_row:
                vals = [cells[(rr, col)].text.strip() for col in cols]
                if any(vals):
                    data.append(vals)
                    rr += 1
                    continue
                if data:
                    break
                rr += 1
            return r, headers, data
    return None, None, []


def render_screen(sheet: SheetInfo, start_row: int) -> str:
    header_row, headers, data = find_field_table(sheet, start_row)
    lines = ['### 画面概要', '']

    notes = []
    for c in anchors(sheet, start_row):
        t = c.text.strip()
        if header_row and c.row >= header_row:
            continue
        if not t or t in {'1. 画面レイアウト','2. 画面項目定義','画面レイアウト','画面項目定義'}:
            continue
        if re.fullmatch(r'\[.*input.*\]', t, re.I):
            continue
        if re.fullmatch(r'[↓↑←→↔┌┐└┘─\s]+', t):
            continue
        if t not in notes:
            notes.append(t)

    if notes:
        lines += [f'- {esc(t)}' for t in notes]
    lines.append('')

    if not headers or not data:
        lines += ['### 画面項目', '', render_list(sheet, start_row)]
        return '\n'.join(lines).rstrip() + '\n'

    width = len(headers)
    data = [x + [''] * (width - len(x)) for x in data]
    lines += [
        '### 画面項目', '',
        '| ' + ' | '.join(esc(x) for x in headers) + ' |',
        '| ' + ' | '.join('---' for _ in headers) + ' |',
    ]
    lines += ['| ' + ' | '.join(esc(x) for x in row[:width]) + ' |' for row in data]
    lines += ['', '### 画面フォーム参考', '', '<form>']

    index = {norm(h): i for i, h in enumerate(headers)}
    for row in data:
        def get(name):
            i = index.get(norm(name))
            return row[i].strip() if i is not None and i < len(row) else ''

        label = get('項目名')
        fid = get('項目ID')
        typ = get('種別').lower()
        required = get('必須')
        length = get('桁数')

        if not label:
            continue
        req = ' required' if required in {'○','必須','yes','true'} else ''
        maxlen = f' maxlength="{html.escape(length)}"' if length.isdigit() else ''

        if typ in {'text','password','email','number'}:
            lines.append(
                f'  <label>{html.escape(label)} '
                f'<input type="{html.escape(typ)}" name="{html.escape(fid or label)}"{maxlen}{req}></label><br>'
            )
        elif typ == 'button':
            button_type = 'reset' if 'クリア' in label or 'reset' in fid.lower() else 'button'
            lines.append(
                f'  <button type="{button_type}" id="{html.escape(fid or label)}">{html.escape(label)}</button>'
            )

    lines += ['</form>', '']
    return '\n'.join(lines).rstrip() + '\n'


def render_semantic(sheet: SheetInfo) -> str:
    start = sheet.header_rows + 1 if sheet.header_rows else 1
    out = []
    if sheet.kind != 'cover' and sheet.header_rows:
        out.append(render_header(sheet))

    if sheet.kind == 'cover':
        out.append(render_cover(sheet))
    elif sheet.kind == 'flow':
        out.append(render_flow(sheet, start))
    elif sheet.kind == 'screen':
        out.append(render_screen(sheet, start))
    else:
        out.append(render_list(sheet, start))
    return '\n'.join(out)


def requirements(info) -> list[str]:
    result = []
    seen = set()
    for sheet in info.sheets:
        if sheet.kind not in {'article','flow','screen','grid'}:
            continue
        for c in anchors(sheet):
            t = c.text.strip()
            nt = norm(t)
            if c.bold or len(t) < 12 or not any(term.lower() in nt for term in REQ_TERMS):
                continue
            if nt not in seen:
                seen.add(nt)
                result.append(t)
    return result


def unmapped_facts(info, rendered: str) -> dict[str, list[str]]:
    nrendered = norm(rendered)
    trivial = {norm(x) for x in {
        '機能名','作成者','作成日','版数','文書種別','改訂履歴',
        '処理フロー','画面レイアウト','画面項目定義'
    }}
    result = {}

    for sheet in info.sheets:
        values = []
        seen = set()
        for c in anchors(sheet):
            t = c.text.strip()
            nt = norm(t)
            if not t or nt in trivial or t.startswith('='):
                continue
            if re.fullmatch(r'[↓↑←→↔┌┐└┘─\s]+', t):
                continue
            if nt in nrendered or nt in seen:
                continue
            seen.add(nt)
            values.append(t)
        if values:
            result[sheet.name] = values
    return result


def document_title(info) -> str:
    cover = next((s for s in info.sheets if s.kind == 'cover'), None)
    if cover:
        for c in anchors(cover):
            t = c.text.strip()
            if c.bold and len(t) >= 3 and '改訂' not in t:
                return re.sub(r'\s+', ' ', t.replace('\n', ' ')).strip()
    return info.title


def convert_workbook(path: str | Path, fidelity: int = 1) -> str:
    info = load_xlsx(path)
    lines = [
        f'# {document_title(info)}',
        '',
        f'> Source workbook: {Path(path).name} · Semantic conversion pass: {fidelity}/5',
        '',
    ]

    for sheet in info.sheets:
        if sheet.kind == 'cover':
            lines.append(render_semantic(sheet))
        else:
            lines += [f'## {sheet.name}', '', render_semantic(sheet)]

    if fidelity >= 2:
        lines += ['## AI analysis index', '', '| Source section | Type |', '|---|---|']
        lines += [f'| {esc(s.name)} | {s.kind} |' for s in info.sheets]
        lines.append('')

    if fidelity >= 3:
        reqs = requirements(info)
        if reqs:
            lines += ['## Extracted requirements and rules', '']
            lines += [f'- **REQ-{i:03d}**: {esc(value)}' for i, value in enumerate(reqs, 1)]
            lines.append('')

    if fidelity >= 4:
        lines += ['## Source traceability', '']
        lines += [
            f'- **{s.name}**: rendered as {s.kind} content; visual Excel layout is intentionally not reproduced.'
            for s in info.sheets
        ]
        lines.append('')

    if fidelity >= 5:
        missing = unmapped_facts(info, '\n'.join(lines))
        if missing:
            lines += [
                '## Additional source facts', '',
                '> These facts were not represented elsewhere and are preserved as semantic notes, not cell-coordinate dumps.',
                '',
            ]
            for sheet_name, values in missing.items():
                lines += [f'### {sheet_name}', '']
                lines += [f'- {esc(v)}' for v in values]
                lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def main() -> int:
    p = argparse.ArgumentParser(
        description='Convert .xlsx programming/system specifications into AI-readable Markdown.'
    )
    p.add_argument('xlsx')
    p.add_argument('-o', '--output')
    p.add_argument('--fidelity', type=int, choices=range(1, 6), default=1)
    a = p.parse_args()

    output = Path(a.output) if a.output else Path('output') / (Path(a.xlsx).stem + '.md')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(convert_workbook(a.xlsx, a.fidelity), encoding='utf-8')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
