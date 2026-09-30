from __future__ import annotations
import unittest
from types import SimpleNamespace
from xml.etree import ElementTree as ET
from src.visible_scope import SheetScope, WorkbookScope, coordinates, safe_xml

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
D = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"

def sheet_xml(body="", fmt=""):
    return (f'<worksheet xmlns="{M}">{fmt}{body}</worksheet>').encode()

def anchor(r1, c1, r2=None, c2=None, edit_as=None):
    attrs = f' editAs="{edit_as}"' if edit_as else ""
    body = f'<xdr:from><xdr:col>{c1-1}</xdr:col><xdr:row>{r1-1}</xdr:row></xdr:from>'
    if r2 is not None:
        body += f'<xdr:to><xdr:col>{c2}</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>{r2}</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:to>'
    return ET.fromstring(f'<xdr:twoCellAnchor xmlns:xdr="{D}"{attrs}>{body}</xdr:twoCellAnchor>')

class VisibilityTests(unittest.TestCase):
    def test_hidden_sheet(self):
        self.assertFalse(SheetScope.from_xml("秘匿", None, "hidden").included)

    def test_veryhidden_sheet(self):
        self.assertFalse(SheetScope.from_xml("内部", None, "veryHidden").included)

    def test_legend_and_history(self):
        for name in ("凡例", "変更履歴", "改訂履歴", " revision history "):
            with self.subTest(name=name):
                self.assertFalse(SheetScope.from_xml(name, None).included)

    def test_hidden_row(self):
        s=SheetScope.from_xml("画面",sheet_xml('<sheetData><row r="2" hidden="1"/></sheetData>'))
        self.assertFalse(s.cell_visible("A2"))
        self.assertTrue(s.cell_visible("A3"))

    def test_hidden_column_interval(self):
        s=SheetScope.from_xml("画面",sheet_xml('<cols><col min="3" max="6" hidden="1"/></cols>'))
        self.assertTrue(s.cell_visible("B1"))
        self.assertFalse(s.cell_visible("C1"))
        self.assertFalse(s.cell_visible("F1"))
        self.assertTrue(s.cell_visible("G1"))

    def test_zero_height_and_width(self):
        s=SheetScope.from_xml("画面",sheet_xml('<cols><col min="2" max="2" width="0"/></cols><sheetData><row r="4" ht="0"/></sheetData>'))
        self.assertFalse(s.cell_visible("B3"))
        self.assertFalse(s.cell_visible("A4"))
        self.assertTrue(s.cell_visible("A3"))

    def test_outline_is_not_hidden(self):
        s=SheetScope.from_xml("画面",sheet_xml('<cols><col min="1" max="2" outlineLevel="1" collapsed="1"/></cols><sheetData><row r="2" outlineLevel="2"/></sheetData>'))
        self.assertTrue(s.cell_visible("A2"))

    def test_default_hidden_rows(self):
        s=SheetScope.from_xml("画面",sheet_xml('<sheetData><row r="3" ht="15"/></sheetData>', '<sheetFormatPr zeroHeight="1"/>'))
        self.assertFalse(s.cell_visible("A2"))
        self.assertTrue(s.cell_visible("A3"))

    def test_visible_formula_cell(self):
        s=SheetScope.from_xml("画面",sheet_xml('<cols><col min="2" max="2" hidden="1"/></cols><sheetData><row r="1"><c r="A1"><f>B1+1</f><v>5</v></c><c r="B1"><v>4</v></c></row></sheetData>'))
        self.assertTrue(s.cell_visible("A1"))
        self.assertFalse(s.cell_visible("B1"))

    def test_mask_values_and_comments(self):
        cells=[SimpleNamespace(coordinate="A1",value="VISIBLE",comment=None,hyperlink=None),
               SimpleNamespace(coordinate="B1",value="DO_NOT_EXPORT",comment="HIDDEN_NOTE",hyperlink="HIDDEN_URL")]
        ws=SimpleNamespace(title="画面",iter_rows=lambda:[cells])
        wb=SimpleNamespace(worksheets=[ws])
        s=SheetScope.from_xml("画面",sheet_xml('<cols><col min="2" max="2" hidden="1"/></cols>'))
        WorkbookScope({"画面":s}).mask_loaded_workbook(wb)
        self.assertEqual(cells[0].value,"VISIBLE")
        self.assertIsNone(cells[1].value)
        self.assertIsNone(cells[1].comment)
        self.assertIsNone(cells[1].hyperlink)

    def test_resize_object_fully_hidden(self):
        s=SheetScope.from_xml("画面",sheet_xml('<cols><col min="2" max="4" hidden="1"/></cols>'))
        self.assertEqual(s.anchor_state(anchor(1,2,3,4)),"excluded")

    def test_partial_object_requires_review(self):
        s=SheetScope.from_xml("画面",sheet_xml('<cols><col min="2" max="4" hidden="1"/></cols>'))
        self.assertEqual(s.anchor_state(anchor(1,1,3,4)),"review")

    def test_floating_object_not_dropped_by_origin(self):
        s=SheetScope.from_xml("画面",sheet_xml('<cols><col min="2" max="4" hidden="1"/></cols>'))
        self.assertEqual(s.anchor_state(anchor(1,2,3,4,"oneCell")),"review")

    def test_visible_object(self):
        s=SheetScope.from_xml("画面",sheet_xml())
        self.assertEqual(s.anchor_state(anchor(1,1,3,4)),"visible")

    def test_reject_dtd_and_bad_coordinates(self):
        with self.assertRaises(ValueError):
            safe_xml(b'<!DOCTYPE x><x/>')
        with self.assertRaises(ValueError):
            coordinates("A0")
        self.assertEqual(coordinates("$AA$21"),(21,27))

if __name__ == "__main__":
    unittest.main()
