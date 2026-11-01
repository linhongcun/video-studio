import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill} from 'remotion';
import {C,FONT,MONO} from './theme';
import {Text,Frame,Path,clamp,lerp} from './objects';
export const EXAMPLE={recipient:'buyer17@shop.example',text:'订单17已发货',reference:'Q17'};

export const ProductPanel:React.FC<{state?:'ready'|'submitting'|'accepted';click?:number;replay?:boolean}>=({state='ready',click=0,replay=false})=>{
 const accepted=state==='accepted',submitting=state==='submitting';
 return <>
  <Frame x={180} y={325} w={1560} h={470} label="商家工作台 / 订单详情 · 教学示意，无真实外发" color={C.blue}/>
  <div style={{position:'absolute',left:715,top:405,height:325,width:2,background:C.edge}}/>
  <Text x={235} y={417} w={420} size={30} color={C.muted}>示例订单</Text>
  <Text x={235} y={465} w={420} size={67} weight={750}>订单17</Text>
  <Text x={235} y={562} w={420} size={32} color={C.teal}>订单状态：已发货</Text>
  <Text x={235} y={672} w={420} size={26} color={C.muted}>{replay?'同一次提交 · Q17':'给买家发送发货提醒'}</Text>
  <Text x={785} y={414} w={850} size={26} color={C.muted}>收件人</Text>
  <div style={{position:'absolute',left:785,top:459,width:885,height:66,padding:0,border:'2px solid '+C.edge,borderRadius:9,background:C.surface}}/>
  <Text x={805} y={472} w={845} size={29}>{EXAMPLE.recipient}</Text>
  <Text x={785} y={548} w={850} size={26} color={C.muted}>提醒正文</Text>
  <div style={{position:'absolute',left:785,top:592,width:885,height:66,border:'2px solid '+C.edge,borderRadius:9,background:C.surface}}/>
  <Text x={805} y={604} w={845} size={30}>{EXAMPLE.text}</Text>
  {accepted?<>
   <Text x={785} y={684} w={560} size={32} color={C.teal} weight={750}>已受理</Text>
   <Text x={785} y={733} w={560} size={25} color={C.muted}>等待送达回执 · 受理编号 Q17</Text>
  </>:<Text x={785} y={704} w={560} size={29} color={submitting?C.gold:C.muted}>{submitting?'提交中，等待受理结果':'本次尚未提交'}</Text>}
  <div data-product-submit style={{position:'absolute',left:1380,top:694,width:290,height:65,border:'2px solid '+(accepted?C.edge:C.blue),borderRadius:11,background:accepted?C.surface:C.blue,color:accepted?C.muted:C.bg,display:'flex',alignItems:'center',justifyContent:'center',fontSize:28,fontWeight:750,transform:`scale(${click>.45&&click<.85?.97:1})`}}>{accepted?'已提交':submitting?'提交中':'发送发货提醒'}</div>
  {click>0&&click<1&&<svg width="38" height="48" style={{position:'absolute',left:lerp(1710,1570,Math.min(1,click*2)),top:lerp(805,733,Math.min(1,click*2)),zIndex:5}}><path d="M 3 2 L 3 34 L 12 26 L 20 44 L 28 40 L 20 23 L 33 21 Z" fill={C.text} stroke={C.bg} strokeWidth="3"/></svg>}
 </>;
};

