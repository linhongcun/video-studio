import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots} from './data';
import {C,FONT} from './theme';
import {at,eventAt} from './motion';
import {createBranchNavigator} from '../../../_shared/branch-map';
import {sagaMapForFrame} from './branch-map';
const BranchNavigator = createBranchNavigator(React);
import {Title,Reset,Note,Account,Stock,Txt,Chip,Line,LocalBoundary,MovingChip,Cross,Check,ease} from './objects';
declare const __HAS_VOICE_AUDIO__:boolean;
const phase=(s:Shot,f:number,i:number,a=.08,b=.67)=>ease(f,at(s,i,a),at(s,i,b)-at(s,i,a));
const hit=(s:Shot,f:number,n:string)=>f>=eventAt(s,n);
const cue=(s:Shot,n:string)=>Number(s.cueFrames?.labels?.[n]??1);
const accountBoundary=(color=C.gold,label='账户库 · 本地提交')=><LocalBoundary x={215}y={350}w={610}h={402}color={color}label={label}/>;
const stockBoundary=(color=C.gold,label='库存库 · 本地提交')=><LocalBoundary x={1095}y={350}w={610}h={402}color={color}label={label}/>;
const connect=(p:number,label:string,color=C.gold)=><><Line x1={825}y1={515}x2={1095}y2={515}p={p}color={color}/><MovingChip x1={900}y1={482}x2={1020}y2={482}p={p}width={235}color={color}>{label}</MovingChip></>;
const refundPath=(p:number,label='退款 ＋200',color=C.gold)=><><Line x1={1220}y1={515}x2={825}y2={515}p={p}color={color}/><MovingChip x1={1170}y1={482}x2={920}y2={482}p={p}width={270}color={color}>{label}</MovingChip></>;
const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const t=s.visualType;
 if(t==='hook')return <><Title>扣款成功，缺货了怎么办？</Title><Account value={800}state="扣款已保存"color={C.teal}history="debit"/><Stock value={0}state="缺货 · 本单拒绝"color={C.red}/><Cross x={1400}y={710}/><Chip x={960}y={690}width={340}color={C.gold}>本单还没有收尾</Chip><Note alpha={phase(s,f,1)}>做成的一步，也需要按业务规则处理</Note></>;
 if(t==='example')return <><Title>同一笔订单，先看成功的情况</Title><Reset>成功示例 · 从账户1000、库存4开始</Reset><Account/><Stock/><Chip x={960}y={690}width={430}alpha={phase(s,f,1)}>订单8124 · 买1件 · 200元</Chip><Note>所有数字都是示例，不代表某平台的固定流程</Note></>;
 if(t==='saga'){
  const p=phase(s,f,0),q=phase(s,f,1);
  return <><Title color={C.teal}alpha={f>=cue(s,'Saga')?1:0}>Saga：各步先保存，再推进</Title><Account alpha={.65}/><Stock alpha={.65}/><div style={{opacity:p}}>{accountBoundary(C.blue)}{stockBoundary(C.gold)}</div>{connect(q,'下一步',C.blue)}<Note alpha={q}>一笔业务，分成各自提交的步骤</Note></>;
 }
 if(t==='charge'){
  const done=hit(s,f,'charge-local-commit'),p=phase(s,f,0,.06,.67);
  return <><Title>{done?'第一步：扣款已经提交':'第一步：扣款单独提交'}</Title>{accountBoundary(done?C.teal:C.gold)}<Account value={done?800:1000}state={done?'扣款已保存':'准备扣200元'}color={done?C.teal:C.gold}history={done?'debit':'none'}/><Stock alpha={.25}/><MovingChip x1={1000}y1={495}x2={850}y2={495}p={p}color={C.gold}width={230}>扣款 −200</MovingChip><Note color={done?C.teal:C.muted}>{done?'账户本地已经保存，不等后一步才提交':'先执行账户内的这笔修改'}</Note></>;
 }
 if(t==='stock'){
  const done=hit(s,f,'stock-local-commit'),confirmed=hit(s,f,'order-confirmed');
  return <><Title>第二步：库存完成后确认订单</Title><Account value={800}state="前一步已保存"history="debit"alpha={.4}color={C.teal}/>{stockBoundary(done?C.teal:C.gold)}<Stock value={done?3:4}state={done?'本次扣1件 · 已保存':'本次准备扣1件'}color={done?C.teal:C.gold}/>{connect(phase(s,f,0,.08,.67),'扣1件')}
  <Chip x={960}y={690}width={400}color={confirmed?C.teal:C.gold}>{confirmed?'订单8124 · 已确认':'订单8124 · 待确认'}</Chip><Note color={confirmed?C.teal:C.muted}>{confirmed?'两步各自完成，本例业务成功':'前一步已经提交，后一步继续执行'}</Note></>;
 }
 if(t==='failure-reset')return <><Title>换个结果：库存已经没有了</Title><Reset>另一分支重置 · 账户从1000、库存从0开始</Reset><Account/><Stock value={0}state="没有可用库存"color={C.red}/>{connect(phase(s,f,1),'先扣款，再查库存',C.gold)}<Note>这是新的失败示例，不延续刚才的库存3</Note></>;
 if(t==='failure'){
  const charged=hit(s,f,'charge-local-commit'),rejected=hit(s,f,'stock-business-rejected');
  return <><Title>{rejected?'钱已扣，库存明确拒绝':charged?'扣款已保存，等待库存结果':'先扣款，再尝试处理库存'}</Title>{accountBoundary(charged?C.teal:C.gold)}{stockBoundary(rejected?C.red:C.edge)}<Account value={charged?800:1000}state={charged?'扣款已保存':'准备扣款'}color={charged?C.teal:C.gold}history={charged?'debit':'none'}/><Stock value={0}state={rejected?'缺货 · 本单拒绝':'等待检查库存'}color={rejected?C.red:C.text}/>{connect(phase(s,f,1,.06,.56),'扣1件',rejected?C.red:C.gold)}{rejected&&<Cross x={1640}y={710}/>}<Note color={C.gold}>本地步骤成功，不等于整笔业务已经成功</Note></>;
 }
 if(t==='already-committed'){
  const plan=hit(s,f,'refund-planned'),p=phase(s,f,0);
  return <><Title>已提交的扣款，不能跨库回滚</Title>{accountBoundary(C.teal)}{stockBoundary(C.red)}<Account value={800}state="原扣款已提交"history="debit"pendingRefund={plan}color={C.teal}/><Stock value={0}state="本地失败"alpha={.45}color={C.red}/><Line x1={1095}y1={515}x2={825}y2={515}p={p}color={C.red}dashed/><Cross x={960}y={515}alpha={p}/><Note color={C.gold}>{plan?'需要新的退款操作，余额暂时仍是800':'另一库的回滚，不能撤销已保存的扣款'}</Note></>;
 }
 if(t==='compensation'){
  const p=phase(s,f,1,.1,.68),arrived=hit(s,f,'refund-request-arrives');
  return <><Title color={C.teal}alpha={f>=cue(s,'补偿')?1:0}>补偿：新的业务操作</Title><Account value={800}state="等待退款"history="debit"pendingRefund color={C.gold}/>{accountBoundary(C.gold)}<Txt x={1400}y={391}center size={29}color={C.muted}>新的退款请求</Txt><Txt x={1400}y={447}center size={63}color={C.gold}>R8124</Txt><Txt x={1400}y={550}center size={29}color={C.gold}>本例应退200元</Txt>{refundPath(p)}<Note color={C.gold}>{arrived?'请求到了，仍要等退款真正保存':'原扣款保留，用新动作按规则收尾'}</Note></>;
 }
 if(t==='refund'){
  const done=hit(s,f,'refund-local-commit'),history=hit(s,f,'original-and-refund-visible');
  return <><Title>{done?'新退款保存，旧流水仍然保留':'新的退款，等待本地保存'}</Title>{accountBoundary(done?C.teal:C.gold)}<Account value={done?1000:800}state={done?'退款已保存':'等待退款保存'}history={done?'refund':'debit'}pendingRefund={!done}color={done?C.teal:C.gold}/><Txt x={1400}y={389}center size={27}color={C.muted}>订单8124</Txt><Txt x={1400}y={448}center size={65}color={done?C.teal:C.gold}>{done?'已取消':'待收尾'}</Txt><Txt x={1400}y={556}center size={26}color={C.muted}>库存仍是0</Txt>{done&&<Check x={1400}y={650}/>}<Note color={done?C.teal:C.gold}>{history?'扣款−200与新退款＋200，都能查到':'补偿不是抹除之前发生的事情'}</Note></>;
 }
 if(t==='duplicate'){
  const done=hit(s,f,'duplicate-refund-recognized'),boundary=hit(s,f,'local-dedup-boundary');
  return <><Title>同一退款重发，不再退第二次</Title>{accountBoundary(C.teal,boundary?'退款与处理标记 · 同一本地提交':'账户已保存的退款结果')}<Account value={1000}state={done?'识别为已退款 · 仍是1000':'本单已经退款'}history="refund"mark={boundary}color={C.teal}/><Txt x={1400}y={390}center size={28}color={C.muted}>同一笔退款再次发送</Txt><Txt x={1400}y={450}center size={62}color={C.gold}>R8124</Txt>{refundPath(phase(s,f,0,.1,.67),'重复 R8124',C.gold)}<Note color={C.teal}>相同业务操作，保存一次效果</Note></>;
 }
 if(t==='refund-failed'){
  const failed=hit(s,f,'refund-attempt-failed');
  return <><Title>补偿本身，也可能失败</Title><Reset>另一分支 · 从已扣款800、退款未完成开始</Reset>{accountBoundary(C.teal)}<Account value={800}state="已扣款 · 仍待退款"history="debit"pendingRefund color={C.gold}/><Txt x={1400}y={390}center size={28}color={C.muted}>退款服务</Txt><Chip x={1400}y={455}width={430}color={failed?C.red:C.gold}>{failed?'故障 · 退款未完成':'尝试执行R8124'}</Chip>{refundPath(phase(s,f,1,.05,.5),'退款请求',failed?C.red:C.gold)}{failed&&<Cross x={1030}y={515}/>}<Note color={C.gold}>退款没有保存，不能说整单已经收尾</Note></>;
 }
 if(t==='recover'){
  const stopped=hit(s,f,'program-interrupted'),restored=hit(s,f,'progress-restored'),escalated=hit(s,f,'repeated-failure-escalated');
  return <><Title>持久记录，给恢复留下依据</Title><Account value={800}state="退款仍待完成"history="debit"color={C.gold}alpha={.6}/>
   <Txt x={1170}y={366}size={26}color={C.muted}>订单8124 · 已保存的流程进度</Txt>
   <Txt x={1170}y={425}size={32}color={C.teal}>扣款：完成</Txt><Txt x={1170}y={484}size={32}color={C.red}>库存：拒绝</Txt><Txt x={1170}y={543}size={32}color={C.gold}>退款：待完成</Txt>
   <div style={{opacity:stopped && !restored ? .15 : 1}}><Chip x={960}y={680}width={380}color={escalated?C.red:C.blue}>{escalated?'持续失败 · 告警处理':restored?'程序恢复 · 读取进度':'执行中的程序'}</Chip></div>
   {restored&&<Line x1={1100}y1={680}x2={1390}y2={622}p={phase(s,f,1,.22,.65)}color={escalated?C.red:C.gold}/>}
   {escalated&&<Txt x={1400}y={663}center size={27}color={C.red}>必要时人工介入</Txt>}
   <Note color={C.gold}>安全重试有边界，不能承诺持续失败也会自动成功</Note></>;
 }
 const read=hit(s,f,'intermediate-value-read'),finish=hit(s,f,'suitable-business-boundary');
 return <><Title>先确定业务能不能接受和补偿</Title><Reset>回看各步已经提交的阶段 · 示例账户800</Reset><Account value={800}state="已经本地提交"history="debit"color={C.teal}/><Txt x={1400}y={390}center size={27}color={C.muted}>另一笔操作读取</Txt><Txt x={1400}y={445}center size={90}color={read?C.gold:C.muted}>{read?'800':'?'}</Txt><Line x1={825}y1={515}x2={1100}y2={515}p={phase(s,f,0,.1,.68)}color={C.gold}/><Chip x={1400}y={620}width={470}color={C.gold}>中间结果可能对外可见</Chip><Note color={C.teal}>{finish?'各步先提交；失败用新的业务操作收尾':'这不是天然的全局隔离'}</Note><Txt x={960}y={885}center size={23}color={C.muted}alpha={finish?1:0}>IT小村 · 原创</Txt></>;
};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame();
 const sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 86% 8%, #173B5555, transparent 62%)'}}/>
  <Txt x={100}y={54}size={24}color={C.muted}>分布式 · 一种实现</Txt>
  <Txt x={1700}y={54}size={25}>IT小村</Txt><Txt x={1650}y={103}center width={420}size={19}color={C.muted}>示例数据 · 订单8124</Txt>
  <BranchNavigator spec={sagaMapForFrame(s,f)} shotId={s.id} frame={f} durationInFrames={s.durationInFrames}><Scene s={s}f={f}/></BranchNavigator>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:40,fontWeight:500,lineHeight:1.4,textAlign:'center',background:`${C.bg}F8`,borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id}from={s.from}durationInFrames={s.durationInFrames}><ShotView shot={s}captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
