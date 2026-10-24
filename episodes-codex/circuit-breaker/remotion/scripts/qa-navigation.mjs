// Episode-specific sample/range plan; shared QA owns bundling and rendering.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const repo=path.resolve(dir,'../..');
const helper=path.join(repo,'episodes-codex/_shared/branch-map/qa.mjs');
const out='/workspace/.video-studio-flow-audit/circuit-breaker-remake';
const plan={
 '01':[0,70,177,209,251],
 '02':[0,30,42,48,69,90,135,180],
 '03':[60,232,272],
 '04':[0,28,40,45,65,110,154,155,243,275],
 '05':[0,1,31,42,48,63,70,92,128,148,168],
 '06':[0,1,63,176,216],
 '07':[210,260,281,311],
 '08':[0,30,42,48,78,108,167,194,221,222,272,308],
 '09':[0,26,39,52,58,80,103,118,139,159,160,176,198,220,240,287,305],
 '10':[0,200,349],
};
const data=JSON.parse(fs.readFileSync(path.join(dir,'storyboard.json'),'utf8'));
const frames=[];let offset=0;
for(const shot of data.scenes.flatMap(s=>s.shots)){for(const local of plan[shot.id]??[])frames.push(offset+local);offset+=shot.durationInFrames;}
const stages={
 prototype:{frames:[251,282,807,1051,1085,2233,2309,2925]},
 stills:{frames},
 'closed-to-open':{range:[740,1560],silent:true},
 'probe-failure-recovery':{range:[1910,2610],silent:true},
};
const selected=process.argv.find(a=>a.startsWith('--stage='))?.slice(8);
for(const name of selected?[selected]:['stills','closed-to-open','probe-failure-recovery']){
 const stage=stages[name];if(!stage)throw Error(`Unknown stage ${name}`);
 const args=[helper,`--dir=${dir}`,`--out=${path.join(out,name)}`];
 if(stage.frames)args.push(`--frames=${stage.frames.join(',')}`);
 if(stage.range)args.push(`--range=${stage.range.join(':')}`);
 if(stage.silent)args.push('--no-captions');
 if(process.argv.includes('--audit-only'))args.push('--audit-only');
 console.log(`Circuit-breaker navigation QA: ${name}`);
 const result=spawnSync(process.execPath,args,{cwd:repo,stdio:'inherit',env:{...process.env,TMPDIR:'/workspace/.video-studio-tmp'}});
 if(result.error)throw result.error;
 if(result.status!==0)process.exit(result.status??1);
}
