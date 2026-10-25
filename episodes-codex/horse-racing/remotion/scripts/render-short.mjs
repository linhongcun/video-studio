import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition,openBrowser} from '@remotion/renderer';
import webpack from 'webpack';

const D=path.resolve('..'),repo=path.resolve('../../..'),R=path.join(D,'revisions/short-ending'),out=path.resolve('out/short-ending');
const run=process.argv.includes('--run'),getArg=(name,fallback)=>{const i=process.argv.indexOf(name);return i<0?fallback:process.argv[i+1];};
const load=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const source=load(path.join(R,'source.json')),current=load(path.join(D,'storyboard.json')),before=load(path.join(R,'before-storyboard.json'));
const flatten=s=>s.scenes.flatMap(scene=>scene.shots),oldShots=flatten(before),newShots=flatten(current);
const prefix=source.prefixFrames,hold=source.holdFrames,total=current.meta.durationInFrames;
if(prefix+hold!==total||total!==source.frames||newShots.length!==16)throw new Error('Wrong short-ending timeline');
for(let i=0;i<16;i++)for(const field of ['id','from','visualType','narration','voice','cueFrames'])if(JSON.stringify(oldShots[i][field])!==JSON.stringify(newShots[i][field]))throw new Error(`Changed prefix input ${i+1}/${field}`);
if(oldShots.slice(0,16).reduce((n,s)=>n+s.durationInFrames,0)!==prefix||newShots[15].durationInFrames!==oldShots[15].durationInFrames+hold)throw new Error('Changed legacy-result interval');
fs.mkdirSync(out,{recursive:true});
const oldVideo=path.resolve(getArg('--old-video',path.join(out,'baseline-'+source.version+'.mp4'))),relativeOld='episodes/horse-racing/video.mp4';
if(!fs.existsSync(oldVideo)){
 const media=execFileSync('git',['show',`${source.version}:${relativeOld}`],{cwd:repo,maxBuffer:64*1024*1024});fs.writeFileSync(oldVideo,media);
}
if(sha(oldVideo)!==source.videoSHA256)throw new Error('Old video differs from published baseline');
const probe=p=>loadJSON('ffprobe',['-v','error','-select_streams','v:0','-show_streams','-of','json',p]).streams[0];
function loadJSON(program,args){return JSON.parse(execFileSync(program,args,{encoding:'utf8',maxBuffer:32*1024*1024}));}
const v=probe(oldVideo),packets=loadJSON('ffprobe',['-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,flags','-of','json',oldVideo]).packets;
const first=packets.slice(0,prefix),rest=packets.slice(prefix),maxPrefixPTS=Math.max(...first.map(p=>Math.round(Number(p.pts_time)*30))),minRestPTS=Math.min(...rest.map(p=>Math.round(Number(p.pts_time)*30)));
if(first.length!==prefix||maxPrefixPTS!==prefix-1||minRestPTS!==prefix||!rest[0].flags.includes('K'))throw new Error('Prefix packet dependencies are not closed; stream-copy cut requires review');
const cardPNG=path.join(out,'card.png'),cardVideo=path.join(out,'card.mp4'),prefixVideo=path.join(out,'prefix-video.mp4'),joined=path.join(out,'joined-video.mp4'),voiceVideo=path.resolve('out/voice-short.mp4'),voice=path.join(D,'voice.wav');
const colorArgs=['-pix_fmt',v.pix_fmt];if(v.color_range&&v.color_range!=='unknown')colorArgs.push('-color_range',v.color_range);if(v.color_space&&v.color_space!=='unknown')colorArgs.push('-colorspace',v.color_space);
const copyPrefix=['ffmpeg','-y','-v','error','-i',oldVideo,'-map','0:v:0','-frames:v',String(prefix),'-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',prefixVideo];
const encodeCard=['ffmpeg','-y','-v','error','-loop','1','-framerate','30','-i',cardPNG,'-frames:v',String(hold),'-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2',...colorArgs,'-video_track_timescale','90000','-movflags','+faststart',cardVideo];
const list=path.join(out,'concat.txt');fs.writeFileSync(list,[prefixVideo,cardVideo].map(p=>"file '"+p.replaceAll("'","'\\''")+"'").join('\n')+'\n');
const concat=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',list,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',joined];
const mux=['ffmpeg','-y','-v','error','-i',joined,'-i',voice,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',(total/30).toFixed(10),'-movflags','+faststart',voiceVideo];
const plan={method:'Copy existing first-16 H264 packets, encode only one static 37-frame result card, concatenate without video re-encode, mux checked short voice.wav; shared BGM mix is a following package command.',sourceTag:source.version,oldVideo,oldVideoSHA256:sha(oldVideo),prefixFrames:prefix,holdFrames:hold,totalFrames:total,cardFrame:total-1,packetClosure:{maxPrefixPTSFrame:maxPrefixPTS,minRemainingPTSFrame:minRestPTS,nextPacketIsKey:true},commands:[copyPrefix,encodeCard,concat,mux],outputs:{cardPNG,cardVideo,prefixVideo,joined,voiceVideo}};
fs.writeFileSync(path.join(out,'render-plan.json'),JSON.stringify(plan,null,2)+'\n');console.log(JSON.stringify({prefixFrames:prefix,holdFrames:hold,totalFrames:total,packetClosure:plan.packetClosure,run}));
if(run){
 execFileSync('python3',[path.join(D,'freeze.py'),'--verify'],{stdio:'inherit'});
 const inputProps={hideSubtitles:false,auditLayout:false},serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
 const browserExecutable='/usr/bin/chromium',browser=await openBrowser('chrome',{browserExecutable});
 try{const selected=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps});await renderStill({serveUrl,composition:{...selected,props:{...selected.props,...inputProps}},frame:total-1,output:cardPNG,imageFormat:'png',browserExecutable,puppeteerInstance:browser,inputProps});}finally{await browser.close({silent:true});}
 for(const command of [copyPrefix,encodeCard,concat,mux])execFileSync(command[0],command.slice(1),{stdio:'inherit'});
 const actual=probe(voiceVideo);if(Number(actual.nb_frames)!==total||actual.r_frame_rate!=='30/1')throw new Error('Short output count/rate mismatch');
 const display=loadJSON('ffprobe',['-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',voiceVideo]).frames;
 if(display.length!==total||display.some((frame,i)=>Math.abs(Number(frame.best_effort_timestamp_time)-i/30)>2e-6))throw new Error('Non-continuous short output timestamps');
 const hashes=[];
 for(const [name,movie] of [['old',oldVideo],['new',voiceVideo]]){const file=path.join(out,'prefix-'+name+'.framemd5');execFileSync('ffmpeg',['-y','-v','error','-i',movie,'-map','0:v:0','-frames:v',String(prefix),'-an','-f','framemd5',file],{stdio:'inherit'});hashes.push(fs.readFileSync(file,'utf8').split('\n').filter(s=>s&&!s.startsWith('#')).map(s=>s.split(',').at(-1).trim()));}
 const exact=hashes[0].length===prefix&&hashes[1].length===prefix&&hashes[0].every((h,i)=>h===hashes[1][i]);if(!exact)throw new Error('Stream-copied first-16 decoded pixels changed');
 execFileSync('python3',[path.join(D,'freeze.py'),'--verify'],{stdio:'inherit'});
 fs.writeFileSync(path.join(out,'render-result.json'),JSON.stringify({status:'passed',prefixFrames:prefix,holdFrames:hold,totalFrames:total,first5581DecodedYUVFramesExact:exact,continuousDisplayPTS:true,sha256:sha(voiceVideo),cardPNG_SHA256:sha(cardPNG),planSHA256:sha(path.join(out,'render-plan.json'))},null,2)+'\n');console.log('Short ending passed; every prefix decoded frame is identical.');
}