export type RoleFocus='none'|'client'|'target'|'adapter'|'sdk'|'assembly';
export const RoleStructure:React.FC<{adapter?:boolean;focus?:RoleFocus;scope?:boolean}>=({adapter=false,focus='none',scope=false})=>{
 const ink=(v:RoleFocus)=>focus===v?C.gold:C.teal;
 return <>
  <Path points={[[570,648],[620,648],[620,415],[675,415]]} color={focus==='client'||focus==='target'?C.gold:C.edge} dashed/>
  <Text x={200} y={447} w={380} size={24} color={C.muted}>业务依赖自己的通知约定</Text>
  {adapter&&<><Path points={[[960,575],[960,495]]} color={focus==='adapter'||focus==='target'?C.gold:C.teal} dashed/><Text x={990} y={518} w={260} size={23} color={C.muted}>履行目标约定</Text><Path points={[[1170,665],[1350,665]]} color={focus==='adapter'?C.gold:C.edge}/><Text x={1175} y={592} w={170} size={23} center color={C.muted}>持有并调用</Text></>}
  <div data-target-contract style={{position:'absolute',left:675,top:330,width:570,height:165,border:'2px dashed '+ink('target'),borderRadius:17,background:C.surface}}>
   <Text x={24} y={13} w={522} size={28} color={ink('target')}>目标通知约定</Text>
   <Text x={24} y={65} w={522} size={29}>收件人、正文 → 受理结果</Text>
   <Text x={24} y={116} w={522} size={23} color={C.muted}>Target · Notifier</Text>
  </div>
  <Frame x={150} y={575} w={420} h={190} label="业务方" color={ink('client')}/>
  <Text x={178} y={638} w={364} size={29}>发起订单17发货提醒</Text>
  <Text x={178} y={708} w={364} size={22} color={C.muted}>Client · ShipmentReminder</Text>
  {adapter?<><Frame x={750} y={575} w={420} h={190} label="适配器" color={scope?C.gold:ink('adapter')}/><Text x={778} y={638} w={364} size={29}>转换请求和结果</Text><Text x={778} y={708} w={364} size={22} color={C.muted}>Adapter · NotificationAdapter</Text></>:<Text x={750} y={636} w={420} size={32} center color={C.red}>两套使用约定之间的缺口</Text>}
  <Frame x={1350} y={575} w={420} h={190} label="外部通知服务" color={ink('sdk')}/>
  <Text x={1378} y={638} w={364} size={29}>提交通知，返回受理结果</Text>
  <Text x={1378} y={708} w={364} size={22} color={C.muted}>Adaptee · VendorSdk</Text>
 </>;
};

export const RuntimeNodes:React.FC<{focus?:'client'|'adapter'|'sdk';returned?:boolean}>=({focus='client',returned=false})=><>
 {[[150,'业务方','ShipmentReminder','client'],[750,'适配器','NotificationAdapter','adapter'],[1350,'教学模拟服务','VendorSdk','sdk']].map(([x,label,name,key])=><React.Fragment key={String(key)}>
  <Frame x={Number(x)} y={330} w={420} h={150} label={String(label)} color={focus===key?C.gold:C.teal}/><Text x={Number(x)+24} y={406} w={372} size={26} color={C.muted}>{String(name)}</Text>
 </React.Fragment>)}
 <Text x={150} y={503} w={1620} size={24} color={C.muted} center>{returned?'结果原路交回：服务 → 适配器 → 业务方':'请求直接执行：业务方 → 适配器 → 所持有的服务'}</Text>
</>;

export const MessageCard:React.FC<{x:number;kind:'business'|'service';active?:boolean;alpha?:number}>=({x,kind,active=false,alpha=1})=><div style={{opacity:alpha}}>
 <Frame x={x} y={565} w={660} h={220} label={kind==='business'?'业务请求':'服务接受的请求'} color={active?C.gold:C.edge}/>
 <Text x={x+26} y={635} w={608} size={27} color={C.muted}>{kind==='business'?'收件人':'接收目标'} <span style={{color:C.text}}>{EXAMPLE.recipient}</span></Text>
 <Text x={x+26} y={702} w={608} size={31} color={C.muted}>{kind==='business'?'提醒正文':'消息内容'} <span style={{color:C.text}}>{EXAMPLE.text}</span></Text>
</div>;

