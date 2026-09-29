from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from src.drawing_content import extract
from src.form_conversion import convert, comment, context
from src.form_review import DOM,form_review
from src.form_evolution import run
from src.xlsx_spec import load_xlsx

ROOT=Path(__file__).resolve().parents[1]
X=ROOT/'input/japanese_program_spec_with_callouts.xlsx'
CONTRACT=ROOT/'tests/fixtures/japanese_program_spec_with_callouts.contract.json'
LAYOUT=ROOT/'tests/fixtures/login_hardcopy.layout.json'

@unittest.skipUnless(X.is_file(), "Download the form/callout run bundle and place its XLSX fixtures in input/.")
class FormCalloutTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.md=self.root/'spec.md'
        convert(X,LAYOUT,self.md)
    def tearDown(self):self.tmp.cleanup()
    def test_final_passes(self):
        result=form_review(X,self.md,CONTRACT,LAYOUT)
        self.assertEqual((result['passed_checks'],result['total_checks']),(39,39))
    def test_true_floating_callouts_and_picture(self):
        inv=extract(X)
        self.assertEqual(len(inv['images']),1);self.assertEqual(len(inv['callouts']),5)
        self.assertTrue(all(c['geometry']=='wedgeRoundRectCallout' for c in inv['callouts']))
        self.assertEqual([c['target'] for c in inv['callouts']],['userId','password','loginButton','clearButton','errorArea'])
        cells='\n'.join(c.text for s in load_xlsx(X).sheets for c in s.nonempty)
        for c in inv['callouts']:self.assertNotIn(c['text'],cells)
    def test_original_five_sheets_unchanged(self):
        a=load_xlsx(ROOT/'input/japanese_program_spec_test.xlsx')
        b=load_xlsx(X)
        self.assertEqual(len(b.sheets),6)
        for orig,new in zip(a.sheets,b.sheets[:5]):
            self.assertEqual(orig.name,new.name)
            left={c.coordinate:c.formula or c.text for c in orig.nonempty}
            right={c.coordinate:c.formula or c.text for c in new.nonempty}
            self.assertEqual(left,right)
    def test_reproducible_three_loop_history(self):
        with contextlib.redirect_stdout(io.StringIO()):
            r=run(X,CONTRACT,LAYOUT,self.root/'out.md',self.root/'report')
        self.assertEqual([h['acceptance']['passed_checks'] for h in r['loops']],[26,37,39])
        self.assertTrue(r['source_unchanged']);self.assertEqual(r['selected_loop'],3)
    def test_literal_html_comments_alone_are_insufficient(self):
        convert(X,LAYOUT,self.md,visible=False)
        r=form_review(X,self.md,CONTRACT,LAYOUT)
        self.assertEqual([c['id'] for c in r['checks'] if not c['passed']],['H07','H08'])
    def test_unknown_or_changed_screenshot_is_not_guessed(self):
        data=json.loads(LAYOUT.read_text());data['image_sha256']='0'*64
        wrong=self.root/'wrong.json';wrong.write_text(json.dumps(data))
        with self.assertRaises(ValueError):convert(X,wrong,self.md)
    def test_unbound_callout_requires_review(self):
        inv=extract(X);inv['callouts'][0]['target']=None
        with patch('src.form_conversion.extract',return_value=inv):
            with self.assertRaises(ValueError):context(X,LAYOUT,None)
    def test_comment_cannot_inject_html(self):
        s=comment({'id':'C01','target':'userId','note':'x --> <script>alert(1)</script><!-- y'})
        d=DOM();d.feed(s)
        self.assertEqual(len(d.comments),1);self.assertFalse(d.nodes)
    def test_mutations_fail(self):
        good=self.md.read_text();htmlfile=self.md.with_name('spec.form.html');goodhtml=htmlfile.read_text()
        cases={
            'wrong user limit':lambda t:t.replace('maxlength="50"','maxlength="51"'),
            'wrong password limit':lambda t:t.replace('maxlength="128"','maxlength="50"'),
            'password no longer masked':lambda t:t.replace('type="password"','type="text"'),
            'required removed':lambda t:t.replace(' required maxlength="50"',' maxlength="50"'),
            'incorrect label target':lambda t:t.replace('for="userId"','for="password"'),
            'wrong comment target':lambda t:t.replace('data-target="userId"','data-target="password"'),
            'visible comments removed':lambda t:re.sub(r'<aside class="spec-comments".*?</aside>','',t,flags=re.S),
            'comments hidden':lambda t:t.replace('<aside class="spec-comments"','<aside hidden class="spec-comments"'),
            'literal comments removed':lambda t:re.sub(r'<!-- callout .*?-->','',t,flags=re.S),
            'wrong description binding':lambda t:t.replace('aria-describedby="comment-C01"','aria-describedby="comment-C02"'),
            'invented default':lambda t:t.replace('name="userId"','name="userId" value=""'),
            'invented submit endpoint':lambda t:t.replace('<form id="login"','<form action="https://invalid.example/login" id="login"'),
            'submit button substituted':lambda t:t.replace('id="loginButton" type="button"','id="loginButton" type="submit"'),
            'unsafe executable content':lambda t:t+'\n<script>bad()</script>\n',
            'raw grid added':lambda t:t+'\n### Source grid\n|A1|value|\n',
            'picture removed':lambda t:re.sub(r'\[原本のハードコピー画像\]\([^)]+\)','',t),
            'split action groups':lambda t:t.replace('<button id="clearButton"','</div><div class="spec-actions"><button id="clearButton"'),
            'changed callout text':lambda t:t.replace('最大50文字。','最大51文字。'),
            'duplicated form':lambda t:t+'\n<form id="unexpected"></form>',
        }
        for name,mutate in cases.items():
            with self.subTest(name=name):
                changed=mutate(good);self.assertNotEqual(changed,good)
                self.md.write_text(changed)
                fragment=re.search(r'<section class="spec-form">.*?</section>',changed,re.S)
                original_fragment=re.search(r'<section class="spec-form">.*?</section>',good,re.S).group()
                htmlfile.write_text(goodhtml.replace(original_fragment,fragment.group()) if fragment else goodhtml)
                r=form_review(X,self.md,CONTRACT,LAYOUT)
                self.assertFalse(r['passed'],name)
        self.md.write_text(good);htmlfile.write_text(goodhtml.replace('maxlength="50"','maxlength="51"'))
        self.assertFalse(form_review(X,self.md,CONTRACT,LAYOUT)['passed'],'standalone HTML drift')

if __name__=='__main__':unittest.main()
