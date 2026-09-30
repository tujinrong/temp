from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from src.sheet_order import Chapter, NS, assemble, markdown_headings, validate_order, workbook_chapters


class SheetOrderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'metadata-fixture.xlsx'
        root = ET.Element(NS+'workbook')
        sheets = ET.SubElement(root, NS+'sheets')
        # Metadata-only parser fixture; not a user-facing Excel workbook.
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

    def test_leading_cover_is_introduction_with_stable_source_key_and_anchor(self):
        cover=Chapter(1,1,'21','表紙 ')
        body=Chapter(2,3,'5','処理概要')
        text=assemble('文書',[cover,body],{'表紙 ':'共通情報','処理概要':'固有の目的'})
        self.assertEqual(cover.label,'はじめに')
        self.assertEqual(cover.source_name,'表紙 ')
        self.assertEqual(cover.anchor,'sheet-21')
        self.assertEqual(markdown_headings(text),[(1,'文書'),(2,'1. はじめに'),(2,'2. 処理概要')])
        self.assertTrue(validate_order(text,[cover,body]))

    def test_old_cover_heading_is_rejected(self):
        c=Chapter(1,1,'21','表紙')
        text=assemble('文書',[c],{'表紙':'本文'})
        self.assertFalse(validate_order(text.replace('1. はじめに','1. 表紙'),[c]))

    def test_display_label_is_not_a_source_key(self):
        with self.assertRaises(ValueError):
            assemble('文書',[Chapter(1,1,'21','表紙')],{'はじめに':'本文'})

    def test_does_not_invent_or_move_a_cover(self):
        self.assertEqual(Chapter(1,1,'8','概要').label,'概要')
        self.assertEqual(Chapter(2,2,'21','表紙').label,'表紙')
        self.assertEqual(Chapter(1,1,'8','Cover').label,'はじめに')

    def test_reviewed_common_fragment_and_local_override_are_preserved(self):
        chapters=[Chapter(1,1,'21','表紙'),Chapter(2,2,'5','概要')]
        sections={'表紙':'### 共通情報\n\n<a id="common"></a>\n共通値A','概要':'共通情報は[冒頭](#common)。このシートだけ値B。'}
        text=assemble('文書',chapters,sections)
        self.assertEqual(text.count('共通値A'),1)
        self.assertIn('このシートだけ値B。',text)
        self.assertIn('[冒頭](#common)',text)
        self.assertTrue(validate_order(text,chapters))


if __name__ == '__main__':
    unittest.main()
