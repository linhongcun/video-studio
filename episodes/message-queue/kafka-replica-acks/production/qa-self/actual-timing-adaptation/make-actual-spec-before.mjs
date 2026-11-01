// Run only after root finalAccepted. Derives author sampling from the exact Main
// timing function; independent QA must independently assess the semantics.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {createRequire} from 'node:module';
const D=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..'),req=createRequire(path.join(D,'remotion/package.json')),ts=req('typescript');
const main=fs.readFileSync(path.join(D,'remotion/src/Main.tsx'),'utf8'),begin=main.indexOf('export function sceneTiming('),end=main.indexOf('export function stateAt(');if(begin<0||end<begin)throw Error('Timing function not found');
const code=ts.transpileModule('type Shot=any;type Step=any;type Flight=any;'+main.slice(begin,end).replace('export function','function'),{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText;
const timing=new Function(code+';return sceneTiming;')();
const board=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));if(board.meta?.timingSource?.kind==='PREVOICE_ESTIMATED_NOT_ACTUAL_VOICE')throw Error('Actual board required');
let from=0;const shots=board.scenes.flatMap(s=>s.shots).map(s=>{const v={...s,id:String(s.id).padStart(2,'0'),from};from+=s.durationInFrames;return v;});
const all=[],points=new Map();const add=(frame,label)=>{if(frame>=0&&frame<from){const old=points.get(frame);points.set(frame,{frame,label:old?old.label+' / '+label:label});}};
for(const s of shots){const t=timing(s);all.push({shot:s.id,from:s.from,durationInFrames:s.durationInFrames,steps:t.steps.map(q=>({...q,firstIntegerLocal:Math.ceil(q.at),firstIntegerFrame:s.from+Math.ceil(q.at)})),flights:t.flights.map(q=>({...q,firstIntegerFrame:s.from+Math.ceil(q.start),endFirstIntegerFrame:s.from+Math.ceil(q.end)}))});
 add(s.from+Math.floor(s.durationInFrames*.5),'s'+s.id+'-middle');add(s.from+s.durationInFrames-20,'s'+s.id+'-stable-end');
 for(const q of t.steps){const n=s.from+Math.ceil(q.at);add(n,'s'+s.id+'-'+q.id);if(['07','08','09','12'].includes(s.id))add(n-1,'before-'+q.id);}
 for(const q of t.flights)add(s.from+Math.floor((q.start+q.end)/2),'s'+s.id+'-'+q.kind+'-flight-middle');
}
for(const n of [0,60,150,450,from-1])add(n,'global-review-point');
const samples=[...points.values()].sort((a,b)=>a.frame-b.frame);const Q=path.join(D,'qa-self/actual-frames');fs.mkdirSync(Q,{recursive:true});if(fs.existsSync(path.join(Q,'spec.json')))throw Error('Preserve earlier actual spec');
fs.writeFileSync(path.join(Q,'spec.json'),JSON.stringify({kind:'author-actual-voice-frame-spec',samples},null,2)+'\n');
const timingReport={kind:'author-source-derived-thresholds-not-independent-semantics',MainSHA256:crypto.createHash('sha256').update(main).digest('hex'),boardSHA256:crypto.createHash('sha256').update(fs.readFileSync(path.join(D,'storyboard.json'))).digest('hex'),totalBodyFrames:from,shots:all};fs.writeFileSync(path.join(D,'qa-self/actual-state-timing.json'),JSON.stringify(timingReport,null,2)+'\n');
const getShot=id=>shots.find(s=>s.id===id),getStep=(id,state)=>all.find(s=>s.shot===id).steps.find(q=>q.id===state).firstIntegerFrame;
const clips=[{name:'second-copy-then-report-no-subtitles',from:getStep('07','all3-b2-copy')-15,to:getStep('08','all3-b2-reported')+40},{name:'third-copy-hw-and-response-no-subtitles',from:getStep('09','all3-b3-fetch0')-8,to:getStep('09','all3-success')+40},{name:'stable-two-and-one-reset-no-subtitles',from:getShot('11').from,to:getStep('12','all1-rejected')+40}];
if(clips.some(q=>q.to-q.from>1200))throw Error('Narrow oversized clip window');const CQ=path.join(D,'qa-self/actual-clips');fs.mkdirSync(CQ,{recursive:true});if(fs.existsSync(path.join(CQ,'spec.json')))throw Error('Preserve earlier clip spec');fs.writeFileSync(path.join(CQ,'spec.json'),JSON.stringify({clips},null,2)+'\n');
console.log(JSON.stringify({bodyFrames:from,samples:samples.length,clips}));
