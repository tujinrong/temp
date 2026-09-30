// Create a local-only import map. Requires TypeScript for syntax-aware imports.
// No network requests, package downloads or renderer modifications are made.
const fs=require('fs'),path=require('path');
let ts; try { ts=require('typescript'); } catch { const cp=require('child_process'); ts=require(path.join(cp.execFileSync('npm',['root','-g'],{encoding:'utf8'}).trim(),'typescript')); }
const [rootArg,entry,out,version='unidentified',adapter='']=process.argv.slice(2);
if(!rootArg||!entry||!out){console.error('Usage: node prepare_mermaid_assets.cjs ROOT ENTRY OUTPUT VERSION [gradio-preload]');process.exit(2);}
const root=path.resolve(rootArg),modules={};
function visit(rel){
 if(Object.hasOwn(modules,rel))return;
 const file=path.resolve(root,rel);if(path.relative(root,file).startsWith('..'))throw Error('Dependency outside asset root.');
 let code=fs.readFileSync(file,'utf8');modules[rel]='';
 if(adapter==='gradio-preload'&&rel==='index-B5Zu_GVg.js'){
  const start=code.indexOf('Y=function(t,s,n){'),end=code.indexOf('},yt=',start);
  if(start<0||end<0)throw Error('Installed preload adapter does not match.');
  code=code.slice(0,start)+'Y=function(t,s,n){return t()'+code.slice(end);
 }
 const ast=ts.createSourceFile(rel,code,ts.ScriptTarget.Latest,true,ts.ScriptKind.JS),edits=[];
 function target(n){
  if(!n||!ts.isStringLiteral(n)||!n.text.startsWith('.'))return;
  const filePath=path.resolve(path.dirname(file),n.text),dep=path.relative(root,filePath).split(path.sep).join('/');
  if(dep.startsWith('..'))throw Error('Dependency outside root: '+dep);
  if(filePath.endsWith('.css'))modules[dep]='export {};';else visit(dep);
  edits.push([n.getStart(ast),n.getEnd(),JSON.stringify('offline-assets/'+dep)]);
 }
 function scan(n){
  if(ts.isImportDeclaration(n)||ts.isExportDeclaration(n))target(n.moduleSpecifier);
  if(ts.isCallExpression(n)&&n.expression.kind===ts.SyntaxKind.ImportKeyword)target(n.arguments[0]);
  ts.forEachChild(n,scan);
 }
 scan(ast);edits.sort((a,b)=>b[0]-a[0]);for(const [a,b,text]of edits)code=code.slice(0,a)+text+code.slice(b);
 modules[rel]=code;
}
try{visit(entry);fs.mkdirSync(path.dirname(path.resolve(out)),{recursive:true});fs.writeFileSync(out,JSON.stringify({entry,version,modules,adapter}));console.log('Prepared',Object.keys(modules).length,'local modules.');}catch(e){console.error(String(e));process.exit(2);}
