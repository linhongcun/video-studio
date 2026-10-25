import fs from 'node:fs';import {transform} from 'esbuild';
const load=async file=>{const js=await transform(fs.readFileSync(file,'utf8'),{loader:'ts',format:'esm'});return import('data:text/javascript;base64,'+Buffer.from(js.code).toString('base64'));};
const m=await load('src/monty-model.ts'),issues=[],cases=[];let samples=0;
for(const initial of m.DOORS)for(const prize of m.DOORS)for(const host of m.legalHostDoors(initial,prize)){
 const w=m.createWorld(prize,initial,host);if((w.target===prize)!==(initial!==prize))issues.push({type:'switch-equivalence',w});
 for(let n=0;n<=500;n++)for(const stage of ['host','swap','reveal']){const q=n/500,p={pick:1,host:stage==='host'?q:1,swap:stage==='host'?0:stage==='swap'?q:1,reveal:stage==='reveal'?q:0},s=m.stateAt(w,p);samples++;if(s.resultCommitted&&s.selection!==w.target)issues.push({type:'early-result',s});if(stage==='swap'&&q>0&&q<1&&s.selection!==null)issues.push({type:'in-flight-choice',s});}
 for(const layout of [m.HERO,...m.ROWS])for(let n=0;n<=500;n++){const p=n/500,s=m.selectorAt(w,p,layout);if(s.stage==='travel')for(const x of layout.xs){const overlapX=Math.abs(s.x-x)<(s.w+layout.width)/2,overlapY=Math.abs(s.y-layout.y)<(s.h+layout.height)/2;if(overlapX&&overlapY)issues.push({type:'travel-crosses-card',w,p,layout,s});}}
 cases.push(w);
}
const report={status:issues.length?'failed':'passed',stateSamples:samples,hostCases:cases.length,cases,issues};fs.mkdirSync('out',{recursive:true});fs.writeFileSync('out/monty-state-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify({stateSamples:samples,hostCases:cases.length,issues:issues.length}));if(issues.length)process.exitCode=1;
if(fs.existsSync('../storyboard.json')){
 const t=await load('src/timeline.ts');let from=0;const shots=JSON.parse(fs.readFileSync('../storyboard.json')).scenes.flatMap(x=>x.shots).map(s=>{const shot={...s,from};from+=s.durationInFrames;return shot;});const events=[],errors=[],sampleFrames=new Set([0,from-1]);
 for(const s of shots){sampleFrames.add(s.from);sampleFrames.add(s.from+s.durationInFrames-1);for(const c of s.cueFrames?.sentences??[])sampleFrames.add(s.from+Math.min(s.durationInFrames-1,c+24));
  const previous={pick:0,host:0,swap:0,reveal:0},firstEvents={};for(let f=0;f<s.durationInFrames;f++){
   const p=t.gameProgress(s,f);let w=s.visualType==='initially-right'||s.visualType==='right-switch-loses'?m.WORLDS[0]:s.visualType==='initially-wrong-three'?m.WORLDS[2]:m.WORLDS[1];m.stateAt(w,p);
   if(['example-open','example-switch','initially-right','right-switch-loses','initially-wrong-three'].includes(s.visualType))for(const key of ['pick','host','swap','reveal']){if(p[key]>0&&previous[key]===0&&!firstEvents[key+'Start'])firstEvents[key+'Start']=f;if(p[key]===1&&previous[key]<1&&!firstEvents[key+'End'])firstEvents[key+'End']=f;previous[key]=p[key];}
  }
  if(Object.keys(firstEvents).length){const event={shot:s.id,visualType:s.visualType,...firstEvents};events.push(event);for(const f of Object.values(firstEvents))for(const d of [-1,0,1])sampleFrames.add(s.from+Math.max(0,Math.min(s.durationInFrames-1,f+d)));for(let p=.1;p<1;p+=.2)sampleFrames.add(s.from+Math.round(s.durationInFrames*p));
   const firstEnd=Number(s.voice?.[0]?.localEnd??s.cueFrames.sentences[1]-14);if(['example-open','example-switch','right-switch-loses'].includes(s.visualType)){const end=firstEvents.revealEnd??firstEvents.hostEnd;if(end>firstEnd)errors.push({type:'result-after-first-sentence',shot:s.id,end,firstEnd});}
  }
  if(s.visualType==='three-positions')for(const p of [0,.2,.4,.6,.8,1])sampleFrames.add(s.from+Math.min(s.durationInFrames-1,Math.round(p*(s.cueFrames.sentences[1]+8))));
  if(s.visualType==='add-the-chances')for(const p of [.2,.4,.6,.8,1])sampleFrames.add(s.from+Math.round(s.cueFrames.sentences[1]+p*(s.durationInFrames-35-s.cueFrames.sentences[1])));
 }
 fs.writeFileSync('out/real-timing-events.json',JSON.stringify({status:errors.length?'failed':'passed',events,errors,sampleFrames:[...sampleFrames].sort((a,b)=>a-b)},null,2));console.log(JSON.stringify({events,errors}));if(errors.length)process.exitCode=1;
}
