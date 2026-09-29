"""Run up to five evaluated form/callout revisions, preserving every candidate."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from .semantic_repair import convert as baseline
from .form_conversion import convert
from .form_review import form_review

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(xlsx,contract,layout,output,report_dir,max_loops=5):
    if not 1<=max_loops<=5: raise ValueError('max_loops must be 1..5')
    xlsx,contract,layout,output,report_dir=map(Path,(xlsx,contract,layout,output,report_dir))
    report_dir.mkdir(parents=True,exist_ok=True); source=sha(xlsx); history=[]
    strategies=['Previous accepted semantic converter, on expanded workbook',
                'Extract drawing text and reconstruct HTML; literal HTML comments',
                'Retain comments visibly and link notes to controls for AI analysis']
    for loop in range(1,max_loops+1):
        path=report_dir/f'loop{loop}.md'
        if loop==1: path.write_text(baseline(xlsx,4),encoding='utf-8')
        else: convert(xlsx,layout,path,visible=loop>=3)
        ev=form_review(xlsx,path,contract,layout)
        item={'loop':loop,'strategy':strategies[min(loop,3)-1],'sha256':sha(path),'candidate':str(path),
              'responding_to':[c['id'] for c in history[-1]['acceptance']['checks'] if not c['passed']] if history else [],'acceptance':ev}
        history.append(item)
        (report_dir/f'loop{loop}.json').write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f"Loop {loop}: {ev['passed_checks']}/{ev['total_checks']} — {ev['status']}")
        for check in ev['checks']:
            if not check['passed']:print(f"  {check['id']}: {check['check']}")
        if ev['passed']:break
        if loop>1 and history[-2]['sha256']==item['sha256']:
            item['stop_reason']='No candidate change; further automatic repetition has no benefit.';break
    best=max(history,key=lambda h:(h['acceptance']['passed'],h['acceptance']['passed_checks'],-h['loop']))
    output.parent.mkdir(parents=True,exist_ok=True)
    if best['loop']>1: convert(xlsx,layout,output,visible=best['loop']>=3)
    else: output.write_text(Path(best['candidate']).read_text(encoding='utf-8'),encoding='utf-8')
    final=form_review(xlsx,output,contract,layout)
    if sha(xlsx)!=source:raise RuntimeError('Source workbook was modified during conversion.')
    receipt={'source':str(xlsx),'source_sha256':source,'source_unchanged':True,'contract_sha256':sha(contract),'layout_review_sha256':sha(layout),'selected_loop':best['loop'],'status':final['status'],'final':str(output),'final_sha256':sha(output),'final_acceptance':final,'loops':history,
             'scope':'Synthetic source-reviewed screenshot. Deterministic acceptance checks, not an AI-understanding score. Other screenshots need their own visual mapping; no automatic OCR/vision service is included.'}
    (report_dir/'evaluation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Form hard-copy and callout evolution run','','The same 39 checks (25 existing + 14 drawing/HTML checks) were applied to every revision.','', '| Loop | Change | Checks | Outcome |','|---|---|---:|---|']
    for h in history:
        e=h['acceptance'];lines.append(f"| {h['loop']} | {h['strategy']} | {e['passed_checks']}/{e['total_checks']} | {e['status']} |")
    for h in history:
        lines+=['',f"## Loop {h['loop']}",'',f"Candidate SHA-256: `{h['sha256']}`",'']
        failures=[c for c in h['acceptance']['checks'] if not c['passed']]
        lines += [f"- {c['id']}: {c['check']}. {c['evidence_or_repair']}" for c in failures] or ['All acceptance checks passed.']
    lines+=['','## Final result','',f"Selected loop: {best['loop']}. Status: **{final['status']}**.",'',
            'The expanded workbook contains one embedded hard-copy PNG and five editable DrawingML callouts. Callouts export as HTML comments plus visible, target-linked specification notes. The HTML is a static form layout, not a login implementation.','',
            'Source unchanged during the conversion run: true.','',receipt['scope'],'',f'Source SHA-256: `{source}`','']
    (report_dir/'evaluation.md').write_text('\n'.join(lines),encoding='utf-8')
    return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('xlsx',type=Path)
    p.add_argument('--contract',required=True,type=Path);p.add_argument('--layout-review',required=True,type=Path)
    p.add_argument('--output',type=Path,default=Path('output/japanese_program_spec_with_callouts.md'))
    p.add_argument('--report-dir',type=Path,default=Path('reports/forms'));p.add_argument('--max-loops',type=int,choices=range(1,6),default=5)
    a=p.parse_args();r=run(a.xlsx,a.contract,a.layout_review,a.output,a.report_dir,a.max_loops)
    raise SystemExit(0 if r['status']=='ACCEPTANCE_CHECKS_PASS' else 2)
if __name__=='__main__':main()
