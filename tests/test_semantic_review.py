"""Regression and deliberate-corruption tests for the reviewed Japanese fixture."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.semantic_repair import convert
from src.spec_review import review
from src.xlsx_to_markdown import convert_workbook

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'input/japanese_program_spec_test.xlsx'
CONTRACT = ROOT / 'tests/fixtures/japanese_program_spec.contract.json'


class SemanticReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SOURCE.exists():
            raise RuntimeError('Run python tests/make_japanese_spec_test.py first.')
        cls.good = convert(SOURCE, revision=4)

    def check_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'spec.md'
            path.write_text(text, encoding='utf-8')
            return review(SOURCE, path, CONTRACT)

    def test_final_passes(self):
        self.assertTrue(self.check_text(self.good)['passed'])

    def test_baseline_is_not_a_true_pass(self):
        result = self.check_text(convert_workbook(SOURCE))
        self.assertFalse(result['passed'])
        self.assertEqual(result['passed_checks'], 15)

    def test_progressive_repairs(self):
        self.assertEqual(self.check_text(convert(SOURCE, revision=2))['passed_checks'], 19)
        self.assertEqual(self.check_text(convert(SOURCE, revision=3))['passed_checks'], 21)

    def test_source_unchanged(self):
        before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        convert(SOURCE, revision=4)
        self.assertEqual(before, hashlib.sha256(SOURCE.read_bytes()).hexdigest())

    def test_corruptions_are_rejected(self):
        mutations = {
            'swapped_field_limit': self.good.replace('| ○ | 50 |', '| ○ | 128 |'),
            'optional_user_id': self.good.replace('| text | ○ |', '| text | 任意 |'),
            'lost_password_mask': self.good.replace('| マスク表示 |', '| 平文表示 |'),
            'wrong_clear_action': self.good.replace('| 入力値を消去 |', '| 画面を終了 |'),
            'reversed_branches': self.good.replace('N4 -->|いいえ| N5', 'N4 -->|はい| N5').replace('N4 -->|はい| N6', 'N4 -->|いいえ| N6'),
            'unconditional_api_call': self.good.replace('N2 -->|入力チェック成功| N3', 'N2 --> N3'),
            'negation_removed': self.good.replace('パスワードはログへ出力しない', 'パスワードはログへ出力する'),
            'wrong_lock_threshold': self.good.replace('5回連続失敗で', '4回連続失敗で'),
            'wrong_error_mapping': self.good.replace('| E001 | ユーザーID未入力 |', '| E001 | パスワード未入力 |'),
            'missing_error': '\n'.join(line for line in self.good.splitlines() if not line.startswith('| E004 |')),
            'comment_only_coverage': '<!--\n' + self.good + '\n-->',
            'conflicting_duplicate_field': self.good + '\n| 項目ID | 種別 | 必須 | 桁数 | 備考 |\n|---|---|---|---|---|\n| userId | text | ○ | 128 | 半角英数字 |\n',
            'source_grid_appended': self.good + '\n### Source grid\n\n| A1 | merge=A1:D1; col_width=2 |\n',
        }
        for name, text in mutations.items():
            with self.subTest(name=name):
                self.assertNotEqual(text, self.good, f'Mutation did not change text: {name}')
                self.assertFalse(self.check_text(text)['passed'], name)

    def test_contract_mismatch_cannot_pass(self):
        contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
        contract['source_content_sha256'] = '0' * 64
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p/'contract.json').write_text(json.dumps(contract), encoding='utf-8')
            (p/'spec.md').write_text(self.good, encoding='utf-8')
            with self.assertRaises(ValueError):
                review(SOURCE, p/'spec.md', p/'contract.json')


if __name__ == '__main__':
    unittest.main()
