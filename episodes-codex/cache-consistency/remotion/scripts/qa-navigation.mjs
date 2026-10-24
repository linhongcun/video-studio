// Episode-specific frame/range selection; shared QA owns rendering and camera sampling.
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),repo=path.resolve(dir,'../..');
const out='/workspace/.video-studio-flow-audit/cache-consistency-remake';
const local={
 '01':[0,120,165],'02':[42,250],'03':[24,42,67,92],'04':[36,136],
 '05':[0,1,63,174,229],'06':[0,55,170,267],'07':[15,30,55,90,134,175,223],
 '08':[24,42,135,267],'09':[0,24,42,74,195,273],'10':[18,63,210,269],
 '11':[0,30,147,181,182,247],'12':[30,48,108,151,192,288,300,380],
};
const from={'01':0,'02':255,'03':599,'04':834,'05':1060,'06':1343,'07':1638,'08':1883,'09':2169,'10':2511,'11':2808,'12':3083};
const stages={
 prototype:{frames:[200,623,1813,2169,2269,2993,3423]},
 states:{frames:Object.entries(local).flatMap(([id,frames])=>frames.map(f=>from[id]+f))},
 'write-miss-hit':{range:[1503,2043],silent:true},
 'wrong-interleaving':{range:[2169,2741],silent:true},
 'delete-failure-expiry':{range:[2965,3293],silent:true},
};
const selected=process.argv.find(a=>a.startsWith('--stage='))?.slice(8);
for(const name of selected?[selected]:['states','write-miss-hit','wrong-interleaving','delete-failure-expiry']){
 const stage=stages[name];if(!stage)throw Error(`Unknown QA stage ${name}`);
 const args=[path.join(repo,'episodes-codex/_shared/branch-map/qa.mjs'),`--dir=${dir}`,`--out=${path.join(out,name)}`];
 if(stage.frames)args.push(`--frames=${stage.frames.join(',')}`);
 if(stage.range)args.push(`--range=${stage.range.join(':')}`);
 if(stage.silent)args.push('--no-captions');
 if(process.argv.includes('--audit-only'))args.push('--audit-only');
 console.log(`Cache-consistency ${name}`);
 const result=spawnSync(process.execPath,args,{cwd:repo,stdio:'inherit',env:{...process.env,TMPDIR:'/workspace/.video-studio-tmp'}});
 if(result.error)throw result.error;if(result.status!==0)process.exit(result.status??1);
}
