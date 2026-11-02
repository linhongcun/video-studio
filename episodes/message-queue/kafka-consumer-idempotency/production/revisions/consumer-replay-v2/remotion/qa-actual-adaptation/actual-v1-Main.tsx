import React from 'react';
import{AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame}from'remotion';
import{C,FONT}from'./theme';
import{Shot,parseBoard}from'./data';
import{T,Box,Header,Footer,World,ModelView,Motion,Flight}from'./components';
import model from'../../model.json';
import plan from'../../plan.json';
const M=model as any,PLAN=plan as any[];
export const snapshot=(id:string)=>{const v=M.snapshots.find((s:any)=>s.id===id);if(!v)throw Error('Missing model snapshot '+id);return v;};
type Step={at:number;id:string};
export function sceneTiming(s:Shot){
 const d=s.durationInFrames,a=s.voice?.[0]?.localStart??12,b=s.voice?.[0]?.localEnd??d*.44,c=s.voice?.[1]?.localStart??d*.51,e=s.voice?.[1]?.localEnd??d-25;
 const first=(p:number)=>a+(b-a)*p,last=(p:number)=>c+(e-c)*p,n=Number(s.id),ids=PLAN.find(q=>q.id===s.id)?.modelStages as string[];
 if(!ids?.length)throw Error('Missing modelStages '+s.id);let times:number[]=[0],flights:Flight[]=[];
 const fly=(start:number,end:number,kind:Flight['kind'],offset=0)=>flights.push({start,end,kind,offset});
 if(n===3){times=[0,first(.15),first(.88)];fly(times[1],first(.43),'fetch');fly(first(.46),times[2],'record-copy');}
 if(n===5)times=[first(.25),first(.84)];
 if(n===6)times=[0,first(.76)];
 if(n===7){times=[0,last(.25),last(.70)];fly(first(.22),first(.75),'offset-query');fly(last(.05),times[1],'load-committed');}
 if(n===8){times=[0,first(.40),last(.48)];fly(times[1],first(.78),'fetch');fly(last(.08),times[2],'record-copy');}
 if(n===9)times=[0,first(.25),first(.83)];
 if(n===10){times=[0,first(.37),first(.64),first(.90),last(.02),last(.20),last(.36),last(.51),last(.79)];fly(times[1],times[2],'commit',1);fly(times[4],last(.11),'offset-query',1);fly(last(.12),times[5],'load-committed',1);fly(times[7],times[8],'fetch',1);}
 if(n===11){times=[0,last(.05),last(.22),last(.39),last(.47),last(.58),last(.68),last(.77),last(.93)];fly(times[4],last(.52),'offset-query');fly(last(.53),times[5],'load-committed');fly(times[7],last(.84),'fetch');fly(last(.85),times[8],'record-copy');}
 if(n===12){times=[0,first(.23),first(.66),first(.89),last(.12)];fly(times[2],times[3],'commit',1);}
 // DB pending is an actual state. Before the first transaction begins retain
 // the prior poll snapshot rather than treating a pending effect as committed.
 if(times.length!==ids.length)throw Error('Timing/modelStages length mismatch '+s.id);
 const steps:Step[]=times.map((at,i)=>({at,id:ids[i]}));
 if(n===5)steps.unshift({at:0,id:'a-polled'});
 return {a,b,c,e,steps,flights};
}
export const stateAt=(s:Shot,f:number)=>{const t=sceneTiming(s);return [...t.steps].reverse().find(q=>f>=q.at)?.id??t.steps[0].id;};
const Intro:React.FC<{v:any}>=({v})=><><Header stage={0}title="账户已经加了10分，同一条事件为什么又来？"tag="订单7042 · 会员17 · 一次支付完成后的积分业务示例"/>
 <Box x={160}y={330}w={900}h={385}color={C.orange}owner="order-points-task"/><T x={200}y={365}w={820}size={34}color={C.orange}>订单7042 · 支付完成</T><T x={200}y={455}w={820}size={38}>积分事件 E01：给会员17加10分</T><T x={200}y={555}w={820}size={32}>同一条记录，为什么再次交给业务？</T>
 <Box x={1180}y={330}w={580}h={385}color={C.blue}owner="account-points-view"/><T x={1210}y={365}w={520}size={30}color={C.blue}>会员17 · 已提交积分</T><T x={1210}y={451}w={520}size={86}align="center">{v.db.points} 分</T><T x={1210}y={594}w={520}size={27}align="center">已经加过这10分</T><Footer>这次只追踪同一事件的消费恢复，不引入生产者第二次发送</Footer></>;
