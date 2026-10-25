import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from './data';
import javaCard from './java-card.json';
import {C,FONT} from './theme';
import {at,beat} from './motion';
import {Heading,Note,Text,Frame,Path,clamp,lerp} from './objects';
import {createMiddlewareIdentity} from '../../../_shared/middleware-identity';
declare const __HAS_VOICE_AUDIO__:boolean;
type State='待付款'|'已付款'|'已发货';
type Points=[number,number][];
const MiddlewareMark=createMiddlewareIdentity(React);
const termAt=(s:Shot,key:string)=>Number(s.cueFrames?.labels?.[key]??0);
const completed=(p:number)=>p>=.99;

// The marker moves on the actual path. It vanishes on receipt, before the effect.
const Packet:React.FC<{points:Points;p:number;label?:string;color?:string}>=({points,p,label='已付款',color=C.gold})=>{
 const lengths=points.slice(1).map((v,i)=>Math.hypot(v[0]-points[i][0],v[1]-points[i][1]));
 const total=lengths.reduce((a,b)=>a+b,0),inset=Math.min(54,total*.3);
 let distance=inset+(total-2*inset)*clamp(p),x=points[0][0],y=points[0][1];
 for(let i=0;i<lengths.length;i++){
  const part=clamp(distance/Math.max(1,lengths[i]));x=lerp(points[i][0],points[i+1][0],part);y=lerp(points[i][1],points[i+1][1],part);
  if(distance<=lengths[i])break;distance-=lengths[i];
 }
 return p>0&&p<.99?<div style={{position:'absolute',left:x-51,top:y-21,width:102,height:42,background:C.bg,border:'2px solid '+color,borderRadius:9,boxSizing:'border-box',zIndex:4}}><Text x={4} y={4} w={90} size={22} center color={color}>{label}</Text></div>:null;
};
const Receiver:React.FC<{kind:'summary'|'record';summaryState?:State;recordStates?:State[];stopped?:boolean;active?:boolean;goal?:boolean;alpha?:number}>=({kind,summaryState='待付款',recordStates=[],stopped=false,active=false,goal=false,alpha=1})=>{
 const summary=kind==='summary',y=summary?350:610,h=summary?220:180,color=stopped?C.muted:active?C.gold:C.teal;
 return <div style={{opacity:alpha}}><Frame x={1320} y={y} w={450} h={h} label={summary?'订单摘要':'变化记录'} color={color}/>
  {summary?<>
   <Text x={1346} y={y+64} w={398} size={25} color={stopped?C.muted:C.text}>{goal?'付款后需要显示':stopped?'最后收到 · 已停止接收':summaryState==='待付款'?'初始显示':'最后收到的状态'}</Text>
   <Text x={1346} y={y+110} w={398} size={43} color={stopped?C.muted:active?C.gold:C.text} weight={700}>{goal?'17 · 已付款':('17 · '+summaryState)}</Text>
   {stopped&&<Text x={1346} y={y+174} w={398} size={22} color={C.muted}>保留旧值，不代表当前订单状态</Text>}
  </>:goal?<Text x={1346} y={y+85} w={398} size={33} color={C.muted}>付款后需要新增一条</Text>:recordStates.length===0?<Text x={1346} y={y+89} w={398} size={30} color={C.muted}>尚未收到变化</Text>:recordStates.map((state,i)=><Text key={i} x={1346} y={y+58+i*49} w={398} size={34} color={i===recordStates.length-1&&active?C.gold:C.text}>17 · {state}</Text>)}
 </div>;
};
const CloseButton:React.FC<{active?:boolean}>=({active=false})=><div style={{position:'absolute',left:1701,top:367,width:43,height:43,border:'1px solid '+(active?C.gold:C.edge),borderRadius:8,color:active?C.gold:C.muted,fontSize:31,textAlign:'center',lineHeight:'38px'}}>×</div>;
const Cursor:React.FC<{x:number;y:number;click?:number}>=({x,y,click=0})=><div style={{position:'absolute',left:x,top:y,pointerEvents:'none',zIndex:9}}>
 {click>0&&click<1&&<div style={{position:'absolute',left:-24,top:-24,width:48,height:48,border:'3px solid '+C.gold,borderRadius:'50%',opacity:1-click,transform:`scale(${.5+click})`}}/>}
 <svg width={34} height={43} viewBox="0 0 34 43"><path d="M3 2 L3 34 L12 27 L19 40 L25 37 L18 24 L30 23 Z" fill={C.text} stroke={C.bg} strokeWidth={2}/></svg>
