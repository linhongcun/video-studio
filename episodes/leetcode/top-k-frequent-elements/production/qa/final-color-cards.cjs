/** Read-only final-media seek, actual fullscreen and color observation. */
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const {chromium}=require('playwright');
const media=path.resolve('video.mp4'),out=path.resolve('qa/final-color-cards');fs.mkdirSync(out,{recursive:true});const size=fs.statSync(media).size;
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const server=http.createServer((req,res)=>{
 if(req.url==='/'){res.setHeader('Content-Type','text/html');return res.end('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#0f172a}video{width:100vw;max-height:100vh}button{position:absolute;right:0;top:0}</style><video controls muted playsinline src="/video.mp4"></video><button id="full" onclick="document.querySelector(\'video\').requestFullscreen()">Fullscreen</button>');}
 if(req.url==='/video.mp4'){const m=/bytes=(\d+)-(\d*)/.exec(req.headers.range??''),start=m?Number(m[1]):0,end=m&&m[2]?Math.min(Number(m[2]),size-1):size-1;res.writeHead(m?206:200,{'Content-Type':'video/mp4','Accept-Ranges':'bytes','Content-Length':end-start+1,...(m?{'Content-Range':`bytes ${start}-${end}/${size}`}:{})});return fs.createReadStream(media,{start,end}).pipe(res)}res.writeHead(404);res.end();
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--autoplay-policy=no-user-gesture-required','--no-sandbox']});const page=await browser.newPage({viewport:{width:1920,height:1080}});const report={media,sha256:hash(media),startedAt:new Date().toISOString(),scope:'Actual standalone Chromium fullscreen paused screenshots and requestVideoFrameCallback after seeks; not semantic listening, not a physical device',samples:[]};
 try{
  await page.goto(`http://127.0.0.1:${server.address().port}`);await page.waitForFunction(()=>document.querySelector('video')?.readyState>=2);await page.click('#full');await page.waitForFunction(()=>document.fullscreenElement===document.querySelector('video'));report.fullscreen=true;
  const targets=[['body',1],['code-middle',5579/30],['code-last',5653/30],['reference-first',5654/30],['reference-middle',5729/30],['reference-last',5803/30]];
  for(const [name,time] of targets){
   const shown=await page.$eval('video',async(v,time)=>{v.pause();const frame=new Promise(resolve=>v.requestVideoFrameCallback((_,m)=>resolve({mediaTime:m.mediaTime,presentedFrames:m.presentedFrames})));const sought=new Promise(resolve=>v.addEventListener('seeked',resolve,{once:true}));v.currentTime=time;await sought;return {...await frame,currentTime:v.currentTime,paused:v.paused,fullscreen:document.fullscreenElement===v,error:v.error?.message??null}},time);
   await page.waitForFunction(()=>document.querySelector('video').readyState>=3);await page.waitForTimeout(650);
   const file=path.join(out,name+'.png');await page.screenshot({path:file});report.samples.push({name,requestedTime:time,file,sha256:hash(file),...shown});
  }
  report.status=report.samples.every(x=>x.fullscreen&&x.paused&&!x.error&&Math.abs(x.mediaTime-x.requestedTime)<.034)?'passed':'failed';
 }catch(error){report.status='failed';report.error=String(error);throw error;}
 finally{report.completedAt=new Date().toISOString();fs.writeFileSync(path.join(out,'actual-browser.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
 console.log(JSON.stringify({status:report.status,fullscreen:report.fullscreen,samples:report.samples.length}));
})().catch(error=>{console.error(error);server.close();process.exitCode=1});
