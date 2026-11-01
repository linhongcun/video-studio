import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT,MONO} from './theme';
import {shots,Shot,PREVOICE} from './data';
import modelSource from '../../model.json';
import {createMiddlewareIdentity} from '../../../../../_shared/middleware-identity';
declare const __HAS_VOICE_AUDIO__:boolean;
const KafkaMark=createMiddlewareIdentity(React);
const M=modelSource as any;
export const modelState=(id:string)=>{const v=M.timeline.find((x:any)=>x.id===id);if(!v)throw Error('Missing model state '+id);return v;};
const IDS=['B1','B2','B3'];
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const tween=(f:number,a:number,b:number)=>{const t=clamp((f-a)/Math.max(1,b-a));return t*t*(3-2*t);};
type Step={at:number;id:string};
type Flight={from:string;to:string;start:number;end:number;kind:'request'|'record-copy'|'report'|'success'|'failure';label:string};
export function sceneTiming(s:Shot){
 const d=s.durationInFrames,a=s.voice?.[0]?.localStart??15,b=s.voice?.[0]?.localEnd??d*.43,c=s.voice?.[1]?.localStart??d*.51,e=s.voice?.[1]?.localEnd??d-35;
 const early=(p:number)=>a+(b-a)*p,late=(p:number)=>c+(e-c)*p,n=Number(s.id);
 const st=(at:number,id:string):Step=>({at,id});let steps:Step[]=[];let flights:Flight[]=[];
 if(n===1||n===2)steps=[st(0,'acks1-initial')];
 if(n===3){const sent=early(.25),appended=late(.17),response=late(.53),success=late(.83);steps=[st(0,'acks1-initial'),st(sent,'acks1-sent'),st(appended,'acks1-appended'),st(response,'acks1-response'),st(success,'acks1-success')];flights=[{from:'B1',to:'website',start:response,end:success,kind:'success',label:'成功响应'}];}
 if(n===4)steps=[st(0,'acks1-success'),st(early(.40),'acks1-leader-down'),st(late(.42),'acks1-takeover-missing')];
 if(n===5)steps=[st(0,'all3-initial')];
 if(n===6)steps=[st(0,'all3-initial'),st(early(.12),'all3-sent'),st(early(.48),'all3-admitted'),st(early(.79),'all3-appended')];
 if(n===7){const request=early(.12),copy=early(.62),append=late(.52);steps=[st(0,'all3-appended'),st(request,'all3-b2-fetch0'),st(copy,'all3-b2-copy'),st(append,'all3-b2-appended')];flights=[{from:'B2',to:'B1',start:request,end:copy-5,kind:'request',label:'B2 → B1：Fetch(P0, 0)'},{from:'B1',to:'B2',start:copy,end:append,kind:'record-copy',label:'B1 → B2：E01 @ offset 0 的副本'}];}
 if(n===8){const request=early(.18),report=early(.70);steps=[st(0,'all3-b2-appended'),st(report,'all3-b2-reported'),st(late(.25),'all3-wait-third')];flights=[{from:'B2',to:'B1',start:request,end:report,kind:'report',label:'B2 → B1：下一次 Fetch(P0, 1) 报告进度'}];}
 if(n===9){const request=early(.08),copy=early(.34),append=early(.67),reportStart=late(.02),report=late(.29),response=late(.56),success=late(.84);steps=[st(0,'all3-wait-third'),st(request,'all3-b3-fetch0'),st(copy,'all3-b3-copy'),st(append,'all3-b3-appended'),st(report,'all3-hw-ready'),st(response,'all3-response'),st(success,'all3-success')];flights=[{from:'B3',to:'B1',start:request,end:copy-3,kind:'request',label:'B3 → B1：Fetch(P0, 0)'},{from:'B1',to:'B3',start:copy,end:append,kind:'record-copy',label:'B1 → B3：E01 @ offset 0 的副本'},{from:'B3',to:'B1',start:reportStart,end:report,kind:'report',label:'B3 → B1：下一次 Fetch(P0, 1) 报告进度'},{from:'B1',to:'website',start:response,end:success,kind:'success',label:'成功响应'}];}
 if(n===10)steps=[st(0,'all3-settled'),st(early(.50),'all3-leader-down'),st(late(.43),'all3-takeover-retained')];
 if(n===11){const request=late(.17),copy=late(.32),append=late(.47),reportStart=late(.49),report=late(.66),response=late(.78),success=late(.91);steps=[st(0,'all2-initial'),st(early(.17),'all2-sent'),st(early(.66),'all2-admitted'),st(late(.04),'all2-appended'),st(request,'all2-b2-fetch0'),st(copy,'all2-b2-copy'),st(append,'all2-b2-appended'),st(report,'all2-hw-ready'),st(response,'all2-response'),st(success,'all2-success')];flights=[{from:'B2',to:'B1',start:request,end:copy-2,kind:'request',label:'B2 → B1：Fetch(P0, 0)'},{from:'B1',to:'B2',start:copy,end:append,kind:'record-copy',label:'B1 → B2：E01 @ offset 0 的副本'},{from:'B2',to:'B1',start:reportStart,end:report,kind:'report',label:'B2 → B1：Fetch(P0, 1)'},{from:'B1',to:'website',start:response,end:success,kind:'success',label:'成功响应'}];}
 if(n===12){const response=late(.25),failed=late(.68);steps=[st(0,'all1-initial'),st(early(.72),'all1-sent'),st(response,'all1-response'),st(failed,'all1-rejected')];flights=[{from:'B1',to:'website',start:response,end:failed,kind:'failure',label:'拒绝响应'}];}
 if(n===13)steps=[];
 return {a,b,c,e,steps,flights};
}
export function stateAt(s:Shot,f:number){const t=sceneTiming(s);return [...t.steps].reverse().find(q=>f>=q.at)?.id??null;}
type TextProps={x:number;y:number;w:number;size?:number;color?:string;align?:'left'|'center'|'right';alpha?:number;mono?:boolean;children:React.ReactNode};
const T:React.FC<TextProps>=({x,y,w,size=27,color=C.text,align='left',alpha=1,mono=false,children})=>{
 const ref=useRef<HTMLDivElement>(null);useLayoutEffect(()=>{const el=ref.current;if(el&&alpha>.1&&el.scrollWidth>el.clientWidth+2)console.error('COPYFIT',el.textContent,el.scrollWidth,el.clientWidth);});
 return <div ref={ref} data-text data-copyfit style={{position:'absolute',left:x,top:y,width:w,fontSize:size,lineHeight:1.35,fontWeight:600,color,opacity:alpha,textAlign:align,fontFamily:mono?MONO:FONT,whiteSpace:'nowrap'}}>{children}</div>;
};
const Box:React.FC<{x:number;y:number;w:number;h:number;color?:string;owner?:string}>=({x,y,w,h,color=C.edge,owner})=><div data-panel data-owner={owner} style={{position:'absolute',left:x,top:y,width:w,height:h,border:`2px solid ${color}`,borderRadius:16,background:C.surface,boxSizing:'border-box'}}/>;
const Header:React.FC<{title:string;stage:number;tag?:string;ending?:boolean}>=({title,stage,tag,ending=false})=><>
 <T x={100}y={43}w={480}size={25}color={C.orange}>Kafka · MQ15 · 多副本确认</T>
 {['主副本确认','复制进度','同步数量','确认边界'].map((q,i)=><T key={q}x={650+i*213}y={45}w={190}size={24}align="center"color={i===stage?C.orange:C.muted}>{q}</T>)}
 <T x={ending?1540:1660}y={43}w={ending?280:160}size={25}align="right">{ending?'IT小村 · 原创':'IT小村'}</T>
 <T x={100}y={126}w={1720}size={44}>{title}</T>
 {tag&&<T x={100}y={204}w={1720}size={23}color={C.muted}>{tag}</T>}
