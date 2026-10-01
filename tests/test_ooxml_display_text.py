import unittest
from xml.etree.ElementTree import fromstring
from src.ooxml_display_text import display_text

class DisplayTextTests(unittest.TestCase):
    def test_plain(self):self.assertEqual(display_text(fromstring('<si><t>支払案内書</t></si>')), '支払案内書')
    def test_phonetics_excluded(self):self.assertEqual(display_text(fromstring('<si><t>支払案内書</t><rPh><t>シハライアンナイショ</t></rPh></si>')), '支払案内書')
    def test_rich_order(self):self.assertEqual(display_text(fromstring('<si><r><t>口座</t></r><r><t>0100486</t></r><rPh><t>コウザ</t></rPh></si>')), '口座0100486')
    def test_whitespace(self):self.assertEqual(display_text(fromstring('<si><t>  前後  \n改行</t></si>')), '  前後  \n改行')
    def test_namespace(self):self.assertEqual(display_text(fromstring('<si xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><t>住所</t><rPh><t>ジュウショ</t></rPh></si>')), '住所')
    def test_none(self):self.assertEqual(display_text(None), '')

if __name__=='__main__':unittest.main()
