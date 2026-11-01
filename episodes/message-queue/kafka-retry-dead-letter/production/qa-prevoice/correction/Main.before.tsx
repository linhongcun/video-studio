import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import model from '../../model.json';
import plan from '../../plan.json';
import {Shot,shots} from './data';
import {C,FONT,MONO} from './theme';
import {createMiddlewareIdentity} from '../../../../../_shared/middleware-identity';
declare const __HAS_VOICE_AUDIO__:boolean;
const KafkaMark=createMiddlewareIdentity(React);
const M=model as any;
const state=(id:string)=>{const s=M.timeline.find((r:any)=>r.id===id);if(!s)throw Error('Missing snapshot '+id);return s;};
export const getStages=(id:string):string[]=>{
 const row=(plan as any[]).find(r=>r.id===id);if(!row)throw Error('Missing shot '+id);
 return id==='03'?row.modelStages.filter((s:string)=>s!=='first-backoff'):row.modelStages;
};
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const T:React.FC<{x:number;y:number;w:number;size?:number;color?:string;align?:'left'|'center'|'right';alpha?:number;mono?:boolean;children:React.ReactNode}>=({x,y,w,size=28,color=C.text,align='left',alpha=1,mono=false,children})=>{
 const ref=useRef<HTMLDivElement>(null);useLayoutEffect(()=>{const e=ref.current;if(e&&alpha>.1&&e.scrollWidth>e.clientWidth+2)console.error('COPYFIT',e.textContent,e.scrollWidth,e.clientWidth);});
 return <div ref={ref} data-text data-copyfit style={{position:'absolute',left:x,top:y,width:w,fontSize:size,lineHeight:1.4,fontWeight:600,fontFamily:mono?MONO:FONT,color,textAlign:align,opacity:alpha,whiteSpace:'nowrap'}}>{children}</div>;
};
const Box:React.FC<{x:number;y:number;w:number;h:number;color?:string;children?:React.ReactNode}>=({x,y,w,h,color=C.edge,children})=><div data-panel style={{position:'absolute',left:x,top:y,width:w,height:h,background:C.surface,border:`2px solid ${color}`,borderRadius:16,boxSizing:'border-box'}}>{children}</div>;
const titles:Record<string,string>={
 '01':'同一条通知一直失败，后面的事件怎么办？','02':'先保留E01，暂停后续交付',
 '03':'先保存调用名额，再调用业务','04':'到期判断属于应用，poll仍继续',
 '05':'第二个名额已经占用，进程却退出了','06':'同一目录恢复预算，不重新领三次',
 '07':'服务恢复：业务成功后，再保存原进度','08':'第三次仍失败，就挡住第四次调用',
 '09':'明确永久拒绝，第一次就转待处置','10':'死信记录保留问题，不等于业务成功',
 '11':'发送返回、写入确认、本机记住，分开看','12':'再确认原位置，才放行后续事件',
 '13':'目标不可用，不能假装转存完成','14':'没记住上次确认，重发可能多一份',
 '15':'预算、时间门、确认边界，各有职责'};
const chapter=(id:string)=>Number(id)<=4?0:Number(id)<=7?1:Number(id)<=12?2:3;
const Header:React.FC<{id:string;s:any}>=({id,s})=><>
 <T x={100} y={45} w={540} size={25} color={C.orange}>Kafka · MQ08 · 重试与死信</T>
 {['保存预算','同目录恢复','退出处置','两个边界'].map((v,i)=><T key={v} x={745+i*190} y={46} w={170} size={23} align="center" color={chapter(id)===i?C.orange:C.muted}>{v}</T>)}
 <T x={1540} y={45} w={280} size={25} align="right">{id==='15'?'IT小村 · 原创':'IT小村'}</T>
 <T x={100} y={135} w={1720} size={44}>{id==='05'?(s.id==='second-ready'?'到期且有名额，先保存第二次预留':s.consumer.active?'第二个名额已占用，结果仍未决':'第二个名额已占用，进程却退出了'):id==='09'?(s.journal.phase==='DLQ_PENDING'?'已经收到永久拒绝，直接等待处置':'永久拒绝分支：首次结果决定是否停止'):titles[id]}</T>
 <T x={100} y={216} w={1720} size={23} color={C.muted}>E01 · 订单7042 · 逻辑业务notify · 3个预留名额含首次 · 同机保留状态目录</T>
