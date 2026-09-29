"""Source-driven repair strategies. No LLM calls or workbook writes.

Revisions are frozen for the recorded experiment: 2 = structure, 3 = data
semantics, 4 = guarded flows and explicit review questions. The algorithm is
heuristic; unrecognized layouts still require source review.
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from . import xlsx_to_markdown as old
from .xlsx_spec import SheetInfo, CellInfo, load_xlsx


def text_cell(cell: CellInfo, sheet: SheetInfo, revision: int) -> str:
    if not cell.formula:
        return cell.text
    if revision < 3:
        return "calculated in source workbook"
    if cell.text != cell.formula:
        return cell.text + "（原本の保存済み計算値。鮮度は未検証）"
    # Intentionally support only a direct local COUNTA over literal cells.
    match = re.fullmatch(r"=COUNTA\(([A-Z]+\d+):([A-Z]+\d+)\)", cell.formula, re.I)
    if match:
        a, b, c, d = old.range_boundaries(":".join(match.groups()))
        selected = [v for v in sheet.cells if a <= v.col <= c and b <= v.row <= d]
        if not any(v.formula for v in selected):
            count = sum(v.value is not None for v in selected)
            return f"{count}（参照範囲の空でない項目を検算。Excel全体の再計算ではない）"
    return "計算結果は未確定（保存済み値なし・この数式の評価は未対応）"


def blocks(sheet: SheetInfo, revision: int) -> str:
    by_row = old.rows(sheet, sheet.header_rows + 1)
    keys = sorted(by_row)
    lookup = old.lookup(sheet)
    lines = []
    i = 0
    while i < len(keys):
        r = keys[i]
        items = by_row[r]
        if len(items) == 1:
            cell = items[0]
            text = text_cell(cell, sheet, revision).strip()
            # A broad merge is not sufficient evidence of a heading.
            is_heading = (cell.bold or re.match(r"^\d+[.． ]", text)) and "。" not in text and len(text) <= 80
            lines += [f"### {text}" if is_heading else text, ""]
            i += 1
            continue
        if len(items) == 2:
            lines += [f"- **{old.esc(items[0].text)}**: {old.esc(text_cell(items[1], sheet, revision))}", ""]
            i += 1
            continue
        columns = [v.col for v in items]
        lines += ["| " + " | ".join(old.esc(v.text) for v in items) + " |",
                  "| " + " | ".join("---" for _ in items) + " |"]
        i += 1
        last = r
        while i < len(keys):
            rr = keys[i]
            data = by_row[rr]
            if len(data) < 2 or rr - last > 3 or any(v.col not in columns for v in data):
                break
            values = [text_cell(lookup[(rr, col)], sheet, revision) for col in columns]
            lines.append("| " + " | ".join(old.esc(v) for v in values) + " |")
            last = rr
            i += 1
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def screen(sheet: SheetInfo, revision: int) -> str:
    _, headers, data = old.find_field_table(sheet, sheet.header_rows + 1)
    if not headers:
        return blocks(sheet, revision)
    result = old.render_screen(sheet, sheet.header_rows + 1).split("### 画面フォーム参考")[0]
    # Do not repeat field labels as disconnected overview bullet points.
    labels = {row[headers.index('項目名')] for row in data}
    result = "\n".join(line for line in result.splitlines()
                       if not (line.startswith("- ") and line[2:] in labels))
    result = result.replace("### 画面概要\n", "### 画面上のメッセージ\n")
    if revision >= 3:
        result += "\n\n初期値の空欄は「原本記載なし」を意味する。空文字を設定する仕様とは断定しない。\n"
        result += "必須欄の○は必須。ボタン行の必須・桁数の空欄から入力制約を推定しない。\n"
    return result.strip() + "\n"


def guarded_flow(sheet: SheetInfo, info, revision: int) -> str:
    result = old.render_flow(sheet, sheet.header_rows + 1)
    if revision < 4:
        return result
    nodes = old.flow_nodes(sheet, sheet.header_rows + 1)
    source_text = "\n".join(c.text for s in info.sheets for c in old.anchors(s))
    # Reuse node labels, but read branch labels from the source, never from a
    # fixed left=No/right=Yes convention. Fall back to unknown labels.
    for i, node in enumerate(nodes):
        if not any(mark in node.text for mark in ('?', '？', '判定', '確認', '有無', '場合')):
            continue
        if i + 2 >= len(nodes) or nodes[i + 1].row != nodes[i + 2].row:
            continue
        branch_marks = []
        for cell in old.anchors(sheet):
            if node.row < cell.row < nodes[i + 1].row:
                match = re.search(r"(いいえ|はい|Yes|No|YES|NO)", cell.text)
                if match:
                    branch_marks.append((cell.col, match.group(1)))
        branch_marks.sort()
        labels = [p[1] for p in branch_marks] if len(branch_marks) == 2 else ['原本ラベル要確認'] * 2
        for offset, label in enumerate(labels, 1):
            result = re.sub(rf'N{i+1} -->\|[^|]+\| N{i+offset+1}\b',
                            f'N{i+1} -->|{label}| N{i+offset+1}', result)
    # This explicit Japanese condition is supported only when both corresponding
    # nodes and the source statement exist. Do not synthesize failure behavior.
    if '入力チェック成功後' in source_text:
        for i in range(len(nodes) - 1):
            if ('入力' in nodes[i].text and 'チェック' in nodes[i].text
                    and 'API' in nodes[i + 1].text):
                result = result.replace(f'N{i+1} --> N{i+2}',
                                        f'N{i+1} -->|入力チェック成功| N{i+2}')
    note = ('> 参考図：接続は原本の配置から再構成したもの。分岐ラベルは原本から転記し、'
            '明記された条件は本文を優先する。原本で明示されない接続・失敗経路は要確認。\n\n')
    result = note + result.replace('### 処理フロー\n\n', '', 1)
    # Source security notes belong in the security section rather than being
    # repeated in an unconnected appendix.
    return result


def questions(info) -> list[str]:
    corpus = "\n".join(c.text for s in info.sheets for c in old.anchors(s))
    result = []
    if 'API' in corpus:
        absent = [label for label, patterns in [
            ('エンドポイント', ('http://', 'https://', '/api/', 'エンドポイント')),
            ('HTTPメソッド', ('HTTP', 'POST', 'GET', 'PUT', 'DELETE')),
            ('タイムアウト', ('タイムアウト', 'timeout')),
            ('再試行', ('再試行', 'retry')),
        ] if not any(p in corpus for p in patterns)]
        if absent:
            result.append('APIの' + '・'.join(absent) + 'は原本記載なし。実装前に確認する。')
    if '入力チェック成功後' in corpus:
        result.append('入力チェック不成功時の後続処理・遷移先は要確認。未入力のメッセージ定義だけで、桁数超過時のコードや遷移を補完しない。')
    if 'ロック' in corpus and '失敗' in corpus and 'リセット' not in corpus:
        result.append('失敗回数のリセット条件・ロック解除条件の詳細は原本記載なし。管理者向け解除機能の存在と解除条件は区別する。')
    cover_ids = [v for s in info.sheets if s.kind == 'cover'
                 for k, v in old.metadata_pairs(s, s.max_row) if old.norm(k) == '機能id']
    list_ids = []
    for s in info.sheets:
        if s.kind != 'list':
            continue
        for _, cells in old.rows(s, s.header_rows + 1).items():
            if cells and re.match(r'[A-Z]+-\d+', cells[0].text):
                list_ids.append(cells[0].text)
    for fid in cover_ids:
        if list_ids and fid not in list_ids:
            result.append(f'表紙の機能ID `{fid}` と機能一覧のID（' + '、'.join(f'`{x}`' for x in list_ids)
                          + '）の対応は明記されていない。同一IDとして統合しない。')
    if any(s.images or s.charts for s in info.sheets):
        result.append('画像・グラフ内の情報はこのテキスト変換で検証していない。原本の目視レビューが必要。')
    return result


def convert(path: str | Path, revision: int = 4) -> str:
    if revision not in (2, 3, 4, 5):
        raise ValueError('revision must be 2..5')
    info = load_xlsx(path)
    covers = [s for s in info.sheets if s.kind == 'cover']
    title = old.document_title(info)
    for cover in covers:
        title = next((v for k, v in old.metadata_pairs(cover, 16) if k == '文書名'), title)
    lines = [f'# {title}', '']
    metadata = {}
    for cover in covers:
        lines += [old.render_cover(cover)]
        metadata.update(old.metadata_pairs(cover, 16))
    domain_titles = {'list': '関連機能', 'screen': '画面・入力仕様', 'flow': '処理フロー', 'article': '動作仕様'}
    types = {v for s in info.sheets for k, v in old.metadata_pairs(s, max(4, s.header_rows)) if k == '文書種別'}
    common_type = next(iter(types)) if len(types) == 1 else None
    mapping = []
    for sheet in info.sheets:
        if sheet.kind == 'cover':
            mapping.append((sheet.name, '文書全体', '文書情報・改訂履歴'))
            continue
        pairs = old.metadata_pairs(sheet, max(4, sheet.header_rows))
        function = next((v for k, v in pairs if k in ('機能名', '処理名', '画面名')), sheet.name)
        domain = domain_titles.get(sheet.kind, sheet.name)
        title = f'{domain} — {function}'
        mapping.append((sheet.name, function, title))
        lines += [f'## {title}', '']
        # Retain differing per-function metadata; consolidate only identical facts.
        overrides = [(k, v) for k, v in pairs if k not in ('機能名', '処理名', '画面名') and metadata.get(k) != v and not (k == '文書種別' and v == common_type)]
        for k, v in overrides:
            lines += [f'- **{old.esc(k)}**: {old.esc(v)}']
        if overrides:
            lines.append('')
        body = (screen(sheet, revision) if sheet.kind == 'screen' else
                guarded_flow(sheet, info, revision) if sheet.kind == 'flow' else blocks(sheet, revision))
        # Avoid an empty level of heading that only repeats the parent concept.
        if sheet.kind in ('list', 'flow'):
            body = re.sub(r'^### (?:機能一覧|処理フロー)\s*\n', '', body).lstrip()
        lines += [body]
    if revision >= 4:
        pending = questions(info)
        if pending:
            lines += ['## 確認事項（変換時レビュー）', '',
                      '以下は未記載・不明点の指摘であり、新しい要求や決定事項ではない。', '']
            lines += [f'- {item}' for item in pending]
            lines.append('')
    lines += ['## 出典対応', '', f'原本: `{Path(path).name}`。' + (f' 共通文書種別: {common_type}。' if common_type else ''), '',
              '| 原本シート | 原本の機能名・範囲 | 本文の対応セクション |', '|---|---|---|']
    lines += ['| ' + ' | '.join(old.esc(v) for v in row) + ' |' for row in mapping]
    return '\n'.join(lines).strip() + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xlsx', type=Path)
    parser.add_argument('-o', '--output', type=Path, required=True)
    parser.add_argument('--revision', type=int, default=4, choices=(2, 3, 4, 5))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(convert(args.xlsx, args.revision), encoding='utf-8')


if __name__ == '__main__':
    main()
