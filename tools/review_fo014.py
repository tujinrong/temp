"""Independent source-specific checks for FO-014; never imports its builder.
Checks source tuple preservation, prerequisites, financial formulas, diagrams,
HTML, visibility, QA and links. Mermaid is validated separately by the existing
actual-parser/browser gate. This is not a general AI-understanding score.
"""
from pathlib import Path
import argparse,hashlib,json,re,zipfile,posixpath
from xml.etree import ElementTree as E
from bs4 import BeautifulSoup
SOURCE_SHA='8cfb0e50272542dc6270dd318d911b279661175a6b9433f7535930a3eb383d55'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def display(e):
    if e is None or e.tag.rsplit('}',1)[-1] in ('rPh','phoneticPr'):return ''
    if e.tag.rsplit('}',1)[-1]=='t':return e.text or ''
    return ''.join(display(c) for c in e)

def source(path):
    result=[]
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        shared=[display(x) for x in E.fromstring(z.read('xl/sharedStrings.xml'))]
        rels={r.get('Id'):posixpath.normpath('xl/'+r.get('Target')) for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for sh in E.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
            if sh.get('state','visible')!='visible' or sh.get('name')=='変更履歴':continue
            part=rels[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            root=E.fromstring(z.read(part));values={}
            for row in root.findall('m:sheetData/m:row',NS):
                if row.get('hidden') in ('1','true') or (row.get('ht') is not None and float(row.get('ht'))==0):continue
                for c in row.findall('m:c',NS):
                    v=c.find('m:v',NS)
                    if v is not None:values[c.get('r')]=shared[int(v.text)] if c.get('t')=='s'else v.text
            result.append((sh.get('name'),values))
    return result

def tables(md):
    out=[];cur=[]
    for line in md.splitlines()+['']:
        if line.startswith('|'):cur.append(line);continue
        if len(cur)>1:
            split=lambda l:[x.strip().strip('`') for x in re.split(r'(?<!\\)\|',l[1:-1])]
            head=split(cur[0]);sep=split(cur[1])
            if len(head)==len(sep) and all(re.fullmatch(':?-{3,}:?',x)for x in sep):
                out.append([dict(zip(head,split(l)))for l in cur[2:]])
        cur=[]
    return out

def review(xlsx,mdpath,qapath):
    xlsx,mdpath,qapath=map(Path,(xlsx,mdpath,qapath));raw=mdpath.read_bytes();md=raw.decode('utf-8');qa=qapath.read_text(encoding='utf-8')
    clean=re.sub(r'<!--.*?-->','',md,flags=re.S);tb=tables(clean);s=source(xlsx);S=dict(s);checks=[]
    add=lambda id,title,passed:checks.append({'id':id,'check':title,'passed':bool(passed)})
    def rec(expected):return any(all(row.get(k)==v for k,v in expected.items()) for t in tb for row in t)
    def norm(t):return t.replace('\n','<br>').replace('|','\\|').strip()
    add('A01','Exact reviewed input fingerprint',hashlib.sha256(xlsx.read_bytes()).hexdigest()==SOURCE_SHA)
    names=['はじめに']+[n.rstrip() for n,_ in s[1:]]
    add('A02','16 chapters in saved visible sheet order',re.findall(r'^## (.+)$',md,re.M)==[f'{i}. {n}'for i,n in enumerate(names,1)])
    add('A03','One title and no legend/history chapter',len(re.findall('^# ',md,re.M))==1 and not re.search(r'^##.*(変更履歴|凡例)',md,re.M))
    add('A04','No phonetic metadata appended as document text','シハライアンナイショ' not in md and 'カブシキガイシャ'not in md)
    add('A05','No raw coordinate/grid transcription',not re.search(r'col_width=|merge=[A-Z]|Source grid|^\| (?:セル座標|Cell|Coordinate) \|',md,re.M))
    add('A06','UTF8 BOM-free document and QA',not raw.startswith(b'\xef\xbb\xbf') and not qapath.read_bytes().startswith(b'\xef\xbb\xbf'))
    add('A07','Cover metadata and current version','第1.13版'in md and '2025-05-23'in md and '2024-06-03／JBS秋信'in md and '2024-07-29／サンスター藤田'in md)
    v=S['テーブル一覧']
    add('F01','15 exact logical/physical/I-O table associations',all(rec({'No.':v[f'A{r}'],'論理名':v[f'K{r}'],'物理名':v[f'AC{r}'],'I/O':v[f'AS{r}']})for r in range(6,21)))
    v=S['帳票出力仕様']
    add('F02','47 exact report output values including fixed wording',all(rec({'No.':v[f'H{r}'],'項目名':v[f'J{r}'],'出力値':norm(v[f'AO{r}'])})for r in range(8,55)))
    add('F03','47 source and Tmp field associations',all(rec({'No.':v[f'H{r}'],'取得元テーブル.フィールド':v[f'CC{r}']+'.'+v[f'CO{r}'],'TmpTable.フィールド':v[f'DG{r}']+'.'+v[f'DT{r}']})for r in range(8,55)))
    add('F04','All item formats, alignment and widths',all(rec({'No.':v[f'H{r}'],'フォーマット':v.get(f'V{r}','原資料空欄'),'横位置':v[f'AB{r}'],'縦位置':v[f'AE{r}'],'最大項目長（項目幅）':v[f'AK{r}']})for r in range(8,55)))
    v=S['テーブル出力仕様']
    add('F05','20 exact Tmp logical/physical/formula mappings',all(rec({'No.':v[f'A{r}'],'論理名':v[f'C{r}'],'物理名':v[f'M{r}'],'設定内容':norm(v[f'W{r}'])})for r in range(9,29)))
    v=S['オブジェクト一覧']
    add('F06','7 exact object names and types',all(rec({'No.':v[f'A{r}'],'オブジェクト名':v[f'C{r}'],'属性（原表記）':v[f'S{r}']})for r in range(6,13)))
    add('F07','Supplier multiple and range syntax; mode only multiple','「..」で範囲指定'in md and '「,」で複数入力'in md and '支払方法にも範囲指定があるとは記載されていない'in md)
    add('F08','Date blank versus historical parameter values','支払年月日 | 日付 | 可 | 必須 | 空欄'in md and '確認済みレビューR09'in md)
    add('F09','Parameter required flags and per-company persistence','支払方法 | テキスト | 可 | 必須 | 前回設定値'in md and '法人ごとに保持'in md)
    add('F10','Voucher base-date derives from LastSettleVoucher','VendTrans.Voucher | 2-1-3で取得したLastSettleVoucher'in md and '取り消し線'in md)
    add('F11','Bank account joins voucher-specific account not current unconditional master',all(x in md for x in ('VendBankAccount.AccountID = VendTrans.ThirdPartyBankAccountId','VendBankAccount.VendAccount = VendTrans.AccountNum')))
    add('F12','Monthly offset aggregation is not silently given missing filters','MONTH(VendTrans.TransDate)'in md and '追加条件を推測せず'in md and 'Q04'in qa and 'Q05'in qa)
    add('F13','Voucher posting/trans-type and general-ledger join types',all(x in md for x in ('LedgerPostingType::Bank','LedgerTransType::Payment','| Outer | GeneralJournalEntry.RecId = GeneralJournalAccountEntry.GeneralJournalEntry')))
    add('F14','COMMON parameter and configurable account code',rec({'機能ID(FunctionId)':'COMMON','項目ID(ItemId)':'MAINACCOUNT','Key(Key)':'1','値(Value)':'2090144'}))
    add('F15','Fee amount joins and final subtraction',all(x in md for x in ('CustVendPaymJournalFee.RefRecId = LedgerJournalTrans.RecId','AmountOfPayment = 2-1-6-1で取得したAmountMST − BankTransferFeeAmount','49,340')))
    add('F16','Delivery sum, offset sum, previous purchase month',all(x in md for x in ('DeliveryPaymentAmount = AmountOfPayment + OffsetAmountForGoods + BankTransferFeeAmount','OffsetAmountForGoods = 未収入金相殺額 + 預かり売掛金相殺額','PurchaseMonth = 債務の支払基準日 − 1か月')))
    add('F17','Exact message IDs, text, substitution and severity',all(rec(e)for e in [
        {'ID':'SJ00343','種別':'情報ログ／Warning','メッセージ':'入力されたパラメーターでは%1の対象となるデータは存在しません。'},
        {'ID':'SJ00353','種別':'情報ログ／Warning','発生条件':'支払伝票を複数取得'},
        {'ID':'SJ00224','種別':'情報ログ／Error','発生条件':'汎用パラメータを取得不可'}]))
    add('F18','Year, supplier, fee and fax discrepancies retained in QA',all(x in qa for x in ('MONTH(TransDate)','FeeValue','AccountingCurrencyAmount','DirPartyAddress','DirPartyTable','Locator','Description')))
    add('F19','Contact selection uses purpose containment and Phone/Fax',all(x in md for x in ('like "%支払案内書%"','LogisticsElectronicAddressMethodType::Phone','LogisticsElectronicAddressMethodType::Fax','Descriptionを問合せ先部署名')))
    graphs=re.findall(r'```mermaid\n(.*?)\n```',md,re.S)
    add('G01','Source review expects two diagrams',len(graphs)==2)
    g='\n'.join(graphs)
    add('G02','DFD read/write directions',all(x in g for x in ('DBS[','--> P21','P22 --> TMP','TMP --> P23')))
    add('G03','OK/no, voucher/non-single, missing parameter branches',all(x in g for x in ('OK -->|いいえ| END','ONE -->|いいえ| ERROR','PARAM -->|いいえ| ERROR','ERROR --> END','FILE --> END')))
    add('G04','Program flow source sequence preserved',all(x in g for x in ('O1 --> O2','VENDOR --> COMPANY','COMPANY --> VENDTRANS','BANK --> AMOUNT','TMP --> FILE')))
    soup=BeautifulSoup(md,'html.parser');frames=soup.find_all('section',id=re.compile('^fo014-'))
    add('H01','11 outer screen/report frames and static controls',len(frames)==11 and all('border:'in f.get('style','')for f in frames) and not soup.find('script'))
    add('H02','Dialog three labels, text fields and sample values',all(soup.find('input',id=id)and soup.find('input',id=id).get('value')==v for id,v in [('fo014-date','2024/08/20'),('fo014-vendor','1111111'),('fo014-mode','T')]))
    add('H03','No explanatory source comments inside frames',not any('callout 'in str(f)for f in frames))
    add('H04','Five target-associated comments have visible copies',all(f'callout C{i:02d}'in md and f'**C{i:02d}'in clean for i in range(1,6)))
    add('H05','Modern report excludes legacy VAN but legacy is preserved','VAN立替金'not in str(soup.find(id='fo014-report')) and 'VAN立替金'in str(soup.find(id='fo014-legacy')))
    add('H06','Bank account leading zero and legacy arithmetic preserved','0100486'in clean and '29,180,322'in clean and '29,179,992'in clean)
    add('H07','Examples not treated as initial values','実データや入力の初期値ではない'in md and '画面画像の例示'in md)
    from markdown_it import MarkdownIt
    rendered_html = MarkdownIt('commonmark', {'html': True}).enable('table').render(md)
    rendered = BeautifulSoup(rendered_html, 'html.parser')
    add('H08','Rendered Markdown contains all report amount-table rows',all(
        rendered.find(id=prefix+'-delivery') and rendered.find(id=prefix+'-fee')
        and len(rendered.find(id=prefix+'-delivery').find_parent('table').find_all('tr'))==count
        for prefix,count in [('fo014-report',4),('fo014-sample',4),('fo014-legacy',5)]))
    add('H09','HTML markup never leaks as visible source code',not any(
        re.search(r'<(?:tr|td|th|span)\b',pre.get_text()) for pre in rendered.find_all('pre')))

    add('Q01','Twelve unique unanswered QA IDs',set(re.findall(r'<a id="(q\d+)"></a>',qa))=={f'q{i:02d}'for i in range(1,13)} and qa.count('**回答**：未回答')==12)
    add('Q02','All thirteen reviewed records, no demand for re-answer',all(f'<a id="r{i:02d}">'in qa for i in range(1,14)) and '再回答を求めない'in qa)
    add('Q03','QA selections include other/unknown',qa.count('未定・要調査')==12 and qa.count('その他')>=12)
    ids=set(re.findall(r'\bid="([^"]+)"',md));qids=set(re.findall(r'\bid="([^"]+)"',qa))
    links=re.findall(r'\]\(([^)]+)\)',md)
    add('Q04','Internal and QA anchors resolve',all((x[1:]in ids if x.startswith('#')else x.split('#')[1]in qids if '../qa/'in x and '#'in x else True)for x in links))
    add('Q05','No duplicate output HTML ids',len(ids)==len(re.findall(r'\bid="([^"]+)"',md)))
    return {'status':'PASS'if all(c['passed']for c in checks)else'FAIL','passed':all(c['passed']for c in checks),'markdown_sha256':hashlib.sha256(raw).hexdigest(),'qa_sha256':hashlib.sha256(qapath.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(xlsx.read_bytes()).hexdigest(),'checks':checks,'passed_checks':sum(c['passed']for c in checks),'total_checks':len(checks),'scope':'Source-reviewed FO-014 checks, not a business approval or general-purpose conversion guarantee.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('xlsx',type=Path);p.add_argument('markdown',type=Path);p.add_argument('qa',type=Path);p.add_argument('--json',type=Path,required=True);a=p.parse_args();data=review(a.xlsx,a.markdown,a.qa);a.json.parent.mkdir(exist_ok=True,parents=True);a.json.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(data['status'],data['passed_checks'],data['total_checks']);print([c['id']for c in data['checks']if not c['passed']]);raise SystemExit(0 if data['passed']else 1)
