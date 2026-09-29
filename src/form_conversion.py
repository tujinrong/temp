"""Convert a source-reviewed screenshot layout and DrawingML notes to semantic HTML.

The reviewed layout supplies placement ONLY. IDs/types/limits come from source
cells and notes come from source drawings. No requirement text is copied from
an evaluator contract. Unknown screenshot layouts require review, not guessing.
"""
from __future__ import annotations
import html
import json
from pathlib import Path
from .drawing_content import extract, drawing_fingerprint
from .semantic_repair import convert as semantic_convert
from .xlsx_spec import load_xlsx
from .xlsx_to_markdown import find_field_table, metadata_pairs

CSS='''body{font:16px "Noto Sans CJK JP","Yu Gothic",sans-serif;color:#20344a;background:#edf2f7;margin:24px}
.spec-form{max-width:680px;margin:0 auto;background:white;padding:28px;border:1px solid #c5d3e0;border-radius:10px}
.spec-form h2{margin-top:0}.spec-row{display:grid;grid-template-columns:150px minmax(0,1fr);align-items:center;gap:12px;margin:18px 0}
.spec-row label{font-weight:600}.spec-row input{box-sizing:border-box;width:100%;min-width:0;height:40px;padding:8px;font:inherit;border:1px solid #9baebd;border-radius:4px}
.spec-actions{display:flex;justify-content:flex-end;gap:12px;margin:20px 0}.spec-actions button{padding:10px 22px;font:inherit;border:1px solid #1f4e78;background:white;border-radius:4px;color:#20344a}
.spec-actions button:first-child{background:#1f4e78;color:white}.spec-message{padding:12px;border-left:4px solid #b9472b;background:#fff4f1;font-size:14px}
.spec-comments{border-top:1px solid #d7e0e7;margin-top:24px;padding-top:8px}.spec-comment{font-size:14px;line-height:1.7;margin:12px 0}.spec-source{font-size:13px;line-height:1.7;color:#52687a;max-width:740px;margin:24px auto}
@media(max-width:520px){body{margin:8px}.spec-form{padding:16px}.spec-row{grid-template-columns:1fr}.spec-actions{justify-content:flex-start}}'''

def esc(value): return html.escape(str(value),quote=True)

def comment(note):
    # Do not permit source text to close its containing HTML comment.
    text=f"callout {note['id']} | target={note['target']}: {note['note']}"
    return '<!-- '+esc(text).replace('--','&#45;&#45;')+' -->'

def context(xlsx, layout_path, asset_dir):
    layout=json.loads(Path(layout_path).read_text(encoding='utf-8'))
    inv=extract(xlsx,asset_dir)
    if layout.get('review_status')!='source-reviewed':
        raise ValueError('Screenshot layout needs independent source review.')
    matched=[i for i in inv['images'] if i['sheet']==layout['source_sheet'] and i['sha256']==layout['image_sha256']]
    if len(matched)!=1: raise ValueError('Reviewed image missing or changed; review it again.')
    info=load_xlsx(xlsx)
    sheet=next((s for s in info.sheets if s.name==layout['field_sheet']),None)
    if sheet is None: raise ValueError('Field-definition sheet is missing.')
    _,headers,data=find_field_table(sheet,sheet.header_rows+1)
    if not headers or '項目ID' not in headers: raise ValueError('No supported field-definition table.')
    fields={}
    for row in data:
        record=dict(zip(headers,row)); fid=record.get('項目ID','')
        if not fid or fid in fields: raise ValueError('Missing/duplicate control ID.')
        fields[fid]=record
    ids=[v for row in layout['rows'] for v in row]
    if len(ids)!=len(set(ids)) or set(ids)!=set(fields)|set(layout.get('message_ids',[])):
        raise ValueError('Reviewed layout must map each control exactly once.')
    notes=[c for c in inv['callouts'] if c['sheet']==layout['source_sheet']]
    if any(not c['target'] or c['target'] not in ids for c in notes):
        raise ValueError('Callout target unresolved; do not infer from proximity.')
    if len({c['id'] for c in notes})!=len(notes): raise ValueError('Duplicate callout IDs.')
    return layout,inv,matched[0],fields,notes,info