</div>;
const ProductUI:React.FC<{state?:State;summaryState?:State;records?:State[];stopped?:boolean;showInternalList?:boolean;focus?:'source'|'summary'|'record';buttonActive?:boolean;closeActive?:boolean}>=({state='待付款',summaryState='待付款',records=[],stopped=false,showInternalList=false,focus,buttonActive=false,closeActive=false})=><>
 <Frame x={150} y={350} w={940} h={440} label="商家 · 订单详情" color={focus==='source'?C.gold:C.blue}/>
 <Text x={192} y={416} w={500} size={45} weight={750}>订单17</Text>
 <Text x={192} y={486} w={400} size={25} color={C.muted}>付款与履约状态</Text>
 <div style={{position:'absolute',left:192,top:535,width:330,height:82,borderRadius:12,background:C.surface,border:'1px solid '+(focus==='source'?C.gold:C.edge)}}><Text x={22} y={11} w={286} size={42} weight={750} color={state==='待付款'?C.text:C.teal}>{state}</Text></div>
 <Text x={192} y={650} w={420} size={25} color={C.muted}>教学示意 · 不执行真实支付</Text>
 {showInternalList?<>
  <Text x={644} y={451} w={391} size={26} color={C.muted}>内部：当前接收者</Text>
  <Text x={644} y={511} w={391} size={31} color={stopped?C.muted:C.text}>{stopped?'摘要已移除':'订单摘要'}</Text>
  <Text x={644} y={574} w={391} size={31} color={C.teal}>变化记录</Text>
 </>:<>
  <Text x={650} y={449} w={386} size={27} color={C.muted}>订单操作</Text>
  <div style={{position:'absolute',left:650,top:540,width:386,height:90,border:'2px solid '+(buttonActive?C.gold:state==='待付款'?C.teal:C.edge),borderRadius:12,background:buttonActive?'#4F442B':state==='待付款'?'#19403D':C.surface}}>
   <Text x={10} y={19} w={366} size={32} center color={state==='待付款'?C.teal:C.muted}>{state==='待付款'?'标记为已付款':'已标记付款'}</Text>
  </div>
  <Text x={650} y={663} w={386} size={24} color={C.muted}>操作后，相关面板响应变化</Text>
 </>}
 {stopped?<>
  <Frame x={1320} y={350} w={450} h={152} label="摘要已关闭 · 停止接收" color={C.muted}/>
  <Text x={1346} y={417} w={398} size={28} color={C.muted}>最后收到：17 · 已付款</Text>
 </>:<Receiver kind="summary" summaryState={summaryState} active={focus==='summary'}/>}
 <Receiver kind="record" recordStates={records} active={focus==='record'}/>
 {!stopped&&<CloseButton active={closeActive}/>}
