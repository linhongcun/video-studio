import {PuzzleCanvas} from '../../../../_shared/puzzles-video/Frame';
import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from '../data';
import {C,FONT} from './theme';
import {T,Head,Note} from './primitives';
import {WaterScene} from './WaterScene';
import {STATES,operationAt,ease,BAR,surface,TRANSFER} from '../water-model';
import {operationProgress} from '../timeline';
import {useLayoutAudit} from '../LayoutAudit';
declare const __HAS_VOICE_AUDIO__:boolean;
const cue=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?s.durationInFrames/2:0));
const Reason=({label='思路',lines,color=C.gold}:any)=><g data-reason="true"><T x={300} y={377} size={25} color={C.muted} anchor="middle">{label}</T>{lines.map((line:string,i:number)=><T key={i} x={300} y={438+i*64} size={i===0?37:29} mono={/^[0-9]/.test(line)} color={color} anchor="middle">{line}</T>)}</g>;
const Gap=({alpha=1}:any)=><g opacity={alpha} data-gap="true"><path d="M 827 520 H 852 V 600 H 827" fill="none" stroke={C.gold} strokeWidth={3}/><T x={930} y={571} size={28} color={C.gold} anchor="middle">空位1升</T></g>;
const Scene=({s,f}:{s:Shot;f:number})=>{
 const w=operationProgress(s,f),type=s.visualType;
 if(w){const view=operationAt(w.index,w.progress),titles=['先装满5升，再用小容器接走3升','小容器满了，大容器还剩多少？','先倒空小容器，给两升腾位置','把这两升，全部转进小容器','保留小容器里的2升，再装满大容器','小容器一满，立即停下'];
  return <><Head title={titles[w.index]} sub={`实际操作 ${w.index+1} · ${view.op.title}`}/><WaterScene view={view}/>{w.index===4&&<Gap/>}{w.index===5&&w.progress<TRANSFER.lead&&<Gap/>}<Reason label="停止依据" lines={w.index===0||w.index===4?['装到大容器满',view.complete?'已装满5升':'不靠目测中停']:w.index===2?['倒到小容器空','大容器的2升不动']:w.index===3?['倒到大容器空','小容器还没满']:['倒到小容器满',w.index===5?(view.complete?'接走1升后装满':'原有1升空位'):(view.complete?'小容器接走3升':'小容器容量3升')]}/>{view.complete?<Note color={C.gold}>{view.op.stop}</Note>:<Note>图中水量按操作推算，不是容器刻度</Note>}{w.index===5&&view.complete&&<T x={1630} y={804} size={31} color={C.gold} anchor="middle">目标达成</T>}</>;
 }
 if(type==='hook')return <><Head title="没有刻度，怎样量出4升？" sub="只有3升和5升两个容器，开始都是空的。"/><WaterScene history={false}/><Reason label="目标" lines={['大容器恰好4升','小容器可有水']}/><Note>数字为推算说明，容器本身没有刻度</Note></>;
 if(type==='rules')return <><Head title="只能装满、倒空，或在两壶间互倒" sub="规则示意：两个容器仍为空，尚未开始实际操作。"/><WaterScene history={false}/><defs><marker id="rule-arrow" markerWidth={8} markerHeight={8} refX={7} refY={4} orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill={C.gold}/></marker></defs><g opacity={ease((f-cue(s,0))/18)}><path d="M1530 350 H1240 V570" fill="none" stroke={C.gold} strokeWidth={4} strokeDasharray="9 10" markerEnd="url(#rule-arrow)"/><T x={1438} y={435} size={28} color={C.gold} anchor="middle">装满</T><path d="M570 754 H360" fill="none" stroke={C.gold} strokeWidth={4} strokeDasharray="9 10" markerEnd="url(#rule-arrow)"/><T x={455} y={708} size={28} color={C.gold} anchor="middle">倒空</T></g><g opacity={ease((f-cue(s,1))/18)}><path d="M1115 668 H815" fill="none" stroke={C.gold} strokeWidth={4} strokeDasharray="9 10" markerEnd="url(#rule-arrow)"/><T x={968} y={624} size={30} color={C.gold} anchor="middle">互倒</T></g><Reason label="互倒必须等到" lines={['一边空，或另一边满','不能目测半途停']} color={C.gold}/><Note>水源不限 · 只在明确的空或满边界停止</Note></>;
 if(type==='derive-remainder')return <><Head title="先从容量差，得到一个确定余量" sub="直接装满只有3升或5升，都不是目标4升。"/><WaterScene history={false}/><g opacity={ease((f-cue(s,1))/24)}><Reason label="计划 · 还没有实际装水" lines={['5 − 3 = 2','先准确留下2升']}/></g><Note>当前两壶仍空；先找不需要目测的操作</Note></>;
 if(type==='derive-gap')return <><Head title="有了2升，它能帮我们做什么？" sub="当前真实状态仍为：小容器3升，大容器2升。"/><WaterScene state={STATES[2]} completed={2}/><Reason label="计划 · 不是当前水量" lines={['5 − 1 = 4','如果小壶留2升','就能再接1升']}/><Note>保留这两升，接下来把它转存在小容器</Note></>;
 if(type==='known-gap')return <><Head title="3升容量，已有2升，还空1升" sub="这一升空位，将成为下一次互倒的停止依据。"/><WaterScene state={STATES[4]} completed={4}/><Gap/><Reason label="由当前状态推出" lines={['3 − 2 = 1','小容器一满','就准确接走1升']}/><Note>大容器现在仍为空，下一步先把它装满</Note></>;
 if(type==='closing')return <><Head title="五升容器里，恰好留下4升" sub="小容器有3升也符合题意，目标只看大容器。"/><WaterScene state={STATES[6]} completed={6}/><Reason label="同一套已完成操作" lines={['先留2升','再造1升空位','5 − 1 = 4']}/><T x={1630} y={804} size={31} color={C.gold} anchor="middle">目标达成</T><Note>IT小村 · 原创</Note></>;
 throw Error('Unknown water-jug visualType: '+type);
};
const ShotView=({s,hideSubtitles=false,auditLayout=false}:any)=>{
 const f=useCurrentFrame(),caption=(s.subtitles??[]).find((x:any)=>f>=x.from&&f<(x.to!==undefined?x.to+1:x.from+(x.duration??0)));useLayoutAudit(auditLayout,'main',s.from+f);
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT,color:C.text}}><svg data-audit-scene="true" width={1920} height={1080} viewBox="0 0 1920 1080"><PuzzleCanvas/><Scene s={s} f={f}/><T x={1795} y={82} size={26} color={C.muted} anchor="end">IT小村</T></svg>{!hideSubtitles&&caption&&<div data-subtitle="true" style={{position:'absolute',left:160,right:160,bottom:54,textAlign:'center',fontFamily:FONT,fontSize:31,lineHeight:1.45,color:C.text}}>{caption.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false,auditLayout=false}:{hideSubtitles?:boolean;auditLayout?:boolean})=><AbsoluteFill style={{background:C.bg}}>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles} auditLayout={auditLayout}/></Sequence>)}</AbsoluteFill>;