</>;
const phaseName:Record<string,string>={READY:'可以判断是否开始',BACKOFF:'等待下次尝试时间',IN_FLIGHT:'名额已保存 · 结果未定',BUSINESS_DONE:'业务已返回成功',DLQ_PENDING:'等待处置',DLQ_CONFIRMED:'死信确认已保存',COMMITTED:'原位置确认已保存'};
const resultName:Record<string,string>={'not-called':'尚未调用','in-flight':'调用进行中',temporary:'临时不可用',permanent:'永久业务拒绝',success:'返回成功','unknown-after-crash':'上次结果未知'};

const SourceLog:React.FC<{s:any}>=({s})=><>
 <T x={100} y={289} w={430} size={27}><span style={{display:'inline-flex',gap:12,alignItems:'center'}}><KafkaMark kind="kafka" size={30}/>原主题 · P0</span></T>
 <Box x={100} y={341} w={430} h={429}/>
 {s.source.records.map((r:any,i:number)=><React.Fragment key={r.eventId}>
  <T x={130} y={372+i*122} w={370} size={31} color={i===0?C.orange:C.text}>{r.eventId} · offset {r.offset}</T>
  <T x={130} y={423+i*122} w={370} size={23} color={C.muted}>{i===0?(s.consumer.heldEventId==='E01'?'应用当前持有同一E01':!s.consumer.active?'进程退出，当前无持有者':'等待重读并核验原E01'):s.consumer.nextEventReleased?'已恢复后续交付资格':'同分区后续事件等待'}</T>
 </React.Fragment>)}
 <T x={130} y={644} w={370} size={29} color={s.consumer.committedNextOffset===1?C.success:C.blue}>原已提交位置：{s.consumer.committedNextOffset}</T>
 <T x={130} y={707} w={370} size={21} color={C.muted}>原记录在示例期间始终保留</T>
</>;
const Journal:React.FC<{s:any;id:string}>=({s,id})=>{
 const j=s.journal,c=s.consumer,gate=j.totalStarted<3&&s.clock.nowMs>=j.readyAtMs&&['READY','BACKOFF'].includes(j.phase);
 return <>
  <T x={630} y={289} w={660} size={27} align="center">本机保留状态 · 同一事件的预算</T>
  <Box x={630} y={341} w={660} h={429} color={C.orange}/>
  <T x={660} y={369} w={600} size={30} align="center" mono>notify : E01</T>
  <T x={660} y={424} w={600} size={23} align="center" color={C.muted}>进程{c.process} · {c.active?'读取同一state目录':'已退出，文件状态保留'}</T>
  {[0,1,2].map(i=><React.Fragment key={i}><div data-budget-slot={i+1} style={{position:'absolute',left:766+i*128,top:483,width:102,height:82,borderRadius:14,border:`2px solid ${i<j.totalStarted?C.orange:C.edge}`,background:i<j.totalStarted?C.orange:C.bg}}/><T x={766+i*128} y={496} w={102} size={38} color={i<j.totalStarted?C.bg:C.muted} align="center">{i+1}</T></React.Fragment>)}
  <T x={660} y={583} w={600} size={31} align="center">已用 {j.totalStarted} / 3 · 剩余 {3-j.totalStarted}</T>
  <T x={660} y={637} w={600} size={25} align="center" color={j.phase==='DLQ_PENDING'?C.danger:j.phase==='COMMITTED'?C.success:C.blue}>{phaseName[j.phase]}</T>
  <T x={660} y={710} w={600} size={21} align="center" color={C.muted}>{id==='04'||id==='06'?`相对时间 ${s.clock.nowMs}ms · 下次 ${j.readyAtMs}ms`:gate?'到期且有余额，才允许先保存名额':'名额指预留，不保证实际完成了调用'}</T>
 </>;
};
const Business:React.FC<{s:any;id:string}>=({s,id})=><>
 <T x={1390} y={289} w={430} size={27} align="right">应用调用 · 通知业务</T>
 <Box x={1390} y={341} w={430} h={429} color={s.business.knownComplete?C.success:C.blue}/>
 <T x={1415} y={372} w={380} size={30} align="center">仍是同一个E01</T>
 <T x={1415} y={473} w={380} size={37} align="center" color={s.business.knownComplete?C.success:s.business.earlierOutcomeUnknown?C.danger:C.text}>{resultName[s.business.lastResult]}</T>
 <T x={1415} y={562} w={380} size={25} align="center">{s.consumer.active?'教学业务返回结果':'业务结果可能未知'}</T>
 <T x={1415} y={644} w={380} size={25} align="center" color={C.blue}>{s.journal.phase==='COMMITTED'?'本流程结束，后续可交付':s.consumer.active?'消费者仍持续poll':'没有活跃消费者在poll'}</T>
 <T x={1415} y={711} w={380} size={20} align="center" color={C.muted}>{s.consumer.paused?'P0新交付门：暂停':'P0新交付门：开放'}</T>
