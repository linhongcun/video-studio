import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const Q=path.dirname(fileURLToPath(import.meta.url)),D=path.dirname(Q),R=path.join(D,'remotion');
const req=createRequire(path.join(R,'package.json'));
const {openBrowser,selectComposition,renderMedia}=req('@remotion/renderer');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const prior=JSON.parse(fs.readFileSync(path.join(Q,'cross-corrected.json'))),sourceHashes=prior.sourceHashes;
if(!Object.entries(sourceHashes).every(([n,h])=>sha(path.join(D,n))===h))throw Error('source changed');
const props={showSubtitles:false,hideSubtitles:true},url=path.join(Q,'cross-corrected-bundle');
const out=path.join(Q,'cross-clips');fs.mkdirSync(out,{recursive:true});
const report={sourceHashes,props,clips:[],console:[],scope:'Independent bounded current-source muted no-subtitle preview clips; not full-body viewing, listening or formal encode.'};
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
try{
 const comp=await selectComposition({serveUrl:url,id:'Main',inputProps:props,puppeteerInstance:browser,logLevel:'error'});comp.props={...comp.props,...props};report.resolvedProps=comp.props;
 for(const spec of [{name:'allocation',start:2250,end:2380},{name:'install-fetch',start:3020,end:3260},{name:'independent-read',start:4080,end:4230}]){
  const file=path.join(out,spec.name+'.mp4');
  await renderMedia({serveUrl:url,composition:comp,inputProps:props,frameRange:[spec.start,spec.end],outputLocation:file,codec:'h264',crf:20,muted:true,concurrency:2,puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{if(/COPYFIT|error/i.test(l.text))report.console.push(l.text)}});
  report.clips.push({...spec,file:path.relative(D,file),sha256:sha(file)});
 }
 report.sourceUnchanged=Object.entries(sourceHashes).every(([n,h])=>sha(path.join(D,n))===h);
 fs.writeFileSync(path.join(Q,'cross-clips.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({clips:report.clips,sourceUnchanged:report.sourceUnchanged,console:report.console}));
}finally{await browser.close({silent:true})}
