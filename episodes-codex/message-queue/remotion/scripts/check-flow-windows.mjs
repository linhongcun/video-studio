// Check complete action intervals against the actual shared camera, without rendering.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {actualNavState} from '../../../_shared/branch-map/index.ts';
import {navigationSpec} from '../src/branch-map.ts';
import {actionWindows} from '../src/motion.ts';
const dir=path.resolve(import.meta.dirname,'../..'),file=process.argv[2];
const sb=JSON.parse(fs.readFileSync(path.join(dir,'storyboard.json'),'utf8'));
const rows=[];let checkedFrames=0;
for(const s of sb.scenes.flatMap(c=>c.shots))for(const [name,w]of Object.entries(actionWindows(s))){
 assert(w.start>=0&&w.end<s.durationInFrames&&w.start<=w.end,name);
 const samples=[];
 for(let f=w.start;f<=w.end;f++){
  const state=actualNavState(navigationSpec(s,f),s.id,f,s.durationInFrames);
  assert(state.progress===1&&state.phase==='detail',s.id+' '+name+' hidden during camera at '+f);
  checkedFrames++;
  if([w.start,Math.round((w.start+w.end)/2),w.end].includes(f))samples.push({frame:f,phase:state.phase,progress:state.progress});
 }
 rows.push({shot:s.id,name,...w,samples});
}
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const inputs=['storyboard.json','remotion/src/Main.tsx','remotion/src/motion.ts','remotion/src/branch-map.ts','../_shared/branch-map/index.ts'];
const report={scope:'All frames of declared complete action intervals against actual shared camera; not visual or final-movie review.',design:'flow-map-20261024/#199',passed:true,checkedFrames,windows:rows,sourceSha256:Object.fromEntries(inputs.map(f=>[f,hash(path.resolve(dir,f))]))};
if(file){fs.mkdirSync(path.dirname(path.resolve(file)),{recursive:true});fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n')}
console.log(JSON.stringify({passed:true,windows:rows.length,checkedFrames}));