</>;
const Dlq:React.FC<{s:any}>=({s})=>{
 const q=s.dlq;
 return <>
  <T x={1390} y={289} w={430} size={27} align="right">死信主题 · 另一份新记录</T>
  <Box x={1390} y={341} w={430} h={429} color={C.blue}/>
  <T x={1415} y={368} w={380} size={25}>当前进程{s.consumer.process}的发送结果</T>
  <T x={1415} y={415} w={380} size={28} color={q.futureState==='success'?C.success:q.futureState==='failed'?C.danger:C.muted}>{({none:'没有当前发送结果',pending:'Future · 等待终态',success:'成功metadata',failed:'最终报错 · 不提交原位置'} as any)[q.futureState]}</T>
  {q.records.slice(0,2).map((r:any,i:number)=><T key={i} x={1415} y={489+i*62} w={380} size={32} color={C.text}>E01 · P0 · offset {r.offset}</T>)}
  {!q.records.length&&<T x={1415} y={509} w={380} size={25} color={C.muted}>本例目标尚无追加记录</T>}
  <T x={1415} y={644} w={380} size={23} color={C.blue}>来源：orders / P0 / 0</T>
  <T x={1415} y={711} w={380} size={21} color={C.muted}>次数 {s.journal.totalStarted} · 原事件身份保留</T>
 </>;
};
const Flight:React.FC<{p:number;to:'business'|'dlq'|'source'}>=({p,to})=>{
 if(p<=0||p>=1)return null;
 const source=to==='source',x=source?615:1305,end=source?545:1375;
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d={`M${x} 533H${end}`} stroke={source?C.blue:C.orange} strokeWidth={3}/><circle data-moving-body={to} cx={x+(end-x)*p} cy={533} r={8} fill={source?C.blue:C.orange}/></svg>;
};
const resetText:Record<string,string>={'08':'回到已用2个名额、第三次尚未开始；只改第三次结果','09':'回到未尝试的共同起点；只改为永久业务拒绝','10':'回到3个名额耗尽的路径，整理待处置记录','13':'回到DLQ发送前；只改目标是否可用','14':'回到DLQ发送前；这次在确认后、本机保存前退出'};
const foot=(s:any,id:string)=>{
 if(id==='01')return '错误策略对照：失败便立即再调，没有退出判断';
 if(id==='02')return 'pause只关闭新交付；已取出的E01由应用保留';
 if(id==='03')return '保存成功，才允许调用；保存后未调用就退出也占名额';
 if(id==='04')return 'now ≥ 下次时间 且 已用 < 3，才再预留；时轴压缩非实时';
 if(id==='05')return '已保存的名额不会退回；进行中退出，业务结果可能未知';
 if(id==='06')return '上次结果未知；同一E01再调用，业务不能重复生效（幂等）';
 if(id==='07')return s.journal.phase==='COMMITTED'?'原进度确认后才放行E02；示例不继续执行E02业务':'业务成功与原进度确认分开，等待期间不放行E02';
 if(id==='08')return s.journal.phase==='DLQ_PENDING'?'已用3个名额，不再调用第4次，转为等待处置':'从相同起点改变第三次结果，名额不清零';
 if(id==='09')return s.journal.phase==='DLQ_PENDING'?'永久拒绝由应用分类，首个结果便停止业务重试':'永久拒绝分支从0个名额独立开始';
 if(id==='10')return 'eventId + 原位置 + 已用次数 + 原因；待处置不等于通知成功';
 if(id==='11')return s.journal.phase==='DLQ_CONFIRMED'?'本机已记DLQ确认，原进度仍0':'send返回只是结果对象，须等待终态成功metadata';
 if(id==='12')return s.journal.phase==='COMMITTED'?'原commit成功回调后结束；两个请求并不原子':'先确认死信，再发原commit；原进度等待成功回调';
 if(id==='13')return '最终发送错误保留pending与原0；异常不一概证明目标日志为空';
 if(id==='14')return '新进程没有旧Future；可能再次send，同一事件可有两个DLQ位置';
 return '有限重试不等于业务幂等；转存不等于业务成功';
};
const Recap:React.FC=()=> <>
 <Box x={100} y={340} w={530} h={360} color={C.orange}/><T x={130} y={380} w={470} size={31}>开始业务前的门</T><T x={130} y={462} w={470} size={30}>到期 且 还有名额</T><T x={130} y={535} w={470} size={30}>↓ 先保存 +1 / 进行中</T><T x={130} y={608} w={470} size={30}>↓ 才调用同一事件</T>
 <Box x={695} y={340} w={1125} h={130} color={C.success}/><T x={725} y={382} w={1065} size={31}>业务成功 → 确认原commit → 放行后续</T>
 <Box x={695} y={490} w={1125} h={130} color={C.orange}/><T x={725} y={533} w={1065} size={31}>临时失败 且 还有名额 → 回到等待门</T>
 <Box x={695} y={640} w={1125} h={130} color={C.blue}/><T x={725} y={662} w={1065} size={28}>永久拒绝 或 名额耗尽 → 待处置</T><T x={725} y={709} w={1065} size={28}>→ 确认死信 → 另确认原commit</T>
 </>;

