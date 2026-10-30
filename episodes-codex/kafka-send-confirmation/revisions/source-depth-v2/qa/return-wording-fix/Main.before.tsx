import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {shots, Shot} from './data';
import {C, FONT, MONO} from './theme';
import sourceModel from '../../model.json';
import {createMiddlewareIdentity} from '../../../../../_shared/middleware-identity';

declare const __HAS_VOICE_AUDIO__: boolean;
const KafkaMark = createMiddlewareIdentity(React);
const model = sourceModel as any;
const state = (id: string) => {const s = model.states[id]; if (!s) throw Error('Unknown state ' + id); return s;};
const clamp = (v: number) => Math.min(1, Math.max(0, v));
const tween = (f: number, a: number, b: number) => {const p=clamp((f-a)/Math.max(1,b-a)); return p*p*(3-2*p);};
type TextProps = {x:number;y:number;w:number;size?:number;color?:string;alpha?:number;align?:'left'|'center'|'right';mono?:boolean;weight?:number;children:React.ReactNode};
const Text:React.FC<TextProps> = ({x,y,w,size=28,color=C.text,alpha=1,align='left',mono=false,weight=600,children}) => {
 const ref=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{const el=ref.current;if(el&&alpha>.1&&el.scrollWidth>el.clientWidth+2)console.error('COPYFIT',el.textContent,el.scrollWidth,el.clientWidth);});
 return <div ref={ref} data-text data-copyfit style={{position:'absolute',left:x,top:y,width:w,fontSize:size,lineHeight:1.4,color,opacity:alpha,textAlign:align,fontWeight:weight,fontFamily:mono?MONO:FONT,whiteSpace:'nowrap'}}>{children}</div>;
};
const Panel:React.FC<{x:number;y:number;w:number;h:number;color?:string;alpha?:number;name?:string}> = ({x,y,w,h,color=C.edge,alpha=1,name}) => <div data-panel={name} style={{position:'absolute',left:x,top:y,width:w,height:h,border:`2px solid ${color}`,borderRadius:15,background:C.surface,boxSizing:'border-box',opacity:alpha}}/>;
type Branch='normal'|'unknown'|'local'|'all';
const Header:React.FC<{title:string;tag:string;branch:Branch;ending?:boolean}>=({title,tag,branch,ending=false})=><>
 <Text x={100} y={48} w={485} size={25} color={C.orange}>Kafka · MQ04 · 发送确认</Text>
 {[['normal','成功回应',C.success],['unknown','缺少回应',C.orange],['local','本地失败',C.blue]].map(([id,label,color],i)=><Text key={id} x={670+i*270} y={49} w={235} size={24} align="center" color={branch===id||branch==='all'?color:C.muted}>{label}</Text>)}
 <Text x={ending?1540:1640} y={48} w={ending?280:180} size={25} align="right">{ending?'IT小村 · 原创':'IT小村'}</Text>
 <Text x={100} y={140} w={1720} size={46}>{title}</Text>
 <Text x={100} y={223} w={1720} size={23} color={C.muted}>{tag}</Text>
</>;
const Foot:React.FC<{children:React.ReactNode;alpha?:number;color?:string}>=({children,alpha=1,color=C.orange})=><Text x={100} y={849} w={1720} size={29} align="center" color={color} alpha={alpha}>{children}</Text>;
const identity=(b:any)=>b.producerId===501?'A·0':b.producerId===902?'B·0':'待分配';

