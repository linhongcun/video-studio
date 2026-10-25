import fs from 'node:fs';import {transform} from 'esbuild';
const load=async file=>{const js=await transform(fs.readFileSync(file,'utf8'),{loader:'ts',format:'esm'});return import('data:text/javascript;base64,'+Buffer.from(js.code).toString('base64'));};
const m=await load('src/water-model.ts'),expected=[[0,0],[0,5],[3,2],[0,2],[2,0],[2,5],[3,4]],issues=[],samples=[];let count=0;
if(JSON.stringify(m.STATES)!==JSON.stringify(expected))issues.push({type:'route-endpoints',actual:m.STATES,expected});
for(let index=0;index<6;index++)for(let n=0;n<=500;n++){
 const state=m.operationAt(index,n/500);count++;const total=state.volume[0]+state.volume[1],want=state.start[0]+state.start[1]+state.externalIn-state.externalOut;
 if(Math.abs(total-want)>1e-9)issues.push({type:'water-balance',index,progress:n/500,total,want});
 for(let i=0;i<2;i++)if(state.volume[i]<-1e-9||state.volume[i]>m.CAPACITIES[i]+1e-9)issues.push({type:'capacity',index,n,i});
 if(state.complete&&state.op.kind==='pour'&&state.volume[state.op.from]>1e-9&&Math.abs(state.volume[state.op.to]-m.CAPACITIES[state.op.to])>1e-9)issues.push({type:'illegal-stop',index,n});
 if(n%50===0)samples.push(state);
}
fs.mkdirSync('out',{recursive:true});fs.writeFileSync('out/water-state-audit.json',JSON.stringify({status:issues.length?'failed':'passed',samples:count,issues,states:m.STATES,phaseSamples:samples},null,2));console.log(JSON.stringify({samples:count,issues:issues.length}));if(issues.length)process.exitCode=1;
if(fs.existsSync('../storyboard.json')){
 const t=await load('src/timeline.ts');let from=0;const shots=JSON.parse(fs.readFileSync('../storyboard.json')).scenes.flatMap(x=>x.shots).map(s=>{const shot={...s,from};from+=s.durationInFrames;return shot;});const events=[],errors=[],frames=new Set([0,from-1]);
 for(const s of shots){frames.add(s.from);frames.add(s.from+s.durationInFrames-1);for(const c of s.cueFrames?.sentences??[])frames.add(s.from+Math.min(s.durationInFrames-1,c+24));const w=t.operationWindow(s);if(w){const complete=Math.ceil(w.start+w.span*m.TRANSFER.complete),event={shot:s.id,index:w.index,start:w.start,lead:Math.ceil(w.start+w.span*m.TRANSFER.lead),flow:Math.ceil(w.start+w.span*m.TRANSFER.transfer),complete,globalComplete:s.from+complete,tail:s.durationInFrames-complete-1};events.push(event);if(event.tail<18)errors.push({type:'insufficient-complete-hold',event});for(const p of [0,.12,.2,.25,.4,.6,.8,.82,1])frames.add(s.from+Math.max(0,Math.min(s.durationInFrames-1,Math.ceil(w.start+w.span*p))));}}
 fs.writeFileSync('out/real-timing-events.json',JSON.stringify({status:errors.length?'failed':'passed',events,errors,sampleFrames:[...frames].sort((a,b)=>a-b)},null,2));console.log(JSON.stringify({events:events.length,errors}));if(errors.length)process.exitCode=1;
}