</>;
const JavaCard:React.FC=()=>{
 const lines=(javaCard as any).lines as string[];
 const size=Math.min(30,Math.floor(742/(lines.length*1.4)));
 return <>
  <Text x={130} y={54} w={1660} size={44} weight={750}>{(javaCard as any).title??'观察者模式 · Java关键关系'}</Text>
  <Text x={130} y={124} w={1660} size={27} color={C.gold}>暂停阅读 · 同进程原理示例 · 非 MQ 客户端 · 关键节选</Text>
  <div style={{position:'absolute',left:120,top:190,width:1680,height:790,border:'1px solid '+C.edge,borderRadius:14,background:C.surface}}>
   <Text x={28} y={22} w={1100} h={744} size={size} mono color={C.text}>{lines.join('\n')}</Text>
   <div style={{position:'absolute',left:1166,top:33,width:1,height:721,background:C.edge}}/>
   <Text x={1210} y={33} w={410} size={27} color={C.gold}>与结构角色对应</Text>
   {[
    ['Order','来源与名单'],
    ['OrderObserver','共同约定'],
    ['SummaryObserver','显示最后收到状态'],
    ['ChangeLogObserver','追加变化事实'],
   ].map(([name,role],i)=><React.Fragment key={name}>
    <Text x={1210} y={106+i*153} w={410} size={25} mono color={C.blue}>{name}</Text>
    <Text x={1210} y={151+i*153} w={410} size={27} color={C.text}>{role}</Text>
   </React.Fragment>)}
  </div>
  <Text x={130} y={1004} w={1660} size={23} color={C.muted}>IT小村 · 原创　　角色名与前面的订单、共同约定、摘要和变化记录一致</Text>
 </>;
};


