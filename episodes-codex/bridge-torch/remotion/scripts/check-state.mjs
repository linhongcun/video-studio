import fs from 'node:fs';import {transform} from 'esbuild';
const source=fs.readFileSync('src/crossings.ts','utf8'),js=await transform(source,{loader:'ts',format:'esm'}),m=await import('data:text/javascript;base64,'+Buffer.from(js.code).toString('base64'));
const issues=[],frames=[];let samples=0;
for(const [name,moves,expected]of [['greedy',m.GREEDY,19],['optimal',m.OPTIMAL,17]]){
 for(let i=0;i<moves.length;i++){const state=m.after(moves,i),move=moves[i];for(let n=0;n<=300;n++){
  const p=n/300,positions=m.PEOPLE.map(person=>({person,...m.personPosition(person,state,move,p)})),torch=m.torchPosition(state,move,p),arrived=p>=m.stages.arrive,total=state.total+(arrived?move.minutes:0);samples++;
  for(let a=0;a<4;a++)for(let b=a+1;b<4;b++)if(Math.abs(positions[a].x-positions[b].x)<148&&Math.abs(positions[a].y-positions[b].y)<78)issues.push({name,i,p,type:'person-overlap',a:positions[a],b:positions[b]});
  for(const person of positions)if(Math.abs(person.x-torch.x)<98&&Math.abs(person.y-torch.y)<62)issues.push({name,i,p,type:'torch-person-overlap',person,torch});
  if(!arrived&&total!==state.total)issues.push({name,i,p,type:'early-total'});
  if(n%30===0)frames.push({name,index:i,progress:p,positions,torch,total,arrived});
 }}
 const result=m.after(moves,5);if(result.total!==expected||Object.values(result.sides).some(x=>x!==1)||result.torchSide!==1)issues.push({name,type:'final-state',result});
}
const report={samples,status:issues.length?'failed':'passed',issues,frames};fs.mkdirSync('out',{recursive:true});fs.writeFileSync('out/crossing-state-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify({samples,issues:issues.length,status:report.status}));if(issues.length)process.exitCode=1;
if(fs.existsSync('../storyboard.json')){
 const timelineJS=await transform(fs.readFileSync('src/timeline.ts','utf8'),{loader:'ts',format:'esm'}),timeline=await import('data:text/javascript;base64,'+Buffer.from(timelineJS.code).toString('base64'));
 let offset=0;const shots=JSON.parse(fs.readFileSync('../storyboard.json')).scenes.flatMap(x=>x.shots).map(s=>{const shot={...s,from:offset};offset+=s.durationInFrames;return shot;});
 const events=[],errors=[],sampleFrames=new Set([0,offset-1]);
 for(const s of shots){const w=timeline.crossingWindow(s);sampleFrames.add(s.from);sampleFrames.add(s.from+s.durationInFrames-1);for(const cue of s.cueFrames?.sentences??[])sampleFrames.add(s.from+Math.min(s.durationInFrames-1,cue+25));
  if(w){const span=Math.max(w.count*85,w.end-w.start);for(let i=0;i<w.count;i++){const base=w.start+span/w.count*i,unit=span/w.count,arrive=Math.ceil(base+unit*m.stages.arrive),event={shot:s.id,strategy:w.strategy,move:w.index+i+1,prepare:Math.ceil(base),departure:Math.ceil(base+unit*m.stages.handoff),bridgeStart:Math.ceil(base+unit*m.stages.align),bridgeEnd:Math.ceil(base+unit*m.stages.cross),arrive,globalArrive:s.from+arrive,shotTailFrames:s.durationInFrames-arrive-1};events.push(event);if(event.shotTailFrames<12)errors.push({type:'insufficient-final-hold',event});for(const p of [0,.18,.3,.5,.74,.85,.9,1])sampleFrames.add(s.from+Math.max(0,Math.min(s.durationInFrames-1,Math.ceil(base+unit*p))));}
   for(let f=0;f<s.durationInFrames;f++){const current=timeline.crossingAt(s,f),moves=current.strategy==='greedy'?m.GREEDY:m.OPTIMAL,state=m.after(moves,current.index),move=moves[current.index],arrived=current.progress>=m.stages.arrive,total=state.total+(arrived?move.minutes:0);if(!arrived&&total!==state.total)errors.push({shot:s.id,f,type:'early-total'});}
  }
 }
 fs.writeFileSync('out/real-timing-events.json',JSON.stringify({status:errors.length?'failed':'passed',timingSource:'Final storyboard sentence cue envelopes; no internal word timing claim',events,errors,sampleFrames:[...sampleFrames].sort((a,b)=>a-b)},null,2));console.log(JSON.stringify({realEvents:events.length,errors}));if(errors.length)process.exitCode=1;
}
