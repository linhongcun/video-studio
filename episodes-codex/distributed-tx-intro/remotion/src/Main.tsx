import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots} from './data';
import {C,FONT} from './theme';
import {at,eventAt,navigationMotion} from './motion';
import {createBranchNavigator} from '../../../_shared/branch-map';
import {navigationSpec} from './branch-map';
import {Title,Note,Reset,Order,Stock,SplitBoundaries,Cross,Check,Txt,Chip,Line,LocalBoundary,MovingChip,ease,lerp} from './objects';
declare const __HAS_VOICE_AUDIO__:boolean;
const BranchNavigator=createBranchNavigator(React);
const phase=(s:Shot,f:number,i:number,a=.08,b=.67)=>ease(f,at(s,i,a),at(s,i,b)-at(s,i,a));
const hit=(s:Shot,f:number,name:string)=>f>=eventAt(s,name);
const cue=(s:Shot,name:string)=>Number(s.cueFrames?.labels?.[name]??1);
const local=(p=1,color=C.gold,label='同一笔提交的范围')=><LocalBoundary x={235} y={365} w={1450} h={385} p={p} color={color} label={label}/>;
const request=(p:number,text='扣 1 件',color=C.gold,y=500)=> <>
 <Line x1={805} y1={y+30} x2={1115} y2={y+30} color={color} p={p}/>
 <MovingChip x1={860} y1={y} x2={1050} y2={y} p={p} color={color} width={220}>{text}</MovingChip>
</>;
const RecordRow=({done,alpha=1}:{done:boolean;alpha?:number})=><div style={{position:'absolute',left:1120,top:685,width:570,height:54,borderTop:`2px solid ${done?C.teal:C.gold}`,color:done?C.teal:C.gold,opacity:alpha,fontSize:23,paddingTop:12,textAlign:'center'}}>8124-扣库存　{done?'已完成':'待保存'}</div>;