</>;
const Footer:React.FC<{children:React.ReactNode;color?:string;alpha?:number}>=({children,color=C.orange,alpha=1})=><T x={100}y={849}w={1720}size={28}align="center"color={color}alpha={alpha}>{children}</T>;
const ModelView:React.FC<{v:any;children:React.ReactNode}>=({v,children})=><div data-model-state={v.id}data-branch={v.branch}data-reset-before={v.resetBefore}data-leader={v.leaderId??'none'}data-isr={JSON.stringify(v.isr)}data-hw={v.highWatermark??'none'}data-leader-known-next={JSON.stringify(v.leaderKnownNext)}data-required-offset={v.requiredOffset??'none'}data-producer-future={v.producer.future}data-producer-response={v.producer.response}data-admission-passed={String(v.admission.passed)}data-business-complete={String(v.consumer.businessCompleted)}>{children}</div>;
const Caller:React.FC<{v:any;showGate?:boolean;showISR?:boolean;showAcks?:boolean;intro?:boolean}>=({v,showGate=false,showISR=false,showAcks=true,intro=false})=>{
 const p=v.producer,success=p.future==='success',failed=p.future==='failed',pending=p.future==='pending',color=success?C.success:failed?C.danger:C.orange;
 const result=intro?'任务：等待写入确认':success?'网站已收到成功':failed?'网站收到拒绝':p.response==='in-flight'?(p.error?'拒绝响应在途':'成功响应在途'):pending?'等待这次发送结果':'尚未发送';
 const gate=!v.admission.applies?'无需等待跟随复制':!v.admission.evaluated?'数量准入：待检查':v.admission.passed?`${v.isr.length} ≥ 2 · 准入通过`:`${v.isr.length} < 2 · 追加前拒绝`;
 return <><Box x={100}y={272}w={1720}h={90}owner="website-result"/>
 <T x={125}y={285}w={320}size={24}>网站 · 订单7042 / E01</T><T x={125}y={322}w={340}size={22}color={color}>{result}</T>
 <T x={510}y={285}w={470}size={24}mono={showAcks}color={C.orange}>{showAcks?`acks=${p.acks}`:'确认方式：待比较'}</T><T x={510}y={322}w={460}size={21}color={C.muted}>{showGate?gate:'一次应用发送 · 单条记录'}</T>
 <T x={1040}y={285}w={720}size={24}color={C.blue}>{showISR?`同步名单 ISR：${v.isr.join(' / ')}`:'P0 · 同一分区的三份数据副本'}</T><T x={1040}y={322}w={720}size={21}color={C.muted}>{showISR?`当前 ${v.isr.length} 份　｜　最小数量 minISR = 2`:'一份接收写入，两份跟随复制'}</T>
 </>;
};
const ReplicaLogs:React.FC<{v:any;known?:boolean;highlight?:string}>=({v,known=false,highlight})=><>{IDS.map((id,i)=>{
 const r=v.replicas[id],x=100+i*610,lead=v.leaderId===id,edge=!r.available?C.edge:lead?C.orange:C.blue,records=r.records;
 return <div key={id}data-replica={id}data-role={r.role}data-available={String(r.available)}data-records={JSON.stringify(records)}data-physical-next={r.nextOffset}data-leader-known={v.leaderKnownNext[id]??'none'}data-local-hw={r.localHW}>
 <Box x={x}y={430}w={500}h={350}color={highlight===id?C.success:edge}owner={'log-'+id}/>
 <T x={x+24}y={449}w={450}size={28}color={r.available?edge:C.muted}><span style={{display:'inline-flex',alignItems:'center',gap:12}}><KafkaMark kind="kafka"size={28}/>{id} · {lead?'主副本':r.available?'跟随副本':'离线副本'}</span></T>
 <T x={x+24}y={491}w={450}size={20}color={C.muted}>P0 的本地日志{!r.available&&records.length?' · 字节仍保留':''}</T>
 <div data-log-slot={id}style={{position:'absolute',left:x+24,top:534,width:450,height:74,border:`2px ${records.length?'solid':'dashed'} ${records.length?(!r.available?C.muted:C.orange):C.edge}`,borderRadius:10,boxSizing:'border-box'}}/>
 {records.length?records.map((record:any)=><div key={record.eventId}data-log-record={record.eventId}data-log-owner={id}data-event-id={record.eventId}data-offset={record.offset}data-value={record.value}>
 <T x={x+40}y={548}w={418}size={31}mono color={!r.available?C.muted:C.text}>E01　@ offset 0</T></div>):<T x={x+40}y={553}w={418}size={25}align="center"color={C.muted}>空日志</T>}
 <T x={x+24}y={632}w={450}size={26}color={r.available?C.text:C.muted}>这份日志下一位置：{r.nextOffset}</T>
 {known&&<><div style={{position:'absolute',left:x+24,top:689,width:450,borderTop:`1px solid ${C.edge}`}}/><T x={x+24}y={710}w={450}size={25}color={C.blue}>主副本已知：{v.leaderKnownNext[id]??'无活动主'}</T></>}
 </div>;
 })}</>;
