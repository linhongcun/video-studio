// Frozen D01 flow revision: new head + proven identical old body tail + new Java card.
// The old video's audio is never mapped. The complete current WAV supplies all narration.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const cwd=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const root=path.resolve(cwd,'..');
const planFile=path.join(root,'revisions/flow-ui-java/render-plan.json');
const plan=JSON.parse(fs.readFileSync(planFile,'utf8'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
for(const [file,expected] of Object.entries(plan.inputSha256)){
  const actual=sha(path.join(root,file));
  if(actual!==expected)throw new Error(`Frozen render input changed: ${file}`);
}
const sb=JSON.parse(fs.readFileSync(path.join(root,'storyboard.json'),'utf8'));
const shots=sb.scenes.flatMap(s=>s.shots);let offset=0;
for(const shot of shots){shot.from=offset;offset+=shot.durationInFrames;}
if(offset!==4778||shots.find(s=>s.id==='08')?.from!==2936||sb.meta.javaEndCard?.from!==4628||sb.meta.javaEndCard?.durationInFrames!==150)throw new Error('Render ranges no longer match the final storyboard');

const media=path.join(cwd,'out/flow-render');
const head=path.join(media,'head.mp4'),card=path.join(media,'java.mp4');
const old=path.join(root,plan.reusedVideo.file),voice=path.join(cwd,'public/audio/voice.wav');
const output=path.join(cwd,'out/voice.mp4');
const cli=path.join(cwd,'node_modules/.bin/remotion');
const base=['render','src/index.ts','Main'];
const settings=['--codec=h264','--crf=20','--concurrency=2','--browser-executable=/usr/bin/chromium','--bundle-cache=false','--muted'];
const commands=[
  [cli,[...base,head,...settings,'--frames=0-2935']],
  [cli,[...base,card,...settings,'--frames=4628-4777']],
  ['ffmpeg',['-v','error','-y','-i',head,'-i',old,'-i',card,'-i',voice,
    '-filter_complex','[0:v]setpts=PTS-STARTPTS,format=yuvj420p[h];[1:v]trim=start_frame=2718:end_frame=4410,setpts=PTS-STARTPTS,format=yuvj420p[t];[2:v]setpts=PTS-STARTPTS,format=yuvj420p[j];[h][t][j]concat=n=3:v=1:a=0[v]',
    '-map','[v]','-map','3:a:0','-c:v','libx264','-crf','20','-pix_fmt','yuvj420p','-color_range','pc','-r','30','-frames:v','4778','-c:a','aac','-b:a','192k','-movflags','+faststart',output]],
];
if(process.argv.includes('--plan-only')){
  console.log(JSON.stringify({planFile,planSha256:sha(planFile),inputCount:Object.keys(plan.inputSha256).length,commands},null,2));
  process.exit(0);
}
fs.mkdirSync(media,{recursive:true});
for(const [command,args] of commands){
  const result=spawnSync(command,args,{cwd,stdio:'inherit',env:process.env});
  if(result.error)throw result.error;
  if(result.status!==0)process.exit(result.status??1);
}
const probe=spawnSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,width,height,r_frame_rate','-of','json',output],{encoding:'utf8'});
if(probe.status!==0)throw new Error(probe.stderr);
const stream=JSON.parse(probe.stdout).streams[0];
if(Number(stream.nb_frames)!==4778||stream.width!==1920||stream.height!==1080||stream.r_frame_rate!=='30/1')throw new Error('Final voice video does not match the frozen frame count/geometry');
fs.writeFileSync(path.join(media,'render-provenance.json'),JSON.stringify({planSha256:sha(planFile),strategy:plan.strategy,output:{file:'out/voice.mp4',sha256:sha(output),...stream},audioSource:{file:'public/audio/voice.wav',sha256:sha(voice)},reusedVideoAudioMapped:false},null,2)+'\n');