const Caller:React.FC<{s:any;overview?:boolean;businessFocus?:boolean}>=({s,overview=false})=>{
 const fs=s.future.state, color=fs==='success'?C.success:fs==='failed'?C.danger:C.orange;
 const returned=s.call.returned, local=!!s.call.error;
 const result=fs==='success'?'F1 · 成功':fs==='failed'?'F1 · 超时失败':fs==='pending'?'F1 · 等待中':local?'send 同步抛错':'尚未返回结果';
 const detail=fs==='success'?'P0 / offset 0':fs==='failed'?'旧结果保持失败':fs==='pending'?'连着原批次 B1':'本条事件尚无发送结果';
 const cb=s.callback==='success'?'成功回调':s.callback==='failure'||s.callback.startsWith('new-')?'旧回调：超时失败':'回调尚未调用';
 return <div data-caller data-call-returned={String(returned)} data-call-error={s.call.error??'none'} data-future-id="F1" data-future-state={fs} data-callback-state={s.callback}>
  <Text x={100} y={300} w={300} size={29}>调用方</Text><Panel x={100} y={354} w={300} h={368} name="caller"/>
  <Text x={122} y={373} w={256} size={28}>E01 · 订单7042</Text>
  <Text x={122} y={420} w={256} size={22} color={C.muted}>{local?'编码未通过':returned?'本例 send 已返回':'应用调用 send'}</Text>
  {!overview&&<><Panel x={120} y={474} w={260} h={s.newFuture?104:128} color={local?C.blue:color} name="future-F1"/>
  <Text x={135} y={489} w={230} size={local?26:28} color={local?C.blue:color} align="center">{result}</Text>
  <Text x={135} y={541} w={230} size={22} color={C.muted} align="center" mono={fs==='success'}>{detail}</Text>
  {s.newFuture?<div data-new-future-id="F2" data-new-future-state={s.newFuture.state}><Panel x={120} y={593} w={260} h={105} color={s.newFuture.state==='success'?C.success:C.orange} name="future-F2"/><Text x={135} y={604} w={230} size={27} align="center" color={s.newFuture.state==='success'?C.success:C.orange}>{s.newFuture.state==='success'?'F2 · 成功':'F2 · 等待中'}</Text><Text x={135} y={651} w={230} size={22} align="center" color={C.muted}>{s.newFuture.state==='success'?'新结果 P0 / offset 1':'新发送 B2 的结果'}</Text></div>:<Text x={122} y={650} w={256} size={22} color={s.callback==='success'?C.success:s.callback==='failure'?C.danger:C.muted} align="center">{cb}</Text>}</>}
  {overview&&<Text x={122} y={520} w={256} size={28} align="center" color={C.orange}>结果由这里观察</Text>}
 </div>;
};

const Batch:React.FC<{s:any;x:number;alpha?:number}>=({s,x,alpha=1})=>{const b=s.batch,marked=b.producerId!==null;return <div data-moving-body="batch" data-batch-id={b.id} data-event-id={b.eventId} data-producer-id={b.producerId??'none'} data-producer-epoch={b.epoch??'none'} data-first-sequence={b.firstSeq??'none'} data-last-sequence={b.lastSeq??'none'} style={{position:'absolute',left:x,top:446,width:218,height:160,opacity:alpha,border:`2px solid ${C.orange}`,borderRadius:12,background:C.bg,boxSizing:'border-box'}}>
 <Text x={12} y={10} w={190} size={25} color={C.orange} align="center">{b.id} · 分区 P0</Text>
 <Text x={12} y={52} w={190} size={32} align="center">E01</Text>
 <Text x={12} y={110} w={190} size={marked?20:21} align="center" color={C.muted} mono={marked}>{marked?`${identity(b)} / seq 0..0`:'一条记录组成一批'}</Text>
 </div>;};