type QueueState='empty'|'pending'|'inflight'|'acked';
const Queue:React.FC<{kind:'summary'|'record';state:QueueState;alpha?:number;highlight?:boolean}>=({kind,state,alpha=1,highlight=false})=>{
 const y=kind==='summary'?390:625,color=highlight?C.gold:C.teal;
 return <div style={{opacity:alpha}}>
  <Frame x={1030} y={y} w={280} h={140} label={kind==='summary'?'摘要队列':'记录队列'} color={color}/>
  <Text x={1054} y={y+55} w={232} size={24} color={state==='pending'?C.gold:state==='inflight'?C.blue:C.muted}>{state==='empty'?'尚未入队':state==='pending'?'待处理：1 条':state==='inflight'?'待确认：1 条':'已确认：0 条待处理'}</Text>
  {state!=='empty'&&<Text x={1054} y={y+94} w={232} size={22} color={state==='acked'?C.muted:C.text}>{state==='acked'?'本事件已完成':'17 · 已付款'}</Text>}
 </div>;
};
const Service:React.FC<{kind:'summary'|'record';done?:boolean;offline?:boolean;dedup?:boolean;duplicate?:boolean;alpha?:number}>=({kind,done=false,offline=false,dedup=false,duplicate=false,alpha=1})=>{
 const summary=kind==='summary',y=summary?380:615,color=offline?C.red:dedup?C.gold:C.blue;
 return <div style={{opacity:alpha}}>
  <Frame x={1480} y={y} w={330} h={172} label={summary?'摘要服务':'变化记录服务'} color={color}/>
  <Text x={1504} y={y+57} w={282} size={30} color={offline?C.red:done?C.teal:C.muted}>{offline?'暂时离线':done?(summary?'显示：已付款':'已追加：1 条记录'):'尚未处理事件'}</Text>
  <Text x={1504} y={y+109} w={282} size={22} color={dedup?C.gold:C.muted}>{offline?'不消费，不确认':dedup?'同一事件，跳过重复写入':duplicate?'同一事件再次送达':done?'订单17 · 已付款':'独立进程 · 自己处理'}</Text>
 </div>;
};
const SOURCE_PATH:Points=[[475,555],[650,555]];
const TOP_ROUTE:Points=[[900,555],[960,555],[960,460],[1030,460]];
const BOTTOM_ROUTE:Points=[[900,555],[960,555],[960,695],[1030,695]];
const TOP_DELIVERY:Points=[[1310,460],[1480,460]];
const BOTTOM_DELIVERY:Points=[[1310,695],[1480,695]];
const TOP_ACK:Points=[[1480,568],[1310,568]];
const BOTTOM_ACK:Points=[[1480,803],[1310,803]];
const MQDiagram:React.FC<{
 top?:QueueState;bottom?:QueueState;summaryDone?:boolean;recordDone?:boolean;offline?:boolean;
 dedup?:boolean;duplicate?:boolean;alpha?:number;queueAlpha?:number;publish?:number;route?:number;
 summaryDelivery?:number;recordDelivery?:number;summaryAck?:number;recordAck?:number;lostAck?:number;
 redelivery?:number;focus?:'source'|'queues'|'services';eventId?:boolean;
}>=({top='empty',bottom='empty',summaryDone=false,recordDone=false,offline=false,dedup=false,duplicate=false,alpha=1,queueAlpha=1,publish=0,route=0,summaryDelivery=0,recordDelivery=0,summaryAck=0,recordAck=0,lostAck=0,redelivery=0,focus,eventId=false})=><div style={{opacity:alpha}}>
 <div style={{position:'absolute',left:600,top:310,width:765,height:490,border:'2px dashed '+C.edge,borderRadius:22,boxSizing:'border-box'}}/>
 <Text x={625} y={325} w={720} size={24} color={C.muted}>消息中间件 · RabbitMQ 实现示例</Text>
 <Path points={SOURCE_PATH} color={focus==='source'?C.gold:C.edge}/>
 <Path points={TOP_ROUTE} color={focus==='queues'?C.gold:C.edge} alpha={queueAlpha}/><Path points={BOTTOM_ROUTE} color={focus==='queues'?C.gold:C.edge} alpha={queueAlpha}/>
 <Path points={TOP_DELIVERY} color={focus==='services'?C.gold:C.edge} alpha={queueAlpha}/><Path points={BOTTOM_DELIVERY} color={offline?C.red:focus==='services'?C.gold:C.edge} alpha={queueAlpha} dashed={offline}/>
 <Frame x={135} y={400} w={340} h={310} label="订单服务" color={focus==='source'?C.gold:C.blue}/>
 <Text x={164} y={473} w={282} size={36} weight={750}>订单17</Text><Text x={164} y={531} w={282} size={38} color={C.teal} weight={750}>已付款</Text>
 <Text x={164} y={603} w={282} size={24} color={C.muted}>发布已发生的事实</Text>
 <Frame x={650} y={455} w={250} h={204} label="事件路由" color={C.teal}/>
 <div style={{position:'absolute',left:746,top:511}}><MiddlewareMark kind="rabbitmq" size={48}/></div>
 <Text x={674} y={579} w={202} size={25} center>交换机</Text>
 <Queue kind="summary" state={top} alpha={queueAlpha} highlight={focus==='queues'}/><Queue kind="record" state={bottom} alpha={queueAlpha} highlight={focus==='queues'}/>
 <Service kind="summary" done={summaryDone} alpha={queueAlpha}/><Service kind="record" done={recordDone} offline={offline} dedup={dedup} duplicate={duplicate} alpha={queueAlpha}/>
 {eventId&&<Text x={1504} y={796} w={300} size={21} color={C.gold}>事件编号：e17-1（示例）</Text>}
 <Packet points={SOURCE_PATH} p={publish}/><Packet points={TOP_ROUTE} p={route}/><Packet points={BOTTOM_ROUTE} p={route}/>
 <Packet points={TOP_DELIVERY} p={summaryDelivery}/><Packet points={BOTTOM_DELIVERY} p={recordDelivery}/>
 <Packet points={BOTTOM_DELIVERY} p={redelivery} label="e17-1" color={C.red}/>
 {summaryAck>0&&<><Path points={TOP_ACK} p={summaryAck} color={C.teal}/><Text x={1325} y={572} w={142} size={20} center color={C.teal}>处理成功后确认</Text></>}
 {recordAck>0&&<><Path points={BOTTOM_ACK} p={recordAck} color={C.teal}/><Text x={1325} y={772} w={142} size={20} center color={C.teal}>处理成功后确认</Text></>}
 {lostAck>0&&recordAck===0&&<><Path points={BOTTOM_ACK} p={lostAck*.6} color={C.red}/><Text x={1340} y={786} w={110} size={26} center color={C.red}>×</Text><Text x={1325} y={751} w={142} size={20} center color={C.red}>确认丢失</Text></>}
 </div>;

