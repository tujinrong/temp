"""Independent FO-007 source-bound checks. Does not import the converter.

Checks visible saved source tuples and source-reviewed image relationships.
Run the unchanged src.independent_evaluate Mermaid gate after this check.
"""
from __future__ import annotations
import argparse, hashlib, json, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup

SOURCE_SHA='8120082747ec91321240783199bc67d3c780c74a446aecc106bd90ccde9b564b'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def source_cells(z,member,ss):
    out={}
    for c in ET.fromstring(z.read(member)).findall('.//m:sheetData/m:row/m:c',NS):
        v=c.find('m:v',NS);text=v.text if v is not None else ''
        if c.get('t')=='s' and text:text=ss[int(text)]
        if c.get('t')=='inlineStr':text=''.join(t.text or '' for t in c.findall('.//m:t',NS))
        if text:out[c.get('r')]=text
    return out

def md_tables(text):
    tables=[];block=[]
    def finish():
        if len(block)>1:
            split=lambda x:[a.strip().strip('`') for a in re.split(r'(?<!\\)\|',x.strip().strip('|'))]
            keys=split(block[0]);sep=split(block[1])
            if len(keys)==len(sep) and all(re.fullmatch(':?-{3,}:?',c) for c in sep):
                tables.append([dict(zip(keys,split(line))) for line in block[2:] if len(split(line))==len(keys)])
        block.clear()
    for l in text.splitlines():
        if l.startswith('|'):block.append(l)
        else:finish()
    finish();return tables