export const ReceiptCard:React.FC<{x:number;kind:'service'|'business';alpha?:number;active?:boolean}>=({x,kind,alpha=1,active=false})=><div style={{opacity:alpha}}>
 <Frame x={x} y={565} w={660} h={220} label={kind==='service'?'模拟服务返回的结果':'业务方需要的结果'} color={active?C.gold:C.edge}/>
 <Text x={x+26} y={634} w={608} size={43} color={kind==='service'?C.blue:C.teal}>{kind==='service'?'已排队':'已受理'}</Text>
 <Text x={x+26} y={710} w={608} size={29} color={C.muted}>受理编号 <span style={{color:C.gold}}>Q17</span></Text>
</div>;

export const Passing:React.FC<{from:[number,number];to:[number,number];p:number;label?:string;reverse?:boolean}>=({from,to,p,label,reverse=false})=>{
 const x=lerp(from[0],to[0],p),y=lerp(from[1],to[1],p);
 return <><Path points={[from,to]} p={p} color={C.gold}/>{p>0&&p<1&&<div style={{position:'absolute',left:x-10,top:y-10,width:20,height:20,background:C.gold,border:'3px solid '+C.bg,borderRadius:20}}/>}{label&&<Text x={Math.min(from[0],to[0])-35} y={from[1]-54} w={Math.abs(to[0]-from[0])+70} size={25} center color={C.gold} alpha={p>0?1:0}>{label}</Text>}</>;
};

export const JavaCodeCard:React.FC<{card:{title?:string;subtitle?:string;lines:string[]}}>=({card})=>{
 const ref=useRef<HTMLPreElement>(null);
 useLayoutEffect(()=>{const e=ref.current;if(e&&(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2))console.error('COPYFIT Java key-code card',e.scrollWidth,e.clientWidth,e.scrollHeight,e.clientHeight);},[]);
 return <AbsoluteFill data-java-card style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <Text x={130} y={55} w={1400} size={25} color={C.muted}>设计模式 · 适配器模式 · 教学SDK无真实外发</Text><Text x={1690} y={55} w={150} size={25}>IT小村</Text>
  <Text x={130} y={124} w={1660} size={47} weight={750}>{card.title??'Java关键代码 · 节选'} <span style={{color:C.gold}}> · {card.subtitle??'暂停查看'}</span></Text>
  <pre ref={ref} style={{position:'absolute',left:150,top:217,width:1620,height:750,margin:0,padding:'15px 22px',borderLeft:'3px solid '+C.teal,background:C.surface,fontFamily:MONO,fontSize:30,lineHeight:1.4,whiteSpace:'pre',boxSizing:'border-box'}}>{card.lines.join('\n')}</pre>
  <Text x={150} y={1000} w={1620} size={25} color={C.muted} center>同一次提醒 · Q17 · 已受理不等于已送达</Text>
 </AbsoluteFill>;
};

export const BusinessBenefits:React.FC<{second?:boolean}>=({second=false})=><>
 <Frame x={180} y={350} w={720} h={425} label="先按业务需要定义用法" color={!second?C.gold:C.teal}/>
 <Text x={220} y={433} w={640} size={46} weight={750} color={C.teal}>业务自己定约定</Text>
 <Text x={220} y={527} w={640} size={34}>{'用收件人和正文提交\n取得统一的受理结果'}</Text>
 <Text x={220} y={699} w={640} size={27} color={C.muted}>发货提醒按自己的需要使用</Text>
 <Frame x={1020} y={350} w={720} h={425} label="外部接口细节留在接入处" color={second?C.gold:C.teal}/>
 <Text x={1060} y={433} w={640} size={46} weight={750} color={C.teal}>升级少牵动业务</Text>
 <Text x={1060} y={527} w={640} size={34}>{'请求与回执的格式差异\n集中在接入处转换'}</Text>
 <Text x={1060} y={699} w={640} size={27} color={C.muted}>业务与服务按各自方式演进</Text>
</>;

