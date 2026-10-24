import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const dir=path.resolve(import.meta.dirname,'../..'),root=path.resolve(dir,'../..');
const req=createRequire(path.join(dir,'remotion/package.json')),esbuild=req('esbuild');
function load(file){const build=esbuild.buildSync({entryPoints:[file],bundle:true,write:false,format:'cjs',platform:'node',logLevel:'error'}),m={exports:{}};new Function('require','module','exports',build.outputFiles[0].text)(req,m,m.exports);return m.exports;}
const {actualNavState}=load(path.resolve(dir,'../_shared/branch-map/index.ts'));
const {navigationSpec}=load(path.join(dir,'remotion/src/branch-map.ts'));
const {mechanismWindows}=load(path.join(dir,'remotion/src/motion.ts'));
const sb=JSON.parse(fs.readFileSync(path.join(dir,'storyboard.json'))),shots=sb.scenes.flatMap(c=>c.shots);
const before=JSON.parse(execFileSync('git',['show','6765032:episodes-codex/https/storyboard.json'],{cwd:root,encoding:'utf8'}));
const preserved=s=>({id:s.id,from:s.from,durationInFrames:s.durationInFrames,narration:s.narration,subtitles:s.subtitles,cueFrames:s.cueFrames});
if(JSON.stringify(shots.map(preserved))!==JSON.stringify(before.scenes.flatMap(c=>c.shots).map(preserved)))throw Error('Narration/subtitles/cues/shot timing changed');
const index=JSON.parse(fs.readFileSync(path.join(dir,'revisions/pre-flow-map.json')));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const rel of ['voice.wav','script.md','words.json','captions.srt'])if(sha(path.join(dir,rel))!==index.inputs[rel].sha256)throw Error('Preserved media/input changed: '+rel);
const windows=[];
for(const s of shots)for(const [name,start,end]of mechanismWindows(s)){
 for(let f=start;f<=end;f++){
  const state=actualNavState(navigationSpec(s,f),s.id,f,s.durationInFrames);
  if(state.progress!==1||state.phase!=='detail')throw Error(`${s.id}/${name} frame ${f} intersects ${state.phase}`);
 }
 windows.push({shot:s.id,name,start,end,stableDetailThroughout:true});
}
const spec=navigationSpec(shots.find(s=>s.id==='12'));
for(const failure of ['blocked','rejected'])if(spec.edges.some(e=>e.from===failure))throw Error('Failure incorrectly continues: '+failure);
const sourceFiles=['storyboard.json','remotion/src/Main.tsx','remotion/src/Scenes.tsx','remotion/src/branch-map.ts','remotion/src/motion.ts','../_shared/branch-map/index.ts'];
const result={scope:'Structural and complete action-window navigation audit; no visual/full-listening assertion',frames:shots.reduce((n,s)=>n+s.durationInFrames,0),shots:shots.length,preservedNarrationSubtitlesCueFramesAndTiming:true,preservedFiles:['voice.wav','script.md','words.json','captions.srt'],terminalFailureNodes:['blocked','rejected'],windows,sourceSha256:Object.fromEntries(sourceFiles.map(p=>[p,sha(path.join(dir,p))]))};
const out=process.argv.find(a=>a.startsWith('--out='))?.slice(6);if(out)fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({shots:result.shots,frames:result.frames,completeWindows:windows.length,allStable:true}));
