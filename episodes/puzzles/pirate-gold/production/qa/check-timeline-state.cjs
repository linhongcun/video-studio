/* Independent rule assertions against the actual production timeline exports.
 * It reads source and storyboard; all output is confined to qa/.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const D=path.resolve(__dirname,'..'),REM=path.join(D,'remotion');
const {createRequire}=require('node:module');
const remRequire=createRequire(path.join(REM,'package.json'));
const esbuild=remRequire('esbuild');
const file=path.join(REM,'src/model.ts'),source=fs.readFileSync(file,'utf8');
const result=esbuild.transformSync(source,{loader:'ts',format:'cjs',target:'es2020'});
const sourceRequire=createRequire(file),moduleObject={exports:{}};
new Function('require','module','exports',result.code)(sourceRequire,moduleObject,moduleObject.exports);
const actual=moduleObject.exports;
const board=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));
const shots=board.scenes.flatMap(s=>s.shots);
const oracle={2:{players:[4,5],quota:1,yes:[4],money:{4:100,5:0}},3:{players:[3,4,5],quota:2,yes:[3,5],money:{3:99,4:0,5:1}},4:{players:[2,3,4,5],quota:2,yes:[2,4],money:{2:99,3:0,4:1,5:0}},5:{players:[1,2,3,4,5],quota:3,yes:[1,3,5],money:{1:98,2:0,3:1,4:0,5:1}}};
const checked=[];
for(const [shotId,n] of [[5,2],[7,3],[9,4],[13,5]]){
 const s=shots.find(s=>Number(s.id)===shotId),r=oracle[n];
 if(!s)throw Error('Missing real shot '+shotId);
 let acceptedFrames=0;
 for(const id of r.players){if(actual.isYes(n,id)!==r.yes.includes(id))throw Error(`Wrong ballot for ${n} people / pirate ${id}`);}
 for(let f=0;f<s.durationInFrames;f++){
  const state=actual.election(s,n,f),arrived=r.players.filter(id=>f>=state.arrivals[String(id)]),yes=arrived.filter(id=>r.yes.includes(id)).length;
  if(state.yes!==yes||state.quota!==r.quota)throw Error(`Wrong actual count at ${shotId}/${f}`);
  if(state.passed&&yes<r.quota)throw Error(`PREMATURE PASS at ${shotId}/${f}`);
  if(state.passed&&arrived.length!==r.players.length)throw Error(`PASS before all shown ballots at ${shotId}/${f}`);
  if(state.passed&&f<s.voice[1].localStart)throw Error(`PASS before second-sentence election at ${shotId}/${f}`);
  if(new Set(Object.values(state.arrivals)).size!==r.players.length)throw Error('Non-sequential ballot arrivals');
  if(state.passed)acceptedFrames++;
 }
 const tail=actual.election(s,n,s.durationInFrames-1);
 if(!tail.passed||tail.yes!==r.yes.length)throw Error('No correct final approval');
 if(acceptedFrames<63)throw Error('Approved state has fewer than 63 readable frames');
 checked.push({shot:shotId,people:n,totalFrames:s.durationInFrames,quota:r.quota,yesVotes:r.yes,actualPassAt:tail.passAt,approvedFrames:acceptedFrames,checkedEveryFrame:true});
}
const report={executor:'Independent motion QA',passed:true,scope:'Actual timeline functions tested at every integer frame; visual DOM/media reviewed separately.',sourceSHA256:crypto.createHash('sha256').update(source).digest('hex'),shots:checked};
fs.writeFileSync(path.join(D,'qa/timeline-rule-check.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:true,shots:checked}));