export const UpgradeBoundary:React.FC<{requestV2?:boolean;requestChanging?:boolean;receiptV2?:boolean;receiptProgress?:number;requestUpdated?:boolean;receiptUpdated?:boolean;assemblyUpdated?:boolean;stable?:boolean}>=({requestV2=false,requestChanging=false,receiptV2=false,receiptProgress=0,requestUpdated=false,receiptUpdated=false,assemblyUpdated=false,stable=false})=>{
 const changed=requestUpdated||receiptUpdated,pack=receiptV2?1:receiptProgress;
 return <>
  <Frame x={130} y={330} w={500} h={450} label="业务约定和发货流程" color={C.teal}/>
  <Text x={160} y={411} w={440} size={31} color={C.teal}>收件人 + 提醒正文</Text>
  <Text x={160} y={479} w={440} size={26}>{EXAMPLE.recipient}</Text>
  <Text x={160} y={531} w={440} size={32}>{EXAMPLE.text}</Text>
  <div style={{position:'absolute',left:160,top:608,width:440,height:2,background:C.edge}}/>
  <Text x={160} y={644} w={440} size={31} color={C.teal}>受理结果：已受理 · Q17</Text>
  <Text x={160} y={720} w={440} size={22} color={C.muted}>Notifier · ShipmentReminder</Text>
  <Frame x={710} y={330} w={500} h={450} label="接入处集中处理变化" color={changed?C.gold:C.edge}/>
  <Text x={740} y={421} w={440} size={31} color={requestUpdated?C.gold:C.muted}>请求转换：{requestUpdated?'已更新':requestV2?'需要调整':'原有映射'}</Text>
  <Text x={740} y={514} w={440} size={31} color={receiptUpdated?C.gold:C.muted}>回执转换：{receiptUpdated?'已更新':receiptV2?'需要调整':'原有映射'}</Text>
  <Text x={740} y={624} w={440} size={29} color={assemblyUpdated?C.gold:C.muted}>{assemblyUpdated?'创建与接线：改接V2服务':'由接入处连接外部服务'}</Text>
  <Text x={740} y={720} w={440} size={22} color={C.muted}>{changed?'NotificationAdapterV2':'NotificationAdapter'}</Text>
  <Frame x={1290} y={330} w={500} h={450} label={'外部通知服务 · '+(requestV2||receiptV2?'V2':'V1')} color={C.blue}/>
  <div style={{position:'absolute',left:1320,top:408,width:440,height:130,border:'2px solid '+(requestV2?C.gold:C.edge),borderRadius:12,background:C.surface}}/>
  <Text x={1340} y={423} w={400} size={25} color={C.muted}>请求格式{requestV2?'已变化':''}</Text>
  <Text x={1340} y={476} w={400} size={26} mono color={requestV2?C.gold:C.text}>{requestChanging?'请求格式调整中':requestV2?'destination / content':'target / body'}</Text>
  <div style={{position:'absolute',left:1320,top:572,width:440,height:176,border:'2px solid '+(receiptV2?C.gold:C.edge),borderRadius:12,background:C.surface}}/>
  <Text x={1340} y={586} w={400} size={25} color={C.muted}>{pack>0?'返回多了一层包装':'返回结果'}</Text>
  {pack>0&&<div style={{opacity:pack,position:'absolute',left:1340,top:634,width:400,height:98,border:'2px solid '+C.blue,borderRadius:9,background:C.bg}}/>}
  <Text x={1360} y={635+9*pack} w={360} size={30} color={C.blue}>已排队 · Q17</Text>
  <Text x={1360} y={698} w={360} size={22} mono color={receiptV2?C.gold:C.muted}>{receiptV2?'ENQUEUED / reference':'QUEUED / ticket'}</Text>
  {stable&&<Text x={160} y={270} w={1050} size={27} color={C.teal}>本例业务需要不变：左侧保持，外部变化在接入处处理</Text>}
 </>;
};
