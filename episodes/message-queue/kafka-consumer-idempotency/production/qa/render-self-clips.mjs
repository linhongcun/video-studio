// Source-owner bounded clips, using the exact fresh bundle/identity of self frames.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const Q=path.dirname(fileURLToPath(import.meta.url)),D=path.dirname(Q),R=path.join(D,'remotion');
const req=createRequire(path.join(R,'package.json'));
const {openBrowser,selectComposition,renderMedia}=req('@remotion/renderer');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const prior=JSON.parse(fs.readFileSync(path.join(Q,'self-final.json'))),sourceHashes=prior.sourceHashes;
if(!Object.entries(sourceHashes).every(([n,h])=>sha(path.join(D,n))===h))throw Error('Source changed since actual self frames');
const timing=JSON.parse(fs.readFileSync(path.join(Q,'state-timing.json'))).shots;
const clips=[];
const edge=(shot,id)=>timing.find(s=>s.shot===shot).stateThresholds.find(s=>s.state===id).local;
function add(name,shot,start,end){const s=timing.find(s=>s.shot===shot);clips.push({name,shot,start:s.from+Math.max(0,Math.floor(start)),end:s.from+Math.min(s.duration-1,Math.ceil(end))});}
add('07-new-row-gate','07',edge('07','index-check-protected')-10,edge('07','t1-award-pending')+20);
add('08-flashback-to-current-wait','08',edge('08','t1-insert-returned')-12,edge('08','t2-waits-for-t1')+25);
add('09-commit-then-recheck','09',edge('09','t1-committed')-12,edge('09','t2-rechecked-existing')+20);
add('12-rollback-takeover','12',edge('12','t2-insert-after-abort')-12,edge('12','t2-committed-after-abort')+25);
const props={showSubtitles:false,hideSubtitles:true},url=path.join(Q,'self-final-bundle'),out=path.join(Q,'self-clips');fs.mkdirSync(out,{recursive:true});
const report={kind:'source-owner-bounded-current-media-self-review',sourceHashes,props,clips:[],console:[],visualReviewed:false};
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
try{
 const comp=await selectComposition({serveUrl:url,id:'Main',inputProps:props,puppeteerInstance:browser,logLevel:'error'});comp.props={...comp.props,...props};report.resolvedProps=comp.props;
 for(const spec of clips){
  const file=path.join(out,spec.name+'.mp4');
  await renderMedia({serveUrl:url,composition:comp,inputProps:props,frameRange:[spec.start,spec.end],outputLocation:file,codec:'h264',crf:20,muted:true,concurrency:2,puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{if(/COPYFIT|error/i.test(l.text))report.console.push(l.text)}});
  report.clips.push({...spec,file:path.relative(D,file),sha256:sha(file)});
  fs.writeFileSync(path.join(Q,'self-clips.json'),JSON.stringify(report,null,2)+'\n');
 }
 report.sourceUnchanged=Object.entries(sourceHashes).every(([n,h])=>sha(path.join(D,n))===h);
 report.scope='New real muted no-subtitle bounded preview clips. No full-body viewing/listening or formal render claim.';
 fs.writeFileSync(path.join(Q,'self-clips.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({clips:report.clips,sourceUnchanged:report.sourceUnchanged,console:report.console}));
}finally{await browser.close({silent:true})}
