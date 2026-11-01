import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';
import webpack from 'webpack';
import {bundle} from '@remotion/bundler';
import {openBrowser, selectComposition, renderStill, renderMedia} from '@remotion/renderer';

// Local, measured-timing review only. This is not the formal production renderer.
const R=process.cwd(), D=path.resolve(R,'..'), O=path.join(D,'qa-self-finaltiming');
fs.mkdirSync(O,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const inputs=['remotion/src/Main.tsx','model.json','storyboard.json','voice.wav','script.md','article-figure-plan.json'];
const identity=Object.fromEntries(inputs.map(p=>[p,sha(path.join(D,p))]));
if(identity['voice.wav']!=='f4f478dcedbd17e10df0f50ed6ae5f724726f5f5ef580f99db4d4fcca49c2803')throw Error('Voice differs from accepted MQ07 final');
if(sha(path.join(R,'public/audio/voice.wav'))!==identity['voice.wav'])throw Error('Public audio copy differs');
const board=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));
let from=0;const shots=board.scenes.flatMap(s=>s.shots).map(s=>{const q={...s,from};from+=s.durationInFrames;return q;});
if(from!==6058)throw Error('Body does not match final measured voice');
const local=(id,p)=>{const s=shots.find(q=>q.id===id),v=s.voice[0];return s.from+v.localStart+(v.localEnd-v.localStart)*p;};
const second=(id)=>{const s=shots.find(q=>q.id===id);return s.from+s.voice[1].localStart;};
const boundaries=[
 ['sort-start',local('03',.35)],['sort-ranked',local('03',.72)],['sort-ranked-visible',local('03',.72)+12],
 ['quota-calculated',second('04')],['assign-P0',local('05',.35)],['assign-P1',local('05',.85)],
 ['new-arrivals',local('06',.55)],['fetch-request-start',shots[6].from+shots[6].voice[0].localStart+8],
 ['fetch-request-arrived',local('07',.26)],['fetch-response-start',local('07',.34)],['poll-position-advanced',local('07',.72)],
 ['business-completed',shots[7].from+shots[7].voice[0].localEnd-8],
 ...[2,3,4,5].map(k=>['growth-step-'+k,local('09',(k-1)/4)]),
 ...Array.from({length:10},(_,i)=>{const s=shots[10],c=s.voice[1].localStart,e=s.voice[1].localEnd;return ['drain-step-'+(i+1),s.from+c+(e-c)*.068*(i+1)];}),
 ['after-clear-next-input',(()=>{const s=shots[10];return s.from+s.voice[1].localStart+(s.voice[1].localEnd-s.voice[1].localStart)*.86;})()],
];
const samples=[];
for(const s of shots)for(const p of [.12,.50,.88])samples.push({label:'shot-'+s.id+'-'+p,frame:s.from+Math.round(s.durationInFrames*p)});
for(const [label,x]of boundaries){const n=Math.ceil(x);samples.push({label:label+'-before',frame:n-1},{label:label+'-at',frame:n});}
for(const [id,p]of [['05',.18],['05',.60],['07',.14],['07',.50]])samples.push({label:'motion-'+id+'-'+p,frame:Math.round(local(id,p))});
const figures=JSON.parse(fs.readFileSync(path.join(D,'article-figure-plan.json'),'utf8')).figures;
for(const q of figures){if(!Number.isInteger(q.frame)||Math.abs(q.seconds-q.frame/30)>1e-9)throw Error('Noninteger figure');samples.push({label:'figure-'+path.basename(q.file,'.jpg'),frame:q.frame});}
const unique=[...new Set(samples.map(q=>q.frame))].sort((a,b)=>a-b), logs=[];
const serveUrl=await bundle({entryPoint:path.join(R,'src/index.ts'),publicDir:path.join(R,'public'),outDir:path.join(R,'out/self-finaltiming-bundle'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...(c.resolve?.alias??{}),'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(R,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:'true'})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium'});
const onBrowserLog=x=>{if(x.type==='error'||x.text?.includes('COPYFIT'))logs.push(x);};
const report={status:'in-progress',identity,bodyFrames:from,scope:'Actual measured-timing PNG and short continuous previews, not frozen inputs, final MP4, full listening, or independent QA.',boundaries:boundaries.map(([label,n])=>({label,firstIntegerFrame:Math.ceil(n)})),samples,renderedFrames:unique,png:[],clips:[],logs,visualReviewed:false};
const save=()=>fs.writeFileSync(path.join(O,'report.json'),JSON.stringify(report,null,2)+'\n');save();
try{
 const captionProps={showSubtitles:true,hideSubtitles:false},plainProps={showSubtitles:false,hideSubtitles:true};
 const composition=await selectComposition({serveUrl,id:'Main',puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',inputProps:captionProps});
 const plainComposition=await selectComposition({serveUrl,id:'Main',puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',inputProps:plainProps});
 report.captionCompositionProps=composition.props;report.plainCompositionProps=plainComposition.props;
 if(composition.durationInFrames!==6058||plainComposition.props.showSubtitles!==false||plainComposition.props.hideSubtitles!==true)throw Error('Resolved composition/props mismatch');
 if(!process.argv.includes('--clips-only'))for(const frame of unique){
  const file=`frame-${String(frame).padStart(5,'0')}.png`;
  await renderStill({serveUrl,composition,frame,output:path.join(O,file),puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',inputProps:captionProps,onBrowserLog});
  report.png.push({frame,file,sha256:sha(path.join(O,file))});
  if(report.png.length%12===0){save();console.log('PNG '+report.png.length+'/'+unique.length);}
 }
 if(!process.argv.includes('--png-only'))for(const [name,start,end]of [
  ['sort',[920][0],1065],['assign',1875,2085],['fetch-poll',2840,3130],['business-growth',3500,4105],['drain',5155,5510],
 ]){
  const file=`${name}-no-subtitles.mp4`;console.log('Clip '+name+' '+start+'..'+end);
  await renderMedia({serveUrl,composition:plainComposition,codec:'h264',outputLocation:path.join(O,file),puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',inputProps:plainProps,frameRange:[start,end],scale:.5,crf:28,concurrency:2,onBrowserLog});
  report.clips.push({name,file,start,end,frames:end-start+1,sha256:sha(path.join(O,file)),captions:false,resolvedProps:plainComposition.props});save();
 }
 for(const p of inputs)if(sha(path.join(D,p))!==identity[p])throw Error('Input changed during previews: '+p);
 report.status='generated-awaiting-actual-visual-review';save();console.log(JSON.stringify({png:report.png.length,clips:report.clips.length,logs,output:O}));
}catch(error){report.status='preview-execution-failed';report.error=String(error.stack??error);save();throw error;}finally{await browser.close({silent:true});}