const Client:React.FC<{s:any;move?:number;overview?:boolean;requestMap?:boolean;completion?:boolean}>=({s,move,overview=false,requestMap=false,completion=false})=>{
 const queued=s.queue.length>0, flying=s.inflight.length>0;
 const x=move!==undefined?490+315*move:queued?490:805;
 const showBatch=move!==undefined||queued||flying;
 return <div data-client data-queue={s.queue.join(',')} data-inflight={s.inflight.join(',')} data-request-id={s.request?.id??'none'} data-request-partition-map={s.request?`P0:${s.request.recordsByPartition.P0}`:'none'}>
 <Text x={460} y={300} w={650} size={29}>生产者客户端</Text><Panel x={460} y={354} w={650} h={368} name="client"/>
 <Panel x={480} y={375} w={244} h={245} name="partition-queue"/><Panel x={795} y={375} w={295} h={245} name="sender-inflight"/>
 <Text x={493} y={390} w={218} size={25} align="center" color={C.blue}>P0 批次队列</Text>
 <Text x={810} y={390} w={265} size={25} align="center" color={C.blue}>Sender · 在途集合</Text>
 {!showBatch&&!overview&&<><Text x={493} y={510} w={218} size={24} color={C.muted} align="center">空</Text><Text x={810} y={510} w={265} size={24} color={C.muted} align="center">空</Text></>}
 {overview&&<><Text x={493} y={500} w={218} size={25} color={C.muted} align="center">按分区暂存批次</Text><Text x={810} y={500} w={265} size={25} color={C.muted} align="center">发出并等待回应</Text></>}
 {showBatch&&<Batch s={s} x={x}/>}
 <Text x={485} y={650} w={600} size={23} align="center" color={completion?C.success:C.muted}>{requestMap&&s.request?`${s.request.id} 上下文：P0 → 原批次 B1`:completion?'原批次完成 → 回调 / 原结果 F1':flying?'已登记在途，原结果仍待定':'缓冲与结果对象，记录不同的状态'}</Text>
 </div>;
};

const Broker:React.FC<{s:any;overview?:boolean;dedup?:boolean}>=({s,overview=false,dedup=false})=><div data-broker data-log-count={s.log.length} data-log-end={s.logEnd} data-duplicate={String(s.duplicate)} data-producer-state-ids={Object.keys(s.brokerStates).join(',')}>
 <Text x={1170} y={300} w={650} size={29}><span style={{display:'inline-flex',alignItems:'center',gap:12}}><KafkaMark kind="kafka" size={34}/>Kafka Broker</span></Text>
 <Panel x={1170} y={354} w={650} h={368} name="broker" color={dedup&&s.duplicate?C.success:C.edge}/>
 <Text x={1195} y={373} w={600} size={25} color={C.blue}>orders / P0 · 日志</Text>
 {[0,1].map(i=>{const r=s.log[i];return r?<div key={i} data-log-record={r.eventId} data-offset={r.offset} data-log-producer-id={r.producerId} style={{position:'absolute',left:1195+i*300,top:421,width:280,height:112,border:`2px solid ${i===1?C.orange:C.edge}`,borderRadius:11,background:C.bg,boxSizing:'border-box'}}><Text x={12} y={9} w={252} size={23} color={C.muted} align="center">offset {r.offset}</Text><Text x={12} y={50} w={252} size={30} align="center">E01 <span style={{fontSize:20,color:C.muted}}>· {r.producerId===501?'A·0':'B·0'}</span></Text></div>:<div key={i} data-empty-offset={i} style={{position:'absolute',left:1195+i*300,top:421,width:280,height:112,border:`2px dashed ${C.edge}`,borderRadius:11}}/>;})}
 <Text x={1195} y={550} w={600} size={23} color={C.muted}>{s.log.length?`实际记录 ${s.log.length} 条 · 下一位置 ${s.logEnd}`:overview?'实际追加的记录留在这里':'日志为空 · 下一位置 0'}</Text>
 <div data-producer-state style={{position:'absolute',left:1195,top:592,width:600,height:108,borderTop:`1px solid ${C.edge}`}}>
 <Text x={0} y={8} w={600} size={21} color={C.muted}>近期发送状态（本例仍保留）</Text>
 {Object.entries(s.brokerStates).map(([pid,p]:[string,any],i)=><Text key={pid} x={0} y={40+i*29} w={600} size={22} mono color={dedup&&pid==='501'?C.success:C.text}>{pid==='501'?'A·0':'B·0'} / seq {p.batches[0].firstSeq}..{p.batches[0].lastSeq} → offset {p.batches[0].offset}</Text>)}
 {!Object.keys(s.brokerStates).length&&<Text x={0} y={46} w={600} size={23} color={C.muted}>{overview?'按发送身份保存近期批次':'尚无本例发送者的状态'}</Text>}
 </div>
