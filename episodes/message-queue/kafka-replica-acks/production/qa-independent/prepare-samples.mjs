import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';import crypto from 'node:crypto';
const D=path.resolve('episodes/message-queue/kafka-replica-acks/production'),Q=path.join(D,'qa-independent');
const read=p=>JSON.parse(fs.readFileSync(path.join(D,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(D,p))).digest('hex');
const handoff=read('qa-self/actual-handoff.json');for(const [p,h]of Object.entries(handoff.sourceHashes))if(sha(p)!==h)throw Error('Changed handed-off input '+p);
const board=read('storyboard.json'),shots=board.scenes.flatMap(x=>x.shots),raw=fs.readFileSync(path.join(D,'remotion/src/Main.tsx'),'utf8');
let fn=raw.slice(raw.indexOf('export function sceneTiming'),raw.indexOf('export function stateAt'));
fn=fn.replace('export function sceneTiming(s:Shot)','function sceneTiming(s)').replaceAll(':number','').replaceAll(':string','').replaceAll(':Step[]','').replaceAll(':Flight[]','').replaceAll(':Step','');
const context={};vm.runInNewContext(fn+';this.compute=sceneTiming;',context);const byframe=new Map(),computed=[];
const author=read('qa-self/actual-state-timing.json');
function expected(frame){const s=shots.find(x=>frame>=x.from&&frame<x.from+x.durationInFrames);if(!s)return null;const t=context.compute(s);return [...t.steps].reverse().find(x=>frame-s.from>=x.at)?.id??null;}
function add(frame,note){if(frame<0||frame>=board.meta.durationInFrames)return;const old=byframe.get(frame)??{frame,expectedState:expected(frame),notes:[]};old.notes.push(note);byframe.set(frame,old);}
for(const s of shots){const t=context.compute(s),a=author.shots.find(x=>x.shot===s.id);if(!a)throw Error('No author threshold '+s.id);
 if(t.steps.length!==a.steps.length)throw Error('Stepcount');t.steps.forEach((x,i)=>{if(x.id!==a.steps[i].id||Math.abs(x.at-a.steps[i].at)>1e-7||s.from+Math.ceil(x.at)!==a.steps[i].firstIntegerFrame)throw Error('Mismatch author time '+s.id);});
 computed.push({shot:s.id,from:s.from,durationInFrames:s.durationInFrames,...t});
 for(const step of t.steps){const n=s.from+Math.ceil(step.at);for(const delta of [-1,0,1])add(n+delta,`${s.id} ${step.id} boundary${delta}`);}
 for(const f of t.flights)for(const p of [.2,.5,.8])add(s.from+Math.round(f.start+(f.end-f.start)*p),`${s.id} ${f.kind} flight${p}`);
 add(s.from+s.durationInFrames-1,`${s.id} final visible`);
}
for(const frame of [0,60,150,450])add(frame,'opening/title safe');
for(const f of read('article-figure-plan.json').figures)add(f.frame,'article figure '+f.file);
const samples=[...byframe.values()].sort((a,b)=>a.frame-b.frame);
for(const name of ['dynamic-v1-spec.json','independent-timing.json'])if(fs.existsSync(path.join(Q,name)))throw Error('Preserve prior '+name);
fs.writeFileSync(path.join(Q,'dynamic-v1-spec.json'),JSON.stringify({kind:'independent-sampling-exact-actual-source-timing',sourceHashes:handoff.sourceHashes,samples},null,2)+'\n');
fs.writeFileSync(path.join(Q,'independent-timing.json'),JSON.stringify({source:'Actual sceneTiming pure function extracted without JSX/import/module execution; voice localStart/localEnd from actual board. Author thresholds only compared after own computation.',authorThresholdComparisonPassed:true,shots:computed},null,2)+'\n');
console.log(JSON.stringify({samples:samples.length,states:[...new Set(samples.map(s=>s.expectedState).filter(Boolean))].length,frames:samples.map(x=>x.frame)}));
