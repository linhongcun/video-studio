/** Actual Chromium playback of a silent motion preview; does not imply human listening. */
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const {chromium}=require('playwright');
const media=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
fs.mkdirSync(out,{recursive:true});
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const stats=fs.statSync(media);
const server=http.createServer((req,res)=>{
 if(req.url==='/'){res.setHeader('Content-Type','text/html');return res.end('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#0f172a}video{width:100vw;max-height:100vh}</style><video controls muted playsinline src="/video.mp4"></video>');}
 if(req.url==='/video.mp4'){
  const match=/bytes=(\d+)-(\d*)/.exec(req.headers.range??'');
  const start=match?Number(match[1]):0,end=match&&match[2]?Math.min(Number(match[2]),stats.size-1):stats.size-1;
  res.writeHead(match?206:200,{'Content-Type':'video/mp4','Accept-Ranges':'bytes','Content-Length':end-start+1,...(match?{'Content-Range':`bytes ${start}-${end}/${stats.size}`}:{})});return fs.createReadStream(media,{start,end}).pipe(res);
 }
 res.writeHead(404);res.end();
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--autoplay-policy=no-user-gesture-required','--no-sandbox']});
 const page=await browser.newPage({viewport:{width:960,height:540}});
 const report={media,sha256:hash(media),startedAt:new Date().toISOString(),method:'Actual muted Chromium video playback with requestVideoFrameCallback observations, screenshots at intervals; no semantic full-speed human watch claim',screenshots:[]};
 try{
  await page.goto(`http://127.0.0.1:${server.address().port}`);
  await page.waitForFunction(()=>document.querySelector('video')?.readyState>=2);
  report.metadata=await page.$eval('video',v=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,readyState:v.readyState}));
  await page.$eval('video',v=>{window.playedFrames=[];const cb=(t,m)=>{window.playedFrames.push({mediaTime:m.mediaTime,presentedFrames:m.presentedFrames});if(!v.ended)v.requestVideoFrameCallback(cb)};v.requestVideoFrameCallback(cb);return v.play()});
  for(let i=0;i<Math.ceil(report.metadata.duration/8);i++){
   await page.waitForTimeout(Math.min(8000,Math.max(100,(report.metadata.duration-i*8)*1000)));
   const position=await page.$eval('video',v=>({currentTime:v.currentTime,paused:v.paused,ended:v.ended,error:v.error?.message??null}));
   const file=path.join(out,`playing-${String(i).padStart(2,'0')}.png`);await page.screenshot({path:file});report.screenshots.push({file,...position});
  }
  report.played=await page.$eval('video',v=>({currentTime:v.currentTime,ended:v.ended,error:v.error?.message??null,dropped:v.getVideoPlaybackQuality?.().droppedVideoFrames??null,total:v.getVideoPlaybackQuality?.().totalVideoFrames??null,frames:window.playedFrames}));
  report.status=report.played.ended&&!report.played.error?'passed':'failed';
 }catch(error){report.status='failed';report.error=String(error);throw error;}
 finally{report.completedAt=new Date().toISOString();fs.writeFileSync(path.join(out,'playback.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
 console.log(JSON.stringify({status:report.status,duration:report.metadata.duration,presentedFrames:report.played.frames.length,screenshots:report.screenshots.length}));
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
