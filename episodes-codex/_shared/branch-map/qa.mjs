// Same Remotion renderStill API as episode QA, plus real camera samples and
// cross-shot continuous ranges. Does not render the full movie.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const args=process.argv.slice(2),value=k=>args.find(a=>a.startsWith(k+'='))?.slice(k.length+1);
const dir=path.resolve(value('--dir')??''),out=path.resolve(value('--out')??'/workspace/.video-studio-branch-qa');
if(!value('--dir'))throw Error('Use --dir=episodes-codex/tx-2pc --out=/workspace/... [--frames=...|--range=start:end] [--no-captions]');
const project=path.join(dir,'remotion'),req=createRequire(path.join(project,'package.json'));
const {bundle}=req('@remotion/bundler'),{openBrowser,renderStill,selectComposition,renderMedia}=req('@remotion/renderer'),webpack=req('webpack'),esbuild=req('esbuild');
const shared=path.resolve(import.meta.dirname,'index.ts');
function loadTS(file){const r=esbuild.buildSync({entryPoints:[file],bundle:true,write:false,format:'cjs',platform:'node',logLevel:'error'});const module={exports:{}};new Function('require','module','exports',r.outputFiles[0].text)(req,module,module.exports);return module.exports;}
const {actualNavState,navigationEvents}=loadTS(shared),nav=loadTS(path.join(project,'src/branch-map.ts'));
const getSpec=nav.navigationSpec??nav.branchMapFor??nav.getBranchMapSpec??nav.branchMapSpec??nav.branchMap;
if(!getSpec&&!nav.navigationState)throw Error('src/branch-map.ts must export a spec factory or navigationState(shot,frame)');
const specAt=(s,f)=>typeof getSpec==='function'?getSpec(s,f):getSpec;
const stateAt=(s,f)=>nav.navigationState?nav.navigationState(s,f):actualNavState(specAt(s,f),s.id,f,s.durationInFrames);
const navigationSamples=s=>{
 const primary=nav.navigationFrameSamples?nav.navigationFrameSamples(s):navigationEvents(specAt(s,0),s.id,s.durationInFrames);
 const extra=nav.navigationSampleFrames?.(s)??[];
 return [...primary,...extra.map((v,i)=>Array.isArray(v)?v:[`nav-custom-${i}`,v])];
};
const data=JSON.parse(fs.readFileSync(path.join(dir,'storyboard.json'),'utf8')),shots=data.scenes.flatMap(s=>s.shots);let offset=0;for(const s of shots){s.from=offset;offset+=s.durationInFrames;}
const motion=loadTS(path.join(project,'src/motion.ts'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)]);
const inputs=[path.join(dir,'storyboard.json'),path.join(dir,'covers.json'),shared,...walk(path.join(project,'src'))];
const sourceSha256=Object.fromEntries(inputs.map(f=>[path.relative(dir,f),sha(f)]));
let chosen=[];
if(value('--frames'))chosen=value('--frames').split(',').map(Number);
else if(!value('--range')){
 for(const s of shots){
  chosen.push(s.from,s.from+Math.round(s.durationInFrames*.5),s.from+s.durationInFrames-1);
  const events=[...navigationSamples(s),...(motion.events?.(s)??[])];
  for(const [,frame]of events)for(const d of [-1,0])if(frame+d>=0&&frame+d<s.durationInFrames)chosen.push(s.from+frame+d);
  for(const cue of Object.values(s.cueFrames?.labels??{}))for(const delta of [-1,0,62]){const local=Number(cue)+delta;if(local>=0&&local<s.durationInFrames)chosen.push(s.from+local);}
 }
}
chosen=[...new Set(chosen)].sort((a,b)=>a-b);if(chosen.some(f=>!Number.isInteger(f)||f<0||f>=offset))throw Error('Invalid requested frame');
fs.mkdirSync(out,{recursive:true});
if(args.includes('--audit-only')){
 const states=chosen.map(frame=>{const s=shots.find(s=>frame>=s.from&&frame<s.from+s.durationInFrames),local=frame-s.from,state=stateAt(s,local);return {shot:s.id,frame,local,navShotId:state.shotId,phase:state.phase,progress:state.progress,focusId:state.focusId,camera:state.camera}});
 fs.writeFileSync(path.join(out,'audit.json'),JSON.stringify({scope:'Pure Node navigation state/sample audit; no browser or image rendering',sourceSha256,states},null,2)+'\n');
 console.log(JSON.stringify({auditFrames:states.length,virtualShotIds:[...new Set(states.map(s=>s.navShotId))],file:path.join(out,'audit.json')}));
 process.exit(0);
}
const hideSubtitles=args.includes('--no-captions'),inputProps={hideSubtitles,showSubtitles:!hideSubtitles};
const url=await bundle({entryPoint:path.join(project,'src/index.ts'),publicDir:path.join(project,'public'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(dir,'storyboard.json'),'@covers':path.join(dir,'covers.json')},modules:[path.join(project,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'}),samples=[],clips=[];
try{
 const composition=await selectComposition({serveUrl:url,id:'Main',puppeteerInstance:browser,inputProps,logLevel:'error'});
 for(const frame of chosen){
  const s=shots.find(s=>frame>=s.from&&frame<s.from+s.durationInFrames),local=frame-s.from,state=stateAt(s,local),file=path.join(out,`frame-${String(frame).padStart(5,'0')}.png`);
  await renderStill({composition,serveUrl:url,frame,output:file,puppeteerInstance:browser,inputProps,scale:.5,imageFormat:'png',logLevel:'error'});
  samples.push({shot:s.id,visualType:s.visualType,frame,local,file,nav:{shotId:state.shotId,phase:state.phase,progress:state.progress,focusId:state.focusId,camera:state.camera}});
 }
 if(value('--range')){
  const range=value('--range').split(':').map(Number);if(range.length!==2||range.some(f=>!Number.isInteger(f)||f<0||f>=offset)||range[1]<range[0])throw Error('Invalid range');
  const file=path.join(out,`continuous-${range[0]}-${range[1]}.mp4`);
  await renderMedia({composition,serveUrl:url,codec:'h264',outputLocation:file,frameRange:range,inputProps,scale:.5,crf:22,concurrency:1,puppeteerInstance:browser,logLevel:'error'});
  const relevant=[];for(const s of shots)for(const [name,local]of navigationSamples(s)){const frame=s.from+local;if(frame>=range[0]&&frame<=range[1])relevant.push({name,shot:s.id,frame,clipFrame:frame-range[0]});}
  clips.push({file,frameRange:range,hideSubtitles,voice:false,navEvents:relevant});
 }
 for(const [rel,want]of Object.entries(sourceSha256))if(sha(path.resolve(dir,rel))!==want)throw Error('Preview source changed while bundling/rendering: '+rel);
 fs.writeFileSync(path.join(out,'frames.json'),JSON.stringify({scope:'Real branch camera states and/or cross-shot continuous silent previews; not final movie',sourceSha256,hideSubtitles,voice:false,samples,clips},null,2)+'\n');
 console.log(JSON.stringify({samples:samples.length,clips:clips.map(c=>({file:c.file,frameRange:c.frameRange,navEvents:c.navEvents.length}))}));
}finally{await browser.close({silent:true});}