const HW:React.FC<{v:any;named?:boolean}>=({v,named=true})=>{
 const positions=v.hwCalculation.positions,values=v.isr.map((id:string)=>positions[id]),active=v.leaderId!==null,hw=v.highWatermark,target=v.requiredOffset,ready=v.completionConditionNow;
 const expression=active&&values.every((q:any)=>q!==null)?`min(${values.join(', ')}) = ${v.hwCalculation.candidate}`:'等待控制面恢复后的稳定状态';
 return <div data-hw-participants={JSON.stringify(v.hwCalculation.participants)}data-hw-expression={expression}data-completion-condition={String(ready)}>
 <Box x={100}y={807}w={1720}h={86}color={ready?C.success:C.blue}owner="common-progress"/>
 <T x={125}y={820}w={840}size={26}color={C.blue}>{named?'共同进度 HW':'共同进度'}：{hw??'无活动主'}　{expression}</T>
 <T x={1050}y={820}w={740}size={25}align="right"color={ready?C.success:C.orange}>{target===null?'尚无本条完成目标':`本条目标 ${target}　·　${ready?'完成条件已满足':'继续等待'}`}</T>
 <T x={125}y={859}w={1660}size={20}color={C.muted}>{target===null?'尚未追加本条记录；追加后才设置本条所需位置':hw===1?'位置1涵盖 E01@0；响应抵达前，网站结果仍可能等待':hw===0?'位置0尚未越过 E01@0；本例稳定ISR，无待加入或额外追齐候选':'接管展示稳定结果；数据副本不相互投票'}</T>
 </div>;
};
function pointAlong(points:number[][],t:number){const lens=points.slice(1).map((p,i)=>Math.hypot(p[0]-points[i][0],p[1]-points[i][1]));let dist=clamp(t)*lens.reduce((a,b)=>a+b,0);for(let i=0;i<lens.length;i++){if(dist<=lens[i]||i===lens.length-1){const p=dist/Math.max(1,lens[i]);return [points[i][0]+(points[i+1][0]-points[i][0])*p,points[i][1]+(points[i+1][1]-points[i][1])*p];}dist-=lens[i];}return points[0];}
const Motion:React.FC<{flight:Flight;f:number}>=({flight,f})=>{
 if(f<flight.start||f>=flight.end)return null;const {from,to,kind,label}=flight,ack=to==='website',sx=350+610*IDS.indexOf(from),tx=350+610*IDS.indexOf(to),color=kind==='record-copy'?C.orange:kind==='success'?C.success:kind==='failure'?C.danger:C.blue;
 const points=ack?[[100,560],[72,560],[72,318],[100,318]]:[[sx,430],[sx,414],[tx,414],[tx,430]],p=pointAlong(points,tween(f,flight.start,flight.end)),path=points.map((q,i)=>(i?'L':'M')+q.join(' ')).join(' ');
 return <><svg width={1920}height={1080}style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d={path}fill="none"stroke={color}strokeWidth={3}/><circle data-moving-body={kind}data-moving-record={kind==='record-copy'?'E01':undefined}data-from={from}data-to={to}cx={p[0]}cy={p[1]}r={11}fill={color}stroke={C.bg}strokeWidth={3}/></svg>{!ack&&<T x={200}y={372}w={1520}size={21}color={color}align="center">{label}</T>}</>;
};
const Scene:React.FC<{s:Shot}>=({s})=>{
 const f=useCurrentFrame(),n=Number(s.id),timing=sceneTiming(s),{c,e}=timing,at=stateAt(s,f),late=tween(f,c+5,c+35);
 if(n===13)return <><Header stage={3}ending title="成功确认，要把这三个条件放在一起看"tag="固定本例：ELR关闭、非同步选主关闭；不推演所有ISR过渡或追加后错误"/>
 {[{x:100,t:'确认方式',a:'acks=1：主追加后可回复',b:'acks=all：检查复制完成',color:C.orange},{x:690,t:'当前同步名单',a:'本例门槛：至少2份',b:'ISR3时，不能只等2份',color:C.blue},{x:1280,t:'共同进度',a:'HW 越过 E01@0',b:'目标位置：0 + 1 = 1',color:C.success}].map(q=><React.Fragment key={q.x}><Box x={q.x}y={362}w={540}h={343}color={q.color}/><T x={q.x+25}y={394}w={490}size={35}color={q.color}align="center">{q.t}</T><T x={q.x+25}y={497}w={490}size={27}align="center">{q.a}</T><T x={q.x+25}y={558}w={490}size={27}align="center">{q.b}</T></React.Fragment>)}
 <T x={100}y={771}w={1720}size={32}align="center"alpha={late}color={C.orange}>复制确认 ≠ 每块磁盘都强制刷盘 ≠ 订单通知已完成</T><Footer alpha={late}color={C.muted}>按本次请求的确认边界解释成功，不把失败一律当作没有写入</Footer></>;
 const v=modelState(at!),known=n>=7&&n!==10&&n!==12,hw=n===6||n===7||n===8||n===9||n===11;
 const titles:Record<number,string>={1:'网站收到成功时，哪几份日志已经有这条记录？',2:'先认清同一分区的三份日志与下一位置',3:'先选只确认主副本，观察它何时回应',4:v.controller.selected?'存活副本接管后，新主没有这条记录':'已收到成功后，只停掉原主节点',5:'同一条事件，从三份空日志重新比较',6:'先检查同步数量，再追加并设置完成目标',7:'第二份主动拉取，再写入自己的日志',8:'第二份写好了，主副本还要收到下一次进度报告',9:v.producer.future==='success'?'三份追齐后，成功回复已经抵达网站':'第三份拉取、写入、报告后，再检查共同进度',10:v.controller.selected?'新主接管后，已有记录仍然保留':'这次已复制完成，再停掉原主节点',11:'重置为空日志：当前同步名单只有两份',12:'再重置为空日志：只剩一份，先检查准入'};
 const tags:Record<number,string>={1:'订单7042 · 单条事件 E01 · 三份数据副本',2:'本例范围：RF3 / minISR2 · ELR与非同步选主关闭 · 单producer / 禁用幂等 / 无重试',3:'acks=1 · 选定这次两份跟随副本尚未来得及复制的窗口',4:'只停止一台Broker · 原主的离线字节保留 · 不模拟KRaft投票',5:'相同 E01 / 相同配置 / 相同空日志 · 改为 acks=all · 本分支ISR稳定',6:'数量门槛通过在前，本地追加在后；记录offset0，对应所需下一位置1',7:'响应携带记录副本；原日志不移动 · 本地末尾与主副本已知进度分开',8:'本例稳定ISR3，且无额外近期追齐候选 · minISR2不等于固定只等两份',9:'下一次Fetch先报告进度，满足完成判断后才产生成功响应',10:'选定复制与进度已收敛的故障点 · 展示clean接管后的稳定结果',11:'相同事件从头比较 · 稳定ISR=[B1,B2] · 第三份不可用且非额外候选',12:'相同事件从头比较 · 稳定ISR=[B1] · minISR=2 · acks=all'};
 return <ModelView v={v}><Header stage={n<=4?0:n<=10?1:2}title={titles[n]}tag={tags[n]}/><Caller v={v}showGate={n>=6}showISR={n>=5}showAcks={n>=3}intro={n===1}/><ReplicaLogs v={v}known={known}highlight={v.event.kind==='follower-append'?v.event.to:undefined}/>{hw&&<HW v={v}named={n>8||(n===8&&f>=c+(e-c)*.55)}/>} {timing.flights.map((q,i)=><Motion key={i}flight={q}f={f}/>)}
 {n===1&&<Footer alpha={late}>网站得到的成功，需要沿日志与复制进度来解释</Footer>}
 {n===2&&<Footer alpha={late}>下一位置0：日志为空；追加 offset0 后，下一位置才变成1</Footer>}
 {n===3&&<Footer alpha={late}>{v.producer.future==='success'?'本例网站已成功，两份跟随日志仍空':'主副本追加后，成功响应还要返回网站'}</Footer>}
 {n===4&&<Footer alpha={late}color={v.controller.selected?C.danger:C.orange}>{v.controller.selected?'clean新主B2没有E01；原主离线文件仍保留E01':'等待控制面从存活ISR候选中选择新主'}</Footer>}
 {n===5&&<Footer alpha={late}>跟进名单 ISR：包含主副本的当前三份；不代表三份都已拥有新记录</Footer>}
 {n===10&&<Footer alpha={late}color={C.success}>{v.controller.selected?'B2新主与B3跟随日志中，E01仍然存在':'本次三份已保留E01，再比较单节点故障'}</Footer>}
 {n===12&&<Footer alpha={late}color={v.producer.future==='failed'?C.danger:C.orange}>{v.producer.future==='failed'?'本次追加前拒绝、日志为空；不能推广成所有失败都没写':'先做1 < 2的数量判断，尚未追加这条记录'}</Footer>}
 </ModelView>;
};
const ShotView:React.FC<{s:Shot;captions:boolean}>=({s,captions})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from+(q.duration??1)-1));
 return <AbsoluteFill data-shot={s.id}data-prevoice={String(PREVOICE)}style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}><Scene s={s}/>{captions&&sub&&<div data-subtitle style={{position:'absolute',left:110,right:110,top:929,height:108,padding:'0 20px',boxSizing:'border-box',display:'flex',alignItems:'center',justifyContent:'center',fontSize:37,lineHeight:1.4,textAlign:'center',background:C.bg+'F5',borderRadius:14}}>{sub.text}</div>}</AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id}from={s.from}durationInFrames={s.durationInFrames}><ShotView s={s}captions={showSubtitles&&!hideSubtitles}/></Sequence>)}</AbsoluteFill>;