export const StageView:React.FC<{shotId:string;stage?:number;motion?:number}>=({shotId,stage=0,motion=0})=>{
 const ids=getStages(shotId),idx=Math.max(0,Math.min(ids.length-1,stage)),s=state(ids[idx]),id=s.id;
 const terminal=Number(shotId)>=10&&shotId!=='15';
 const flying=id.includes('reserved')?'business':id==='dlq-send-pending'||id==='duplicate-second-send'?'dlq':s.consumer.sourceCommitState==='pending-callback'?'source':null;
 return <AbsoluteFill style={{backgroundColor:C.bg,fontFamily:FONT,color:C.text}}><div data-model-state={id} data-view-mode={shotId==='15'?'concept-recap':'current'} data-process={s.consumer.process} data-journal-phase={s.journal.phase} data-total-started={s.journal.totalStarted} data-ready-at={s.journal.readyAtMs} data-now={s.clock.nowMs} data-original-committed={s.consumer.committedNextOffset} data-current-future={s.dlq.futureState} data-current-result={s.dlq.senderObservedResult} data-current-metadata={JSON.stringify(s.dlq.metadata)} data-source-records={JSON.stringify(s.source.records)} data-dlq-records={JSON.stringify(s.dlq.records)}>
  <Header id={shotId} s={s}/>
  {shotId==='15'?<Recap/>:<><SourceLog s={s}/><Journal s={s} id={shotId}/>{terminal?<Dlq s={s}/>:<Business s={s} id={shotId}/>}</>}
  {shotId==='01'&&<T x={660} y={787} w={600} size={26} color={C.danger} align="center">如果只看失败：再调 → 失败 → 再调 …</T>}
  {idx===0&&resetText[shotId]&&<><Box x={310} y={447} w={1300} h={201} color={C.blue}/><T x={340} y={477} w={1240} size={29} align="center" color={C.blue}>回到共同状态，再改变条件</T><T x={340} y={548} w={1240} size={27} align="center">{resetText[shotId]}</T></>}
  {flying&&<Flight p={clamp(motion)} to={flying as any}/>}
  <T x={100} y={842} w={1720} size={26} color={C.orange} align="center">{foot(s,shotId)}</T>
 </div></AbsoluteFill>;
};

