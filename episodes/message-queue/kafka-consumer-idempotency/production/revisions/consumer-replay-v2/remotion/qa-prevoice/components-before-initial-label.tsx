import React,{useLayoutEffect,useRef}from'react';
import{C,FONT,MONO}from'./theme';
import{createMiddlewareIdentity}from'../../../../../../../_shared/middleware-identity';
const KafkaMark=createMiddlewareIdentity(React);
export const T:React.FC<{x:number;y:number;w:number;size?:number;color?:string;align?:'left'|'center'|'right';mono?:boolean;alpha?:number;children:React.ReactNode}>=({x,y,w,size=27,color=C.text,align='left',mono=false,alpha=1,children})=>{const ref=useRef<HTMLDivElement>(null);useLayoutEffect(()=>{const el=ref.current;if(el&&alpha>.1&&el.scrollWidth>el.clientWidth+2)console.error('COPYFIT',el.textContent,el.scrollWidth,el.clientWidth);});return <div ref={ref}data-text data-copyfit style={{position:'absolute',left:x,top:y,width:w,fontSize:size,lineHeight:1.35,fontWeight:600,fontFamily:mono?MONO:FONT,color,textAlign:align,opacity:alpha,whiteSpace:'nowrap'}}>{children}</div>;};
export const Box:React.FC<{x:number;y:number;w:number;h:number;color?:string;owner?:string}>=({x,y,w,h,color=C.edge,owner})=><div data-panel data-owner={owner}style={{position:'absolute',left:x,top:y,width:w,height:h,border:`2px solid ${color}`,borderRadius:16,background:C.surface,boxSizing:'border-box'}}/>;
export const Header:React.FC<{title:string;stage:number;tag?:string;ending?:boolean}>=({title,stage,tag,ending=false})=><><T x={90}y={43}w={490}size={25}color={C.orange}>Kafka · MQ05 · 消费幂等</T>{['同一条原记录','读取与恢复','退出后再读取','避免重复效果'].map((q,i)=><T key={q}x={630+i*220}y={45}w={200}size={24}align="center"color={i===stage?C.orange:C.muted}>{q}</T>)}<T x={ending?1540:1660}y={43}w={ending?290:170}size={25}align="right">{ending?'IT小村 · 原创':'IT小村'}</T><T x={90}y={126}w={1740}size={44}>{title}</T>{tag&&<T x={90}y={205}w={1740}size={23}color={C.muted}>{tag}</T>}</>;
export const Footer:React.FC<{children:React.ReactNode;color?:string;alpha?:number}>=({children,color=C.orange,alpha=1})=><T x={90}y={848}w={1740}size={28}align="center"color={color}alpha={alpha}>{children}</T>;
const DBMark=()=> <svg aria-hidden width={30}height={32}viewBox="0 0 30 32"><path d="M3 7v18c0 6 24 6 24 0V7"fill="none"stroke={C.orange}strokeWidth={2}/><ellipse cx={15}cy={7}rx={12}ry={5}fill="none"stroke={C.orange}strokeWidth={2}/><path d="M3 16c0 6 24 6 24 0"fill="none"stroke={C.orange}strokeWidth={2}/></svg>;
export const ModelView:React.FC<{v:any;children:React.ReactNode}>=({v,children})=><div data-model-state={v.id}data-branch={v.branch}data-reset-from={v.resetFrom??''}data-client-owner={v.consumer.owner??'none'}data-client-active={String(v.consumer.active)}data-client-position={v.consumer.position??'none'}data-committed-loaded={v.consumer.committedLoaded??'none'}data-fetch-offset={v.consumer.fetchOffset??'none'}data-returned={JSON.stringify(v.consumer.returned)}data-group-committed={v.group.committed.P0}data-db-points={v.db.points}data-processed-keys={JSON.stringify(v.db.processedKeys)}data-db-transaction={v.db.transaction}data-db-effect={v.db.effect}data-producer-send-count={v.log.producerSendCount}data-log-append-count={v.log.appendCount}data-log-records={JSON.stringify(v.log.records)}>{children}</div>;
export const World:React.FC<{v:any;terms?:boolean;showKey?:boolean;intro?:boolean}>=({v,terms=false,showKey=false,intro=false})=>{
 const consumer=v.consumer,db=v.db,records=v.log.records,position=consumer.position,committed=v.group.committed.P0,returned=consumer.returned??[],owner=consumer.owner;
 const activeText=consumer.active?`进程 ${owner??'等待归属'}`:'没有活动消费进程';
 const positionText=position===null?'尚未安装读取位置':`下次读取位置：${position}`;
 const loadedText=consumer.committedLoaded===null?'尚未取得恢复位置':`已查得恢复位置：${consumer.committedLoaded}`;
 const actualKey=db.processedKeys?.join(' / ')||'无业务去重标记',pendingKey=db.pendingKeys?.join(' / ')||'';
 return <><Box x={90}y={430}w={490}h={355}color={C.blue}owner="retained-kafka-log"/><T x={115}y={449}w={440}size={28}color={C.blue}><span style={{display:'inline-flex',gap:11,alignItems:'center'}}><KafkaMark kind="kafka"size={29}/>Kafka · 原分区日志</span></T>
 <div data-log-slot style={{position:'absolute',left:115,top:515,width:440,height:72,border:`2px ${records.length?'solid':'dashed'} ${records.length?C.orange:C.edge}`,borderRadius:10}}/>
 {records.map((r:any)=><div key={r.eventId}data-log-record={r.eventId}data-event-id={r.eventId}data-offset={r.offset}data-partition={r.partition??'P0'}><T x={131}y={532}w={408}size={28}mono>{r.eventId} · P0 @ offset {r.offset}</T></div>)}
 {!records.length&&<T x={131}y={537}w={408}size={25}color={C.muted}align="center">尚未追加</T>}
 <T x={115}y={605}w={440}size={22}color={C.muted}>原日志 {records.length} 条 · 追加 {v.log.appendCount} 次</T>
 <div style={{position:'absolute',left:115,top:651,width:440,borderTop:`1px solid ${C.edge}`}}/>
 <T x={115}y={672}w={440}size={23}color={C.blue}>{terms?'已提交位置 committed':'Kafka 保存的恢复位置'}：{committed}</T>
 <T x={115}y={725}w={440}size={21}color={C.muted}>积分消费组 points · 持久保存</T>
 <Box x={710}y={430}w={490}h={355}color={consumer.active?C.orange:C.edge}owner="consumer-memory"/><T x={735}y={449}w={440}size={28}color={consumer.active?C.orange:C.muted}>{activeText} · 本地内存</T>
 <T x={735}y={523}w={440}size={27}>{consumer.active?positionText:'读取位置：已随进程消失'}</T>
 <T x={735}y={580}w={440}size={22}color={C.muted}>{consumer.active?loadedText:'不继承旧进程的内存位置'}</T>
 <T x={735}y={645}w={440}size={25}color={C.blue}>{consumer.fetchOffset===null?'尚无本次 Fetch 请求':`本次 Fetch(P0, ${consumer.fetchOffset})`}</T>
 <T x={735}y={707}w={440}size={23}color={returned.length?C.text:C.muted}>{returned.length?'交给应用：'+returned.map((r:any)=>r.eventId??r).join(' / '):v.action==='poll-return'?'本次返回：空列表':'本次尚未交付记录'}</T>
 <Box x={1340}y={430}w={490}h={355}color={C.orange}owner="external-database"/><T x={1365}y={449}w={440}size={28}color={C.orange}><span style={{display:'inline-flex',gap:11,alignItems:'center'}}><DBMark/>业务数据库 · 积分</span></T>
 <T x={1365}y={511}w={440}size={23}color={C.muted}>会员17 · 订单7042 · 本次应加10</T><T x={1365}y={550}w={440}size={65}align="center"color={db.points===20?C.danger:C.text}>{db.points} 分</T>
 {db.transaction==='open'&&<T x={1365}y={645}w={440}size={22}color={C.orange}>事务未提交 · 拟写积分 {db.pendingPoints??db.points}</T>}
 {db.transaction!=='open'&&<T x={1365}y={645}w={440}size={23}color={db.effect==='skipped'?C.success:C.muted}>{db.effect==='skipped'?'同一业务已处理 · 本次跳过':db.effect==='applied'?'业务效果已提交':'本次业务效果尚未提交'}</T>}
 {showKey&&<T x={1365}y={708}w={440}size={21}color={db.processedKeys?.length?C.success:C.muted}>{pendingKey?`拟登记 ${pendingKey}（未提交）`:actualKey}</T>}
 {!showKey&&<T x={1365}y={708}w={440}size={21}color={C.muted}>数据库提交与 Kafka 提交分开</T>}
 </>;
};
export type Flight={start:number;end:number;kind:'offset-query'|'fetch'|'record-copy'|'load-committed'|'commit';offset:number};
const lerp=(a:number,b:number,p:number)=>a+(b-a)*p;
export const Motion:React.FC<{flight:Flight;f:number}>=({flight,f})=>{if(f<flight.start||f>=flight.end)return null;const t=Math.max(0,Math.min(1,(f-flight.start)/Math.max(1,flight.end-flight.start))),p=t*t*(3-2*t),reverse=flight.kind==='fetch'||flight.kind==='commit'||flight.kind==='offset-query',x=reverse?lerp(955,335,p):lerp(335,955,p),color=flight.kind==='record-copy'?C.orange:C.blue,label=flight.kind==='offset-query'?'新进程 → Kafka：查询 points/P0 已提交位置':flight.kind==='fetch'?`进程 → Kafka：Fetch(P0, ${flight.offset})`:flight.kind==='record-copy'?`Kafka → 进程：同一条 E01@offset0 的副本`:flight.kind==='load-committed'?`Kafka 保存的位置 ${flight.offset} → 新进程`:`进程 → Kafka：提交下次恢复位置 ${flight.offset}`;return <><T x={90}y={363}w={1740}size={22}color={color}align="center">{label}</T><svg width={1920}height={1080}style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d="M335 430V414H955V430"stroke={color}strokeWidth={3}fill="none"/><circle data-moving-body={flight.kind}data-moving-record={flight.kind==='record-copy'?'E01':undefined}data-offset={flight.offset}cx={x}cy={414}r={11}fill={color}stroke={C.bg}strokeWidth={3}/></svg></>;};
