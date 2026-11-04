// Numeric precheck of current production trajectories, not a rendered visual audit.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {createRequire} from 'node:module';

const D=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const require=createRequire(path.join(D,'remotion/package.json'));
const localTS=require('typescript');
const ts=typeof localTS.transpileModule==='function'?localTS:createRequire(path.resolve(D,'../../../../site/package.json'))('typescript');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const name='independent-motion-numeric-v1',reportPath=path.join(D,'qa',name+'.json');
if(fs.existsSync(reportPath))throw Error('Preserve the previous numeric precheck.');
const files=['remotion/src/model.ts','remotion/src/Main.tsx','model-data.json'];
const before=Object.fromEntries(files.map(p=>[p,sha(path.join(D,p))]));
const source=fs.readFileSync(path.join(D,'remotion/src/model.ts'),'utf8');
const javascript=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,esModuleInterop:true}}).outputText;
const module={exports:{}};
const context={module,exports:module.exports,require:name=>{if(name!=='../../model-data.json')throw Error('Unexpected production import '+name);return JSON.parse(fs.readFileSync(path.join(D,'model-data.json'),'utf8'));}};
vm.runInNewContext(javascript,context,{filename:'current-production-model.cjs'});
const model=module.exports,ids=Array.from({length:12},(_,i)=>i+1),pairs=[];
for(let i=0;i<12;i++)for(let j=i+1;j<12;j++)pairs.push([ids[i],ids[j]]);
const rows=[];let layoutsChecked=0;
function inspect(label,frames,read){
  let nearest={distance:Infinity},flaggedFrames=0;const runs=[];let current=null;
  for(const frame of frames){
    const layout=read(frame);layoutsChecked++;
    if(Object.keys(layout).length!==12)throw Error('Expected12 physical identities '+label+' '+frame);
    let nearestFrame={distance:Infinity};
    for(const [a,b]of pairs){
      const x=layout[a],y=layout[b];if(![x.x,x.y,y.x,y.y].every(Number.isFinite))throw Error('Nonfinite center');
      const distance=Math.hypot(x.x-y.x,x.y-y.y);
      if(distance<nearestFrame.distance)nearestFrame={distance,pair:[a,b],centers:[x,y]};
    }
    if(nearestFrame.distance<nearest.distance)nearest={frame,...nearestFrame};
    if(nearestFrame.distance<58){flaggedFrames++;if(!current)current={from:frame,to:frame,minimum:nearestFrame};else{current.to=frame;if(nearestFrame.distance<current.minimum.distance)current.minimum=nearestFrame;}}
    else if(current){runs.push(current);current=null;}
  }
  if(current)runs.push(current);
  rows.push({label,samples:frames.length,nearest,flaggedFrames,flaggedRuns:runs,pass:flaggedFrames===0});
}
const integerFrames=Array.from({length:1001},(_,i)=>i);
for(const [from,to]of [['L','LL'],['L','LR'],['L','LB'],['','R'],['R','RR'],['','B'],['B','BB'],['B','BR']])inspect(`safeTransition ${from||'root'} -> ${to}`,integerFrames,f=>model.safeTransition(model.node(from),model.node(to),f,0,1000).layout);
inspect('firstWeighingLayout a=0',Array.from({length:135},(_,i)=>i),f=>model.firstWeighingLayout(f,0));
const sourceUnchanged=files.every(p=>sha(path.join(D,p))===before[p]);
const report={executor:'Codex independent numeric motion precheck',checkedAtUTC:new Date().toISOString(),
  inputSHA256:before,episodeTypescriptVersion:localTS.version,typescriptTranspilerVersion:ts.version,typescriptAPIFallback:typeof localTS.transpileModule!=='function'?'Episode native typescript7 has no transpileModule API; current site typescript5.9.3 used only for read-only QA transpilation.':null,method:'Transpile current production model.ts to CommonJS and evaluate with a custom require that only reads current model-data.json; call each exported production trajectory on an independent integer-frame grid.',
  threshold:{circleDiameterPixels:58,flagWhenCenterDistanceBelowPixels:58},layoutsChecked,centerPairComparisons:layoutsChecked*pairs.length,
  rows,sourceUnchanged,pass:sourceUnchanged&&rows.every(r=>r.pass),
  limitations:['Pure code and floating-point center arithmetic precheck; no actual DOM, PNG, circle stroke, text label, rectangle or overlay inspection.','Integer samples over each specified interval; unsampled fractional times are not asserted collision-free.','This result does not establish causal timing, object visibility, caption correctness or final encoded-media behavior.']};
fs.writeFileSync(path.join(D,'qa',name+'-model-source.txt'),source);
fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({pass:report.pass,layoutsChecked,sourceUnchanged,rows:rows.map(r=>({label:r.label,minimumDistance:r.nearest.distance,frame:r.nearest.frame,pair:r.nearest.pair,flaggedFrames:r.flaggedFrames})),report:reportPath}));
