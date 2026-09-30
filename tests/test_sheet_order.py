from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from src.sheet_order import NS, assemble, markdown_headings, validate_order, workbook_chapters


class SheetOrderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'metadata-fixture.xlsx'
        root = ET.Element(NS+'workbook')
        sheets = ET.SubElement(root, NS+'sheets')
        # Small workbook-metadata fixture, not a full user-facing XLSX.
        for name, sid, state in [('後ろの名前', '80', 'visible'), ('非表示テスト', '2', 'hidden'), ('変更履歴', '3', 'visible'), ('先の名前 ', '10', 'visible'), ('秘密テスト', '4', 'veryHidden'), ('凡例', '8', 'visible')]:
            ET.SubElement(sheets, NS+'sheet', {'name':name, 'sheetId':sid, 'state':state})
        with ZipFile(self.path, 'w') as z:
            z.writestr('xl/workbook.xml', ET.tostring(root))
        self.chapters = workbook_chapters(self.path)
        self.sections = {'後ろの名前':'本文A', '先の名前 ':'本文B'}

    def tearDown(self):
        self.tmp.cleanup()

    def test_tab_order_not_id_or_name_sort(self):
        self.assertEqual([c.sheet_id for c in self.chapters], ['80', '10'])
        self.assertEqual([c.tab_position for c in self.chapters], [1, 4])

    def test_exclusions_and_consecutive_numbering(self):
        self.assertEqual([c.number for c in self.chapters], [1, 2])
        self.assertEqual(len(self.chapters), 2)

    def test_exact_name_keys_trim_only_heading(self):
        self.assertEqual(self.chapters[1].source_name, '先の名前 ')
        text = assemble('文書', self.chapters, self.sections)
        self.assertIn('## 2. 先の名前\n', text)
        self.assertTrue(validate_order(text, self.chapters))

    def test_missing_fragment_rejected(self):
        with self.assertRaises(ValueError):
            assemble('文書', self.chapters, {'後ろの名前':'A'})

    def test_excluded_fragment_rejected(self):
        with self.assertRaises(ValueError):
            assemble('文書', self.chapters, {**self.sections, '非表示テスト':'禁止'})

    def test_empty_body_rejected(self):
        with self.assertRaises(ValueError):
            assemble('文書', self.chapters, {**self.sections, '後ろの名前':''})

    def test_h2_in_body_rejected_but_code_is_allowed(self):
        with self.assertRaises(ValueError):
            assemble('文書', self.chapters, {**self.sections, '後ろの名前':'## 別の章'})
        text=assemble('文書', self.chapters, {**self.sections, '後ろの名前':'```text\n## コード内の見出し\n```\n\n本文'})
        self.assertTrue(validate_order(text, self.chapters))

    def test_swapped_sections_rejected(self):
        text=assemble('文書', self.chapters, self.sections)
        text=text.replace('## 1. 後ろの名前','## 1. 先の名前').replace('## 2. 先の名前','## 2. 後ろの名前')
        self.assertFalse(validate_order(text, self.chapters))

    def test_unclosed_fence_rejected(self):
        with self.assertRaises(ValueError):
            markdown_headings('```mermaid\nflowchart TD\nA-->B')

    def test_comment_only_headings_not_counted(self):
        self.assertEqual(markdown_headings('<!--\n## 偽の章\n-->\n# 本文'), [(1,'本文')])


if __name__ == '__main__':
    unittest.main()
