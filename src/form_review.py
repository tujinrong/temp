"""Source-bound form/callout acceptance checks; no AI-understanding score."""
from __future__ import annotations
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from .drawing_content import extract,drawing_fingerprint
from .spec_review import review

class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.nodes=[];self.comments=[];self.stack=[]
    def handle_starttag(self,tag,attrs):
        n={'tag':tag,'attrs':dict(attrs),'text':'','ancestors':list(self.stack)}
        self.nodes.append(n)
        if tag not in {'input','img','br','meta','link','hr','source'}: self.stack.append(n)
    def handle_startendtag(self,tag,attrs): self.handle_starttag(tag,attrs)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']==tag: del self.stack[i:];break
    def handle_data(self,text):
        for node in self.stack: node['text']+=text
    def handle_comment(self,text): self.comments.append(html.unescape(text))
    def byid(self,key): return [n for n in self.nodes if n['attrs'].get('id')==key]

def form_review(xlsx,markdown,contract,layout_path):
    spec=json.loads(Path(contract).read_text(encoding='utf-8'))
    if drawing_fingerprint(xlsx)!=spec['source_drawing_sha256']:
        raise ValueError('Pictures/drawings/notes changed: source review is stale.')
    inv=extract(xlsx); layout=json.loads(Path(layout_path).read_text(encoding='utf-8'))
    expected=spec['drawing_expectations']; image=expected['images'][0]
    if layout['image_sha256']!=image['sha256'] or layout.get('review_status')!='source-reviewed':
        raise ValueError('Screenshot layout is not bound to the reviewed source image.')
    result=review(xlsx,markdown,contract); checks=result['checks']
    path=Path(markdown); text=path.read_text(encoding='utf-8'); dom=DOM();dom.feed(text)
    form=dom.byid(layout['form_id'])
    def one(fid):
        found=dom.byid(fid);return found[0] if len(found)==1 else None
    def add(key,title,ok,evidence):
        checks.append({'id':key,'check':title,'passed':bool(ok),'evidence_or_repair':evidence})
    assets=[]
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if link.startswith('assets/'):
            p=path.parent/link
            if p.is_file(): assets.append(hashlib.sha256(p.read_bytes()).hexdigest())
    add('H01','Original hard-copy image preserved and linked',image['sha256'] in assets,'Require the actual embedded PNG bytes; filename occurrence is not coverage.')
    add('H02','Semantic HTML form, not an image-only or Excel-grid export',len(form)==1 and sum(n['tag']=='form' for n in dom.nodes)==1 and form[0]['tag']=='form' and not any(n['tag']=='table' for n in dom.nodes),'One real form; no raw spreadsheet HTML table.')
    inputok=True
    for f in spec['fields']:
        n=one(f['項目ID']); a=n['attrs'] if n else {}
        inputok &= bool(n and n['tag']=='input' and a.get('name')==f['項目ID'] and a.get('type')==f['種別'] and a.get('maxlength')==f['桁数'] and ('required' in a)==(f['必須']=='○'))
    add('H03','Control type, ID, required flag and limit remain associated',inputok,'Check exact source field tuples, including password masking and both length limits.')
    buttonok=all((n:=one(b['項目ID'])) and n['tag']=='button' and n['text'].strip()==b['項目名'] and n['attrs'].get('type')=='button' for b in spec['buttons'])
    add('H04','Login and clear represented without invented runtime behavior',buttonok,'Static type=button controls; actual event requirements remain in source-backed text.')
    add('H05','Mockup explicitly distinguished from functioning application',form and form[0]['attrs'].get('data-reference-only')=='true' and '認証・クリア処理を実行しない' in text,'Do not claim a working login page or infer API URLs from a screenshot.')
    annotations=expected['callouts']
    add('H06','All five source callouts exported as associated HTML comments',all(sum(f"callout {c['id']} | target={c['target']}: {c['note']}" in x for x in dom.comments)==1 for c in annotations),'Compare original DrawingML text and target together; do not read notes from cells.')
    visibleok=True
    for c in annotations:
        n=one('comment-'+c['id'])
        visibleok &= bool(n and n['attrs'].get('data-target')==c['target'] and c['note'] in n['text'] and 'hidden' not in n['attrs'] and not any('hidden' in a['attrs'] for a in n['ancestors']) and not re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',n['attrs'].get('style',''),re.I))
    add('H07','Callout meaning remains visible to Markdown/HTML analysis',visibleok,'HTML comments alone are insufficient. Keep a visible specification-comment copy.')
    bindings=all((n:=one(c['target'])) and 'comment-'+c['id'] in n['attrs'].get('aria-describedby','').split() for c in annotations)
    add('H08','Each field or region references its own comment',bindings,'Use explicit target IDs; never attach a nearby bubble by guesswork.')
    ordered=[n['attrs'].get('id') for n in dom.nodes if n['attrs'].get('id') in {v for row in layout['rows'] for v in row}]
    expected_order=[v for row in layout['rows'] for v in row]
    add('H09','Message, user ID, password, then buttons follow reviewed layout',ordered==expected_order,'Use semantic order and grouped actions rather than width-2 spreadsheet coordinates.')
    labelok=all(sum(n['tag']=='label' and n['attrs'].get('for')==f['項目ID'] and n['text'].strip()==f['項目名'] for n in dom.nodes)==1 for f in spec['fields'])
    add('H10','Visible labels bind to the correct controls',labelok,'A label for userId must not point to password, and vice versa.')
    unsafe=any(n['tag'] in {'script','iframe','object','embed'} or any(k.startswith('on') for k in n['attrs']) or 'action' in n['attrs'] or 'formaction' in n['attrs'] for n in dom.nodes)
    add('H11','HTML is an inert layout reference',not unsafe,'No scripts, event handlers, submit destination, embedded active content or invented API endpoint.')
    defaults=all((n:=one(f['項目ID'])) and ('value' not in n['attrs'] if not f['初期値'] else n['attrs'].get('value')==f['初期値']) for f in spec['fields'])
    add('H12','Unspecified defaults are not fabricated',defaults and '初期値が空文字であるとは断定しない' in text,'An empty screenshot input is not evidence of a specified empty-string default.')
    htmlfile=path.with_name(path.stem+'.form.html')
    fragment=re.search(r'<section class="spec-form">.*?</section>',text,re.S)
    detached=htmlfile.is_file() and fragment and fragment.group() in htmlfile.read_text(encoding='utf-8')
    add('H13','Standalone HTML and Markdown contain the same form',detached,'Publish a directly viewable HTML file and the same semantic HTML in the Markdown.')
    buttons=[one(b['項目ID']) for b in spec['buttons']]
    groups=[{id(a) for a in n['ancestors'] if a['attrs'].get('class')=='spec-actions'} if n else set() for n in buttons]
    common=bool(groups and set.intersection(*groups))
    allids=[n['attrs']['id'] for n in dom.nodes if 'id' in n['attrs']]
    add('H14','Buttons grouped; IDs unique; no silently unsupported drawings',common and len(allids)==len(set(allids)) and not inv['warnings'] and not inv['notes'],'Group both actions on one row and surface unsupported drawing content.')
    failed=[c for c in checks if not c['passed']]
    result.update(passed_checks=len(checks)-len(failed),total_checks=len(checks),passed=not failed,status='ACCEPTANCE_CHECKS_PASS' if not failed else 'RETRY',source_drawing_sha256=spec['source_drawing_sha256'])
    return result
