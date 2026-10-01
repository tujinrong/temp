"""Discover linked, saved OLE previews without executing embedded documents.

Additive helper: existing cell/drawing converters are not changed. A hidden
DrawingML OLE placeholder is not the visibility of its VML picture. Resolve
matching worksheet OLE + VML shape first. Ambiguous visibility is REVIEW_REQUIRED.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

M='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
V='urn:schemas-microsoft-com:vml'
X='urn:schemas-microsoft-com:office:excel'
NS={'m':M,'v':V,'x':X}

def _zero(value: str | None) -> bool:
    try:return value is not None and float(value)==0
    except ValueError:return False

def _target(member: str, relative: str) -> str:
    path=posixpath.normpath(relative.lstrip('/') if relative.startswith('/') else posixpath.join(posixpath.dirname(member),relative))
    if path.startswith('../') or path in {'.','..'}:
        raise ValueError('ZIP relationship escapes the archive.')
    return path

def _rels(z: zipfile.ZipFile, member: str) -> dict:
    rp=posixpath.join(posixpath.dirname(member),'_rels',posixpath.basename(member)+'.rels')
    if rp not in z.namelist():return {}
    return {r.get('Id'):{'target':_target(member,r.get('Target')),'type':r.get('Type','')}
            for r in ET.fromstring(z.read(rp)) if r.get('TargetMode')!='External'}

def discover_previews(xlsx: str | Path) -> list[dict]:
    """Return metadata only. Never open/execute an embedded OLE package."""
    results=[]
    with zipfile.ZipFile(xlsx) as z:
        book=ET.fromstring(z.read('xl/workbook.xml'));br=_rels(z,'xl/workbook.xml')
        for tab,sheet in enumerate(book.findall('m:sheets/m:sheet',NS),1):
            if sheet.get('state','visible')!='visible':continue
            if sheet.get('name','').strip() in {'変更履歴','改訂履歴','凡例'}:continue
            member=br[sheet.get('{'+R+'}id')]['target'];root=ET.fromstring(z.read(member));rels=_rels(z,member)
            vml={}
            for rel in rels.values():
                if rel['type'].endswith('/vmlDrawing'):
                    for shape in ET.fromstring(z.read(rel['target'])).findall('v:shape',NS):
                        vml[shape.get('id','').removeprefix('_x0000_s')]=shape
            seen=set()
            for ole in root.findall('.//m:oleObject',NS):
                sid=ole.get('shapeId');props=ole.find('m:objectPr',NS)
                if sid in seen or props is None:continue
                seen.add(sid)
                image=rels.get(props.get('{'+R+'}id'),{}).get('target')
                if not image:continue
                shape=vml.get(sid);style=(shape.get('style','') if shape is not None else '').lower()
                if re.search(r'(?:visibility\s*:\s*hidden|display\s*:\s*none)',style):continue
                client=shape.find('x:ClientData',NS) if shape is not None else None
                visible_flag=client.find('x:Visible',NS) if client is not None else None
                if visible_flag is not None and (visible_flag.text or '').strip().lower() in {'false','0'}:continue
                status='VISIBLE' if shape is not None else 'REVIEW_REQUIRED'
                # Do not infer visibility across partially hidden rows/columns.
                anchor=client.findtext('x:Anchor','',NS) if client is not None else ''
                coords=[int(n) for n in re.findall(r'\d+',anchor)]
                if len(coords)==8:
                    c1,_,r1,_,c2,_,r2,_=coords
                    rows={int(r.get('r')) for r in root.findall('m:sheetData/m:row',NS)
                          if r.get('hidden') in {'1','true'} or _zero(r.get('ht'))}
                    cols=[]
                    for col in root.findall('m:cols/m:col',NS):
                        if col.get('hidden') in {'1','true'} or _zero(col.get('width')):
                            cols.append((int(col.get('min')),int(col.get('max'))))
                    if any(r1+1<=r<=r2+1 for r in rows) or any(a<=c2+1 and b>=c1+1 for a,b in cols):status='REVIEW_REQUIRED'
                    sf=root.find('m:sheetFormatPr',NS)
                    if sf is not None and (sf.get('zeroHeight') in {'1','true'} or _zero(sf.get('defaultRowHeight')) or _zero(sf.get('defaultColWidth'))):status='REVIEW_REQUIRED'
                else:status='REVIEW_REQUIRED'
                raw=z.read(image)
                results.append({'sheet':sheet.get('name'),'tab':tab,'shape_id':sid,
                                'preview_member':image,'sha256':hashlib.sha256(raw).hexdigest(),
                                'status':status,'basis':'worksheet OLE objectPr + matching VML picture; embedded package not executed'})
    return results

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('xlsx',type=Path);p.add_argument('--json',type=Path,required=True);a=p.parse_args()
    if a.json.resolve()==a.xlsx.resolve():p.error('Report must not overwrite source.')
    try:data=discover_previews(a.xlsx)
    except (OSError,ValueError,KeyError,ET.ParseError,zipfile.BadZipFile) as exc:p.error(str(exc))
    a.json.parent.mkdir(parents=True,exist_ok=True);a.json.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(data)} linked OLE previews; '+str(a.json));return 0
if __name__=='__main__':raise SystemExit(main())