</div>;

const Flight:React.FC<{p:number;response?:boolean;blocked?:boolean}>=({p,response=false,blocked=false})=>{
 const y=response?660:490,x=response?1163-58*p:1105+58*p,color=response?C.success:C.orange;
 return <svg data-flight={response?'response':'request'} data-response-blocked={response&&blocked?true:undefined} width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}>
 {p>0&&<><path d={`M1105 ${y}H1163`} stroke={color} strokeWidth={3} opacity={.5}/>{p<1&&(!blocked||p<.42)&&<circle data-moving-dot data-route={response?'response':'request'} cx={x} cy={y} r={8} fill={color} stroke={C.bg} strokeWidth={2}/>}</>}
 {response&&blocked&&<path d={`M1125 ${y-10}L1145 ${y+10}M1145 ${y-10}L1125 ${y+10}`} stroke={C.orange} strokeWidth={4}/>}</svg>;
};
const IdentityDetail:React.FC<{s:any;compare?:boolean;alpha?:number}>=({s,compare=false,alpha=1})=><div data-identity-detail data-identity-existing="first-drain" style={{opacity:alpha}}>
 <Panel x={460} y={752} w={1360} h={76} color={compare&&s.duplicate?C.success:C.orange} name="identity-detail"/>
 <Text x={480} y={757} w={570} size={25} color={C.orange}>{compare?'来批 A·0 = 已存 A·0':'本次发送身份 A·0 · 始终未换'}</Text>
 <Text x={1090} y={757} w={700} size={25} color={compare&&s.duplicate?C.success:C.text}>{compare?'完整范围 0..0 = 已存 0..0':'本分区批序号 0..0 · 始终未变'}</Text>
 <Text x={480} y={795} w={570} size={18} color={C.muted} mono>producerId 501 · epoch 0</Text>
 <Text x={1090} y={795} w={700} size={18} color={C.muted} mono>{compare?'firstSequence 0 / lastSequence 0':'sequence 0..0（本例一条记录）'}</Text>
</div>;
const World:React.FC<{id:string;move?:number;send?:number;response?:number;blocked?:boolean;overview?:boolean;requestMap?:boolean;completion?:boolean;detail?:boolean;dedup?:boolean;alpha?:number;businessFocus?:boolean;note?:string}>=({id,move,send=0,response=0,blocked=false,overview=false,requestMap=false,completion=false,detail=false,dedup=false,alpha=1,businessFocus=false,note})=>{
 const s=state(id);return <div data-model-state={id} style={{opacity:alpha}}><Caller s={s} overview={overview}/><Client s={s} move={move} overview={overview} requestMap={requestMap} completion={completion}/><Broker s={s} overview={overview} dedup={dedup}/><Flight p={send}/><Flight p={response} response blocked={blocked}/>
 {detail?<IdentityDetail s={s} compare={dedup}/>:<><Text x={1170} y={755} w={650} size={25} color={businessFocus?C.orange:C.muted} align="right">下游订单通知：待处理</Text>{note&&<Text x={100} y={797} w={1720} size={24} color={C.muted} align="center">{note}</Text>}</>}
 <div data-business-state="pending" data-business-complete="false"/>
 </div>;
};
const Reset:React.FC<{label:string}>=({label})=><><Panel x={360} y={413} w={1200} h={265} color={C.blue} name="branch-reset"/><Text x={400} y={446} w={1120} size={38} color={C.blue} align="center">回到共同起点，切换独立对照</Text><Text x={400} y={524} w={1120} size={29} align="center">同一事件 E01 · 原日志为空 · 业务仍待处理</Text><Text x={400} y={603} w={1120} size={27} color={C.muted} align="center">{label}</Text></>;
const Recap:React.FC<{alpha:number}>=({alpha})=>{const rows=[['调用返回','得到原批次的结果对象','此刻可以仍在等待',C.orange],['成功回应','找到原批，完成 F1 / 回调','有本次发送的成功证据',C.success],['缺少回应','实际可能已经追加','最终失败也不能删去事实',C.orange]];return <><Text x={100} y={305} w={1720} size={28} color={C.muted} align="center">同一条 E01：发送结果、日志事实、业务完成分别判断</Text>{rows.map(([title,line1,line2,color],i)=><div key={title}><Panel x={100+i*590} y={388} w={540} h={295} color={color}/><Text x={125+i*590} y={420} w={490} size={37} align="center" color={color}>{title}</Text><Text x={125+i*590} y={510} w={490} size={27} align="center">{line1}</Text><Text x={125+i*590} y={579} w={490} size={25} align="center" color={C.muted}>{line2}</Text></div>)}<Panel x={380} y={731} w={1160} h={92} color={C.blue} alpha={alpha}/><Text x={400} y={755} w={1120} size={28} color={C.blue} align="center" alpha={alpha}>同批重传：核对发送身份 + 完整批序号 · 不读业务 eventId</Text></>;};

