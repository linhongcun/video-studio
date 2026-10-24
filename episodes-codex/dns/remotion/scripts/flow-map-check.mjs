// Pure Node checks: original audio/timeline preservation plus complete action windows.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const dir=path.resolve(import.meta.dirname,'../..'),repo=path.resolve(dir,'../..'),req=createRequire(path.join(dir,'remotion/package.json')),esbuild=req('esbuild');
const out=process.argv[2]??'/workspace/.video-studio-flow-audit/dns-remake/check.json';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex'),baseline='6765032d772c3266f2006de8019f7b69712a134c';
const old=rel=>execFileSync('git',['show',baseline+':'+rel],{cwd:repo,maxBuffer:64*1024*1024});
const load=file=>{const r=esbuild.buildSync({entryPoints:[file],bundle:true,write:false,format:'cjs',platform:'node'});const m={exports:{}};new Function('require','module','exports',r.outputFiles[0].text)(req,m,m.exports);return m.exports;};
const assert=(v,m)=>{if(!v)throw Error(m)};
const {actualNavState}=load(path.join(dir,'../_shared/branch-map/index.ts')),{navigationSpec}=load(path.join(dir,'remotion/src/branch-map.ts')),{mechanismWindows}=load(path.join(dir,'remotion/src/motion.ts'));
const sb=JSON.parse(fs.readFileSync(path.join(dir,'storyboard.json'))),shots=sb.scenes.flatMap(c=>c.shots),original=JSON.parse(old('episodes-codex/dns/storyboard.json')).scenes.flatMap(c=>c.shots);
const timing=s=>({id:s.id,from:s.from,durationInFrames:s.durationInFrames,narration:s.narration,subtitles:s.subtitles,voice:s.voice,cueFrames:s.cueFrames});
assert(JSON.stringify(shots.map(timing))===JSON.stringify(original.map(timing)),'Original narration/captions/timing changed');
assert(shots.length===12&&shots.reduce((n,s)=>n+s.durationInFrames,0)===3200,'12 shots/3200 frames changed');
const retained={};for(const rel of ['script.md','voice.wav','words.json','remotion/public/audio/voice.wav','article.mdx','covers.json']){const bytes=fs.readFileSync(path.join(dir,rel));assert(sha(bytes)===sha(old('episodes-codex/dns/'+rel)),rel+' differs from baseline');retained[rel]=sha(bytes);}
let stableFrames=0;const windows=[];
for(const s of shots){
 for(let f=0;f<s.durationInFrames;f++){
  const spec=navigationSpec(s,f),st=actualNavState(spec,s.id,f,s.durationInFrames);
  assert(Object.values(st.camera).every(Number.isFinite),'Nonfinite camera '+s.id+'/'+f);
  assert(spec.edges.filter(e=>['root','tld','authority'].includes(e.to)).every(e=>e.from==='resolver'),'Client must not directly ask authoritative servers');
  assert(spec.edges.find(e=>e.id==='root-referral').to==='resolver'&&spec.edges.find(e=>e.id==='tld-referral').to==='resolver','Referral must return to resolver');
  if(s.id==='04')assert(st.activeEdges.includes('local-hit')&&!st.activeEdges.includes('ask-resolver'),'Shot04 conditional reuse must not turn into local miss before Shot05');
  if(s.id==='10'&&f>=176)assert(!st.activeEdges.includes('ask-root'),'TTL expiry cannot promise restart at root');
 }
 for(const [name,start,end]of mechanismWindows(s)){
  for(let f=start;f<=end;f++){const st=actualNavState(navigationSpec(s,f),s.id,f,s.durationInFrames);assert(st.phase==='detail'&&st.progress===1&&st.detailOpacity===1,`${s.id} ${name} hidden at ${f}`);stableFrames++;}
  windows.push({shot:s.id,name,start,end,globalStart:s.from+start,globalEnd:s.from+end});
 }
}
const paths=['storyboard.json','remotion/src/Main.tsx','remotion/src/Scenes.tsx','remotion/src/branch-map.ts','remotion/src/motion.ts','remotion/src/Primitives.tsx','remotion/scripts/flow-map-check.mjs','remotion/scripts/motion-qa.mjs','freeze.py','../_shared/branch-map/index.ts','../_shared/branch-map/qa.mjs'];
const sourceSha256=Object.fromEntries(paths.map(p=>[p,sha(fs.readFileSync(path.join(dir,p)))]));
const report={scope:'Pure Node checks only; no final freeze or final encoding; actual image/MP4 viewing recorded separately',baseline,retained,shots:12,frames:3200,wholeTimelineCameraFrames:3200,completeStableActionFrames:stableFrames,windows,sourceSha256,passed:true};
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:true,frames:3200,completeStableActionFrames:stableFrames,out}));
