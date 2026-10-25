import fs from 'node:fs';
import {build} from 'esbuild';
const load=async file=>{const r=await build({entryPoints:[file],bundle:true,platform:'node',format:'esm',write:false});return import('data:text/javascript;base64,'+Buffer.from(r.outputFiles[0].text).toString('base64'));};
const m=await load('src/egg-model.ts'),scene=await load('src/scene-state.ts'),timeline=await load('src/timeline.ts');
const issues=[],strategies=[];let states=0,phaseSamples=0,poseSamples=0;
for(const [name,points,expectedMax] of [['decreasing',m.CHECKPOINTS,14],['fixed-ten',m.TEN_POINTS,19]]){
 const results=[],traces=new Set();
 for(let F=0;F<=100;F++){
  const r=m.run(F,points);states+=r.states.length;results.push({F,drops:r.world.drops});traces.add(JSON.stringify(r.trials));
  if(r.world.safe!==F||!m.resolved(r.world))issues.push({type:'threshold-not-identified',name,F});
  for(let i=0;i<r.trials.length;i++){
   const before=r.states[i],trial=r.trials[i];
   for(const p of [...Array.from({length:101},(_,n)=>n/100),m.STAGES.land-.00001,m.STAGES.land,m.STAGES.commit-.00001,m.STAGES.commit]){
    const q=m.trialView(before,trial,p);phaseSamples++;
    if(q.world.drops!==before.drops+(p>=m.STAGES.commit?1:0))issues.push({type:'count-before-commit',F,i,p});
    if(q.committed&&!q.landed)issues.push({type:'commit-before-ground',F,i,p});
    for(const id of [1,2]){const pose=m.eggPose(id,q.world,q,{low:0,high:100,amount:0});poseSamples++;if(pose.broke&&id===trial.egg&&!q.landed)issues.push({type:'break-before-ground',F,i,p});if(q.landed&&id===trial.egg&&pose.y<819)issues.push({type:'land-not-on-ground',F,i,p,pose});}
   }
  }
 }
 const maximum=Math.max(...results.map(x=>x.drops));if(maximum!==expectedMax||traces.size!==101)issues.push({type:'strategy-guarantee',name,maximum,traces:traces.size});
 strategies.push({name,thresholds:101,maximum,observableTraces:traces.size,dropCounts:results});
}
const example=m.ACTUAL;if(JSON.stringify(example.trials.map(t=>[t.egg,t.floor,t.broke]))!==JSON.stringify([[1,14,false],[1,27,false],[1,39,true],[2,28,false],[2,29,false],[2,30,false],[2,31,false],[2,32,true]]))issues.push({type:'actual-eight-trace'});
if(example.world.drops!==8||example.world.safe!==31||m.remaining(example.world)!==0)issues.push({type:'actual-final-state'});
fs.mkdirSync('out',{recursive:true});fs.writeFileSync('out/egg-state-audit.json',JSON.stringify({status:issues.length?'failed':'passed',states,phaseSamples,poseSamples,strategies,example,issues},null,2));
let from=0;const sb=JSON.parse(fs.readFileSync('../storyboard.json')),shots=sb.scenes.flatMap(x=>x.shots).map(s=>{const v={...s,from};from+=s.durationInFrames;return v;});
const events=[],errors=[],frames=new Set([0,from-1]);let lastActual=null;
for(const s of shots){
 const c=timeline.cues(s),windows=timeline.actionWindows(s);frames.add(s.from);frames.add(s.from+s.durationInFrames-1);
 for(const x of [c.first,c.second,c.firstEnd,c.secondEnd])for(const d of [-1,0,1])frames.add(s.from+Math.max(0,Math.min(s.durationInFrames-1,Math.round(x)+d)));
 for(let i=0;i<windows.length;i++){
  const w=windows[i],values=Object.values(w);if(values.some((n,i)=>i&&n<=values[i-1])||w.start<0||w.end>=s.durationInFrames)errors.push({type:'invalid-action-window',shot:s.id,i,w});
  for(const [stage,n] of Object.entries(w))for(const d of [-1,0,1])frames.add(s.from+Math.max(0,Math.min(s.durationInFrames-1,Math.round(n)+d)));
  events.push({shot:s.id,index:i,...w,holdAfterCommit:s.durationInFrames-w.commit-1});
 }
 for(let f=0;f<s.durationInFrames;f++){
  const q=scene.sceneState(s,f),w=q.world;
  if(q.view?.committed&&!q.view.landed)errors.push({type:'early-counter',shot:s.id,f});
  if(w.id==='F-31'){
   if(lastActual&&w.drops<lastActual.drops)errors.push({type:'actual-trace-replay',shot:s.id,f});lastActual=w;
   if(!m.remaining(w)&&!m.resolved(w))errors.push({type:'actual-eggs-exhausted-before-answer',shot:s.id,f});
  }
  if(!m.remaining(w)&&!m.resolved(w)&&w.id!=='skip-last-hypothesis')errors.push({type:'unlabeled-failed-hypothesis',shot:s.id,f,world:w.id});
  if(s.visualType==='decreasing-route'&&w.drops!==2)errors.push({type:'plan-executed-as-real-test',shot:s.id,f});
 }
 if(['first-fourteen','next-twenty-seven'].includes(s.visualType))frames.add(s.from+Math.min(s.durationInFrames-1,windows[0].commit+30));
 if(s.visualType==='actual-linear')for(let f=0;f<=50;f++)frames.add(s.from+f);
 if(s.visualType==='fixed-ten-plan')for(let f=c.second;f<=c.second+43;f++)frames.add(s.from+f);
 if(['next-twenty-seven','actual-first-egg','actual-linear'].includes(s.visualType)&&windows.length){const last=windows.at(-1);if(c.secondEnd-last.commit<45)errors.push({type:'insufficient-recap-hold',shot:s.id,last,c});}
 if(s.visualType==='threshold-found'&&windows[0].commit>c.firstEnd)errors.push({type:'final-result-after-first-sentence',shot:s.id});
}
fs.writeFileSync('out/real-timing-events.json',JSON.stringify({status:errors.length?'failed':'passed',frames:from,events,errors,sampleFrames:[...frames].sort((a,b)=>a-b),timingMethod:'Real sentence envelopes plus semantic clause ordering; no internal word alignment or ASR claim.'},null,2));
console.log(JSON.stringify({states,phaseSamples,poseSamples,strategies:strategies.map(({name,maximum})=>({name,maximum})),issues:issues.length,frames:from,events:events.length,errors}));if(issues.length||errors.length)process.exitCode=1;