const titles=['调用返回，就能显示发送成功吗？','沿着同一条事件，跟一次内部接力','先进入分区队列：一条记录组成批次 B1','调用返回 F1，它连着原批次的完成结果','队列出批 → Sender 登记在途 → 发出请求','校验后追加，并保留这批发送的状态','成功回应找到原批，再完成回调与 F1','发送已确认，订单通知业务仍未完成','换一条对照：追加成功，却缺少回应','重传原批：沿用早已分配的发送标记','找到近期状态，核对身份和完整批序号','等待总发送期限，观察最终结果','应用换新会话：同一业务事件，已是新的发送','入缓冲前编码失败：本条记录未发出','调用返回、发送证据、业务完成，分别判断'];
const Scene:React.FC<{s:Shot}>=({s})=>{
 const f=useCurrentFrame(),n=Number(s.id),d=s.durationInFrames,a=s.voice?.[0]?.localStart??1,b=s.voice?.[0]?.localEnd??d/2,c=s.voice?.[1]?.localStart??d/2,e=s.voice?.[1]?.localEnd??d-20;
 const at=(p:number)=>a+(b-a)*p,bt=(p:number)=>c+(e-c)*p,late=tween(f,c+10,c+45);
 const common='源码机制教学示例 · orders / P0 · 非事务 · 一记录一批 · 非Broker网络实测';
 if(n===1)return <><Header title={titles[0]} tag="网站订单通知任务 · 本片只判断发送结果能证明什么" branch="all"/><Panel x={230} y={348} w={1460} h={412} color={C.orange}/><Text x={280} y={382} w={1360} size={33} color={C.orange}>订单通知 · 发送检查</Text><Text x={280} y={477} w={650} size={38}>事件 E01 · 订单7042</Text><Text x={280} y={566} w={650} size={30} color={C.muted}>应用调用事件发送</Text><Panel x={1030} y={441} w={600} h={224}/><Text x={1060} y={465} w={540} size={26} color={C.muted}>调用返回后，发送状态该怎样显示？</Text><Text x={1060} y={522} w={540} size={42} color={C.orange}>待确认</Text><Text x={1060} y={601} w={540} size={28}>下游通知：待处理</Text><Foot alpha={late}>日志可能已有记录，发送方却没有成功证据</Foot></>;
 if(n===2)return <><Header title={titles[1]} tag={common} branch="normal"/><World id="normal-start" overview note="记录向右发送，结果沿原批次回到调用方"/><Foot alpha={late}>本地队列、在途集合与实际日志，记录着不同状态</Foot></>;
 if(n===3){const added=at(.65);return <><Header title={titles[2]} tag={common} branch="normal"/><World id={f<added?'normal-start':'normal-buffer'} note={f<added?'先编码并选择 P0；本例还未进入批次缓冲':'P0 的队列持有 B1；本例只有一条 E01'}/><Foot alpha={late}>队列按分区组织批次，这里只跟踪 P0</Foot></>;}
 if(n===4){const ret=at(.48);return <><Header title={titles[3]} tag="固定一个返回时仍待定的合法调度；实际调度也可在send返回前完成" branch="normal"/><World id={f<ret?'normal-buffer':'normal-returned'} note="B1 仍在原队列；F1 等待的正是这批记录的完成结果"/><Foot alpha={late}>拿到结果对象，还没有拿到成功结果</Foot></>;}
 if(n===5){const start=at(.18),drained=at(.46),sent=at(.83),id=f<start?'normal-returned':'normal-inflight';return <><Header title={titles[4]} tag="满足发送条件后，首次出队时分配本批发送标记；本片省略实际等待" branch="normal"/><World id={id} move={f<drained?tween(f,start,drained):undefined} send={tween(f,drained+2,sent)} note="B1 离开队列，保留在途；原结果 F1 一直等待"/><Foot alpha={late}>在途不是发送成功，而是已经发出、仍待响应</Foot></>;}
 if(n===6){const append=at(.63);return <><Header title={f<append?'Kafka先校验这批记录，再追加日志':titles[5]} tag="本例acks=all条件成立后才发成功回应；本片不展开副本算法" branch="normal"/><World id={f<append?'normal-inflight':'normal-appended'} note={f<append?'Broker检查发送身份及批序号是否合法':'日志已到 offset 0；近期状态也记下 A·0 / seq 0..0 → 0'}/><Foot alpha={late}>实际记录已写入，发送方 F1 此刻仍在等待</Foot></>;}
 if(n===7){const received=at(.27),callback=bt(.18),done=bt(.65),id=f<received?'normal-appended':f<callback?'normal-response':f<done?'normal-callback':'normal-complete';return <><Header title={titles[6]} tag="R1的请求上下文：P0 → 原B1 → 原F1，回应沿同一关系返回" branch="normal"/><World id={id} response={tween(f,a,received)} requestMap={f<done} completion={f>=callback} note={f<received?'成功回应返回R1：P0 / offset 0':f<callback?'先填原B1的内部完成元数据：P0 / offset 0':f<done?'同一批次完成处理中，先通知成功回调':'原F1结束等待，成功结果仍定位原来的P0 / offset 0'}/><Foot alpha={late} color={C.success}>原批次的同一次完成，驱动回调与原结果对象</Foot></>;}
 if(n===8)return <><Header title={titles[7]} tag="发送结果定位本次写入；本例消费者业务尚未执行" branch="normal"/><World id="normal-complete" businessFocus completion note="F1已成功，Kafka有E01@0；下游通知仍然待处理"/><Foot alpha={late} color={C.blue}>发送成功，不代表下游业务完成</Foot></>;
 if(n===9){const send=bt(.12),append=bt(.43),id=f<send?'unknown-start':f<append?'unknown-inflight':'unknown-appended';return <><Header title={f<append?'换一条对照：从同一空日志重新发送':titles[8]} tag="独立未知分支：E01重新从相同空日志起点出发，不继承正常分支记录" branch="unknown"/><World id={id} alpha={f<c-6?.18:1} send={tween(f,send,append)} response={f>=append?tween(f,append+3,e-12):0} blocked={f>=append} note={f>=append?'实际追加了 E01@0，但成功回应没被发送方处理':'相同空日志起点，重新跟踪同一业务事件'}/>{f<c-6&&<Reset label="改看成功回应一直没有被发送方处理的分支"/>}<Foot alpha={late}>{f>=append?'实际日志有记录，F1仍在等成功回应':'切换分支时清楚重置，不混用两条对照的日志'}</Foot></>;}
 if(n===10){const requeue=at(.3),drain=at(.66),id=f<requeue?'unknown-appended':f<drain?'unknown-requeued':'unknown-retry-inflight';return <><Header title={titles[9]} tag="展开早已存在的标记；一次应用send，原B1自动重传 · 省略等待，非性能测量" branch="unknown"/><World id={id} send={tween(f,drain,bt(.15))} detail note=""/><Foot alpha={late}>同一个发送身份、同一个完整批序号，重传时一起保持</Foot></>;}
 if(n===11){const match=at(.69),id=f<match?'unknown-retry-inflight':'unknown-duplicate';return <><Header title={f<match?titles[10]:'认出原批：直接复用位置0，跳过日志追加'} tag="按来批发送者找到近期状态，身份与完整范围相同才复用；未命中也要先校验" branch="unknown"/><World id={id} detail dedup response={f>=match?tween(f,match+3,bt(.45)):0} blocked={f>=match}/><Foot alpha={late} color={C.success}>{f>=match?'日志仍1条、下一位置仍1；eventId不参与这次判断':'把来批标记与已保存的近期批次逐项对上'}</Foot></>;}
 if(n===12){const failed=at(.84),id=f<failed?'unknown-duplicate':'unknown-expired';return <><Header title={f<failed?titles[11]:'总发送期限到达：原F1最终超时失败'} tag="本例成功响应始终没有被处理；总发送期限不是Future.get的一次短等待" branch="unknown"/><World id={id} note={f<failed?'Broker复用过offset 0，仍不等于发送方F1已收到成功':'原F1与回调均报告超时失败；Kafka已有的E01@0保留'}/><Foot alpha={late}>没有成功证据，不能断定日志里没有记录</Foot></>;}
 if(n===13){const fresh=at(.5),append=bt(.3),done=bt(.77),id=f<fresh?'unknown-expired':f<append?'new-inflight':f<done?'new-appended':'new-complete';return <><Header title={titles[12]} tag="本分支继续：旧A关闭，新B重新send；旧日志保留，旧F1不会变成成功" branch="unknown"/><World id={id} send={tween(f,fresh+2,append)} response={f>=append?tween(f,append+3,done):0} note={f<fresh?'旧F1已失败，实际日志仍保留原E01@0':f<append?'新B2的发送身份B·0（PID902）不同；新结果叫F2':f<done?'新身份通过校验后追加E01@1，原E01@0不变':'F2成功定位offset 1；同一eventId已有两条，旧F1仍失败'}/><Foot alpha={late}>同一业务编号，不会让新的发送变成原批次重传</Foot></>;}
 if(n===14){const failed=bt(.32),id=f<failed?'local-start':'local-failed';return <><Header title={titles[13]} tag="独立短对照：只断言本条Produce记录未发出，不声称完全没有元数据网络请求" branch="local"/><World id={id} alpha={f<c-6?.18:1} note={f<failed?'同一空日志起点，换成编码器无法编码的内容':'send内部直接抛错：没有入批次队列，也没有正常返回F1'}/>{f<c-6&&<Reset label="改看入缓冲前就失败的本地编码"/>}<Foot alpha={late} color={C.blue}>这个确定的本地错误，本条记录没有发出</Foot></>;}
 return <><Header title={titles[14]} tag="内部结构决定哪些证据已经成立；不把教学状态轨迹当作Broker实测" branch="all" ending/><Recap alpha={late}/><Foot alpha={late}>成功回应完成原批；自动重传沿用标记；新会话属于新发送</Foot></>;
};

const ShotView:React.FC<{s:Shot;captions:boolean}>=({s,captions})=>{const f=useCurrentFrame(),sub=s.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from+(q.duration??1)-1));return <AbsoluteFill data-shot={s.id} style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}><img src={staticFile('series-background.png')} style={{position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'cover',opacity:.12}}/><Scene s={s}/>{captions&&sub&&<div data-subtitle style={{position:'absolute',left:110,right:110,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:37,lineHeight:1.4,textAlign:'center',padding:'0 18px',boxSizing:'border-box',background:`${C.bg}F5`,borderRadius:14}}>{sub.text}</div>}</AbsoluteFill>;};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}</AbsoluteFill>;
