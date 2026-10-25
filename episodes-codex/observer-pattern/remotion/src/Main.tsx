import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots,Shot} from './data';
import javaCard from './java-card.json';
import {C,FONT} from './theme';
import {at,beat} from './motion';
import {Heading,Note,Text,Frame,Path,clamp,lerp} from './objects';
import {createMiddlewareIdentity} from '../../../_shared/middleware-identity';
const MiddlewareMark=createMiddlewareIdentity(React);
declare const __HAS_VOICE_AUDIO__:boolean;
type State='待付款'|'已付款'|'已发货';
type Focus='source'|'list'|'summary'|'record'|'contract';
const SummaryPath:[number,number][]=[[1090,490],[1320,490]];
const RecordPath:[number,number][]=[[1090,700],[1320,700]];
const reverse=(a:[number,number][])=>[...a].reverse() as [number,number][];
const termAt=(s:Shot,key:string)=>Number(s.cueFrames?.labels?.[key]??0);

const Notification:React.FC<{points:[number,number][];p:number;state?:State;text?:string;registration?:boolean}>=({points,p,state='已付款',text,registration=false})=>{
 const w=registration?140:154,direction=Math.sign(points[1][0]-points[0][0]),inset=w/2+1;
 const x=lerp(points[0][0]+direction*inset,points[1][0]-direction*inset,clamp(p)),y=lerp(points[0][1],points[1][1],clamp(p));
 const alpha=1-clamp((p-.92)/.08),color=registration?C.blue:C.gold;
 return <><Path points={points} p={p} color={color}/><div style={{position:'absolute',left:x-w/2,top:y-24,width:w,height:48,border:'2px solid '+color,borderRadius:9,background:C.bg,opacity:alpha,boxSizing:'border-box'}}><Text x={6} y={3} w={w-12} size={registration?24:23} center color={color}>{text??('17 · '+state)}</Text></div></>;
};
const Contract:React.FC<{alpha?:number;active?:boolean}>=({alpha=1,active=false})=><Text x={170} y={284} w={1590} size={28} center color={active?C.gold:C.teal} alpha={alpha}>共同通知约定：订单号 ＋ 新状态</Text>;
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
const Source:React.FC<{state?:State;summaryMember?:boolean;recordMember?:boolean;direct?:boolean;focus?:Focus;alpha?:number;empty?:boolean;cost?:boolean}>=({state='待付款',summaryMember=true,recordMember=true,direct=false,focus,alpha=1,empty=false,cost=false})=><div style={{opacity:alpha}}>
 <Frame x={150} y={350} w={940} h={440} label={direct?'订单处理':'订单来源'} color={focus==='source'?C.gold:C.edge}/>
 <Text x={195} y={430} w={390} size={35} color={C.blue} weight={700}>订单17</Text>
 <Text x={195} y={494} w={390} size={27} color={C.muted}>当前状态</Text>
 <Text x={195} y={544} w={390} size={51} color={focus==='source'?C.gold:C.text} weight={750}>{state}</Text>
 <div style={{position:'absolute',left:625,top:407,width:2,height:331,background:focus==='list'?C.gold:C.edge}}/>
 <Text x={666} y={389} w={370} size={28} color={focus==='list'?C.gold:C.muted}>{direct?'内部点名通知安排':'当前接收者'}</Text>
 {[['summary','订单摘要',summaryMember,454],['record','变化记录',recordMember,664]].map(([key,name,member,y])=><div key={String(key)} style={{position:'absolute',left:666,top:Number(y),width:375,height:74,borderLeft:'4px solid '+(member&&!empty?(focus==='list'?C.gold:C.teal):C.edge),background:member&&!empty?C.surface:'transparent'}}>
  <Text x={20} y={12} w={335} size={33} color={member&&!empty?(focus==='list'?C.gold:C.text):C.muted}>{member&&!empty?(direct?'通知'+(key==='summary'?'摘要':'记录'):String(name)):'—'}</Text>
 </div>)}
 {cost&&<Text x={195} y={679} w={390} size={24} color={C.gold}>仍需维护接收关系</Text>}
