import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from src.mermaid_validate import extract_diagrams, portability_issues, validate
from src.independent_evaluate import combine


class MermaidValidationTests(unittest.TestCase):
    def test_three_fences(self):
        d,e=extract_diagrams(('```mermaid\nflowchart LR\nA-->B\n```\n'*3))
        self.assertEqual(len(d),3);self.assertFalse(e)
    def test_unclosed(self):
        self.assertTrue(extract_diagrams('```mermaid\nA-->B')[1])
    def test_empty(self):
        self.assertTrue(extract_diagrams('```mermaid\n```')[1])
    def test_ignore_examples_inside_other_fences(self):
        self.assertFalse(extract_diagrams('````markdown\n```mermaid\nA-->B\n```\n````')[0])
    def test_ignore_html_comment(self):
        self.assertFalse(extract_diagrams('<!--\n```mermaid\nA-->B\n```\n-->')[0])
    def test_tilde_fence(self):
        self.assertEqual(len(extract_diagrams('~~~mermaid\nflowchart LR\nA-->B\n~~~')[0]),1)
    def test_ordered_list_risk(self):
        self.assertTrue(portability_issues('A["1. text"]'))
    def test_markdown_list_risk(self):
        self.assertTrue(portability_issues('A["`title\n- item`"]'))
    def test_entity_preserves_number_without_list_token(self):
        self.assertFalse(portability_issues('A["1#46; text"]'))
    def test_missing_runtime_is_blocked(self):
        with TemporaryDirectory() as t:
            f=Path(t)/'x.md';f.write_text('```mermaid\nflowchart LR\nA-->B\n```')
            result=validate(f,expected_count=1)
            self.assertEqual(result['status'],'BLOCKED');self.assertFalse(result['passed'])
    def test_deleted_diagram_is_failure(self):
        with TemporaryDirectory() as t:
            f=Path(t)/'x.md';f.write_text('# empty\n')
            result=validate(f,expected_count=1)
            self.assertEqual(result['status'],'FAIL')
    def test_combiner_refuses_stale_and_blocked_reports(self):
        with TemporaryDirectory() as t:
            f=Path(t)/'x.md';f.write_text('# Example')
            digest=hashlib.sha256(f.read_bytes()).hexdigest()
            acceptance={'markdown_sha256':digest,'checks':[{'passed':True}]}
            m={'markdown_sha256':digest,'expected_count':1,'diagram_count':1,'runtime_status':'BLOCKED','passed':False}
            self.assertEqual(combine(f,acceptance,m)['status'],'BLOCKED')
            m.update(runtime_status='EXECUTED',passed=True,diagrams=[{'profiles':[{'passed':True},{'passed':True}]}])
            self.assertTrue(combine(f,acceptance,m)['passed'])
            acceptance['markdown_sha256']='stale'
            self.assertFalse(combine(f,acceptance,m)['passed'])
    def test_content_score_cannot_override_render_failure(self):
        with TemporaryDirectory() as t:
            f=Path(t)/'x.md';f.write_text('# Example');d=hashlib.sha256(f.read_bytes()).hexdigest()
            acceptance={'markdown_sha256':d,'checks':[{'passed':True} for _ in range(100)]}
            m={'markdown_sha256':d,'expected_count':1,'diagram_count':1,'runtime_status':'EXECUTED','passed':False,'diagrams':[{'profiles':[{'passed':False},{'passed':False}]}]}
            self.assertFalse(combine(f,acceptance,m)['passed'])

if __name__=='__main__':unittest.main()