def review(xlsx,markdown,qa):
    raw=Path(markdown).read_bytes();m=raw.decode('utf8');q=Path(qa).read_text(encoding='utf8')
    clean=re.sub(r'<!--.*?-->','',m,flags=re.S);tables=md_tables(clean);soup=BeautifulSoup(clean,'html.parser');checks=[]
    def add(id,title,condition):checks.append({'id':id,'check':title,'passed':bool(condition)})
    def record(wanted):return any(all(r.get(k)==str(v) for k,v in wanted.items()) for table in tables for r in table)
    sha=hashlib.sha256(Path(xlsx).read_bytes()).hexdigest();add('A01','Reviewed source SHA-256',sha==SOURCE_SHA)
    if sha!=SOURCE_SHA:return {'checks':checks,'passed':False,'markdown_sha256':hashlib.sha256(raw).hexdigest()}
    with zipfile.ZipFile(xlsx) as z:
        ss=[''.join(t.text or '' for t in e.findall('m:t',NS)+e.findall('m:r/m:t',NS)) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        wb=ET.fromstring(z.read('xl/workbook.xml'));all_sheets=wb.findall('m:sheets/m:sheet',NS)
        wanted=[e.get('name').strip() for e in all_sheets if e.get('state','visible')=='visible' and e.get('name').strip() not in {'凡例','変更履歴','改訂履歴'}];wanted[0]='はじめに'
        source_main=source_cells(z,'xl/worksheets/sheet9.xml',ss);source_set=source_cells(z,'xl/worksheets/sheet13.xml',ss)
        source_table=source_cells(z,'xl/worksheets/sheet14.xml',ss);source_obj=source_cells(z,'xl/worksheets/sheet19.xml',ss)
    add('A02','15 chapter names and exact source tab order',re.findall(r'^## \d+\. (.+)$',m,re.M)==wanted)
    add('A03','No excluded legend/history chapters',not re.search(r'^#{1,4}[^\n]*(凡例|変更履歴|改訂履歴)',m,re.M))
    add('A04','One title, report content not in specification',len(re.findall(r'^# ',m,re.M))==1 and '## 対象範囲と読み方' not in m and '## 評価ループ' not in m)
    add('A05','Metadata dates and source associations',all(record(r) for r in [{'項目':'版数','内容':'第1.9版'},{'項目':'作成日・作成者','内容':'2024-06-03／JBS井田'},{'項目':'基本設計部確認日・確認者','内容':'2024-07-18／サンスター藤田'}]))
    add('A06','No raw grid dumps; UTF8 without BOM',not raw.startswith(b'\xef\xbb\xbf') and '\r' not in m and not re.search(r'Source grid|col_width=|data-grid-width|merge=[A-Z]+\d',m))
    add('F01','Table I/O associations',record({'論理名':'仕入先トランザクション','物理名':'VendTrans','I/O':'I/O'}) and record({'論理名':'財務タグ','物理名':'FinTag','I/O':'I'}))
    source_rows=[]
    for r in range(9,88,3):
        source_rows.append({'項目名':source_main['H'+str(r)],'種類':source_main['Q'+str(r)]+source_main.get('Q'+str(r+1),''),'入力':'不可','必須':'任意','表示内容・動作':source_main.get('Y'+str(r+1),'') if source_main['Y'+str(r)]=='＜表示内容＞' else source_main['Y'+str(r)]})
    add('F02','All 27 read-only field/type/source tuples',all(record(r) for r in source_rows))
    hidden=[r for r in source_rows if r['表示内容・動作']=='非表示にする']
    add('F03','Application-hide requirements not removed as Excel hidden data',len(hidden)==11 and all(record(r) for r in hidden))
    add('F04','Four settlement fields remain editable and optional',all(record({'項目名':source_set['H'+str(r)],'入力':'可','必須':'任意','表示・更新先':source_set['Y'+str(r+1)]}) for r in (9,12,15,18)))
    add('F05','Three exact VendTrans output fields and update conditions',all(record({'論理名':source_table['C'+str(r)],'物理名':source_table['M'+str(r)],'更新時の設定内容（原文）':source_table['W'+str(r)]}) for r in (9,11,13)))
    add('F06','Eleven object name/type associations',all(record({'オブジェクト名':source_obj['C'+str(r)],'属性':source_obj['S'+str(r)]}) for r in range(6,17)))
    add('F07','Company selection stays source-scoped',all(s in m for s in ['ログインしている法人','法人を切り替えて実行']))
    add('F08','Caller-dependent supplier/name visibility',record({'呼出し元':'すべての仕入先画面 ＞ トランザクションボタン','仕入先':'非表示','名前':'非表示'}) and record({'呼出し元':'仕入先トランザクション一覧画面','仕入先':'表示','名前':'表示'}))
    add('F09','Disabled tags do not retrieve information',record({'機能有効化の状態':'≠有効化','処理':'情報を取得せず処理を終了する。'}))
    add('F10','Active tags, maximum 20 and personalization',all(s in m for s in ['アクティブ化され','20個','右端','パーソナライズ','タグ名・登録順を固定しない']))
    add('F11','Conflicting tag slots explicitly preserved',record({'原図の項目名':'RefVoucherNum','原図の参照先':'FinTag.Tag02'}) and record({'原図の項目名':'DataClass','原図の参照先':'FinTag.Tag03'}) and 'Tag03' in q and 'Tag02' in q)
    add('F12','Conflicting base-date spelling not silently corrected','VendTrans.SJ_PaymBaseDate' in m and 'SJ_PaymtBaseDate' in m and 'SJ_PaymtBaseDate' in q and 'SJ_PaymBaseDate' in q)
    diagrams=re.findall(r'```mermaid\n(.*?)\n```',m,re.S)
    add('G01','Two source-backed Mermaid diagrams',len(diagrams)==2)
    dfd=diagrams[0] if diagrams else '';flow=diagrams[-1] if diagrams else ''
    add('G02','DFD read direction for both callers',all(s in dfd for s in ['--> P1','--> P2','V1[','F1[','V2[','F2[']) and not re.search(r'P[12]\s*-->\s*[VF][12]',dfd))
    add('G03','Enabled and disabled branches preserve behavior','A -->|はい| F[' in flow and 'A -->|いいえ| N[' in flow and '財務タグ含まない' in flow and 'F --> T[' in flow and 'N --> E' in flow)
    add('G04','Original join expression remains visible and queried','FinTagRecId. = LedgerJournalTrans.FinTag' in clean and 'VendTrans.RecId = LedgerJournalTrans.VendTransId' in clean and 'FinTagRecId.' in q)
    add('G05','16 program-flow field references','VendTable.Name' in clean and 'VendTrans.DocumentNum' in clean and 'VendTrans.LastSettleVoucher' in clean and sum('参照先（原図表記）' in r for tb in tables for r in tb)==16)
    add('H01','Five static forms, no executable scripts or requests',len(soup.find_all('form'))==5 and not soup.find('script') and not soup.select('[onclick], [onchange], form[action], iframe'))
    frames=soup.find_all('section');add('H02','Six visible screen frames',len(frames)==6 and all('border:1px solid' in x.get('style','') for x in frames))
    main=soup.find('table',id='fo007-list-grid');ind=soup.find('table',id='fo007-individual-grid')
    add('H03','List 24 visible rows x 21 source columns',main is not None and len(main.select('tbody tr'))==24 and len(main.select('th'))==21 and all(len(row.find_all('td'))==21 for row in main.select('tbody tr')))
    add('H04','Individual excerpt excludes supplier/name columns',ind is not None and len(ind.select('th'))==19 and all(t.get_text() not in ['仕入先','名前'] for t in ind.select('th')) and len(ind.select('tbody tr'))==3 and '先頭3行を抜粋' in m)
    add('H05','Financial-tag settings example','Item' in soup.find(id='fo007-tag-grid').get_text() and len(soup.select('#fo007-tag-grid tbody tr'))==3)
    add('H06','Settlement source example and absence of fabricated new positions',len(soup.select('#fo007-set-grid tbody tr'))==3 and '-550,000.00' in clean and '最終配置は図示されていない' in m)
    add('H07','Callout comments are outside frames',all(not re.search(r'<!--|C-[LTM A]\d',str(f)) for f in frames))
    add('H08','All thirteen visible callout/text annotations',len(re.findall(r'<!-- callout C-',m))==13 and len(re.findall(r'> \*\*C-',m))==13)
    add('H09','Samples distinguished from defaults','初期値・処理条件ではない' in m and '例示' in m)
    add('Q01','Nine stable QA IDs and unanswered fields',re.findall(r'<a id="(q\d+)"',q)==['q01','q07','q06','q02','q04','q08','q03','q09','q05'] and q.count('**回答**：未回答')==9)
    add('Q02','QA choices include alternatives and uncertainty',q.count('未定・要調査')==9 and q.count('その他')==9)
    add('Q03','Completed review record and confirmation date','2024-07-18' in q and '原資料では確認済み' in q and 'Req325' in q)
    anchors=set(re.findall(r'<a id="([^"\n]+)"',q));refs=re.findall(r'\.md#(q\d+|review-records)\)',m)
    add('Q04','All QA links resolve',set(refs)<=anchors and set(f'q{i:02}' for i in range(1,10))<=set(refs))
    return {'source_sha256':sha,'markdown_sha256':hashlib.sha256(raw).hexdigest(),'qa_sha256':hashlib.sha256(Path(qa).read_bytes()).hexdigest(),'checks':checks,'passed':all(c['passed'] for c in checks),'passed_checks':sum(c['passed'] for c in checks),'total_checks':len(checks),'scope':'FO-007 source-specific content acceptance, not a general accuracy score.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('xlsx');p.add_argument('markdown');p.add_argument('qa');p.add_argument('--json',type=Path,required=True);a=p.parse_args()
    if a.json.resolve() in [Path(x).resolve() for x in [a.xlsx,a.markdown,a.qa]]:p.error('Do not overwrite source files.')
    r=review(a.xlsx,a.markdown,a.qa);a.json.parent.mkdir(parents=True,exist_ok=True);a.json.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(r.get('passed_checks'),r.get('total_checks'),r['passed'])
    for c in r['checks']:
        if not c['passed']:print(c)
    return 0 if r['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