const LocalBrief:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const register=beat(s,f,'register'),state=beat(s,f,'state'),summary=beat(s,f,'summary'),record=beat(s,f,'record'),roles=beat(s,f,'roles');
 return <>
  <Heading>{f>=termAt(s,'观察者模式')?'观察者模式：先登记，变化后再通知':'接收方先登记，来源变化后再通知'}</Heading>
  <Text x={170} y={282} w={1590} size={26} center color={C.gold}>机制回放 · 本次付款前 → 已付款 · 同一程序内</Text>
  <Path points={[[820,470],[1320,470]]} color={C.edge}/><Path points={[[820,700],[1320,700]]} color={C.edge}/>
  <Frame x={150} y={350} w={670} h={440} label="订单来源 · Order" color={state>0?C.gold:C.blue}/>
  <Text x={190} y={427} w={570} size={41} color={completed(state)?C.teal:C.text}>订单17 · {completed(state)?'已付款':'待付款'}</Text>
  <Text x={190} y={501} w={570} size={27} color={C.muted}>当前接收者</Text>
  <Text x={190} y={551} w={570} size={33}>{completed(register)?'订单摘要、变化记录':'尚未登记'}</Text>
  <Text x={190} y={651} w={570} size={27} color={C.teal}>共同约定：订单号 ＋ 新状态</Text>
  <Receiver kind="summary" summaryState={completed(summary)?'已付款':'待付款'} active={summary>0&&!completed(summary)}/>
  <Receiver kind="record" recordStates={completed(record)?['已付款']:[]} active={record>0&&!completed(record)}/>
  <Packet points={[[1320,470],[820,470]]} p={register} label="登记" color={C.blue}/><Packet points={[[1320,700],[820,700]]} p={register} label="登记" color={C.blue}/>
  <Packet points={[[820,470],[1320,470]]} p={summary}/><Packet points={[[820,700],[1320,700]]} p={record}/>
  <Note>{roles>.1?'摘要自己显示，记录自己留痕；来源只按共同约定通知':completed(record)?'来源变化后，两个观察者分别响应':completed(state)?'先改变订单状态，再依约定通知':'先登记接收关系，再回放同一次付款'}</Note>
 </>;
};