def render_fragment(layout,fields,notes,visible=True):
    links={key:' '.join('comment-'+n['id'] for n in notes if n['target']==key)
           for row in layout['rows'] for key in row}
    lines=['<section class="spec-form">',f'<h2 id="form-title">{esc(layout["title"])}</h2>',
           f'<form id="{esc(layout["form_id"])}" aria-labelledby="form-title" data-reference-only="true">']
    for row in layout['rows']:
        buttons=all(fields.get(fid,{}).get('種別')=='button' for fid in row)
        if buttons: lines.append('<div class="spec-actions">')
        for fid in row:
            for note in notes:
                if note['target']==fid: lines.append(comment(note))
            aid=f' aria-describedby="{esc(links[fid])}"' if visible and links[fid] else ''
            if fid in layout.get('message_ids',[]):
                lines.append(f'<div id="{esc(fid)}" class="spec-message" role="status"{aid}>エラーメッセージ表示領域（位置の参考・実際の文言はメッセージ一覧を参照）</div>')
                continue
            field=fields[fid]; typ=field['種別']; label=field['項目名']
            if typ=='button':
                lines.append(f'<button id="{esc(fid)}" type="button"{aid}>{esc(label)}</button>')
            elif typ in {'text','password','email','number'}:
                required=' required' if field.get('必須')=='○' else ''
                limit=field.get('桁数',''); limit=f' maxlength="{esc(limit)}"' if limit.isdigit() else ''
                default=field.get('初期値',''); default=f' value="{esc(default)}"' if default else ''
                lines += ['<div class="spec-row">',f'<label for="{esc(fid)}">{esc(label)}</label>',
                    f'<input id="{esc(fid)}" name="{esc(fid)}" type="{esc(typ)}"{required}{limit}{default}{aid}>','</div>']
            else: raise ValueError(f'Unsupported control type: {typ}; review required.')
        if buttons: lines.append('</div>')
    lines.append('</form>')
    if visible:
        lines += ['<aside class="spec-comments" aria-label="吹き出しコメント">','<h3>吹き出しコメント</h3>']
        for note in notes:
            lines.append(f'<p class="spec-comment" id="comment-{esc(note["id"])}" data-target="{esc(note["target"])}"><strong>{esc(note["id"])} · {esc(note["target"])}</strong> — {esc(note["note"])}</p>')
        lines.append('</aside>')
    lines.append('</section>')
    return '\n'.join(lines)

def convert(xlsx, layout_path, output: Path, *, visible=True) -> dict:
    """Write Markdown, a standalone HTML form, PNG assets, and a provenance map."""
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    layout,inv,image,fields,notes,info=context(xlsx,layout_path,output.parent/'assets')
    fragment=render_fragment(layout,fields,notes,visible)
    name=output.stem+'.form.html'; asset='assets/'+image['file']
    source_note=('配置はレビュー済みハードコピー、項目ID・型・必須・桁数は画面項目定義、コメントは原本の吹き出し図形に基づく。'
                 '画像だけから制約を推測したものではない。これは静的な配置参考であり、認証・クリア処理を実行しない。'
                 '空欄から初期値が空文字であるとは断定しない。色・寸法は実装要件ではない。')
    standalone='<!doctype html>\n<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    standalone+=f'<title>{esc(layout["title"])} — HTML配置参考</title><style>{CSS}</style></head><body>\n{fragment}\n<p class="spec-source">{source_note}</p></body></html>\n'
    output.with_name(name).write_text(standalone,encoding='utf-8')
    sheet=next(s for s in info.sheets if s.name==layout['source_sheet'])
    meta=' / '.join(f'{k}: {v}' for k,v in metadata_pairs(sheet,max(4,sheet.header_rows)))
    extra='## 画面ハードコピー（HTML再構成）\n\n'+meta+'\n\n'+source_note+'\n\n'
    extra+=f'[HTMLフォームを開く]({name}) · [原本のハードコピー画像]({asset})\n\n'+fragment+'\n\n'
    base=semantic_convert(xlsx,4,excluded_sheets={layout['source_sheet']})
    if len(inv['images'])==1 and not inv['warnings'] and not any(s.charts for s in info.sheets):
        base=base.replace('- 画像・グラフ内の情報はこのテキスト変換で検証していない。原本の目視レビューが必要。\n','')
    output.write_text(base.replace('## 出典対応',extra+'## 出典対応',1),encoding='utf-8')
    record={'image':image,'source_drawing_sha256':drawing_fingerprint(xlsx),'layout_review':str(layout_path),
            'method':'reviewed visual layout + source field definitions + DrawingML text; no OCR',
            'callouts':notes,'unhandled':inv['warnings'],'html':name}
    output.with_suffix('.source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return record
