"""Read-only independent Mermaid gate: fences, portability, parse, SVG rendering.

This module does not import conversion code, rewrite diagrams or award a quality
score. Missing runtime is BLOCKED, not PASS. Supply a local browser bundle or
an offline ESM asset map; no diagram content is sent to external services.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path


def extract_diagrams(markdown: str) -> tuple[list[dict], list[str]]:
    diagrams, errors = [], []
    fence = None
    comment = False
    current = None
    for line_no, original in enumerate(markdown.splitlines(), 1):
        # Comments outside code are not renderable diagram content.
        line = original
        if fence is None:
            if comment:
                if '-->' not in line:
                    continue
                line = line.split('-->', 1)[1]
                comment = False
            while '<!--' in line:
                before, after = line.split('<!--', 1)
                if '-->' in after:
                    line = before + after.split('-->', 1)[1]
                else:
                    line, comment = before, True
                    break
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence is None and match:
            token, info = match.groups()
            fence = (token[0], len(token))
            if info.strip().lower() == 'mermaid':
                current = {'number': len(diagrams) + 1, 'line': line_no, 'lines': []}
            continue
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= fence[1] and not match[2].strip():
                if current is not None:
                    current['source'] = '\n'.join(current.pop('lines'))
                    diagrams.append(current)
                    if not current['source'].strip():
                        errors.append(f"Empty Mermaid block at line {current['line']}.")
                fence, current = None, None
            elif current is not None:
                current['lines'].append(original)
    if current is not None:
        errors.append(f"Unclosed Mermaid fence at line {current['line']}.")
    return diagrams, errors


def portability_issues(source: str) -> list[str]:
    # This is a portability lint, NOT the Mermaid grammar parser.
    labels = re.findall(r'"([^"\n]*(?:\n[^"\n]*)*)"', source)
    problems = []
    for label in labels:
        for line in label.strip('`').splitlines():
            if re.match(r'^\s*(?:\d+[.)]|[-+*])\s+', line):
                problems.append('List-like label: ' + line.strip())
    return problems


BOOTSTRAP = r'''async payload => {
  if (payload.modules) {
    const imports = {};
    for (const [key, source] of Object.entries(payload.modules)) {
      imports['offline-assets/' + key] = URL.createObjectURL(new Blob([source], {type:'text/javascript'}));
    }
    const map = document.createElement('script'); map.type='importmap';
    map.textContent=JSON.stringify({imports}); document.head.appendChild(map);
    const m = await import('offline-assets/' + payload.entry);
    const values = Object.values(m).flatMap(v => [v, v?.default]);
    window.validationMermaid = values.find(v => v?.mermaidAPI && v?.parse && v?.render && v?.initialize)
      || values.find(v => v?.parse && v?.render && v?.initialize);
    const pkg = values.find(v => v?.name === 'mermaid' && typeof v?.version === 'string');
    return pkg?.version || payload.version || 'unidentified';
  }
  window.validationMermaid=window.mermaid;
  return window.mermaid?.version || payload.version || 'unidentified';
}'''

RENDER = r'''async ({source, id, htmlLabels, timeout}) => {
  const m=window.validationMermaid;
  if (!m) throw Error('Mermaid runtime is not loaded.');
  m.initialize({startOnLoad:false, securityLevel:'strict', htmlLabels,
    flowchart:{htmlLabels}, fontFamily:'sans-serif'});
  let timer;
  const operation = (async () => {
    let parsed;
    try { parsed=await m.parse(source, {suppressErrors:false}); }
    catch(error) { return {parsed:false, rendered:false, error:String(error)}; }
    if (!parsed) return {parsed:false, rendered:false, error:'Parser returned false.'};
    try {
      const rendered=await m.render(id, source);
      document.body.innerHTML=rendered.svg;
      await document.fonts.ready;
      const svg=document.querySelector('svg');
      const labelText=[...document.querySelectorAll('svg text, svg .nodeLabel, svg .edgeLabel, svg .cluster-label')]
        .map(x=>x.textContent || '').join('\n');
      const rect=svg?.getBoundingClientRect();
      const artifactError=Boolean(document.querySelector('.error-icon, .error-text')) ||
        /unsupported\s+markdown|syntax\s+error|parse\s+error/i.test(labelText);
      return {parsed:true, rendered:Boolean(svg && rect.width > 0 && rect.height > 0),
        diagram_type:parsed.diagramType || '', artifact_error:artifactError,
        label_text:labelText, svg:rendered.svg,
        error:artifactError ? 'Error text or error graphic in rendered SVG.' : ''};
    } catch(error) { return {parsed:true, rendered:false, error:String(error)}; }
  })();
  try { return await Promise.race([operation, new Promise((_,reject)=>{
    timer=setTimeout(()=>reject(Error('Mermaid render timeout.')), timeout);
  })]); } finally {clearTimeout(timer);}
}'''


def validate(markdown: str | Path, *, asset_map: str | Path | None = None,
             bundle: str | Path | None = None, version: str = 'unidentified',
             browser_path: str | None = None, expected_count: int | None = None,
             artifacts: str | Path | None = None, timeout_ms: int = 15000) -> dict:
    path = Path(markdown)
    raw = path.read_bytes()
    diagrams, errors = extract_diagrams(raw.decode('utf-8-sig'))
    if expected_count is not None and len(diagrams) != expected_count:
        errors.append(f'Expected {expected_count} diagrams; found {len(diagrams)}.')
    results = [dict(number=d['number'], line=d['line'],
                    source_sha256=hashlib.sha256(d['source'].encode()).hexdigest(),
                    portability_issues=portability_issues(d['source']), profiles=[]) for d in diagrams]
    result = {'file': str(path), 'markdown_sha256': hashlib.sha256(raw).hexdigest(),
              'diagram_count': len(diagrams), 'expected_count': expected_count,
              'errors': errors, 'diagrams': results, 'engine_version': version,
              'runtime_status':'NOT_RUN', 'status':'BLOCKED', 'passed':False}
    if not diagrams:
        result.update(status='FAIL' if errors else 'NOT_APPLICABLE',
                      runtime_status='NOT_APPLICABLE', passed=not errors)
        return result
    try:
        from playwright.sync_api import sync_playwright
        if bool(asset_map) == bool(bundle):
            raise ValueError('Supply exactly one local asset_map or browser bundle.')
        payload = json.loads(Path(asset_map).read_text()) if asset_map else {'version': version}
        if asset_map and not all(k in payload for k in ('modules','entry')):
            raise ValueError('Asset map needs modules and entry.')
        runtime_file = Path(asset_map or bundle)
        result['runtime_sha256'] = hashlib.sha256(runtime_file.read_bytes()).hexdigest()
        with sync_playwright() as p:
            opts = {'headless':True}
            if browser_path:
                opts['executable_path'] = browser_path
            with p.chromium.launch(**opts) as browser:
                result['browser_version'] = browser.version
                page = browser.new_page(viewport={'width':1400,'height':900})
                page.route('**/*', lambda route: route.abort())
                page.set_content('<!doctype html><html><head><meta charset="utf-8"></head><body></body></html>')
                if bundle:
                    page.add_script_tag(content=Path(bundle).read_text(encoding='utf-8'))
                result['engine_version'] = page.evaluate(BOOTSTRAP, payload)
                for d, record in zip(diagrams, results):
                    for html_labels in (True, False):
                        profile = 'htmlLabels=' + str(html_labels).lower()
                        try:
                            rendered = page.evaluate(RENDER, {'source':d['source'],
                                'id':f"diagram{d['number']}{int(html_labels)}", 'htmlLabels':html_labels,
                                'timeout': timeout_ms})
                        except Exception as exc:
                            rendered = {'parsed':False,'rendered':False,'error':str(exc)}
                        svg = rendered.pop('svg', None)
                        rendered['profile'] = profile
                        rendered['passed'] = bool(rendered.get('parsed') and rendered.get('rendered')
                                                   and not rendered.get('artifact_error') and not rendered.get('error'))
                        record['profiles'].append(rendered)
                        if artifacts and svg:
                            target=Path(artifacts); target.mkdir(parents=True, exist_ok=True)
                            (target/f"diagram-{d['number']}-{int(html_labels)}.svg").write_text(svg,encoding='utf-8')
                result['runtime_status']='EXECUTED'
    except Exception as exc:
        result['runtime_error'] = str(exc)
        result['runtime_status'] = 'BLOCKED'
    lint_failed = bool(errors or any(r['portability_issues'] for r in results))
    render_failed = any(not p['passed'] for r in results for p in r['profiles'])
    complete = result['runtime_status']=='EXECUTED' and all(len(r['profiles'])==2 for r in results)
    result['status'] = 'FAIL' if lint_failed or render_failed else ('PASS' if complete else 'BLOCKED')
    result['passed'] = result['status']=='PASS'
    result['input_unchanged'] = path.read_bytes()==raw
    if not result['input_unchanged']:
        result.update(status='FAIL',passed=False)
        result['errors'].append('Input file changed while validating.')
    return result


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('markdown',type=Path)
    runtime=parser.add_mutually_exclusive_group()
    runtime.add_argument('--asset-map',type=Path)
    runtime.add_argument('--bundle',type=Path)
    parser.add_argument('--version',default='unidentified')
    parser.add_argument('--browser-path')
    parser.add_argument('--expected-count',type=int)
    parser.add_argument('--artifacts',type=Path)
    parser.add_argument('--json',type=Path,required=True)
    args=parser.parse_args()
    if args.json.resolve()==args.markdown.resolve():
        parser.error('Report path must not overwrite input Markdown.')
    try:
        data=validate(args.markdown,asset_map=args.asset_map,bundle=args.bundle,version=args.version,
                      browser_path=args.browser_path,expected_count=args.expected_count,artifacts=args.artifacts)
    except (OSError,UnicodeError,ValueError) as exc:
        data={'status':'BLOCKED','passed':False,'error':str(exc)}
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(data['status'], args.json)
    return 0 if data['passed'] else (2 if data['status']=='BLOCKED' else 1)

if __name__=='__main__':
    raise SystemExit(main())
