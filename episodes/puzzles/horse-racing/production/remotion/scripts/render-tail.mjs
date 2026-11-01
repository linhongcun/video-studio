import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync,spawnSync} from 'node:child_process';

const dir=path.resolve('..'),run=process.argv.includes('--run');
const getArg=(name,fallback)=>{const index=process.argv.indexOf(name);return index<0?fallback:process.argv[index+1];};
const output=path.resolve(getArg('--out','out/self-contained-ending.mp4'));
const old=JSON.parse(fs.readFileSync(path.join(dir,'revisions/self-contained-ending/before/storyboard.json'),'utf8'));
const current=JSON.parse(fs.readFileSync(path.join(dir,'storyboard.json'),'utf8'));
const oldShots=old.scenes.flatMap(scene=>scene.shots),newShots=current.scenes.flatMap(scene=>scene.shots);
const start=oldShots.slice(0,17).reduce((n,shot)=>n+shot.durationInFrames,0),total=current.meta.durationInFrames;
if(newShots[17].from!==start||newShots.slice(0,17).reduce((n,shot)=>n+shot.durationInFrames,0)!==start)throw new Error('Changed first-17-shot boundary');
const cli=path.resolve('node_modules/@remotion/cli/remotion-cli.js');
const args=[cli,'render','src/index.ts','Main',output,`--frames=${start}-${total-1}`,'--codec=h264','--crf=20','--concurrency=2','--browser-executable=/usr/bin/chromium','--bundle-cache=false'];
const manifest={method:'Render only global frames belonging to replacement shots 18 onward.',startFrame:start,endFrame:total-1,frames:total-start,command:[process.execPath,...args],output,audio:'CLI uses the global frame range. Remix ignores this clip audio and muxes the checked full new voice.wav.'};
const out=path.dirname(output);fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'ending-render-plan.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify(manifest,null,2));
if(run){
 execFileSync('python3',[path.join(dir,'freeze.py'),'--verify'],{stdio:'inherit'});
 const result=spawnSync(process.execPath,args,{stdio:'inherit',env:process.env});if(result.status!==0)process.exit(result.status??1);
 execFileSync('python3',[path.join(dir,'freeze.py'),'--verify'],{stdio:'inherit'});
 const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-show_streams','-of','json',output],{encoding:'utf8'})).streams[0];
 if(Number(probe.nb_frames)!==total-start||probe.r_frame_rate!=='30/1')throw new Error('Rendered tail length/rate differs from storyboard');
 fs.writeFileSync(path.join(out,'ending-render-result.json'),JSON.stringify({...manifest,status:'passed',sha256:crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex')},null,2)+'\n');
}