const Consistency:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const outbox=beat(s,f,'outbox'),delay=beat(s,f,'delay'),gap=beat(s,f,'gap'),solution=f>=at(s,1,0);
 return <>
  <Heading>{solution?'方案示意：业务状态与待发送事件，一起保存':'订单提交了，事件却没发出去，怎么办？'}</Heading>
  <Text x={160} y={281} w={1600} size={26} center color={C.gold}>{solution?'另看一种衔接方案 · 本地消息表（Outbox）':'故障边界 · 数据库更新与发消息不是自动的一笔事务'}</Text>
  <Frame x={170} y={365} w={830} h={420} label={solution?'订单服务 · 同一本地事务':'订单服务'} color={C.blue}/>
  <Frame x={215} y={440} w={740} h={110} label="订单状态" color={C.teal}/><Text x={480} y={470} w={430} size={35} color={C.teal}>订单17 · 已付款</Text>
  {solution?<>
   <Frame x={215} y={590} w={740} h={125} label="本地消息表" color={C.gold} alpha={outbox}/>
   <Text x={480} y={622} w={430} size={28} color={C.gold} alpha={outbox}>已付款事件 · 待发送</Text>
  </>:<Text x={215} y={610} w={740} size={33} color={C.red} alpha={gap}>状态已提交，发布事件可能失败</Text>}
  <Frame x={1240} y={425} w={480} h={285} label="消息中间件" color={solution?C.teal:C.red}/>
  <div style={{position:'absolute',left:1440,top:490}}><MiddlewareMark kind="rabbitmq" size={57}/></div>
  <Text x={1270} y={580} w={420} size={31} center color={solution?C.text:C.red}>{solution?'后台发送，失败重试':'事件尚未到达'}</Text>
  <Path points={[[1000,568],[1240,568]]} color={solution?C.gold:C.red} p={solution?outbox:gap} dashed={solution}/>
  {!solution&&gap>.4&&<Text x={1082} y={538} w={70} size={50} center color={C.red}>×</Text>}
  {solution&&<Text x={1025} y={615} w={190} size={23} center color={C.muted} alpha={outbox}>另设发送与重试</Text>}
  <Note color={solution&&delay>.05?C.gold:C.muted}>{solution&&delay>.05?'异步处理仍有延迟：订单已付款，摘要可能暂时还没更新':solution?'同一本地事务保存业务状态和事件，发送过程再处理确认与重试':'MQ 不会自动补上业务提交与事件发布之间的缺口'}</Note>
 </>;
};
const ScopeChoice:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const local=beat(s,f,'local'),mq=beat(s,f,'mq');
 return <>
  <Heading>按部署范围和通知需求，选择合适的机制</Heading>
  <Frame x={150} y={335} w={750} h={455} label="同一程序里的模块联动" color={local>0?C.gold:C.edge}/>
  <Text x={195} y={422} w={660} size={44} color={local>0?C.gold:C.text}>框架事件监听</Text>
  <Text x={195} y={505} w={660} size={31}>界面组件、应用内通知</Text>
  <Text x={195} y={573} w={660} size={28} color={C.muted}>订阅 → 通知 → 各自响应</Text>
  <Text x={195} y={670} w={660} size={28} color={C.teal} alpha={local}>不必为模块联动引入 MQ</Text>
  <Frame x={1020} y={335} w={750} h={455} label="跨服务的一对多异步通知" color={mq>0?C.gold:C.edge}/>
  <div style={{position:'absolute',left:1065,top:433}}><MiddlewareMark kind="rabbitmq" size={47}/></div>
  <Text x={1130} y={422} w={595} size={44} color={mq>0?C.gold:C.text}>MQ 发布订阅</Text>
  <Text x={1065} y={505} w={660} size={31}>独立队列、各自消费</Text>
  <Text x={1065} y={573} w={660} size={28} color={C.muted}>持久化、确认、重试、幂等</Text>
  <Text x={1065} y={670} w={660} size={28} color={C.teal} alpha={mq}>可靠性与一致性需要具体设计</Text>
  <Note>少手写观察者列表，是工程实现方式的选择；事件通知的思想仍在</Note>
 </>;
};
const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const kind=s.visualType;
 if(kind==='product-update'){
  const click=beat(s,f,'click'),state=beat(s,f,'state'),summary=beat(s,f,'summary'),record=beat(s,f,'record');
  return <><Heading>标记一次付款，两个面板怎样联动？</Heading>
   <ProductUI state={completed(state)?'已付款':'待付款'} summaryState={completed(summary)?'已付款':'待付款'} records={completed(record)?['已付款']:[]} buttonActive={click>.6&&!completed(state)} focus={record>0?'record':summary>0?'summary':state>0?'source':undefined}/>
   <Cursor x={lerp(1060,850,click)} y={lerp(730,581,click)} click={click>.8?(click-.8)/.2:0}/>
   <Note>{completed(record)?'一次状态更新后，摘要显示新状态，变化记录留下事实':completed(summary)?'摘要已经显示已付款，变化记录随后留痕':completed(state)?'订单先变为已付款，两个面板随后响应':'商家在订单详情里操作，观察右侧两项功能'}</Note>
  </>;
 }
 if(kind==='observer-brief')return <LocalBrief s={s} f={f}/>;
 if(kind==='mq-practice'){
  const mq=beat(s,f,'mq'),queues=beat(s,f,'queues'),visible=f>=termAt(s,'消息队列');
  return <>
   <Heading>{visible?'消息队列 · MQ：用发布订阅承接跨服务通知':'理解原理后，转向跨服务的实战部署'}</Heading>
   {visible?<MQDiagram alpha={Math.max(.1,mq)} queueAlpha={queues}/>:<>
    <Frame x={135} y={400} w={340} h={310} label="订单服务" color={C.blue}/><Text x={164} y={480} w={282} size={36}>订单17</Text><Text x={164} y={550} w={282} size={38} color={C.teal}>已付款</Text>
    <Service kind="summary"/><Service kind="record"/>
    <Text x={630} y={437} w={730} size={42} center color={C.gold}>独立服务之间，怎样通知？</Text><Text x={660} y={530} w={670} size={30} center color={C.muted}>通常不会手写远程观察者名单</Text>
   </>}
   <Note>{visible?'跨服务部署教学示例：两个业务分别拥有独立的订阅队列':'这里从进程内机制，切换到跨服务教学方案；不是对真实后台架构的推断'}</Note>
  </>;
 }
 if(kind==='publish-route'){
  const publish=beat(s,f,'publish'),route=beat(s,f,'route');
  return <><Heading>订单发布事实，中间件路由到各自的队列</Heading>
   <Text x={170} y={277} w={1590} size={27} center color={C.gold}>事件：订单17 已付款 · 两个业务各收一份</Text>
   <MQDiagram publish={publish} route={route} top={completed(route)?'pending':'empty'} bottom={completed(route)?'pending':'empty'} focus={route>0?'queues':publish>0?'source':undefined}/>
   <Note>{completed(route)?'两份独立待处理事件；不是多个业务竞争同一个队列':route>0?'交换机按订阅绑定，分别路由到摘要队列和记录队列':publish>0?'订单服务发布已经发生的状态变化，不调用接收方的业务方法':'展开同一次订单变化，接下来观察事件如何进入各自队列'}</Note>
  </>;
 }
 if(kind==='independent-consume'){
  const summary=beat(s,f,'summary'),summaryApply=beat(s,f,'summaryApply'),summaryAck=beat(s,f,'summaryAck'),record=beat(s,f,'record'),recordApply=beat(s,f,'recordApply'),recordAck=beat(s,f,'recordAck'),extend=beat(s,f,'extend');
  return <><Heading>{extend>0?'新增订阅方：消费方接入，订单仍发布同一事件':'两个服务各自消费，处理成功后再确认'}</Heading>
   <Text x={170} y={277} w={1590} size={26} center color={C.gold}>{extend>0?'共同事件约定不变时，可新增队列和消费方':'摘要队列给摘要服务；记录队列给记录服务'}</Text>
   <MQDiagram top={completed(summaryAck)?'acked':completed(summary)?'inflight':'pending'} bottom={completed(recordAck)?'acked':completed(record)?'inflight':'pending'} summaryDone={completed(summaryApply)} recordDone={completed(recordApply)} summaryDelivery={summary} recordDelivery={record} summaryAck={summaryAck} recordAck={recordAck} focus="services"/>
   <Note>{extend>0?'生产方仍依赖共同事件约定；无需点名调用新增订阅方':'收到事件 → 完成业务效果 → 发送消费确认，各服务独立推进'}</Note>
  </>;
 }
 if(kind==='offline-backlog'){
  const summary=beat(s,f,'summary'),apply=beat(s,f,'summaryApply'),ack=beat(s,f,'summaryAck'),durable=beat(s,f,'durable');
  return <><Heading>记录服务离线，摘要仍能处理自己的消息</Heading>
   <Text x={170} y={277} w={1590} size={26} center color={C.gold}>另看一次故障 · 回到两份事件刚入队、尚未消费时</Text>
   <MQDiagram top={completed(ack)?'acked':completed(summary)?'inflight':'pending'} bottom="pending" summaryDone={completed(apply)} offline summaryDelivery={summary} summaryAck={ack}/>
   <Note color={durable>0?C.gold:C.muted}>{durable>0?'前提：持久化队列、持久化消息及相应确认策略；MQ 不自动承诺永不丢失':'摘要推进自己的处理，记录事件仍留在独立队列，等待服务恢复'}</Note>
  </>;
 }
 if(kind==='recover-idempotent'){
  const recover=beat(s,f,'recover'),record=beat(s,f,'record'),apply=beat(s,f,'recordApply'),lost=beat(s,f,'lostAck'),disconnect=beat(s,f,'disconnect'),requeue=beat(s,f,'requeue'),redeliver=beat(s,f,'redeliver'),dedup=beat(s,f,'dedup'),ack=beat(s,f,'recordAck'),idempotent=f>=termAt(s,'幂等');
  return <><Heading>{idempotent?'幂等：同一个事件，只产生一次业务效果':redeliver>0?'确认丢失，同一事件可能再次送达':'服务恢复，接着消费记录队列里的积压'}</Heading>
   <Text x={170} y={277} w={1590} size={26} center color={dedup>0?C.gold:C.muted}>{dedup>0?'已处理事件编号 e17-1 → 跳过重复写入 → 再次确认':'承接上一镜故障：摘要已完成，记录队列仍有待处理事件'}</Text>
   <MQDiagram top="acked" bottom={completed(ack)?'acked':requeue>0&&redeliver===0?'pending':completed(record)?'inflight':'pending'} summaryDone recordDone={completed(apply)} offline={!completed(recover)} recordDelivery={record} lostAck={completed(disconnect)?0:lost} redelivery={redeliver} dedup={dedup>0} duplicate={completed(redeliver)} recordAck={ack} eventId/>
   <Note color={dedup>0?C.gold:C.muted}>{completed(ack)?'记录仍只有一条；去重并确认重复消息，不是把同一业务再做一次':dedup>0?'按事件编号识别重复；去重记录与业务写入须原子提交':redeliver>0?'重投递的仍是 e17-1，不能把它当作新的订单变化':requeue>0?'连接断开被检测到，未确认事件重新入队，等待再次投递':disconnect>0?'消费者连接断开；队列检测到断连后，才安排未确认事件重投':lost>0?'业务已完成，但确认没有抵达队列；可能触发重新投递':'服务恢复后处理积压，完成后才尝试发送确认'}</Note>
  </>;
 }
 if(kind==='consistency-boundary')return <Consistency s={s} f={f}/>;
 if(kind==='scope-choice')return <ScopeChoice s={s} f={f}/>;
 if(kind==='practice-recap'){
  const publish=beat(s,f,'publish'),route=beat(s,f,'route'),response=beat(s,f,'response'),reliability=beat(s,f,'reliability');
  return <><Heading>理解观察者思想，掌握消息机制的工程落地</Heading>
   <Text x={170} y={277} w={1590} size={27} center color={reliability>0?C.gold:C.teal}>{reliability>0?'实战重点：投递与确认 · 重复与幂等 · 业务与消息一致性':'来源发生变化 → 发布事件 → 订阅方各自响应'}</Text>
   <MQDiagram top="acked" bottom="acked" summaryDone recordDone focus={completed(response)?undefined:response>0?'services':route>0?'queues':publish>0?'source':undefined}/>
   <Note color={C.teal}>跨服务常用 MQ 发布订阅；同一程序常用框架事件机制</Note>
  </>;
 }
 throw new Error('Unknown observer visual type: '+kind);
};

const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),javaFrom=s.javaCardFrom==null?Infinity:Number(s.javaCardFrom),sub=f<javaFrom?s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1)):undefined;
 if(f>=javaFrom)return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}><JavaCard/></AbsoluteFill>;
 const local=['product-update','observer-brief'].includes(s.visualType),choice=s.visualType==='scope-choice',beforeMQ=s.visualType==='mq-practice'&&f<termAt(s,'消息队列');
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 3%, #173B5544, transparent 62%)'}}/>
  <Text x={130} y={54} w={1450} size={25} color={C.muted}>设计模式 · {s.chapterTitle??'观察者与消息通知'}</Text><Text x={1690} y={54} w={150} size={25}>IT小村</Text>
  <Text x={130} y={108} w={1650} size={23} color={C.blue}>{local?'教学示意 · 同一程序内的原理 · 订单17':choice?'教学示意 · 按部署范围和业务需求选择':beforeMQ?'跨服务教学示例 · 订单17 · 独立服务之间的事件通知':s.visualType==='consistency-boundary'?'跨服务教学示例 · 业务状态与事件发布的一致性':'跨服务教学示例 · 订单17 · RabbitMQ 发布订阅与手动消费确认'}</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:C.bg+'F8',borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