</div>;
const Diagram:React.FC<{state?:State;summaryState?:State;recordStates?:State[];summaryMember?:boolean;recordMember?:boolean;direct?:boolean;focus?:Focus;stopped?:boolean;contract?:boolean;empty?:boolean;goal?:boolean;cost?:boolean;showPaths?:boolean}>=({state='待付款',summaryState='待付款',recordStates=[],summaryMember=true,recordMember=true,direct=false,focus,stopped=false,contract=true,empty=false,goal=false,cost=false,showPaths=true})=><>
 {showPaths&&!empty&&<>{summaryMember&&<Path points={SummaryPath} color={focus==='summary'?C.gold:C.edge}/>} {recordMember&&<Path points={RecordPath} color={focus==='record'?C.gold:C.edge}/>}</>}
 <Source state={state} summaryMember={summaryMember} recordMember={recordMember} direct={direct} focus={focus} empty={empty} cost={cost}/>
 <Receiver kind="summary" summaryState={summaryState} stopped={stopped} active={focus==='summary'} goal={goal}/>
 <Receiver kind="record" recordStates={recordStates} active={focus==='record'} goal={goal}/>
 {contract&&<Contract active={focus==='contract'}/>}
</>;
const PaidDiagram:React.FC<{focus?:Focus;stopped?:boolean;summaryMember?:boolean;state?:State;recordStates?:State[];cost?:boolean}>=({focus,stopped=false,summaryMember=true,state='已付款',recordStates=['已付款'],cost=false})=><Diagram state={state} summaryState="已付款" recordStates={recordStates} focus={focus} stopped={stopped} summaryMember={summaryMember} cost={cost}/>;

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
const RoleStructure:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const spread=beat(s,f,'expand'),source=beat(s,f,'source'),summary=beat(s,f,'summary'),record=beat(s,f,'record'),contract=beat(s,f,'contract'),active=contract>.15;
 return <>
  <Frame x={150} y={350} w={lerp(940,620,spread)} h={440} label={spread<.5?'商家 · 订单详情':'订单来源 · Order'} color={source>0&&contract===0?C.gold:C.blue}/>
  <Text x={192} y={425} w={500} size={38} color={C.blue} weight={700}>订单17 · 已付款</Text>
  <Text x={192} y={505} w={500} size={31} color={C.text} alpha={source}>维护状态</Text>
  <Text x={192} y={564} w={500} size={31} color={C.text} alpha={source}>保留接收者名单</Text>
  <Text x={192} y={623} w={500} size={31} color={C.text} alpha={source}>状态变化后，按约定通知</Text>
  <Receiver kind="summary" summaryState="已付款" active={summary>0&&record===0&&contract===0}/><Receiver kind="record" recordStates={['已付款']} active={record>0&&contract===0}/>
  <Text x={1346} y={522} w={398} size={22} color={C.blue} alpha={summary}>具体观察者 · SummaryObserver</Text>
  <Text x={1346} y={745} w={398} size={22} color={C.blue} alpha={record}>具体观察者 · ChangeLogObserver</Text>
  {contract>0&&<>
   <Path points={[[770,477],[850,477]]} color={C.blue} alpha={contract}/>
   <Path points={[[1320,490],[1240,490],[1240,477],[1190,477]]} color={C.teal} alpha={contract} dashed/>
   <Path points={[[1320,700],[1240,700],[1240,540],[1190,540]]} color={C.teal} alpha={contract} dashed/>
   <Frame x={850} y={395} w={340} h={216} label="共同观察者约定" color={active?C.gold:C.edge} alpha={contract}/>
   <Text x={874} y={456} w={292} size={26} center mono color={C.blue} alpha={contract}>OrderObserver</Text>
   <Text x={874} y={507} w={292} size={28} center color={C.text} alpha={contract}>接收订单号与新状态</Text>
   <Text x={855} y={639} w={340} size={23} center color={C.muted} alpha={contract}>结构约定，非消息中转</Text>
  </>}
  <Note>{active?'来源按共同约定通知，摘要与记录分别承担显示与留痕':record>0?'同一变化记录，对应负责留痕的具体观察者':summary>0?'同一摘要面板，对应负责显示的具体观察者':'从刚才的产品对象展开职责，当前仍是已付款结果'}</Note>
 </>;
};
const JavaCard:React.FC=()=>{
 const lines=(javaCard as any).lines as string[];
 const size=Math.min(30,Math.floor(742/(lines.length*1.4)));
 return <>
  <Text x={130} y={54} w={1660} size={44} weight={750}>{(javaCard as any).title??'观察者模式 · Java关键关系'}</Text>
  <Text x={130} y={124} w={1660} size={27} color={C.gold}>暂停阅读 · 观察者模式的关键角色与使用 · Java节选</Text>
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

const WhyObserver:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const cost=beat(s,f,'cost'),separate=beat(s,f,'separate'),receivers=beat(s,f,'receivers'),named=f>=termAt(s,'观察者模式');
 return <>
  <Heading>{named?'观察者模式：把来源变化与各方响应分开':'接收方常变化，为什么不全写进订单？'}</Heading>
  <Text x={170} y={282} w={1590} size={27} center color={C.gold}>职责关系说明 · 保留刚才的已付款结果</Text>
  <Path points={SummaryPath} color={separate>0?C.teal:C.edge}/><Path points={RecordPath} color={separate>0?C.teal:C.edge}/>
  <Frame x={150} y={350} w={940} h={440} label={separate>.5?'订单来源：状态与通知':'订单流程：嵌入各方处理细节'} color={cost>0&&separate===0?C.gold:C.blue}/>
  <Text x={195} y={430} w={390} size={35} color={C.blue} weight={700}>订单17</Text>
  <Text x={195} y={494} w={390} size={27} color={C.muted}>当前状态</Text>
  <Text x={195} y={544} w={390} size={51} weight={750}>已付款</Text>
  <div style={{position:'absolute',left:625,top:407,width:2,height:331,background:C.edge}}/>
  <Text x={666} y={402} w={370} size={27} color={separate>.5?C.teal:C.gold}>{separate>.5?'按共同约定通知':'接收需求变化，会牵动这里'}</Text>
  <Text x={666} y={490} w={370} size={31} color={separate>.5?C.text:C.gold}>{separate>.5?'各方先登记接收意愿':'摘要怎样显示'}</Text>
  <Text x={666} y={590} w={370} size={31} color={separate>.5?C.text:C.gold}>{separate>.5?'不掌握各方的处理细节':'记录怎样追加'}</Text>
  <Receiver kind="summary" summaryState="已付款" active={receivers>0&&receivers<.5}/><Receiver kind="record" recordStates={['已付款']} active={receivers>=.5}/>
  <Note>{separate>0?'来源负责变化与通知；观察者登记意愿，自己处理响应':'接收需求一变，订单流程里嵌入的显示与记录细节也要跟着改'}</Note>
 </>;
};
const Application:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const publish=beat(s,f,'publish'),subscribe=beat(s,f,'subscribe'),responses=beat(s,f,'responses');
 return <>
  <Heading>实战一例：借助 MQ 发布订阅，延续通知思想</Heading>
  <Text x={170} y={281} w={1590} size={26} center color={C.gold}>应用映射 · 不是前面原理例子的继续执行</Text>
  <Path points={[[650,545],[800,545]]} color={publish>0?C.gold:C.edge}/>
  <Path points={[[1130,500],[1240,500],[1240,445],[1340,445]]} color={subscribe>0?C.gold:C.edge}/>
  <Path points={[[1130,590],[1240,590],[1240,695],[1340,695]]} color={subscribe>0?C.gold:C.edge}/>
  <Frame x={170} y={370} w={480} h={360} label="订单服务 · 对应来源" color={publish>0?C.gold:C.blue}/>
  <Text x={210} y={455} w={400} size={36} weight={750}>订单17 · 已发货</Text>
  <Text x={210} y={541} w={400} size={31} color={C.teal}>发布变化事件</Text>
  <Text x={210} y={624} w={400} size={26} color={C.muted}>不写入各订阅方的处理细节</Text>
  <Frame x={800} y={430} w={330} h={230} label="MQ · 发布订阅" color={C.teal}/>
  <div style={{position:'absolute',left:940,top:492}}><MiddlewareMark kind="rabbitmq" size={48}/></div>
  <Text x={825} y={568} w={280} size={25} center color={C.muted}>RabbitMQ 实现示例</Text>
  <Frame x={1340} y={350} w={430} h={200} label="摘要订阅方" color={responses>0?C.gold:C.teal}/>
  <Text x={1370} y={426} w={370} size={36} color={C.text}>负责显示状态</Text>
  <Text x={1370} y={493} w={370} size={25} color={C.muted}>收到后自己响应</Text>
  <Frame x={1340} y={610} w={430} h={200} label="记录订阅方" color={responses>0?C.gold:C.teal}/>
  <Text x={1370} y={686} w={370} size={36} color={C.text}>负责追加变化事实</Text>
  <Text x={1370} y={753} w={370} size={25} color={C.muted}>各业务独立订阅</Text>
  <Note>实现借助已有机制，核心仍是：来源发出变化，订阅方各自响应</Note>
 </>;
};
const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const kind=s.visualType;
 if(kind==='product-update'){
  const click=beat(s,f,'click'),state=beat(s,f,'state'),summary=beat(s,f,'summary'),record=beat(s,f,'record');
  return <><Heading>标记一次付款，两个面板怎样联动？</Heading>
   <ProductUI state={state>=.99?'已付款':'待付款'} summaryState={summary>=.99?'已付款':'待付款'} records={record>=.99?['已付款']:[]} buttonActive={click>.6&&state<.99} focus={record>0?'record':summary>0?'summary':state>0?'source':undefined}/>
   <Cursor x={lerp(1060,850,click)} y={lerp(730,581,click)} click={click>.8?(click-.8)/.2:0}/>
   <Note>{record>=.99?'一次状态更新后，摘要显示新状态，变化记录留下事实':summary>=.99?'摘要已经显示已付款，变化记录随后留痕':state>=.99?'订单先变为已付款，两个面板随后响应':'商家在订单详情里操作，观察右侧两项功能'}</Note>
  </>;
 }
 if(kind==='why-observer')return <WhyObserver s={s} f={f}/>;
 if(kind==='observer-roles'){
  return <><Heading>从同一产品对象，展开观察者结构</Heading><RoleStructure s={s} f={f}/></>;
 }
 if(kind==='register-interest'){
  const p=beat(s,f,'summary'),q=beat(s,f,'record'),before=f<termAt(s,'订阅'),registration=!before;
  return <><Heading>{before?'从当前结果，准备回看付款前':'订阅：接收方登记意愿，来源保留当前名单'}</Heading>
   {before?<PaidDiagram/>:<Diagram contract={false} summaryMember={p>=.99} recordMember={q>=.99} showPaths={false}/>}
   {!before&&<Text x={170} y={278} w={1590} size={29} center color={C.gold}>回看 · 本次付款前 · 初始名单为空</Text>}
   {registration&&p>.0&&p<.99&&<Notification points={reverse(SummaryPath)} p={p} text="摘要登记" registration/>}
   {registration&&q>.0&&q<.99&&<Notification points={reverse(RecordPath)} p={q} text="记录登记" registration/>}
   <Note>{before?'承接刚才的已付款与一条记录，接下来回看登记的前置安排':q>=.99?'两项都已登记；订单状态尚未变化':'先回看付款前的空名单，接收方登记抵达后才加入'}</Note>
  </>;
 }
 if(kind==='notify-and-react'){
  const state=beat(s,f,'state'),dispatch=beat(s,f,'dispatch'),summary=beat(s,f,'summary'),summaryResponse=beat(s,f,'summaryResponse'),record=beat(s,f,'record'),recordResponse=beat(s,f,'recordResponse'),responses=beat(s,f,'responses');
  const summaryProgress=f<at(s,1,0)?dispatch*.45:.45+.55*summary;
  return <><Heading>先更新来源，再通知当前观察者，各自响应</Heading>
   <Diagram state={state>=.99?'已付款':'待付款'} summaryState={summaryResponse>=.99?'已付款':'待付款'} recordStates={recordResponse>=.99?['已付款']:[]} focus={record>0?'record':summary>0?'summary':dispatch>0?'list':state>0?'source':undefined}/>
   {dispatch>0&&summaryProgress<.99&&<Notification points={SummaryPath} p={summaryProgress}/>}
   {record>0&&record<.99&&<Notification points={RecordPath} p={record}/>}
   <Note>{responses>0?'本例依次通知；来源不掌握显示和留痕细节，不是模式统一规定顺序':recordResponse>=.99?'记录保留唯一一条已付款事实，各方完成自己的响应':record>0?'摘要处理后，再把同一事实通知变化记录':summaryResponse>=.99?'摘要收到后更新显示，接下来通知变化记录':summary>=.99?'通知已抵达摘要，摘要随后更新自己的显示':dispatch>0?'发出订单号与新状态；接收者收到前不先更新':state>=.99?'来源先采用已付款，再向当前接收者发出事实通知':'承接已建立的订阅关系，回放同一次付款的通知过程'}</Note>
  </>;
 }
 if(kind==='unsubscribe-summary'){
  const close=beat(s,f,'close'),p=beat(s,f,'cancel'),stopped=p>=.99;
  return <><Heading>{f<termAt(s,'取消订阅')?'关闭已不需要的摘要面板，让它退出':'取消订阅：摘要退出名单，变化记录仍然保留'}</Heading>
   <ProductUI state="已付款" summaryState="已付款" records={['已付款']} stopped={stopped} showInternalList={f>=termAt(s,'取消订阅')} closeActive={close>.7&&!stopped}/>
   {close<.99&&<Cursor x={lerp(1600,1712,close)} y={lerp(593,383,close)} click={close>.8?(close-.8)/.2:0}/>}
   <Note>{stopped?'摘要保留最后收到的已付款，已关闭并停止接收，记录继续保留':p>0?'关闭摘要后，将它从当前接收者名单移除':'先回到同一产品页，再关闭不需要继续查看的摘要'}</Note>
  </>;
 }
 if(kind==='notify-remaining'){
  const p=beat(s,f,'state'),q=beat(s,f,'notify'),response=beat(s,f,'response');
  return <><Heading>同一订单变为已发货，只通知当前名单</Heading>
   <PaidDiagram state={p>=.99?'已发货':'已付款'} stopped summaryMember={false} recordStates={response>=.99?['已付款','已发货']:['已付款']} focus={response>0?'record':q>0?'list':p>0?'source':undefined}/>
   {q>0&&q<.99&&<Notification points={RecordPath} p={q} state="已发货"/>}
   <Note>{response>=.99?'记录保留两次变化；摘要没有收到已发货，旧值不再刷新':q>0?'当前名单仅有变化记录，摘要路径不发送消息':'订单先更新状态；退出的摘要保持停止接收'}</Note>
  </>;
 }
 if(kind==='benefits-and-cost'){
  const review=beat(s,f,'review'),contract=beat(s,f,'contract'),lifecycle=beat(s,f,'lifecycle'),direct=beat(s,f,'direct');
  const focus:Focus|undefined=direct>0?undefined:lifecycle>0?'list':contract>0?'contract':review>.5?'record':'list';
  return <><Heading>{f<at(s,1,0)?'增减接收关系，各方维护自己的响应':'共同约定与订阅生命周期，仍要维护'}</Heading>
   <PaidDiagram state="已发货" stopped summaryMember={false} recordStates={['已付款','已发货']} focus={focus} cost={lifecycle>0&&direct===0}/>
   <Note color={direct>0?C.gold:C.muted}>{direct>0?'简单、长期固定的联系，也可以直接调用；按维护成本选择':lifecycle>0?'接收方不用时及时取消，来源仍需要维护接收关系':contract>0?'前提是共同通知约定不变；不是完全没有依赖':'第一次：摘要与记录都收到；第二次：退出的摘要没有再收到'}</Note>
  </>;
 }
 if(kind==='mq-application')return <Application s={s} f={f}/>;
 if(kind==='observer-recap'){
  const source=beat(s,f,'source'),responses=beat(s,f,'responses'),relation=beat(s,f,'relation');
  return <><Heading>来源负责变化与通知，观察者负责各自响应</Heading>
   <PaidDiagram state="已发货" stopped summaryMember={false} recordStates={['已付款','已发货']} focus={relation>0?'list':responses>0?'record':source>0?'source':undefined}/>
   <Note color={C.teal}>{relation>0?'用可增减的订阅关系，连接变化来源与各个观察者':'回到原例：同一订单已发货，摘要已退出，变化记录保留两次事实'}</Note>
   <Text x={640} y={882} w={640} size={23} center color={C.muted}>IT小村 · 原创</Text>
  </>;
 }
 throw new Error('Unknown observer visual type: '+kind);
};

const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),javaFrom=s.javaCardFrom==null?Infinity:Number(s.javaCardFrom),sub=f<javaFrom?s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1)):undefined;
 if(f>=javaFrom)return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}><JavaCard/></AbsoluteFill>;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 3%, #173B5544, transparent 62%)'}}/>
  <Text x={130} y={54} w={1450} size={25} color={C.muted}>设计模式 · {s.visualType==='register-interest'&&f<termAt(s,'订阅')?'建立接收关系':s.visualType==='unsubscribe-summary'&&f<termAt(s,'取消订阅')?'摘要怎样退出':s.chapterTitle??'变化与响应'}</Text><Text x={1690} y={54} w={150} size={25}>IT小村</Text>
  <Text x={130} y={108} w={1650} size={23} color={C.blue}>{s.visualType==='mq-application'?'实战应用映射 · 跨服务发布订阅 · 不是原例的继续执行':s.visualType==='observer-recap'?'观察者模式 · 回到同一程序内的原例 · 订单17':'教学示意 · 同一程序内 · 订单17'}</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:39,fontWeight:500,lineHeight:1.4,textAlign:'center',background:C.bg+'F8',borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