// Fractions anchor only to real measured sentence bounds, never an estimated voice track.
const anchors:Record<string,[number,number][]>={
 '03':[[1,.22],[1,.65]],'04':[[0,.65],[1,.8]],
 '05':[[0,.4],[0,.75],[1,.3]],'06':[[0,.5],[1,.2],[1,.8]],
 '07':[[0,.35],[0,.7],[1,.12],[1,.45],[1,.82]],
 '08':[[1,.12],[1,.52]],'09':[[1,.2],[1,.65]],
 '11':[[0,.32],[0,.75],[1,.25],[1,.68]],'12':[[0,.3],[0,.78]],
 '13':[[1,.5]],'14':[[0,.3],[0,.77],[1,.2],[1,.43],[1,.8]]};
const TimedShot:React.FC<{shot:Shot}>=({shot})=>{
 const f=useCurrentFrame(),a=anchors[shot.id]??[],ids=getStages(shot.id);
 if(!shot.voice?.length)throw Error('Measured sentence bounds required for Main');
 const gates=[0,...a.map(([sentence,p])=>{const v=shot.voice![sentence];return v.localStart+(v.localEnd-v.localStart)*p;})];
 if(gates.length!==ids.length)throw Error('Anchor count mismatch '+shot.id);
 let idx=0;gates.forEach((g,i)=>{if(f>=g)idx=i;});
 const next=gates[idx+1]??shot.durationInFrames;
 return <StageView shotId={shot.id} stage={idx} motion={(f-gates[idx])/Math.max(1,next-gates[idx])}/>;
};
export const Main:React.FC<{hideSubtitles?:boolean;showSubtitles?:boolean}>=({hideSubtitles=false,showSubtitles=true})=><AbsoluteFill style={{backgroundColor:C.bg}}>
 {__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(shot=><Sequence key={shot.id} from={shot.from} durationInFrames={shot.durationInFrames}><TimedShot shot={shot}/>{!hideSubtitles&&showSubtitles&&(shot.subtitles??[]).map((s,i)=><Sequence key={i} from={s.from} durationInFrames={s.duration??Math.max(1,(s.to??shot.durationInFrames)-s.from)}><div data-subtitle style={{position:'absolute',left:100,top:925,width:1720,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:37,lineHeight:1.32,fontWeight:600,fontFamily:FONT,textAlign:'center',color:C.text}}>{s.text}</div></Sequence>)}</Sequence>)}
</AbsoluteFill>;
export const MechanismPreview:React.FC<{shotId?:string;stage?:number}>=({shotId='03',stage=1})=><StageView shotId={shotId} stage={stage} motion={.5}/>;
export const MechanismSequence:React.FC<{shotId?:string}>=({shotId='07'})=>{
 const f=useCurrentFrame();return <StageView shotId={shotId} stage={Math.floor(f/45)} motion={(f%45)/45}/>;
};
