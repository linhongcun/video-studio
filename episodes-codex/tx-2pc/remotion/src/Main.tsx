import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots} from './data';
import {C,FONT} from './theme';
import {at,eventAt} from './motion';
import {Title,Reset,Note,Coordinator,Participant,Token,Cross,Txt,Chip,Line,ease,lerp} from './components';
declare const __HAS_VOICE_AUDIO__:boolean;
const phase=(s:Shot,f:number,i:number,a=.08,b=.68)=>ease(f,at(s,i,a),at(s,i,b)-at(s,i,a));
const hit=(s:Shot,f:number,n:string)=>f>=eventAt(s,n);
const cue=(s:Shot,n:string)=>Number(s.cueFrames?.labels?.[n]??1);
const pair=(order:any,stock:any)=><><Participant kind="order" {...order}/><Participant kind="stock" {...stock}/></>;
const outward=(left:number,right:number,text:string,color=C.gold,alpha=1)=><>
 <Token x1={760} y1={414} x2={480} y2={414} p={left} text={text} color={color} alpha={alpha}/>
 <Token x1={1160} y1={414} x2={1440} y2={414} p={right} text={text} color={color} alpha={alpha}/>
</>;
const inward=(left:number,right:number,text:string,color=C.gold)=><>
 <Token x1={480} y1={414} x2={760} y2={414} p={left} text={text} color={color} alpha={left>0&&left<1?1:0}/>
 <Token x1={1440} y1={414} x2={1160} y2={414} p={right} text={text} color={color} alpha={right>0&&right<1?1:0}/>
