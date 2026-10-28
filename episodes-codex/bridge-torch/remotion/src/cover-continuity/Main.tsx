import React from 'react';
import {PuzzleCanvas} from '../../../../_shared/puzzles-video/Frame';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots,VIDEO} from '../data';
import {C,FONT} from './theme';
import {T,Head,Note,sentenceStart} from './primitives';
import {Bridge} from './Bridge';
import {GREEDY,OPTIMAL,after,initial,clamp,ease,stages} from '../crossings';
import {useLayoutAudit} from '../LayoutAudit';
import {CostLedger} from './CostLedger';
import {crossingWindow,crossingAt} from '../timeline';
declare const __HAS_VOICE_AUDIO__:boolean;
const Crossing=({s,f}: {s:Shot;f:number})=>{
 const w=crossingAt(s,f)!,moves=w.strategy==='greedy'?GREEDY:OPTIMAL,index=w.index,p=w.progress,move=moves[index],done=index===4&&p>=stages.arrive;
 return <><Head title={w.strategy==='greedy'?'方案一：最快的人负责接送':'方案二：让两位慢者一起走'} sub={`第 ${index+1} 趟 · ${move.to?'去程':'返回送手电'}`}/><Bridge state={after(moves,index)} move={move} progress={p}/>{done?<Note color={C.gold}>{w.strategy==='greedy'?'2 + 1 + 5 + 1 + 10 = 19 分钟':'2 + 1 + 10 + 2 + 2 = 17 分钟'}</Note>:<Note>每一趟都要带手电；到岸后再累计本趟用时</Note>}</>;
};
const Scene=({s,f}:{s:Shot;f:number})=>{
 const type=s.visualType;
 if(crossingWindow(s))return <Crossing s={s} f={f}/>;
 if(type==='hook')return <><Head title="四个人，怎样更快地过桥？" sub="每个数字，都是这个人单独过桥需要的分钟数。"/><Bridge state={initial()} labels={false}/><T x={960} y={523} size={40} weight={760} color={C.gold} anchor="middle">全员到右岸</T><T x={960} y={600} size={34} color={C.text} anchor="middle">总时间尽量少</T><Note>已知单程用时：1、2、5、10分钟</Note></>;
 if(type==='torch-rules')return <><Head title="一把手电，最多两人同行" sub="去程、返程都必须有人带着手电。"/><Bridge state={initial()} labels={false}/><g opacity={ease((f-sentenceStart(s,0))/20)}><path d="M 650 480 H 1250 M 1230 462 L 1250 480 L 1230 498" stroke={C.gold} strokeWidth={4} fill="none"/><T x={960} y={455} size={29} color={C.gold} anchor="middle">人和手电一起过去</T></g><g opacity={ease((f-sentenceStart(s,1))/20)}><path d="M 1250 630 H 650 M 670 612 L 650 630 L 670 648" stroke={C.gold} strokeWidth={4} fill="none"/><T x={960} y={605} size={29} color={C.gold} anchor="middle">人把手电送回来</T><Note color={C.gold}>手电不能抛，不能隔岸传递</Note></g></>;
 if(type==='shared-time')return <><Head title="同行耗时，由较慢的人决定" sub="规则示意：5分钟和10分钟的人一起走。"/><Bridge state={initial()} labels={false}/><g opacity={ease((f-sentenceStart(s,0))/20)}><path d="M 393 590 H 465 V 700 H 393" fill="none" stroke={C.gold} strokeWidth={4}/><rect x={575} y={448} width={770} height={224} rx={22} fill={C.surface} stroke={C.gold}/><T x={960} y={518} size={34} color={C.muted} anchor="middle">5分钟 和 10分钟 同行</T><T x={960} y={598} size={38} color={C.gold} anchor="middle" alpha={ease((f-sentenceStart(s,0)-35)/20)}>同行耗时＝较慢者10分钟</T></g><Note alpha={ease((f-sentenceStart(s,1))/20)}>速度固定 · 往返相同 · 每一趟都要计时</Note></>;
 if(type==='reset'){
  const start=sentenceStart(s,1),span=Math.max(100,s.durationInFrames-start-18),p=clamp((f-start)/span),old=p<.44,alpha=old?1-ease((p-.08)/.23):ease((p-.48)/.25);
  return <><Head title="19分钟，还可以怎样省？" sub="换一套安排：重新从四人都在左岸开始。"/><Bridge state={old?after(GREEDY,5):initial()} alpha={alpha}/><g opacity={ease(p/.12)*(1-ease((p-.79)/.15))}><rect x={570} y={437} width={780} height={210} rx={24} fill={C.bg} stroke={C.gold} strokeWidth={2}/><T x={960} y={518} size={45} weight={750} anchor="middle" color={C.gold}>回到起点 · 重新安排</T><T x={960} y={586} size={32} anchor="middle">四人和手电归左岸 · 累计归零</T></g><Note>教学状态重置：不是又走了一趟桥</Note></>;
 }
 if(type==='slow-cost'||type==='remaining-cost'){
  const remaining=type==='remaining-cost',p=clamp((f-sentenceStart(s,1)+20)/Math.max(60,s.durationInFrames-sentenceStart(s,1)-30));
  return <><Head title={remaining?'其余各趟：4分钟变成7分钟':'送两位慢者：15分钟变成10分钟'} sub="回看比较 · 每格是一趟，箭头是方向；不执行新行程。"/><Bridge state={after(OPTIMAL,5)} labels={false}/><CostLedger focus={remaining?'remaining':'slow'} reveal={p}/><T x={960} y={837} size={43} color={C.gold} weight={760} anchor="middle">{remaining?'其余各趟，多花 3 分钟':'两位慢者同行，省下 5 分钟'}</T><Note>{remaining?'新的账目也包括最后一趟：两位快者再去右岸':'同时走完，10分钟的去程也把5分钟的人送到了'}</Note></>;
 }
 if(type==='net-saving'){
  const p=ease((f-sentenceStart(s,1))/36);
  return <><Head title="省5分钟，多3分钟，净省2分钟" sub="同一口径比较：慢者所在去程 + 其余全部往返。"/><Bridge state={after(OPTIMAL,5)} labels={false}/><rect x={530} y={405} width={860} height={305} rx={22} fill={C.bg} stroke={C.edge}/><T x={960} y={474} size={34} color={C.gold} anchor="middle">送慢者：15 → 10，省 5</T><T x={960} y={538} size={34} color={C.muted} anchor="middle">其余各趟：4 → 7，多 3</T><T x={960} y={654} size={63} mono weight={760} color={C.gold} anchor="middle" alpha={p}>5 − 3 = 2</T><T x={960} y={837} size={43} color={C.gold} anchor="middle" alpha={p}>19 分钟 → 17 分钟</T><Note>比较的是所有行程的总和</Note></>;
 }
 if(type==='closing')return <><Head title="慢者同过，快者分担返回" sub="四人和手电都在右岸，这套安排共用17分钟。"/><Bridge state={after(OPTIMAL,5)} labels={false}/><rect x={530} y={444} width={860} height={232} rx={22} fill={C.bg} stroke={C.edge}/><T x={960} y={518} size={32} color={C.muted} anchor="middle">把每一趟往返，一起计入总时间</T><T x={960} y={620} size={51} mono weight={760} color={C.gold} anchor="middle">2 + 1 + 10 + 2 + 2 = 17</T><T x={960} y={837} size={43} color={C.gold} anchor="middle">四人全部到达 · 17 分钟</T><Note>IT小村 · 原创</Note></>;
 throw Error('Unknown bridge visualType: '+type);
};
const ShotView=({s,hideSubtitles=false,auditLayout=false}:any)=>{
 const f=useCurrentFrame(),caption=(s.subtitles??[]).find((x:any)=>f>=x.from&&f<(x.to!==undefined?x.to+1:x.from+(x.duration??0)));
 useLayoutAudit(auditLayout,'main',s.from+f);
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT,color:C.text}}><svg data-audit-scene="true" width={1920} height={1080} viewBox="0 0 1920 1080"><PuzzleCanvas/><Scene s={s} f={f}/><T x={1795} y={82} size={26} color={C.muted} anchor="end">IT小村</T></svg>{!hideSubtitles&&caption&&<div data-subtitle="true" style={{position:'absolute',left:160,right:160,bottom:54,textAlign:'center',fontFamily:FONT,fontSize:31,lineHeight:1.45,color:C.text}}>{caption.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false,auditLayout=false}:{hideSubtitles?:boolean;auditLayout?:boolean})=><AbsoluteFill style={{background:C.bg}}>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles} auditLayout={auditLayout}/></Sequence>)}</AbsoluteFill>;
