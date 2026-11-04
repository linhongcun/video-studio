// Independent P10 real-timing DOM/frame/continuous-preview audit. No production writes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
const D=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..'),REM=path.join(D,'remotion');
const require=createRequire(path.join(REM,'package.json'));
const {bundle}=require('@remotion/bundler'),{openBrowser,selectComposition,renderStill,renderMedia}=require('@remotion/renderer'),webpack=require('webpack');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(path.join(D,p),'utf8'));
const get=k=>process.argv.slice(2).find(v=>v.startsWith(k+'='))?.slice(k.length+1);
const NAME=get('--name')??'independent-preflight-v1',OUT=path.join(D,'qa/out',NAME),REPORT=path.join(D,'qa',NAME+'.json');
if(fs.existsSync(REPORT))throw Error('Keep earlier evidence; choose a fresh --name');
const sb=read('storyboard.json'),truth=read('model-data.json').mainExample;
if(sb.meta.provisionalTiming||sb.meta.pendingAudio)throw Error('Wait for measured finalized voice');
const shots=sb.scenes.flatMap(s=>s.shots),samples=new Map();
if(shots.length!==14||shots.reduce((n,s)=>n+s.durationInFrames,0)!==read('words.json').durationFrames)throw Error('Need actual fourteen-shot assembly');
const eventIndices={5:[0],6:[1,2],7:[3,4],8:[5,6],9:[7,8],10:[9,10],11:[11]};
const windows=s=>(eventIndices[Number(s.id)]??[]).map((index,i)=>({step:truth.steps[index],v:s.voice[Number(s.id)===5?1:i]}));
function add(s,local,reason){local=Math.max(0,Math.min(s.durationInFrames-1,Math.round(local)));const frame=s.from+local,r=samples.get(frame)??{shot:s.id,local,frame,reasons:[]};r.reasons.push(reason);samples.set(frame,r);}
for(const s of shots){
  add(s,0,'first');add(s,s.durationInFrames/2,'middle');add(s,s.durationInFrames-1,'last');
  for(const v of s.voice){for(const t of[v.localStart,v.localEnd])for(const d of[-1,0,1])add(s,t+d,'sentence-boundary');for(const p of[.25,.5,.75])add(s,v.localStart+(v.localEnd-v.localStart)*p,'sentence-quarter');}
  for(const {step,v}of windows(s))for(const p of[0,.22,.43,.66,.78,1]){const first=Math.ceil(v.localStart+(v.localEnd-v.localStart)*p);for(const d of[-1,0,1])add(s,first+d,step.id+'-causal-boundary-'+p);}
  if(Number(s.id)===4){const[a,b]=s.voice;for(const t of[a.localStart+(a.localEnd-a.localStart)*.52,b.localStart,b.localStart+(b.localEnd-b.localStart)*.42])for(const d of[-1,0,1])add(s,Math.ceil(t)+d,'rule-preview-condition');}
  if(Number(s.id)===11){const v=s.voice[1],gate=Math.ceil(v.localStart+(v.localEnd-v.localStart)*.12);for(const d of[-1,0,1])add(s,gate+d,'final-confirmation-gate');}
  if(Number(s.id)===12){const v=s.voice[0];for(const d of[-1,0,1])add(s,Math.ceil(v.localStart+(v.localEnd-v.localStart)*.35)+d,'generalization-3-to-99');}
}
for(const f of(get('--frames')??'').split(',').filter(Boolean).map(Number)){const s=shots.find(s=>f>=s.from&&f<s.from+s.durationInFrames);if(!s)throw Error('Extra frame outside body '+f);add(s,f-s.from,'extra');}
if(get('--explicit-only')==='true')for(const[f,s]of samples)if(!s.reasons.includes('extra'))samples.delete(f);
const props={hideSubtitles:true,auditLayout:true};
const files=['storyboard.json','script.md','voice.wav','words.json','plan.json','model-data.json','covers.json','qa/independent-preflight.mjs','remotion/package.json','remotion/package-lock.json','remotion/remotion.config.ts','remotion/tsconfig.json','../../../_shared/puzzles-video/Frame.tsx','../../../_shared/puzzles-video/theme.ts','../../../_shared/puzzles-covers/catalog.json',...fs.readdirSync(path.join(REM,'src')).filter(v=>/\.(ts|tsx)$/.test(v)).map(v=>'remotion/src/'+v)];
const hashes=Object.fromEntries(files.map(p=>[p,sha(path.join(D,p))])),backups=[];
fs.mkdirSync(OUT,{recursive:true});
for(const rel of files.filter(p=>p.startsWith('remotion/src/')||p==='model-data.json')){const target=path.join(D,'qa/revisions',NAME,rel+'.txt');fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,fs.readFileSync(path.join(D,rel)),{flag:'wx'});backups.push({source:rel,backup:path.relative(D,target),sha256:sha(target)});}
const report={createdAt:new Date().toISOString(),executor:'Codex independent P10 QA',props,sourceHashes:hashes,sourceBackups:backups,samples:[],clips:[],browserLogs:[],pass:false,visualReviewed:false,limitations:['Actual DOM/full1920 frames and encoded preview sequences; no full realtime viewing claim.','No ASR, full semantic listening, physical-phone or audience-comprehension test.']};
const save=()=>fs.writeFileSync(REPORT,JSON.stringify(report,null,2)+'\n');save();
const url=await bundle({entryPoint:path.join(REM,'src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(REM,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});let current=null,metrics=null;
const newPage=browser.newPage.bind(browser);browser.newPage=async options=>{const p=await newPage(options),close=p.close.bind(p);p.close=async options=>{if(current)metrics=await p.evaluate(()=>{
  const visible=e=>{let opacity=1;for(let n=e;n;n=n.parentElement){const s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden')return false;opacity*=Number(s.opacity);}return opacity>.1;};
  const rect=e=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,w:b.width,h:b.height};};
  const texts=[...document.querySelectorAll('svg text')].filter(visible).map(e=>{const r=document.createRange();r.selectNodeContents(e);const b=r.getBoundingClientRect();return{text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height,personOwner:e.closest('[data-person]')?.getAttribute('data-person')??null};});
  const states=[...document.querySelectorAll('svg [data-main-example],svg [data-person],svg [data-light],svg [data-private-memory-display],svg [data-counter-knowledge],svg [data-generalization],svg [data-preview-only]')].filter(visible).map(e=>({attrs:Object.fromEntries([...e.attributes].filter(a=>a.name.startsWith('data-')).map(a=>[a.name,a.value])),text:e.textContent,bounds:rect(e),circle:e.querySelector('circle')?rect(e.querySelector('circle')):null}));
  const overlaps=[];for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){const a=texts[i],b=texts[j],w=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),h=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);if(w>2&&h>2)overlaps.push({a:a.text,b:b.text,w,h});}
  return{texts,states,overlapCandidates:overlaps,subtitles:document.querySelectorAll('[data-subtitle]').length,provisional:document.querySelector('[data-provisional-timing]')?.getAttribute('data-provisional-timing')};
});return close(options);};return p;};
const simple=state=>({light:state.light?'on':'off',count:state.count,sent:state.sentIds.join(','),declared:state.declared?'true':'false'});
function checkState(sample,metrics){
  const problems=[],q=Number(sample.shot),s=shots.find(s=>s.id===sample.shot),main=metrics.states.filter(s=>s.attrs['data-main-example']),people=metrics.states.filter(s=>s.attrs['data-person']);
  if(metrics.provisional!=='false')problems.push('Actual production must not use provisional timing');
  if(q<5||q>11){if(main.length)problems.push('Main trace appears outside its declared scenario');return problems;}
  if(main.length!==1||people.length!==4||new Set(people.map(p=>p.attrs['data-physical-identity'])).size!==4){problems.push('Need one main trace and four unique physical identities');return problems;}
  const a=main[0].attrs,ws=windows(s),w=ws.length===2&&sample.local>=ws[1].v.localStart?ws[1]:ws[0],beforeStart=sample.local<w.v.localStart;
  const p=Math.max(0,Math.min(1,(sample.local-w.v.localStart)/(w.v.localEnd-w.v.localStart))),before=w.step.before,after=w.step.after;
  let expected={...simple(before)},expectedStage='before',committed=false,actor=null;
  if(!beforeStart){actor=w.step.actorId;expectedStage=p<.43?'observe':p<.66?'switch':p<.78?'remember-or-count':'settled';committed=p>=.78;
    if(p>=.43)expected.light=simple(after).light;
    if(p>=.66){expected.count=after.count;expected.sent=after.sentIds.join(',');}
    if(committed)expected=simple(after);
  }
  for(const[key,value]of Object.entries(expected)){const actual=a['data-'+(key==='light'?'view-light':key==='count'?'view-count':key==='sent'?'view-sent':'declared')];if(actual!==String(value))problems.push({field:key,expected:value,actual});}
  if(a['data-current-event']!==(beforeStart?'none':w.step.id))problems.push('Wrong event identity');
  if(a['data-event-stage']!==expectedStage||a['data-event-committed']!==String(committed))problems.push('Wrong explicit operation/commit boundary');
  const expectedVisits=beforeStart?ws[0].step.visitNumber-1:committed?w.step.visitNumber:w.step.visitNumber-1;
  if(Number(a['data-model-committed-visits'])!==expectedVisits)problems.push('Visit ledger skipped or counted an in-flight action');
  const modifying=['send_once','receive_and_increment'].includes(w.step.action),inFlight=!beforeStart&&modifying&&p>=.43&&p<.78;
  if(a['data-transitioning']!==String(inFlight))problems.push('In-flight microstep must be explicit');
  const active=people.filter(p=>p.attrs['data-current-visitor']==='true');if(active.length!==(actor===null?0:1)||(actor!==null&&Number(active[0]?.attrs['data-person'])!==actor))problems.push('One current physical visitor must match the event');
  for(const person of people){const id=Number(person.attrs['data-person']);if(person.attrs['data-physical-identity']!==String(id)||person.attrs['data-person-role']!==(id===0?'counter':'sender'))problems.push('Physical identity/role changed');const expectedSent=id===0?'not-applicable':expected.sent.split(',').filter(Boolean).map(Number).includes(id)?'true':'false';if(person.attrs['data-sent']!==expectedSent)problems.push('Private sent marker differs from displayed state');}
  const lights=metrics.states.filter(p=>p.attrs['data-light']);if(lights.length!==1||lights[0].attrs['data-light']!==expected.light)problems.push('Exactly one shared binary lamp must match state');
  if(!metrics.states.some(p=>p.attrs['data-private-memory-display']==='teaching-only'&&p.attrs['data-role-information']==='each-person-knows-only-own-memory'))problems.push('Global private markers need the explicit teaching-only boundary');
  const knowledge=metrics.states.filter(p=>p.attrs['data-counter-knowledge']);if(knowledge.length!==1||knowledge[0].attrs['data-counter-knowledge']!=='only-lamp-and-own-count')problems.push('Counter knowledge incorrectly expanded');
  const finalGate=s.voice[1].localStart+(s.voice[1].localEnd-s.voice[1].localStart)*.12,visible=expected.declared==='true'&&(q!==11||sample.local>=finalGate);
  if(a['data-declaration-visible']!==String(visible))problems.push('Confirmation title gate differs from committed evidence');
  if(visible&&(expected.count!==3||expected.light!=='off'||expected.sent!=='1,2,3'||!committed))problems.push('Early or false four-person confirmation');
  if(!beforeStart){const observations=metrics.texts.filter(t=>t.text.startsWith('先见灯'));const expectedObservation='先见灯'+(before.light?'亮':'灭')+'；'+(actor===0?'自己的累计：'+before.count:'自己的记忆：'+(before.sentIds.includes(actor)?'已发':'未发'));if(observations.length!==1||observations[0].text!==expectedObservation)problems.push('Visitor observation must use only the actual pre-visit lamp and own private memory');}
  else{const labels=metrics.texts.map(t=>t.text);if(!labels.includes('本镜下一位：'+ws[0].step.actorId+'号')||!labels.includes('灯'+(before.light?'亮':'灭')+'，当前已接收'+before.count+'份'))problems.push('Pre-voice fallback must retain this shot’s actual actor/lamp/count');}
  const renderedText=metrics.texts.map(t=>t.text).join('\n'),sentIds=expected.sent.split(',').filter(Boolean).map(Number);
  if(q===8&&renderedText.includes('2号已发')&&(!sentIds.includes(2)||inFlight))problems.push('Second-sender completed wording precedes stable successful send');
  if(q===10&&(renderedText.includes('最后一份已送出')||renderedText.includes('3人已发'))&&(!sentIds.includes(3)||inFlight))problems.push('Third-sender completed wording precedes stable successful send');
  return problems;
}
try{
  const composition=await selectComposition({serveUrl:url,id:'PrisonersLight',inputProps:props,puppeteerInstance:browser,logLevel:'error'});composition.props={...composition.props,...props};
  for(const sample of [...samples.values()].sort((a,b)=>a.frame-b.frame)){
    current=sample;metrics=null;const file=path.join(OUT,`s${sample.shot}-f${String(sample.frame).padStart(5,'0')}.png`);
    await renderStill({serveUrl:url,composition,frame:sample.frame,output:file,imageFormat:'png',inputProps:props,puppeteerInstance:browser,logLevel:'error',onBrowserLog:log=>{if(/COPYFIT|error/i.test(log.text))report.browserLogs.push({frame:sample.frame,text:log.text});}});
    if(!metrics)throw Error('Missing actual DOM metrics');
    const violations=metrics.texts.filter(t=>t.w>0&&(t.x<-.5||t.y<-.5||t.x+t.w>1920.5||t.y+t.h>820));
    if(metrics.subtitles!==0)violations.push('Unexpected subtitles in mechanism audit');
    const stateViolations=checkState(sample,metrics);
    report.samples.push({...sample,file:path.relative(D,file),sha256:sha(file),metrics,violations,stateViolations});save();if(report.samples.length%25===0)console.log('samples',report.samples.length);
  }
  current=null;
  for(const spec of(get('--clips')??'').split(',').filter(Boolean)){
    const[from,to]=spec.split(':').map(Number);if(!Number.isInteger(from)||!Number.isInteger(to)||from<0||to<from||to>=composition.durationInFrames)throw Error('Bad clip range '+spec);
    const file=path.join(OUT,`no-subtitles-${from}-${to}.mp4`);
    await renderMedia({serveUrl:url,composition,codec:'h264',outputLocation:file,inputProps:props,frameRange:[from,to],crf:23,concurrency:1,scale:.5,puppeteerInstance:browser,logLevel:'error'});
    const stream=JSON.parse(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames,nb_frames,avg_frame_rate,width,height','-of','json',file],{encoding:'utf8'})).streams[0],actualFrames=Number(stream.nb_read_frames??stream.nb_frames),expectedFrames=to-from+1;
    if(actualFrames!==expectedFrames)throw Error('Actual encoded frame count '+actualFrames+' != '+expectedFrames);execFileSync('ffmpeg',['-v','error','-i',file,'-f','null','-'],{stdio:'pipe'});
    report.clips.push({file:path.relative(D,file),from,to,sha256:sha(file),props,expectedFrames,actualFrames,fullDecodePassed:true,stream});save();console.log('clip',from,to);
  }
  report.sourceUnchanged=Object.entries(hashes).every(([p,h])=>sha(path.join(D,p))===h);
  report.pass=report.sourceUnchanged&&!report.browserLogs.length&&report.samples.every(s=>!s.violations.length&&!s.stateViolations.length);save();
  console.log(JSON.stringify({pass:report.pass,samples:report.samples.length,clips:report.clips.length,failures:report.samples.filter(s=>s.violations.length||s.stateViolations.length).map(s=>({frame:s.frame,violations:s.violations,stateViolations:s.stateViolations})),report:REPORT}));
}finally{await browser.close({silent:true});}
