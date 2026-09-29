"""Executable acceptance checks, not an LLM-quality score.

The reviewed source contract is separate from the renderer. Contracts are
workbook-specific; an unknown workbook cannot receive a benchmark PASS.
Markdown comments are excluded. Matching checks validate whole table records,
not scattered keywords. Graph checks apply to the emitted Mermaid subset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def source_fingerprint(path: str | Path) -> str:
    """Hash source cell meaning independent of ZIP timestamps and cached formulas."""
    import posixpath
    payload = []
    with zipfile.ZipFile(path) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(si.itertext()) for si in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        rels = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        book = ET.fromstring(archive.read('xl/workbook.xml'))
        for sheet in book.findall('m:sheets/m:sheet', NS):
            rid = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target = rels[rid]
            member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            root = ET.fromstring(archive.read(member))
            values = []
            for cell in root.findall('.//m:sheetData/m:row/m:c', NS):
                formula = cell.find('m:f', NS)
                raw = cell.find('m:v', NS)
                if formula is not None:
                    value = '=' + (formula.text or '')
                elif cell.attrib.get('t') == 'inlineStr':
                    value = ''.join(t.text or '' for t in cell.findall('.//m:t', NS))
                elif cell.attrib.get('t') == 's' and raw is not None:
                    value = shared[int(raw.text)]
                else:
                    value = raw.text if raw is not None else ''
                if value not in (None, ''):
                    values.append((cell.attrib['r'], value))
            payload.append((sheet.attrib['name'], values))
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def markdown_tables(md: str) -> list[list[dict[str, str]]]:
    tables = []
    block = []
    def flush():
        if len(block) >= 2:
            split = lambda line: [p.strip().strip('`') for p in re.split(r'(?<!\\)\|', line.strip().strip('|'))]
            header = split(block[0])
            separator = split(block[1])
            if len(header) == len(separator) and all(re.fullmatch(r':?-{3,}:?', p.replace(' ', '')) for p in separator):
                records = []
                for line in block[2:]:
                    values = split(line)
                    if len(values) != len(header):
                        records.append({'__invalid__': line})
                    else:
                        records.append(dict(zip(header, values)))
                tables.append(records)
        block.clear()
    for line in md.splitlines():
        if line.strip().startswith('|'):
            block.append(line)
        else:
            flush()
    flush()
    return tables


def _records(tables, key: str, expected: list[dict]) -> bool:
    for record in expected:
        found = [r for table in tables for r in table if r.get(key) == record[key]]
        if not found or any(any(r.get(k) != str(v) for k, v in record.items()) for r in found):
            return False
    return True


def review(xlsx: str | Path, markdown: str | Path, contract: str | Path) -> dict:
    spec = json.loads(Path(contract).read_text(encoding='utf-8'))
    digest = source_fingerprint(xlsx)
    if digest != spec['source_content_sha256']:
        raise ValueError('Source does not match the reviewed contract; prepare an independent contract for this workbook.')
    original = Path(markdown).read_text(encoding='utf-8')
    md = re.sub(r'<!--.*?-->', '', original, flags=re.S)
    tables = markdown_tables(md)
    checks = []
    def add(identifier, title, passed, evidence):
        checks.append({'id': identifier, 'check': title, 'passed': bool(passed), 'evidence_or_repair': evidence})
    add('S01', 'One document title', len(re.findall(r'^# ', md, re.M)) == 1, 'Exactly one H1.')
    add('S02', 'Requirements are prose, not headings', not re.search(r'^#{1,6} .*。', md, re.M), 'Merged prose must remain a paragraph or list item.')
    add('S03', 'Repeated metadata consolidated', len(re.findall(r'^> \*\*作成者', md, re.M)) <= 1, 'Retain overrides but do not repeat identical per-sheet headers.')
    add('S04', 'Domain sections rather than worksheet transcription', all(not re.search(r'^## ' + re.escape(s) + r'\s*$', md, re.M) for s in spec['sheets'] if '_' in s), 'Put source sheet names in traceability, not the main outline.')
    add('S05', 'No raw grid or recovered layout debris', not re.search(r'Source grid|col_width=|merge=[A-Z]+\d|data-grid-width|\[.*input.*\]|┌|─┐', md), 'Keep coordinates, layout metadata and mockup placeholders out of the specification.')
    add('S06', 'No duplicated extracted-requirement appendix', 'Extracted requirements and rules' not in md, 'Repair requirements in their owning sections rather than copying them to an appendix.')
    add('F01', 'Document metadata associations', _records(tables, '項目', spec['metadata']), 'Cover: labels remain attached to the correct values.')
    add('F02', 'Revision history', _records(tables, '版', spec['revisions']), 'Cover revision-history rows.')
    add('F03', 'All related functions and attributes', _records(tables, '機能ID', spec['functions']), 'Function list rows, including name/status/notes.')
    add('F04', 'Function count is usable and labelled', bool(re.search(r'機能数[^\n]*\b4[（ (]', md)), 'COUNTA over four literal function IDs; report derived count, not a generic placeholder.')
    for i, field in enumerate(spec['fields'], 5):
        add(f'F{i:02d}', f"Field association: {field['項目ID']}", _records(tables, '項目ID', [field]), 'Check field ID + type + required + length + notes together.')
    add('F07', 'Button event/action mapping', _records(tables, '項目ID', spec['buttons']), 'Login triggers authentication; clear removes entered values.')
    add('F08', 'Blank defaults explicitly distinguished from empty strings', '原本記載なし' in md and '空文字' in md and '断定しない' in md, 'A blank initial-value cell is not a specified empty-string default.')
    add('F09', 'Authentication outcome condition', bool(re.search(r'SUCCESSの場合は認証成功', md)), 'Detailed specification: SUCCESS is the stated success response.')
    # Semantic labels are read from node definitions; no fixed node IDs in checks.
    nodes = dict(re.findall(r'^\s*(\w+)\s*(?:\(\[|\[|\{)"([^"]+)"', md, re.M))
    edges = re.findall(r'^\s*(\w+)\s*-->\s*(?:\|([^|]*)\|\s*)?(\w+)\s*$', md, re.M)
    validation = {k for k, v in nodes.items() if '入力' in v and 'チェック' in v}
    api = {k for k, v in nodes.items() if 'API' in v}
    calls = [(a, label, b) for a, label, b in edges if a in validation and b in api]
    add('F10', 'Diagram retains validation-success precondition', calls and all('成功' in label for _, label, _ in calls), 'Detailed specification conditions must also hold in Mermaid; unconditional API edges fail.')
    decision = {k for k, v in nodes.items() if '認証成功' in v}
    wanted = [('はい', 'メニュー画面へ遷移'), ('いいえ', 'エラーメッセージ表示')]
    branches_ok = all(any(a in decision and label == condition and nodes.get(b) == target for a, label, b in edges) for condition, target in wanted)
    branches_bad = any(a in decision and any(label == c and nodes.get(b) != t for c, t in wanted) for a, label, b in edges)
    add('F11', 'Yes/no branches lead to the correct outcomes', branches_ok and not branches_bad, 'Flow worksheet: yes -> menu; no -> error message.')
    add('F12', 'Password logging prohibition preserved', 'パスワードはログへ出力しない' in md and 'パスワードはログへ出力する' not in md, 'Negation is mandatory; matching the word password is insufficient.')
    add('F13', 'Consecutive failure threshold and action', bool(re.search(r'認証失敗回数を記録し、5回連続失敗でアカウントをロックする', md)), 'Security paragraph: record attempts and lock after five consecutive failures.')
    add('F14', 'Error code/condition/message tuples', _records(tables, 'コード', spec['messages']), 'All four exact message mappings, not loose occurrence of E001-E004.')
    add('F15', 'Error display location', 'メッセージを画面上部に表示' in md, 'Screen and detailed specifications.')
    add('F16', 'Layout-derived graph marked as tentative', '参考図' in md and '配置' in md and '要確認' in md, 'Unverified visual connections cannot silently become normative behavior.')
    add('F17', 'Unspecified interface behavior and validation failures surfaced', all(s in md for s in ('HTTPメソッド', 'タイムアウト', '再試行', '入力チェック不成功', '原本記載なし')), 'Source review found no interface contract or complete failed-validation path.')
    add('F18', 'Unresolved identifier correspondence surfaced', 'AUTH-LOGIN-001' in md and '同一IDとして統合しない' in md, 'Cover ID and function-list IDs have no explicit correspondence.')
    add('F19', 'All source sheets mapped', all(s in md for s in spec['sheets']), 'Sheet names are allowed in a compact traceability table.')
    failed = [c for c in checks if not c['passed']]
    return {'contract': spec['id'], 'source_content_sha256': digest,
            'passed_checks': len(checks) - len(failed), 'total_checks': len(checks),
            'status': 'ACCEPTANCE_CHECKS_PASS' if not failed else 'RETRY',
            'passed': not failed, 'checks': checks,
            'limitation': 'Workbook-specific deterministic checks plus source review; not a measured AI-understanding score and not proof of general-purpose conversion accuracy.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xlsx')
    parser.add_argument('markdown')
    parser.add_argument('--contract', required=True)
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    result = review(args.xlsx, args.markdown, args.contract)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(payload + '\n', encoding='utf-8')
    raise SystemExit(0 if result['passed'] else 2)


if __name__ == '__main__':
    main()