const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const t=s.visualType;
 if(t==='hook'){
  const q=phase(s,f,0,.02,.32);
  return <><Title>一笔订单，两个结果？</Title>
   <Order exists state="已记录" color={C.teal}/><Stock value={4} state="尚未扣减" color={C.gold}/>
   <Line x1={805} y1={530} x2={1115} y2={530} p={q} color={C.red} dashed/>
   <Cross x={960} y={530} alpha={phase(s,f,0,.36,.55)}/>
   <Chip x={960} y={705} width={420} color={C.gold} alpha={phase(s,f,0,.5,.75)}>整单成功？还不能确认</Chip>
   <Note alpha={phase(s,f,1,.05,.4)}>订单已记录，不等于整笔业务已成功</Note></>;
 }
 if(t==='business-goal'){
  const p=phase(s,f,1,.06,.6);
  return <><Title>同一笔订单，要满足两个条件</Title>
   <Order exists state="目标：订单确认" color={C.teal}/>
   <Line x1={805} y1={530} x2={1115} y2={530} p={p} color={C.teal}/>
   <MovingChip x1={860} y1={495} x2={1050} y2={495} p={p} width={220} color={C.teal}>购买 1 件</MovingChip>
   <Stock value={4} state="当前库存" detail="目标：扣减后为 3" color={C.text}/>
   <Chip x={1400} y={722} width={350} color={C.teal} alpha={p}>目标值 3 · 尚未执行</Chip>
   <Note alpha={p}>示例规则：确认本单之前，库存安排也要落实</Note></>;
 }
 if(t==='scope'){
  const p=phase(s,f,1);
  return <><Title>先只看这两步</Title><Order exists state="记下订单" color={C.text}/><Stock state="扣减库存" color={C.text}/>
   <Line x1={805} y1={530} x2={1115} y2={530} p={p} color={C.teal}/>
   <Chip x={960} y={705} width={520} alpha={p} color={C.teal}>同一个业务目标</Chip>
   <Note>订单 8124 · 商品 7042 · 购买 1 件</Note></>;
 }
 if(t==='local-intro'){
  const p=phase(s,f,0),q=phase(s,f,1);
  return <>{local(p)}<Order pending state="待提交" color={C.gold}/><Stock value={4} state="原库存：4" detail="拟改为 3 · 尚未提交" color={C.gold} alpha={q}/>
   <Note alpha={q}>两处修改，交给同一笔事务管理</Note></>;
 }
 if(t==='local-commit'){
  const done=hit(s,f,'joint-local-commit'),ready=phase(s,f,0,.08,.63);
  return <><Title>提交时，两处修改共同生效</Title>{local(1,done?C.teal:C.gold)}
   <Order pending={!done} exists={done} state={done?'已记录':'修改已就绪 · 待提交'} color={done?C.teal:C.gold}/>
   <Stock value={done?3:4} state={done?'已扣 1 件':'原库存：4'} detail={done?'扣减已保存':'拟改为 3 · 尚未提交'} color={done?C.teal:C.gold}/>
   <Chip x={960} y={263} width={410} color={done?C.teal:C.gold} alpha={ready}>{done?'提交成功':'两步都已做好'}</Chip>
   {done&&<Check x={960} y={535}/>}
   <Note color={done?C.teal:C.muted}>{done?'订单与库存都保存，本单条件满足':'尚未提交，不能只把一处当成完成'}</Note></>;
 }
 if(t==='local-rollback'){
  const failed=hit(s,f,'stock-failed'),undone=hit(s,f,'pending-order-discarded');
  return <><Title>失败时，撤掉尚未提交的修改</Title><Reset>另一种结果 · 示例重置：无本单记录，库存 4</Reset>
   {local(1,undone?C.muted:C.gold)}
   <Order pending={!undone} state={undone?'本单未留下记录':'待提交'} color={undone?C.text:C.gold}/>
   <Stock value={4} state={failed?'库存修改失败':'原库存：4'} color={failed?C.red:C.text}/>
   {failed&&<Cross x={1630} y={700}/>}
   <Chip x={960} y={493} width={350} color={undone?C.muted:C.gold} alpha={phase(s,f,1,.1,.25)}>{undone?'整笔事务已撤销':'撤销待提交修改'}</Chip>
   <Note alpha={phase(s,f,1,.3,.65)}>撤销的是本次修改，原库存仍是 4</Note></>;
 }
 if(t==='local-boundary'){
  const p=phase(s,f,1);
  return <><Title>共同提交，依赖共同的管理范围</Title>
   <Order state="本单未提交" color={C.text}/><Stock value={4} state="原库存" color={C.text}/>
   {local(p,C.teal,'两步都在同一笔事务里')}
   <Chip x={960} y={263} width={390} color={C.teal} alpha={phase(s,f,0)}>一条提交边界</Chip>
   <Note alpha={p}>看清这条边界，才知道它能保证什么</Note></>;
 }
 if(t==='split-boundaries'){
  const w=navigationMotion.split,p=ease(f,w.oldBoundary[0],w.oldBoundary[1]-w.oldBoundary[0]),q=ease(f,w.independentBoundaries[0],w.independentBoundaries[1]-w.independentBoundaries[0]);
  return <><Title>拆开以后，各有各的提交</Title><Reset>架构变化 · 示例重置：无本单记录，库存 4</Reset>
   <Order state="订单库"/><Stock value={4} state="库存库"/>
   <div style={{opacity:1-p}}>{local(1,C.gold,'原来：一笔事务管理')}</div>
   <div style={{opacity:p}}><SplitBoundaries colorLeft={C.blue} colorRight={C.gold} p={q}/></div>
   <div style={{position:'absolute',left:959,top:365,width:2,height:385,background:C.edge,opacity:q}}/>
   <Note alpha={q}>业务还是同一笔，提交已经分成两边</Note></>;
 }
 if(t==='partial-success'){
  const committed=hit(s,f,'order-local-committed'),failed=hit(s,f,'stock-failed'),rolled=hit(s,f,'stock-local-rolled-back');
  return <><Title>{rolled?'库存本地回滚，订单仍已保存':failed?'一边已保存，另一边失败':committed?'订单已保存，等待库存结果':'先保存订单，再处理库存'}</Title>
   <SplitBoundaries colorLeft={committed?C.teal:C.edge} colorRight={failed?C.red:C.gold}/>
   <Order exists={committed} state={committed?'本单已记录':'待提交'} color={committed?C.teal:C.gold}/>
   <Stock value={4} state={rolled?'本地已回滚':failed?'处理失败':'准备扣 1 件'} detail={rolled?'库存仍 4':'本单尚未扣减'} color={failed?C.red:C.gold}/>
   {committed&&<Check x={520} y={700}/>}{failed&&<Cross x={1630} y={705}/>}
   <Line x1={1115} y1={530} x2={805} y2={530} p={phase(s,f,1)} color={C.red} dashed/>
   <Cross x={960} y={530} alpha={phase(s,f,1,.4,.65)}/>
   <Note alpha={phase(s,f,1,.25,.6)} color={C.gold}>库存回滚，撤不掉另一边已经提交的订单</Note></>;
 }
 if(t==='distributed-intro'){
  const p=phase(s,f,0,.08,.6);
  return <><Order exists state="已记录" color={C.teal}/><Stock value={4} state="本单待处理" color={C.gold}/>
   <SplitBoundaries colorLeft={C.teal} colorRight={C.gold}/>
   <Line x1={520} y1={300} x2={1400} y2={300} p={p} color={C.blue} dashed/>
   <Chip x={960} y={267} width={440} color={C.blue} alpha={p}>同一笔业务的协作范围</Chip>
   <Note alpha={phase(s,f,1)} color={C.gold}>协调独立操作，不是自动获得一笔本地提交</Note></>;
 }
 if(t==='not-machine-count'){
  const q=phase(s,f,1);
  return <><Title>关键是操作的边界</Title>
   <SplitBoundaries colorLeft={C.blue} colorRight={C.gold}/>
   <Order exists state="独立提交" color={C.blue}/><Stock value={4} state="独立提交" color={C.gold}/>
   <Line x1={805} y1={530} x2={1115} y2={530} p={q} color={C.muted} dashed/>
   <Chip x={960} y={705} width={620} color={C.teal} alpha={q}>同一笔事务，能覆盖这两步吗？</Chip>
   <Note alpha={phase(s,f,0)}>按提交范围判断，不按机器数量判断</Note></>;
 }
 if(t==='timeout'){
  const saved=hit(s,f,'remote-stock-committed'),lost=hit(s,f,'reply-lost'),unknown=hit(s,f,'caller-timeout-unknown');
  const w=navigationMotion.timeout,req=ease(f,w.request[0],w.request[1]-w.request[0]),reply=ease(f,w.reply[0],w.reply[1]-w.reply[0]);
  return <><Title>请求超时，结果可能仍然发生了</Title><Reset>新分支 · 订单已记录，库存从 4 开始</Reset>
   <SplitBoundaries left="调用方看到的情况" right="库存库实际发生的情况" colorLeft={C.gold} colorRight={saved?C.teal:C.edge}/>
   <Order exists state={unknown?'等待超时 · 结果未知':'等待扣减回复'} color={C.gold}/>
   <Stock value={saved?3:4} state={saved?'已本地保存':'等待请求'} detail={saved?'调用方尚未拿到这个结果':''} color={saved?C.teal:C.text}/>
   {!saved&&request(req)}
   {saved&&!lost&&<MovingChip x1={1060} y1={497} x2={960} y2={497} p={reply} width={230} color={C.teal}>已扣 1 件</MovingChip>}
   {saved&&<Line x1={1115} y1={530} x2={960} y2={530} p={reply} color={lost?C.red:C.teal}/>}
   {lost&&<Cross x={960} y={530}/>}
   <Note alpha={phase(s,f,1,.08,.45)} color={C.gold}>没收到回复 ≠ 对方没有执行</Note></>;
 }
 if(t==='two-possibilities'){
  const b=hit(s,f,'switch-to-already-executed-possibility'),q=phase(s,f,1);
  return <><Title>同一个超时，可能对应不同结果</Title>
   <Reset>{b?'可能 B · 已扣成 3，回复没有回来':'可能 A · 请求没有抵达，库存仍 4'}</Reset>
   <SplitBoundaries left="调用方" right={b?'可能 B：已经执行':'可能 A：没有执行'} colorLeft={C.gold} colorRight={b?C.teal:C.muted}/>
   <Order exists state="超时 · 结果未知" color={C.gold}/><Stock value={b?3:4} state={b?'扣减已保存':'没有发生扣减'} color={b?C.teal:C.text}/>
   <Line x1={805} y1={530} x2={1115} y2={530} color={C.muted} dashed p={phase(s,f,0,.05,.35)}/><Cross x={960} y={530}/>
   <Chip x={960} y={705} width={450} color={C.gold} alpha={q}>调用方的观察：一样</Chip>
   <Note alpha={q}>这是两种可能，不能当成同一次顺序执行</Note></>;
 }
 if(t==='unsafe-retry'){
  const a=hit(s,f,'reset-to-never-executed-branch'),wrong=a?hit(s,f,'wrong-reverse-increment'):hit(s,f,'wrong-double-decrement');
  const p=a?phase(s,f,1,.1,.66):phase(s,f,0,.12,.67);
  return <><Title color={C.red}>{a?'错误示范：盲目反向修改':'错误示范：把同一操作再做一遍'}</Title>
   <Reset>{a?'切换可能 A · 原本未执行，库存从 4 开始':'选择可能 B · 已经扣过，库存从 3 开始'}</Reset>
   <SplitBoundaries colorLeft={C.gold} colorRight={wrong?C.red:C.edge}/>
   <Order exists state="同一笔业务" color={C.gold}/>
   <Stock value={a?(wrong?5:4):(wrong?2:3)} state={wrong?(a?'错误返还':'重复扣减'):(a?'本来没有扣过':'已经扣过 1 件')} color={wrong?C.red:C.text}/>
   {request(p,a?'盲目加 1':'普通扣 1',C.red)}
   <Note color={C.red} alpha={wrong?1:0}>{a?'没有扣过，却多加了一件':'只买一件，库存却被扣了两次'}</Note></>;
 }
 if(t==='durable-progress'){
  const done=hit(s,f,'stock-and-progress-local-commit'),stopped=hit(s,f,'process-interrupted-record-survives'),recovery=hit(s,f,'recovery-checks-record');
  return <><Title>让恢复有据可查</Title><Reset>回看正确写法 · 示例重置：库存 4，操作待保存</Reset>
   <Order x={450} exists state={recovery?'恢复后查证':'调用程序'} color={stopped&&!recovery?C.muted:C.text} alpha={(stopped&&!recovery)?0.35:1}/>
   <LocalBoundary x={1040} y={355} w={700} h={420} color={done?C.teal:C.gold} label="库存变化和操作记录 · 同一笔本地提交"/>
   <Stock x={1400} y={395} value={done?3:4} state={done?'已扣 1 件':'尚未扣减'} color={done?C.teal:C.gold} units={false}/>
   <RecordRow done={done}/>
   <Chip x={700} y={705} width={450} color={stopped&&!recovery?C.red:C.blue} alpha={phase(s,f,1,.08,.25)}>{recovery?'程序恢复 · 查询记录':'程序中断'}</Chip>
   {recovery&&<Line x1={805} y1={530} x2={1040} y2={530} p={phase(s,f,1,.5,.67)} color={C.blue}/>}
   <Note alpha={phase(s,f,1,.35,.65)}>程序可以中断，已保存的进度要能继续查到</Note></>;
 }
 if(t==='safe-retry'){
  const done=hit(s,f,'duplicate-recognized-stock-unchanged'),reject=hit(s,f,'separate-business-rejection-branch');
  const p=phase(s,f,0,.08,.68);
  return <><Title>{reject?'重试，也要区分失败原因':'认出同一笔操作，效果只产生一次'}</Title>
   {reject?<><Reset>另一种结果 · 业务拒绝分支</Reset><Chip x={960} y={425} width={650} color={C.red}>业务规则不允许继续</Chip><Line x1={960} y1={490} x2={960} y2={625} p={phase(s,f,1,.2,.6)} color={C.red}/><Chip x={960} y={625} width={650} color={C.gold} alpha={phase(s,f,1,.45,.75)}>按约定失败收尾</Chip></>:<>
    <Order exists state="重送同一笔操作" color={C.gold}/>
    <LocalBoundary x={1115} y={365} w={570} h={410} color={C.teal} label="已保存的库存与操作记录"/>
    <Stock value={3} state={done?'识别为已处理 · 仍是 3':'本单已扣过 1 件'} color={C.teal} units={false}/><RecordRow done/>
    <Line x1={805} y1={530} x2={1115} y2={530} p={p} color={C.gold}/>
    <MovingChip x1={890} y1={490} x2={1035} y2={490} p={p} color={C.gold} width={300}>8124-扣库存</MovingChip>
    {done&&<Check x={1400} y={650}/>}
   </>}
   <Note color={reject?C.gold:C.teal}>{reject?'暂时故障可重试，业务拒绝不能只靠重试':'同一笔操作再次抵达，不再扣减库存'}</Note></>;
 }
 if(t==='decision-or-workflow'){
  const workflow=hit(s,f,'switch-to-workflow-illustration');
  const first=workflow?hit(s,f,'workflow-first-step-complete'):hit(s,f,'first-participant-applies');
  const second=workflow?hit(s,f,'workflow-second-step-complete'):hit(s,f,'second-participant-applies');
  const decided=hit(s,f,'durable-shared-decision');
  return <><Title>{workflow?'思路二：各步先完成，继续推进':'思路一：先协调决定，再分别落实'}</Title>
   <Reset>{workflow?'另一类思路 · 独立示意，从库存 4 开始':'独立示意 · 从待决定开始'}</Reset>
   <SplitBoundaries colorLeft={first?C.teal:C.gold} colorRight={second?C.teal:C.gold}/>
   <Order pending={!first} exists={first} state={first?'本步已提交':workflow?'本步待处理':'本步待决定'} color={first?C.teal:C.gold}/>
   <Stock value={second?3:4} state={second?'本步已提交':workflow?'后续待处理':'本步待决定'} color={second?C.teal:C.gold}/>
   {!workflow&&<Chip x={960} y={263} width={460} color={decided?C.teal:C.gold}>{decided?'共同决定已记录':'先协调参与方'}</Chip>}
   <Line x1={805} y1={530} x2={1115} y2={530} p={workflow?phase(s,f,1,.28,.7):phase(s,f,0,.42,.82)} color={second?C.teal:C.gold}/>
   <Note>{workflow?'还要为后续失败设计处理路径':'共同决定与各方实际提交，依然有先后'}</Note></>;
 }
 if(t==='eventual-consistency'){
  const stalled=hit(s,f,'rewind-to-stalled-recovery-branch'),done=!stalled&&hit(s,f,'recovery-converges'),paused=stalled&&hit(s,f,'recovery-pauses-business-pending');
  const p=stalled?phase(s,f,1,.1,.4)*.5:phase(s,f,0,.15,.7);
  return <><Reset>{stalled?'回看另一种结果 · 恢复过程暂停':done?'本例已收拢 · 订单确认，库存 3':'约定的中间状态 · 本单仍待确认'}</Reset>
   <SplitBoundaries colorLeft={done?C.teal:C.gold} colorRight={done?C.teal:C.gold}/>
   <Order exists state={done?'订单确认':'已记录 · 整单待确认'} color={done?C.teal:C.gold}/>
   <Stock value={done?3:4} state={done?'本单已扣 1 件':paused?'等待恢复':'本单待处理'} color={done?C.teal:C.gold}/>
   {request(p,paused?'等待恢复':'可靠推进',paused?C.gold:C.blue)}
   {paused&&<Cross x={1060} y={530} color={C.gold}/>}
   <Note color={done?C.teal:C.gold}>{done?'恢复路径落实后，业务结果才收拢':paused?'机制没有继续工作，结果就停在待恢复':'允许中间状态，需要实际的推进与恢复'}</Note></>;
 }
 if(t==='business-boundaries'){
  const b=f>=at(s,1,.05),p=phase(s,f,b?1:0,.1,.6);
  return <><Title>先确定业务允许什么</Title>
   <Order x={440} exists state="订单 8124" color={C.text} alpha={.45}/>
   <div style={{position:'absolute',left:830,top:345,width:2,height:370,background:C.edge}}/>
   <Txt x={960} y={365} size={29} color={C.muted}>{b?'再问失败怎样结束':'先问能不能等待'}</Txt>
   <Txt x={960} y={442} size={47} color={C.gold} width={800}>{b?'已经发生的动作，\n真的能够撤销吗？':'中间过程，\n能否暂时等待？'}</Txt>
   <Line x1={960} y1={645} x2={1620} y2={645} color={C.gold} p={p}/>
   <Note color={C.gold}>{b?'不能撤销，就不能假设事后会自动还原':'规则明确以后，才能选择协作机制'}</Note></>;
 }
 const p=phase(s,f,1,.04,.5);
 return <><Title>先理解问题，再深入方案</Title>
  <div style={{opacity:1-p*.85}}><Order exists state="订单确认" color={C.teal}/><Stock value={3} state="本单已扣 1 件" color={C.teal}/><SplitBoundaries colorLeft={C.teal} colorRight={C.teal}/></div>
  <div style={{position:'absolute',left:lerp(1920,360,p),top:382,width:1200,padding:'45px 55px',boxSizing:'border-box',borderTop:`3px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,background:C.bg}}>
   <div style={{fontSize:27,color:C.muted}}>继续深入 · 独立机制短片</div><div style={{fontSize:49,color:C.teal,marginTop:22}}>按一种机制一集，理解协作与恢复</div>
   <div style={{fontSize:28,color:C.muted,marginTop:25}}>逐步看清动作、失败处理与适用边界</div>
  </div>
  <Note color={C.teal}>一笔业务跨了提交边界，就要设计协作和恢复</Note>
  <Txt x={960} y={885} center size={23} color={C.muted} alpha={p}>IT小村 · 原创</Txt>
 </>;
};
const firstTerms:Record<string,string>={'local-intro':'本地事务','distributed-intro':'分布式事务','eventual-consistency':'最终一致'};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),term=firstTerms[s.visualType];
 const sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 5%, #173B5555, transparent 62%)'}}/>
  <Txt x={100} y={54} size={24} color={C.muted}>分布式 · 概念入门</Txt>
  <Txt x={1700} y={54} size={25}>IT小村</Txt><Txt x={1650} y={103} center width={420} size={19} color={C.muted}>示例数据 · 订单 8124</Txt>
  <BranchNavigator spec={navigationSpec(s,f)} shotId={s.id} frame={f} durationInFrames={s.durationInFrames} foreground={term?<Title color={C.teal} alpha={f>=cue(s,term)?1:0}>{term}</Title>:undefined}><Scene s={s} f={f}/></BranchNavigator>
  {s.visualType==='bridge'&&<Txt x={960} y={885} center size={23} color={C.muted} alpha={phase(s,f,1,.04,.5)}>IT小村 · 原创</Txt>}
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:40,fontWeight:500,lineHeight:1.4,textAlign:'center',background:`${C.bg}F8`,borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
