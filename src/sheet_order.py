"""Assemble reviewed Markdown fragments in visible Excel tab order.

This module determines order only. Callers must supply already reviewed,
visible-only fragments; it does not interpret cells, pictures or callouts.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Mapping
from xml.etree import ElementTree as ET
from zipfile import ZipFile

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
EXCLUDED_NAMES = frozenset({'凡例', '変更履歴', '改訂履歴', 'legend', 'change history', 'revision history'})


@dataclass(frozen=True)
class Chapter:
    number: int
    tab_position: int
    sheet_id: str
    source_name: str

    @property
    def label(self) -> str:
        return self.source_name.strip()

    @property
    def anchor(self) -> str:
        return f'sheet-{self.sheet_id}'


def workbook_chapters(path: str | Path) -> list[Chapter]:
    """Read saved tab sequence, not sheetId order or an alphabetical sort."""
    with ZipFile(path) as z:
        root = ET.fromstring(z.read('xl/workbook.xml'))
    sheets = root.find(NS + 'sheets')
    if sheets is None:
        raise ValueError('Workbook has no sheet list.')
    result: list[Chapter] = []
    for position, sheet in enumerate(sheets, 1):
        if sheet.get('state', 'visible') != 'visible':
            continue
        name = sheet.get('name', '')
        if name.strip().casefold() in EXCLUDED_NAMES:
            continue
        sid = sheet.get('sheetId', '')
        if not name.strip() or not sid.isdigit():
            raise ValueError('Invalid visible sheet name or sheetId.')
        result.append(Chapter(len(result) + 1, position, sid, name))
    if not result:
        raise ValueError('Workbook has no eligible sheets.')
    if len({c.source_name for c in result}) != len(result) or len({c.anchor for c in result}) != len(result):
        raise ValueError('Duplicate sheet names or sheetIds.')
    return result


def markdown_headings(text: str) -> list[tuple[int, str]]:
    """Extract ATX headings outside fenced code and HTML comments."""
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    fence_char = ''
    fence_size = 0
    out: list[tuple[int, str]] = []
    for line in text.splitlines():
        fence = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            mark, tail = fence.groups()
            if not fence_char:
                fence_char, fence_size = mark[0], len(mark)
            elif mark[0] == fence_char and len(mark) >= fence_size and not tail.strip():
                fence_char, fence_size = '', 0
            continue
        if fence_char:
            continue
        heading = re.match(r'^ {0,3}(#{1,6})\s+(.+?)\s*$', line)
        if heading:
            out.append((len(heading[1]), re.sub(r'\s+#+\s*$', '', heading[2])))
    if fence_char:
        raise ValueError('Unclosed Markdown fence.')
    return out


def assemble(title: str, chapters: list[Chapter], sections: Mapping[str, str]) -> str:
    """Assemble one H2 per eligible sheet; exact original names are mapping keys."""
    expected = {c.source_name for c in chapters}
    if set(sections) != expected:
        raise ValueError('Missing, extra or excluded sheet fragments; check source mapping.')
    if not title.strip() or '\n' in title or '\r' in title:
        raise ValueError('Title must be one nonempty line.')
    parts = [f'# {title.strip()}']
    for chapter in chapters:
        body = sections[chapter.source_name].strip()
        if not body or any(level <= 2 for level, _ in markdown_headings(body)):
            raise ValueError(f'Chapter {chapter.number} needs a body without H1/H2 headings.')
        parts.append(f'<a id="{chapter.anchor}"></a>\n## {chapter.number}. {chapter.label}\n\n{body}')
    return '\n\n'.join(parts) + '\n'


def validate_order(markdown: str, chapters: list[Chapter]) -> bool:
    headings = markdown_headings(markdown)
    return (
        len([h for h in headings if h[0] == 1]) == 1
        and [text for level, text in headings if level == 2]
        == [f'{c.number}. {c.label}' for c in chapters]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xlsx', type=Path)
    parser.add_argument('--sections', type=Path, required=True, help='JSON: title and sections keyed by exact source sheet name')
    parser.add_argument('-o', '--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.sections.read_text(encoding='utf-8'))
        result = assemble(payload['title'], workbook_chapters(args.xlsx), payload['sections'])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding='utf-8', newline='\n')
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