</>;
const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const t=s.visualType;
 if(t==='hook'){
  const failed=hit(s,f,'stock-operation-fails');
  return <><Title>一个保存，另一个失败？</Title>
   {pair({mode:'committed'},{mode:failed?'rejected':'empty'})}
   <Line x1={790} y1={585} x2={1130} y2={585} p={phase(s,f,0,.05,.48)} color={C.red} dashed/>
   {failed&&<Cross x={960} y={585}/>}
   <Chip x={960} y={315} width={550} color={C.gold} alpha={phase(s,f,1)}>能否先约好，再共同确认？</Chip>
   <Note alpha={phase(s,f,0,.3,.75)}>同一笔订单，不能只看一边保存成功</Note></>;
 }
 if(t==='mechanism')return <>
  <Title color={C.teal} alpha={f>=cue(s,'两阶段提交')?1:0}>两阶段提交</Title>
  <Reset>成功分支 · 从无本单记录、库存 4 开始</Reset>
  <Coordinator state="尚无共同决定"/>{pair({},{})}
  <Line x1={480} y1={404} x2={1440} y2={404} p={phase(s,f,1)} color={C.blue} dashed/>
  <Note alpha={phase(s,f,1)}>订单 8124 · 商品 7042 · 本次购买 1 件</Note>
 </>;
 if(t==='prepare-request'){
  const a=hit(s,f,'order-work-ready'),b=hit(s,f,'stock-work-ready');
  return <><Title color={C.gold} alpha={f>=cue(s,'准备')?1:0}>准备：先做好修改，不先宣布成功</Title>
   <Coordinator state="先询问两边：能否完成？"/>
   {pair({mode:a?'working':'empty'},{mode:b?'working':'empty'})}
   {outward(phase(s,f,0,.02,.58),phase(s,f,1,.02,.24),'先做好修改')}
   <Note alpha={phase(s,f,1)}>金色是本次待确认修改，不是已完成结果</Note></>;
 }
 if(t==='prepared-votes'){
  const a=hit(s,f,'order-state-durable'),b=hit(s,f,'stock-state-durable');
  const ra=hit(s,f,'order-ready-reply-arrives'),rb=hit(s,f,'stock-ready-reply-arrives');
  return <><Title>先可靠保存，再答复就绪</Title>
   <Coordinator state={rb?'收到两份就绪答复':ra?'收到订单就绪 · 等库存':'收集本次准备结果'} color={rb?C.blue:C.gold}/>
   {pair({mode:'prepared',durable:a},{mode:'prepared',durable:b})}
   {inward(phase(s,f,1,.02,.36),phase(s,f,1,.42,.75),'已经就绪')}
   <Note color={C.gold}>{rb?'两边都能按最终决定完成':'先把可恢复状态存好，才能作出承诺'}</Note></>;
 }
 if(t==='durable-decision'){
  const saved=hit(s,f,'commit-decision-durable');
  return <><Title>共同决定，也要可靠保存</Title>
   <Coordinator state={saved?'已记录：保存修改':'两边都答应 · 等记录决定'} color={saved?C.blue:C.gold}/>
   {pair({mode:'prepared',durable:true},{mode:'prepared',durable:true})}
   <div style={{position:'absolute',left:660,top:392,width:600,height:4,background:C.blue,transform:`scaleX(${phase(s,f,1,.15,.57)})`,transformOrigin:'left'}}/>
   <Note color={C.blue}>{saved?'决定已经记下，两边还没有落实':'不能只把最终决定留在内存里'}</Note></>;
 }
 if(t==='send-decision'){
  const a=phase(s,f,1,.12,.65),b=phase(s,f,1,.25,.8);
  return <><Title color={C.teal} alpha={f>=cue(s,'提交')?1:0}>提交：按共同决定分别落实</Title>
   <Coordinator state="已记录：保存修改"/>
   {pair({mode:'prepared',durable:true},{mode:'prepared',durable:true})}
   {outward(a,b,'最终指令',C.blue,a>0?1:0)}
   <Note>发出指令，不等于所有参与方已经完成</Note></>;
 }
 if(t==='apply-separately'){
  const a=hit(s,f,'order-commits-first'),b=hit(s,f,'stock-commits-later');
  return <><Title>同一个决定，可以先后落实</Title>
   <Coordinator state="已记录：保存修改"/>
   {pair({mode:a?'committed':'prepared',durable:true},{mode:b?'committed':'prepared',durable:true})}
   {outward(phase(s,f,0,.05,.63),phase(s,f,1,.05,.64),'保存修改',C.blue)}
   <Note color={b?C.teal:C.gold}>{b?'库存随后保存成 3 · 两边结果一致':a?'订单先完成，库存还在等最终指令':'同一决定，不要求两个指令同时抵达'}</Note></>;
 }
 if(t==='success'){
  const done=hit(s,f,'all-completions-received');
  return <><Title>两边都落实，本例才完成</Title>
   <Coordinator state={done?'本例完成：订单与库存都已保存':'等待两边完成回执'} color={done?C.teal:C.blue}/>
   {pair({mode:'committed'},{mode:'committed'})}
   {inward(phase(s,f,0,.05,.4),phase(s,f,0,.35,.65),'完成',C.teal)}
   <Note color={C.teal}>统一的是结果，不是每个库同一时刻变化</Note></>;
 }
 if(t==='reject-before-decision'){
  const a=hit(s,f,'order-prepared'),b=hit(s,f,'stock-rejects'),abort=hit(s,f,'abort-decision-durable');
  return <><Title>决定保存前，有人拒绝</Title>
   <Reset>失败分支重置 · 从无本单记录、库存 4 开始</Reset>
   <Coordinator state={abort?'已记录：放弃整笔':b?'库存拒绝 · 不能决定保存':'收集本次答复'} color={abort||b?C.red:C.blue}/>
   {pair({mode:a?'prepared':'empty',durable:true},{mode:b?'rejected':'empty'})}
   <Token x1={1440} y1={414} x2={1160} y2={414} p={phase(s,f,0,.76,.96)} text="不能完成" color={C.red} alpha={b&&!abort?1:0}/>
   <Note color={C.red} alpha={phase(s,f,1)}>有一方不能准备，就不能让另一方单独成功</Note></>;
 }
 if(t==='abort'){
  const gone=hit(s,f,'pending-order-discarded'),done=hit(s,f,'abort-finished');
  return <><Title>按放弃决定，撤掉待确认修改</Title>
   <Coordinator state={done?'放弃收尾完成':'已记录：放弃整笔'} color={done?C.muted:C.red}/>
   {pair({mode:gone?'aborted':'prepared',durable:true},{mode:'aborted'})}
   <Token x1={760} y1={414} x2={480} y2={414} p={phase(s,f,0,.15,.72)} text="撤销待确认修改" color={C.red} width={290}/>
   <Note color={done?C.muted:C.red}>{gone?'没有本单记录，原库存仍是 4':'撤销尚未提交的本次修改'}</Note></>;
 }
 if(t==='in-doubt'){
  const lost=hit(s,f,'coordinator-unreachable');
  return <><Title>已经准备，却不知道共同决定</Title>
   <Reset>新故障分支 · 双方已准备；只显示参与方已知信息</Reset>
   <Coordinator state={lost?'联系中断 · 共同决定未知':'正在查询共同决定'} color={C.gold} detail="参与方视角 · 查询协调者"/>
   {pair({mode:'prepared',durable:true,wait:lost},{mode:'prepared',durable:true,wait:lost})}
   <Line x1={480} y1={426} x2={1440} y2={426} color={lost?C.red:C.gold} dashed p={phase(s,f,0,.06,.6)}/>
   {lost&&<Cross x={960} y={426}/>}
   <Note color={C.gold}>本地等久了，也不能自行改成放弃</Note></>;
 }
 if(t==='recover-decision'){
  const found=hit(s,f,'old-decision-recovered'),a=hit(s,f,'order-recovery-complete'),b=hit(s,f,'stock-recovery-complete');
  return <><Title>恢复以后，继续按原决定处理</Title>
   <Reset>延续失联分支 · 本例揭示故障前已保存的决定</Reset>
   <Coordinator state={found?'故障前已记录：保存修改':'正在读取可靠记录'} color={found?C.blue:C.gold} detail="协调者恢复 · 读取故障前记录"/>
   {pair({mode:a?'committed':'prepared',durable:true},{mode:b?'committed':'prepared',durable:true})}
   {found&&outward(phase(s,f,1,.05,.4),phase(s,f,1,.35,.7),'原保存决定',C.blue)}
   <Note color={b?C.teal:C.blue}>{b?'按同一决定完成，不把重发当成再次购买':'恢复不是临时换一个相反结果'}</Note></>;
 }
 if(t==='resource-boundary'){
  const waiting=hit(s,f,'other-modification-waits');
  return <><Title>准备好的状态，需要付出等待</Title>
   <Reset>回看决定未知的等待阶段</Reset>
   <Coordinator state="共同决定仍待核实" color={C.gold}/>
   {pair({mode:'prepared',durable:true,alpha:.25},{mode:'prepared',durable:true,wait:true})}
   <Token x1={820} y1={626} x2={1040} y2={626} p={phase(s,f,0,.08,.64)} text="其他修改" color={C.muted} width={220}/>
   {waiting&&<Cross x={1120} y={657} color={C.gold}/>}
   <Txt x={960} y={704} width={340} center size={24} color={C.gold} alpha={waiting?1:0}>等待本行资源</Txt>
   <Note color={C.gold}>资源要支持准备与恢复，也要尽快结束占用</Note></>;
 }
 const a=phase(s,f,0,.05,.3),b=phase(s,f,0,.35,.62),c=phase(s,f,1,.05,.38);
 return <><Title>先准备，再按可靠决定收尾</Title>
  <Chip x={430} y={460} width={420} color={C.gold} alpha={a}>准备好本次修改</Chip>
  <Line x1={650} y1={492} x2={740} y2={492} p={b} color={C.blue}/>
  <Chip x={960} y={460} width={420} color={C.blue} alpha={b}>可靠的共同决定</Chip>
  <Line x1={1180} y1={492} x2={1270} y2={492} p={c} color={C.teal}/>
  <Chip x={1490} y={460} width={420} color={C.teal} alpha={c}>各自落实同一结果</Chip>
  <Txt x={960} y={643} width={1400} center size={36} color={C.gold} alpha={c}>代价：等待与资源占用</Txt>
  <Note color={C.teal}>本集只看两阶段提交</Note>
  <Txt x={960} y={886} center size={23} color={C.muted} alpha={c}>IT小村 · 原创</Txt>
 </>;
};
const chapters:Record<string,[number,string]>={question:[1,'共同确认'],prepare:[2,'先把修改做好'],decision:[3,'落实共同结果'],failure:[4,'故障怎样收尾']};
const ShotView:React.FC<{s:Shot;captions:boolean}>=({s,captions})=>{
 const f=useCurrentFrame(),[n,label]=chapters[s.chapterId]??[1,'共同确认'];
 const sub=s.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from+(q.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 86% 2%,#1B435C66,transparent 65%)'}}/>
  <Txt x={100} y={52} size={24} color={C.muted}>分布式 · 独立短片</Txt><Txt x={1700} y={52} size={25}>IT小村</Txt>
  <Txt x={100} y={96} size={22} color={C.blue}>{String(n).padStart(2,'0')} / 04 · {label}</Txt>
  <Txt x={1650} y={104} center width={430} size={19} color={C.muted}>示例数据 · 订单 8124</Txt>
  <div style={{position:'absolute',top:140,left:100,display:'flex',gap:9}}>{[1,2,3,4].map(i=><div key={i} style={{height:4,width:i===n?68:28,borderRadius:4,background:i===n?C.blue:C.edge}}/>)}</div>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',justifyContent:'center',alignItems:'center',fontSize:40,lineHeight:1.4,textAlign:'center',padding:'7px 15px',boxSizing:'border-box',background:`${C.bg}F8`,borderRadius:12}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export const Main:React.FC<{hideSubtitles?:boolean;showSubtitles?:boolean}>=({hideSubtitles=false,showSubtitles=true})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