const Scene:React.FC<{s:Shot}>=({s})=>{
 const f=useCurrentFrame(),n=Number(s.id),timing=sceneTiming(s),v=snapshot(stateAt(s,f)),finished=v.id==='guard-final',step=PLAN.find(q=>q.id===s.id),showKey=n>=11;
 if(n===1)return <ModelView v={v}><Intro v={v}/></ModelView>;
 const title:Record<number,string>={2:'回看第一次读取前：同一日志只保存了一条记录',3:v.id==='a-polled'?'拿到零号记录后，甲的下次读取位置成为1':'甲从位置0请求这条记录',4:'内存里的1，和Kafka保存的0，是两种进度',5:v.db.points===10?'数据库已经提交10分，Kafka恢复位置仍是0':'先完成积分业务，观察数据库自己的提交',6:v.consumer.active?'数据库已提交，Kafka进度尚未提交':'甲的内存消失，日志、积分和恢复值仍保留',7:v.consumer.position===0?'保存的0已装进乙的内存，再从这里读取':'乙先查询组恢复位置，再初始化自己的读取位置',8:v.id==='b-polled-same'?'返回的仍是 E01@offset0，原日志仍只有一条':'把乙的读取位置0，填进下一次请求',9:v.db.points===20?'同一条记录又做一次业务，积分已经变成20':'同一业务再次执行，会产生什么结果？',10:v.id==='early-b-poll-empty'?'从1恢复后，0号业务被越过，积分仍是0':'先对照：提前提交Kafka位置，能解决问题吗？',11:v.db.processedKeys.length?'业务键与10分已保存，恢复0仍可重读':'再回到加分前：把业务键和积分放在同一事务',12:v.group.committed.P0===1?'积分仍是10，Kafka恢复位置已提交为1':v.db.effect==='skipped'?'同一业务键已经处理，这次跳过加分':'乙再次拿到事件后，先看业务键是否已处理'};
 const tag:Record<number,string>={2:'回到首次读取前的共同起点 · 原记录仍在保留范围内 · 不代表永久保留',3:'同组 points · 稳定拥有者只有A · 本例每次poll最多1条',4:'下一读取位置属于当前进程；已提交位置是该组的持久恢复值',5:'外部数据库事务与Kafka进度是两个提交边界，不会由数据库COMMIT自动联动',6:v.consumer.active?'故障窗口在DB完成后；B只在获得P0后恢复，不演示检测与重新分配时长':'A已退出；B随后获得P0后恢复，不暗示主动LeaveGroup或立即交接',7:'B拥有P0后，查询 → 收到保存值 → 安装到本地内存，三个动作分开',8:'Fetch请求中的0来自乙刚安装的位置；返回记录本身的offset仍是0',9:'本例没有新日志追加，也没有生产者重发；第二次业务提交会再次生效',10:'明确重置：A下次读取1 / 组恢复0 / 积分0 / 无业务键；只改变提交顺序',11:'相同重置起点：A下次读取1 / 组恢复0 / 积分0 / 无标记；不是给旧20分现场补键',12:'业务键 points:E01 不包含进程名；先完成或跳过业务，再提交下一恢复位置'};
 const ribbon=n===2?'同一条 E01 · order7042 / account17 / +10 · 生产者仅追加一次':n===10?'提交顺序对照：先提交恢复位置，再进入业务':n===11?'同一个数据库事务：业务键 points:E01 与加10分':n===12?'同一事件、同一业务键；重复调用不重复生效':n===7?'新进程不继承旧进程的内存位置':`跟踪同一条 E01@P0 offset0 · 当前 ${v.consumer.owner??'无活动进程'} · 原日志保留`;
 return <ModelView v={v}><Header stage={n<=2?0:n<=5?1:n<=9?2:3}ending={n===12}title={title[n]}tag={tag[n]}/>
 <Box x={90}y={276}w={1740}h={62}color={step?.resetFrom?C.orange:C.edge}owner="stage-context"/><T x={110}y={291}w={1700}size={25}align="center"color={step?.resetFrom?C.orange:C.muted}>{ribbon}</T>
 <World v={v}terms={n>=4}showKey={showKey}/>{timing.flights.map((flight,i)=><Motion key={i}flight={flight}f={f}/>)}
 {n===2&&<Footer>原日志不因读取而移走：offset0始终是同一条 E01</Footer>}
 {n===3&&<Footer>{v.consumer.position===1?'poll返回同一E01；内存position1只表示下次往后读':'先按当前位置0构造Fetch，再等待记录响应'}</Footer>}
 {n===4&&<Footer>position = 1　≠　committed = 0；读取本身不会自动提交</Footer>}
 {n===5&&<Footer>{v.db.points===10?'数据库积分10已提交；Kafka已提交位置仍为0':v.db.transaction==='open'?'事务中的拟写10分，还不是已提交的积分':'积分业务尚未开始，下一步进入数据库事务'}</Footer>}
 {n===6&&<Footer>{v.consumer.active?'故障窗口：数据库成功之后、Kafka offset1提交之前':'原记录 E01@0 + 数据库10分 + Kafka恢复0 都仍然保留'}</Footer>}
 {n===7&&<Footer>{v.consumer.position===0?'拿到0并安装后，乙才能用它生成读取请求':v.consumer.committedLoaded===0?'已经收到0；乙自己的读取位置还未安装':'查询的是Kafka保存的恢复值，不是A已消失的内存1'}</Footer>}
 {n===8&&<Footer>{v.consumer.position===1?'同一 E01 / 同一 offset0 再次交给应用；这不是第二条日志':'请求参数0决定从哪里取，不改变原记录的身份'}</Footer>}
 {n===9&&<Footer color={v.db.points===20?C.danger:C.orange}>原日志 {v.log.records.length} 条　·　业务尝试 {v.db.businessAttemptCount} 次　·　已提交效果 {v.db.effectCount} 次</Footer>}
 {n===10&&<Footer color={v.id==='early-b-poll-empty'?C.danger:C.orange}>{v.id==='early-b-poll-empty'?'记录没删除，但恢复起点越过它；积分业务尚未执行':'已提交的恢复值可以越过尚未完成的业务；先观察这次对照'}</Footer>}
 {n===11&&<Footer color={v.db.processedKeys.length?C.success:C.orange}>{v.db.processedKeys.length?'业务键与10分均已提交；重启恢复0仍会重读同一记录':v.db.transaction==='open'?'拟登记业务键与加10分，同属一个尚未提交的数据库事务':'从相同首次加分前起点开始；还没有业务去重标记'}</Footer>}
 {n===12&&<Footer color={finished?C.success:C.orange}>{finished?`日志 ${v.log.records.length} 条　·　业务尝试 ${v.db.businessAttemptCount} 次　·　加分效果 ${v.db.effectCount} 次`:'只有数据库业务完成或跳过后，才提交Kafka恢复位置'}</Footer>}
 </ModelView>;
};
const ShotView:React.FC<{s:Shot;captions:boolean;prevoice:boolean}>=({s,captions,prevoice})=>{const f=useCurrentFrame(),sub=s.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from+(q.duration??1)-1));return <AbsoluteFill data-shot={s.id}data-prevoice={String(prevoice)}style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}><Scene s={s}/>{captions&&sub&&<div data-subtitle style={{position:'absolute',left:110,right:110,top:929,height:108,padding:'0 20px',boxSizing:'border-box',display:'flex',alignItems:'center',justifyContent:'center',fontSize:37,lineHeight:1.4,textAlign:'center',background:C.bg+'F5',borderRadius:14}}>{sub.text}</div>}</AbsoluteFill>;};
export type MainProps={storyboard:any;showSubtitles?:boolean;hideSubtitles?:boolean;prevoice?:boolean;withAudio?:boolean};
export const Main:React.FC<MainProps>=({storyboard,showSubtitles=true,hideSubtitles=false,prevoice=false,withAudio=true})=>{const{shots}=parseBoard(storyboard);return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>{withAudio&&!prevoice&&typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id}from={s.from}durationInFrames={s.durationInFrames}><ShotView s={s}captions={showSubtitles&&!hideSubtitles}prevoice={prevoice}/></Sequence>)}</AbsoluteFill>;};
