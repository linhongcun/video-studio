#!/usr/bin/env node
import {writeFileSync} from 'node:fs';
const threshold=(n,strict)=>strict?Math.floor(n/2)+1:Math.ceil(n/2);
const play=function play(ids,coins,strict=false){
  if(!ids.length)return {alive:{},money:{},rounds:[]};
  const me=ids[0],next=play(ids.slice(1),coins,strict),need=threshold(ids.length,strict)-1;
  const costs=ids.slice(1).map(id=>({id,cost:next.alive[id]?next.money[id]+1:0})).sort((a,b)=>a.cost-b.cost||a.id-b.id);
  const chosen=costs.slice(0,need),spend=chosen.reduce((s,r)=>s+r.cost,0);
  if(spend>coins){const out={alive:{...next.alive,[me]:false},money:{...next.money,[me]:0},rounds:next.rounds};out.rounds=[...next.rounds,{ids,coins,threshold:threshold(ids.length,strict),survives:false,proposer:me,costs,reject:next,alive:out.alive,money:out.money}];return out;}
  const money=Object.fromEntries(ids.map(id=>[id,id===me?coins-spend:(chosen.find(c=>c.id===id)?.cost??0)]));
  const alive=Object.fromEntries(ids.map(id=>[id,true]));
  const votes=ids.filter(id=>id===me||!next.alive[id]||money[id]>next.money[id]);
  const round={ids,coins,threshold:threshold(ids.length,strict),survives:true,proposer:me,costs,rejectMoney:next.money,rejectAlive:next.alive,allocation:money,votes};
  return {alive,money,rounds:[...next.rounds,round]};
};
const enumerate=function enumerate(ids,coins,strict,next){
  const arr=Array(ids.length).fill(0),quota=threshold(ids.length,strict);let count=0,best=-1,winning=0,optimalCount=0,examples=[];
  function visit(k,left){
    if(k===ids.length-1){
      arr[k]=left;count++;let yes=1;
      for(let j=1;j<ids.length;j++)if(next.alive[ids[j]]===false||arr[j]>(next.money[ids[j]]??0))yes++;
      if(yes>=quota){winning++;if(arr[0]>best){best=arr[0];optimalCount=1;examples=[arr.slice()];}else if(arr[0]===best){optimalCount++;if(examples.length<8)examples.push(arr.slice());}}return;
    }
    for(let x=0;x<=left;x++){arr[k]=x;visit(k+1,left-x);}
  }
  visit(0,coins);return {checkedAllocations:count,winning,bestProposerCoins:best,optimalCount,optimalExamples:examples};
};
function verifyModel(){
  let smallCases=0;
  for(const strict of [false,true])for(let coins=0;coins<=10;coins++)for(let n=1;n<=5;n++){
    const ids=[1,2,3,4,5].slice(5-n),next=play(ids.slice(1),coins,strict),g=play(ids,coins,strict),e=enumerate(ids,coins,strict,next);
    if(e.bestProposerCoins<0){if(g.alive[ids[0]]!==false)throw Error('survival mismatch');}
    else if(!g.alive[ids[0]]||g.money[ids[0]]!==e.bestProposerCoins)throw Error('optimum mismatch');
    smallCases++;
  }
  const main=[],strictMajorityVariant=[];
  for(let n=1;n<=5;n++){
    const ids=[1,2,3,4,5].slice(5-n);
    for(const strict of [false,true]){
      const p=play(ids,100,strict),e=enumerate(ids,100,strict,play(ids.slice(1),100,strict));
      if((e.bestProposerCoins<0)!==!p.alive[ids[0]])throw Error('survival mismatch');
      if(p.alive[ids[0]]&&p.money[ids[0]]!==e.bestProposerCoins)throw Error('main optimum mismatch');
      (strict?strictMajorityVariant:main).push({n,ids,quota:threshold(n,strict),alive:p.alive,allocation:p.money,...e});
    }
  }
  return {method:'Exact integer enumeration against fixed rational rejection outcomes; ties reject. Small-case continuation ties use lowest actor IDs. No claim of universal equilibrium uniqueness or real human behavior.',smallCases,coins:100,main,strictMajorityVariant};
}
const report=verifyModel();
const index=process.argv.indexOf('--out');
if(index>=0){if(!process.argv[index+1])throw Error('Missing --out path');writeFileSync(process.argv[index+1],JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify(report,null,2));
