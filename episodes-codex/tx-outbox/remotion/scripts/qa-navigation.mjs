// Episode ranges only. All bundling, camera sampling and rendering use shared QA.
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const repo=path.resolve(dir,'../..');
const out='/workspace/.video-studio-branch-qa/tx-outbox';
const helper=path.join(repo,'episodes-codex/_shared/branch-map/qa.mjs');
const stages={
 prototype:{frames:[200,940,1661,2435,2485,3110,3159,3498]},
 stills:{},
 'send-crash-resend':{range:[1532,2127],silent:true},
 'consumer-failure-repeat':{range:[2355,2901],silent:true},
 'business-refusal-return':{range:[2931,3303],silent:true},
};
const selected=process.argv.find(a=>a.startsWith('--stage='))?.slice(8);
const names=selected?[selected]:['stills','send-crash-resend','consumer-failure-repeat','business-refusal-return'];
for(const name of names){
 const stage=stages[name];if(!stage)throw Error(`Unknown stage ${name}`);
 const args=[helper,`--dir=${dir}`,`--out=${path.join(out,name)}`];
 if(stage.frames)args.push(`--frames=${stage.frames.join(',')}`);
 if(stage.range)args.push(`--range=${stage.range.join(':')}`);
 if(stage.silent)args.push('--no-captions');
 if(process.argv.includes('--audit-only'))args.push('--audit-only');
 console.log(`Outbox branch QA: ${name}`);
 const result=spawnSync(process.execPath,args,{cwd:repo,stdio:'inherit',env:{...process.env,TMPDIR:'/workspace/.video-studio-tmp'}});
 if(result.error)throw result.error;
 if(result.status!==0)process.exit(result.status??1);
}
