"""Read embedded pictures and DrawingML text without modifying the workbook.

Floating shapes are not worksheet cell values. Unknown associations stay unknown;
only an explicit `対象: fieldId` annotation establishes a semantic target here.
No OCR, external relationship fetching, VML geometry inference, or macro execution.
"""
from __future__ import annotations
import hashlib
import json
import posixpath
import re
import struct
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from .visible_scope import WorkbookScope, truth

M='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
D='http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
NS={'m':M,'r':R,'xdr':D,'a':A}
MAX_PART=25_000_000

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_part(z, name):
    info=z.getinfo(name)
    if info.file_size>MAX_PART:
        raise ValueError(f'Workbook part too large: {name}')
    return z.read(name)

def xml(z, name):
    data=read_part(z,name)
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('DTD/entity declarations are not accepted.')
    return ET.fromstring(data)

def relationships(z, owner):
    name=posixpath.join(posixpath.dirname(owner),'_rels',posixpath.basename(owner)+'.rels')
    if name not in z.namelist(): return {}
    result={}
    for rel in xml(z,name):
        if rel.get('TargetMode')=='External': continue
        target=rel.get('Target','')
        resolved=(target.lstrip('/') if target.startswith('/') else
                  posixpath.normpath(posixpath.join(posixpath.dirname(owner),target)))
        if resolved.startswith('../') or ':' in resolved: continue
        result[rel.get('Id')]={'part':resolved,'type':rel.get('Type','')}
    return result

def extract(path: str | Path, asset_dir: str | Path | None=None) -> dict:
    """Return a JSON-safe source inventory. Export images only when requested."""
    result={'images':[],'callouts':[],'notes':[],'warnings':[]}
    if asset_dir is not None:
        asset_dir=Path(asset_dir); asset_dir.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path) as z:
        if len(z.infolist())>10000 or sum(i.file_size for i in z.infolist())>150_000_000:
            raise ValueError('Workbook exceeds inspection safety limits.')
        scope=WorkbookScope.from_zip(z)
        rels=relationships(z,'xl/workbook.xml')
        for s in xml(z,'xl/workbook.xml').findall('m:sheets/m:sheet',NS):
            sheet=s.get('name')
            sheet_scope=scope.sheets[sheet]
            if not sheet_scope.included:
                continue
            part=rels[s.get('{'+R+'}id')]['part']
            sr=relationships(z,part)
            for dr in xml(z,part).findall('m:drawing',NS):
                key=dr.get('{'+R+'}id')
                if key not in sr:
                    result['warnings'].append(f'{sheet}: unresolved/external drawing');continue
                drawing=sr[key]['part']; drels=relationships(z,drawing)
                for anchor in xml(z,drawing):
                    anchor_state=sheet_scope.anchor_state(anchor)
                    if anchor_state=='excluded':
                        continue
                    if anchor_state=='review':
                        result['warnings'].append(f'{sheet}: drawing visibility requires visual review')
                    # A hidden parent group suppresses its descendants.
                    for group in list(anchor.findall('.//xdr:grpSp',NS)):
                        prop=group.find('xdr:nvGrpSpPr/xdr:cNvPr',NS)
                        if prop is not None and truth(prop.get('hidden')):
                            for parent in anchor.iter():
                                if group in list(parent):
                                    parent.remove(group)
                                    break
                    origin=anchor.find('xdr:from',NS)
                    position={}
                    if origin is not None:
                        position={ET.QName(c.tag).text.split('}')[-1]:int(c.text or 0) for c in origin}
                    for sp in anchor.findall('.//xdr:sp',NS):
                        prop=sp.find('xdr:nvSpPr/xdr:cNvPr',NS)
                        if prop is not None and truth(prop.get('hidden')):
                            continue
                        geom=sp.find('xdr:spPr/a:prstGeom',NS)
                        paragraphs=[''.join(t.text or '' for t in p.findall('.//a:t',NS))
                                    for p in sp.findall('xdr:txBody/a:p',NS)]
                        text='\n'.join(paragraphs).strip()
                        if not text: continue
                        kind=geom.get('prst','') if geom is not None else 'custom'
                        target=re.search(r'対象\s*[:：]\s*([A-Za-z_][\w.-]*)',text)
                        header, sep, note=text.partition('\n')
                        item={'sheet':sheet,'part':drawing,'shape_id':prop.get('id') if prop is not None else '',
                              'id':prop.get('name') if prop is not None else '', 'geometry':kind,
                              'text':text,'target':target.group(1) if target else None,
                              'note':note if target and sep else text,'anchor':position}
                        result['callouts' if 'callout' in kind.lower() else 'notes'].append(item)
                    for pic in anchor.findall('.//xdr:pic',NS):
                        prop=pic.find('xdr:nvPicPr/xdr:cNvPr',NS)
                        if prop is not None and truth(prop.get('hidden')):
                            continue
                        blip=pic.find('.//a:blip',NS)
                        key=blip.get('{'+R+'}embed') if blip is not None else None
                        if key not in drels:
                            result['warnings'].append(f'{sheet}: external/unresolved picture');continue
                        media=drels[key]['part']; data=read_part(z,media)
                        if data.startswith(b'\x89PNG\r\n\x1a\n'):
                            ext='.png'; width,height=struct.unpack('>II',data[16:24])
                        elif data.startswith(b'\xff\xd8'):
                            ext='.jpg'; width=height=None
                        else:
                            result['warnings'].append(f'{sheet}: unsupported image type {media}');continue
                        file='image-'+digest(data)[:16]+ext
                        if asset_dir is not None: (asset_dir/file).write_bytes(data)
                        result['images'].append({'sheet':sheet,'part':media,'sha256':digest(data),
                            'file':file,'width':width,'height':height,'anchor':position})
            # Plain cell notes use a separate comments relationship, not DrawingML.
            for rel in sr.values():
                if rel['type'].endswith('/comments'):
                    rt=xml(z,rel['part'])
                    for comment in rt.findall('m:commentList/m:comment',NS):
                        if not sheet_scope.cell_visible(comment.get('ref','')):
                            continue
                        text=''.join(t.text or '' for t in comment.findall('.//m:t',NS))
                        result['notes'].append({'sheet':sheet,'part':rel['part'],
                            'cell':comment.get('ref'),'text':text,'target':None,'kind':'cell-comment'})
    return result

def drawing_fingerprint(path: str | Path) -> str:
    """Include graphics, media, notes AND relationships in source-contract binding."""
    with zipfile.ZipFile(path) as z:
        parts=[(name,digest(read_part(z,name))) for name in sorted(z.namelist())
               if name.startswith(('xl/drawings/','xl/media/','xl/comments','xl/threadedComments/'))
               or name.endswith('.rels')]
    return digest(json.dumps(parts,separators=(',',':')).encode())
