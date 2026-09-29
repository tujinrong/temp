from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.evaluate_markdown import evaluate
from tests.make_japanese_spec_test import build

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / 'examples' / 'login_spec.sample.md'


class AiMarkdownEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.xlsx = Path(self.tmp.name) / 'japanese_program_spec_test.xlsx'
        build(self.xlsx)

    def tearDown(self):
        self.tmp.cleanup()

    def test_human_style_sample_passes(self):
        ev = evaluate(self.xlsx, SAMPLE)
        self.assertTrue(ev.passed, ev.to_dict())
        self.assertGreaterEqual(ev.ai_readability_score, 90)
        self.assertGreaterEqual(ev.requirement_score, 80)

    def test_excel_shaped_dump_is_penalized(self):
        bad = Path(self.tmp.name) / 'bad.md'
        text = SAMPLE.read_text(encoding='utf-8')
        rows = '\n'.join(
            f'| A{i} | value {i} | merge=A{i}:D{i}; col_width=2 |'
            for i in range(1, 31)
        )
        bad.write_text(
            text +
            '\n\n### Source grid\n\n| Cell | Value | Layout |\n|---|---|---|\n' +
            rows +
            '\n\n### Workbook layout metadata\n\n- data-grid-width=narrow\n',
            encoding='utf-8',
        )
        ev = evaluate(self.xlsx, bad)
        self.assertFalse(ev.passed, ev.to_dict())
        self.assertLess(ev.ai_readability_score, 80)


if __name__ == '__main__':
    unittest.main()
