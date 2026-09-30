from __future__ import annotations
import ast
import re
import unittest
from pathlib import Path
from types import SimpleNamespace
from src.visible_scope import coordinates

def text_function():
    # Exercise the actual fallback function without importing a spreadsheet engine.
    path = Path(__file__).resolve().parents[1] / "src" / "semantic_repair.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "text_cell")
    def bounds(ref):
        a, b = ref.split(":")
        r1, c1 = coordinates(a)
        r2, c2 = coordinates(b)
        return c1, r1, c2, r2
    env = {"re": re, "CellInfo": object, "SheetInfo": object,
           "old": SimpleNamespace(range_boundaries=bounds)}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), env)
    return env["text_cell"]

class HiddenFormulaTests(unittest.TestCase):
    def setUp(self):
        self.render = text_function()
        self.cell = SimpleNamespace(formula="=COUNTA(A1:A3)", text="=COUNTA(A1:A3)")
        self.sheet = SimpleNamespace(hidden_rows=set(), hidden_cols=set(), cells=[
            SimpleNamespace(row=r, col=1, value=f"ID-{r}", formula=None) for r in (1,2,3)])

    def test_hidden_row_not_recalculated(self):
        self.sheet.hidden_rows = {2}
        self.assertIn("非表示領域", self.render(self.cell, self.sheet, 4))

    def test_hidden_column_not_recalculated(self):
        self.sheet.hidden_cols = {1}
        self.assertIn("非表示領域", self.render(self.cell, self.sheet, 4))

    def test_visible_cached_result_is_retained(self):
        self.sheet.hidden_rows = {2}
        self.cell.text = "3"
        self.assertTrue(self.render(self.cell, self.sheet, 4).startswith("3（"))

    def test_visible_literal_count_still_supported(self):
        self.assertTrue(self.render(self.cell, self.sheet, 4).startswith("3（"))

if __name__ == "__main__":
    unittest.main()
