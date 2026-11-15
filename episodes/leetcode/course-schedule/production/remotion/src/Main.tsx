import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {LeetcodeBackdrop,LeetcodeHeader} from '../../../../../_shared/leetcode-video/Frame';
import {C,FONT,MONO} from '../../../../../_shared/leetcode-video/theme';
import {TRACE,STORYBOARD,shots,Shot,Run,TraceEvent} from './data';
import {actionProgress,clamp,ease} from './timeline';
import {CodeCard} from './CodeCard';
declare const __HAS_VOICE_AUDIO__:boolean;
const WAIT='#A5B4FC',BAD='#FB8C92';
const T=({x,y,children,size=30,color=C.text,anchor='start',mono=false,weight=500,...rest}:any)=><text x={x} y={y} fill={color} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const POS4:Record<number,[number,number]>={0:[560,465],1:[970,270],2:[970,645],3:[1380,465]};
const POS2:Record<number,[number,number]>={0:[720,540],1:[1180,540]};
const R=72;
function edgeEnds(run:Run,from:number,to:number,pos:Record<number,[number,number]>){
 const [x1,y1]=pos[from],[x2,y2]=pos[to];
 const dx=x2-x1,dy=y2-y1,d=Math.hypot(dx,dy)||1,ux=dx/d,uy=dy/d;
 return {x1:x1+ux*(R+8),y1:y1+uy*(R+8),x2:x2-ux*(R+14),y2:y2-uy*(R+14)};
}
function Arrow({run,from,to,pos,state,p=1,flash=false}:{key?:any;run:Run;from:number;to:number;pos:Record<number,[number,number]>;state:'hidden'|'entering'|'live'|'leaving'|'gone';p?:number;flash?:boolean}){
 if(state==='hidden'||state==='gone')return null;
 const {x1,y1,x2,y2}=edgeEnds(run,from,to,pos);
 const mx=(x1+x2)/2-(y2-y1)*0.12,my=(y1+y2)/2+(x2-x1)*0.12;
 const ex=state==='entering'?x1+(x2-x1)*ease(p):x2,ey=state==='entering'?y1+(y2-y1)*ease(p):y2;
 const color=flash?BAD:state==='leaving'?C.muted:C.edge;
 const angle=Math.atan2(ey-my,ex-mx),back=20,spread=8;
 const ax=ex-back*Math.cos(angle),ay=ey-back*Math.sin(angle);
 return <g opacity={state==='leaving'?0.35:1}>
  <path d={`M${x1} ${y1} Q${mx} ${my} ${ex} ${ey}`} fill="none" stroke={color} strokeWidth={5} strokeDasharray={state==='leaving'?'14 10':undefined}/>
  <path d={`M${ax+spread*Math.sin(angle)} ${ay-spread*Math.cos(angle)} L${ex} ${ey} L${ax-spread*Math.sin(angle)} ${ay+spread*Math.cos(angle)}`} fill="none" stroke={color} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round"/>
 </g>;
}
function Node({x,y,n,state,indeg,showIndeg}:{key?:any;x:number;y:number;n:number;state:'wait'|'ready'|'learn'|'done'|'cycle';indeg?:number;showIndeg?:boolean}){
 const color=state==='learn'?C.gold:state==='done'?C.teal:state==='ready'?C.teal:state==='cycle'?BAD:WAIT;
 return <g>
  <circle cx={x} cy={y} r={R} fill={state==='done'||state==='ready'?'#153A3A':state==='cycle'?'#3A1C22':state==='learn'?'#3A2F16':'#1D2A44'} stroke={color} strokeWidth={5}/>
  <T x={x} y={y+18} size={54} anchor="middle" color={color} mono weight={700}>{n}</T>
  {showIndeg&&indeg!==undefined&&<g><rect x={x+R-8} y={y-R-6} width={96} height={46} rx={10} fill={C.surface} stroke={color} strokeWidth={3}/><T x={x+R+40} y={y-R+26} size={25} color={color} anchor="middle">入度 {indeg}</T></g>}
  {state==='done'&&<T x={x} y={y+R+40} size={26} color={C.teal} anchor="middle">已学完</T>}
  {state==='ready'&&<T x={x} y={y+R+40} size={26} color={C.teal} anchor="middle">现在能学</T>}
 </g>;
}
function Queue({queue,done,blocked}:{queue:number[];done:number[];blocked?:boolean}){
 return <g>
  <rect x={220} y={826} width={880} height={66} rx={14} fill={C.surface} stroke={blocked?BAD:C.edge} strokeWidth={blocked?4:2}/>
  <T x={252} y={868} size={27} color={blocked?BAD:C.muted}>队列</T>
  {queue.length===0?<T x={560} y={866} size={25} color={blocked?BAD:C.muted} anchor="middle">空</T>:
   queue.map((c,j)=><g key={c}><rect x={350+j*104} y={838} width={80} height={44} rx={10} fill={j===0?'#153A3A':C.surface} stroke={C.teal} strokeWidth={3}/><T x={390+j*104} y={870} size={29} anchor="middle" color={C.teal} mono weight={700}>{c}</T></g>)}
  <T x={1140} y={868} size={27} color={C.muted}>已学 {done.length} 门</T>
  {done.map((c,j)=><T key={c} x={1300+j*80} y={868} size={29} color={C.teal} mono weight={700}>{c}✓</T>)}
 </g>;
}
function edgeIndex(run:Run,from:number,to:number){return run.events.findIndex(e=>e.kind==='edge'&&e.from===from&&e.to===to);}
function releaseIndex(run:Run,from:number,to:number){return run.events.findIndex(e=>e.kind==='release'&&e.from===from&&e.to===to);}
function edgeState(run:Run,from:number,to:number,idx:number,frac:number):{state:'hidden'|'entering'|'live'|'leaving'|'gone';p:number}{
 const added=edgeIndex(run,from,to),rel=releaseIndex(run,from,to);
 if(added<0||idx<added)return{state:'hidden',p:0};
 if(rel>=0&&idx>rel)return{state:'gone',p:0};
 if(idx===added)return{state:'entering',p:frac};
 if(idx===rel)return{state:'leaving',p:frac};
 return{state:'live',p:1};
}
function nodeState(e:TraceEvent,c:number,run:Run):'wait'|'ready'|'learn'|'done'|'cycle'{
 if(e.kind==='learn'&&e.node===c)return'learn';
 if(e.kind==='blocked'&&e.remaining?.includes(c))return'cycle';
 if(e.kind==='result'&&e.remaining?.includes(c))return'cycle';
 if(e.done?.includes(c))return'done';
 if(e.queue?.includes(c))return'ready';
 return'wait';
}
const notes:Record<string,(e:TraceEvent)=>[string,string]>={
 edge:e=>[`先修课 ${e.from} → 目标课 ${e.to}`,C.edge],
 count:()=>['统计每门课的入度',C.muted],
 enqueue:e=>[`${e.node} 号入度为零 → 进队列`,C.teal],
 learn:e=>[`学 ${e.node} 号，删掉它指出去的边`,C.gold],
 release:e=>e.entered?[`${e.to} 号入度清零 → 进队列`,C.teal]:[`${e.to} 号还剩 ${e.indegrees[e.to!]} 门先修`,WAIT],
 blocked:e=>[`队列空了，${e.remaining?.length} 门课互相等待`,BAD],
 result:e=>e.value?['学完门数 = 课程总数 → 能学成',C.teal]:['先修要求无解 → 不能学成',BAD]};
function Board({run,e,frac,idx,pos=POS4,showIndeg=true}:{run:Run;e:TraceEvent;frac:number;idx:number;pos?:Record<number,[number,number]>;showIndeg?:boolean}){
 const cycleEdges=e.kind==='blocked'||e.kind==='result';
 const inCycle=(a:number,b:number)=>cycleEdges&&(e.remaining??[]).includes(a)&&(e.remaining??[]).includes(b)&&e.kind==='blocked'?undefined:false;
 return <>
  {run.prerequisites.map(([a,b])=><Arrow key={a+'-'+b} run={run} from={b} to={a} pos={pos}
    state={edgeState(run,b,a,idx,frac).state} p={edgeState(run,b,a,idx,frac).p}
    flash={inCycle(b,a)===undefined?inCycle(b,a)!==false:inCycle(b,a)}/>)}
  {Object.keys(pos).map(k=>+k).filter(c=>c<run.numCourses).map(c=><Node key={c} x={pos[c][0]} y={pos[c][1]} n={c}
    state={nodeState(e,c,run)} indeg={e.indegrees[c]} showIndeg={showIndeg&&idx>=run.events.findIndex(ev=>ev.kind==='count')}/>)}
  <Queue queue={e.queue??[]} done={e.done??[]} blocked={e.kind==='blocked'||e.kind==='result'&&!e.value}/>
  {(()=>{const[note,color]=notes[e.kind](e);return <T x={960} y={790} anchor="middle" size={32} color={color}>{note}</T>})()}
 </>;
}
function current(shot:Shot,frame:number,run:Run){
 const acts=(shot.actionCues??[]).filter(a=>a.events?.length);
 let idx=acts.length?acts[0].events![0]:run.events.length-1;
 let frac=0;
 for(const a of acts){
  const p=actionProgress(shot,frame,a.id,0,0.88);
  if(p<=0)break;
  const list=a.events!;
  idx=list[Math.min(list.length-1,Math.floor(p*list.length))];
  frac=p>=0.999?1:(p*list.length-Math.floor(p*list.length));
  if(p<0.999)break;
 }
 return{e:run.events[idx],frac,idx};
}
function Input({shot,frame}:{shot:Shot;frame:number}){
 const run=TRACE.main,p=actionProgress(shot,frame,'second');
 const pos=Object.fromEntries(Object.entries(POS4).map(([k,[x,y]])=>[+k,[x+280,y] as [number,number]])) as Record<number,[number,number]>;
 return <>
  <T x={220} y={300} color={C.muted} size={26}>先修表 · 每一项 [目标课, 先修课]</T>
  {run.prerequisites.map(([a,b],j)=><g key={j}>
   <rect x={220} y={335+j*118} width={440} height={92} rx={14} fill={C.surface} stroke={j===0&&p>0?C.gold:C.edge} strokeWidth={j===0&&p>0?4:2}/>
   <T x={280} y={393+j*118} size={38} mono>[{a}, {b}]</T>
   <T x={480} y={391+j*118} size={26} color={C.muted}>学 {a} 先学 {b}</T>
  </g>)}
  <g opacity={0.4+p*0.6}>
   {Object.keys(pos).map(k=>+k).map(c=><Node key={c} x={pos[c][0]} y={pos[c][1]} n={c} state="wait"/>)}
   {p>0&&<Arrow run={run} from={0} to={1} pos={pos} state="entering" p={p}/>}
   {p>0&&<T x={1430} y={300} size={28} color={C.gold} anchor="middle">先修课 → 目标课</T>}
  </g>
 </>;
}
function Graph({shot,frame}:{shot:Shot;frame:number}){
 const run=TRACE.main,p=actionProgress(shot,frame,'first',0,0.9),q=actionProgress(shot,frame,'second',0,0.95);
 const drawn=Math.round(p*3);
 return <>
  <T x={220} y={290} color={C.muted} size={26}>四项先修全部成边</T>
  {run.prerequisites.slice(0,1+drawn).map(([a,b])=><Arrow key={a+'-'+b} run={run} from={b} to={a} pos={POS4} state="live"/>)}
  {Object.keys(POS4).map(k=>+k).map(c=><Node key={c} x={POS4[c][0]} y={POS4[c][1]} n={c} state="wait"/>)}
  <g opacity={q}>
   <circle cx={1600} cy={330} r={86} fill="none" stroke={BAD} strokeWidth={6} strokeDasharray="16 12"/>
   <path d="M1600 216 l16 22 h-32 Z" fill={BAD} transform="rotate(38 1600 330)"/>
   <T x={1600} y={340} size={30} color={BAD} anchor="middle">环</T>
   <T x={1600} y={455} size={26} color={C.muted} anchor="middle">沿箭头走回起点<br/>= 互相等待</T>
   <T x={960} y={858} size={32} color={C.gold} anchor="middle">有环 → 谁也无法先开始；没环 → 才有学完的课</T>
  </g>
 </>;
}
function Why({shot,frame}:{shot:Shot;frame:number}){
 const q=actionProgress(shot,frame,'second',0,0.5);
 const steps=[['学完一门课','gold',C.gold],['删掉它指出的边','edge',C.edge],['后续课入度 −1','wait',WAIT],['减到零 → 进队列','teal',C.teal]];
 return <>
  <T x={220} y={300} color={C.muted} size={26}>删边与入队的因果</T>
  {steps.map(([label,,color],j)=><g key={label as string}>
   <rect x={230+j*430} y={350} width={360} height={120} rx={16} fill={C.surface} stroke={color as string} strokeWidth={3}/>
   <T x={410+j*430} y={422} size={33} anchor="middle" color={color as string}>{label as string}</T>
   {j<3&&<path d={`M${605+j*430} 410 h${50}`} stroke={C.muted} strokeWidth={4} markerEnd="url(#why-arrow)"/>}
  </g>)}
  <defs><marker id="why-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9Z" fill={C.muted}/></marker></defs>
  <g opacity={q}>
   <rect x={560} y={560} width={800} height={110} rx={18} fill="#153A3A" stroke={C.teal} strokeWidth={3}/>
   <T x={960} y={632} size={38} anchor="middle" color={C.teal} mono>已学 4 门 = 课程总数 4 → true</T>
   <T x={960} y={760} size={30} anchor="middle" color={C.muted}>队列不空，进度就一直在推进</T>
  </g>
 </>;
}
function EdgeCases({shot,frame}:{shot:Shot;frame:number}){
 const q=actionProgress(shot,frame,'second',0,1);
 const two=TRACE.twoCycle,emp=TRACE.empty,iso=TRACE.isolated;
 const twoE=two.events[two.events.length-1],empE=emp.events[emp.events.length-1],isoE=iso.events[iso.events.length-1];
 const mini=(run:Run,e:TraceEvent,pos:Record<number,[number,number]>,x:number,y:number,label:string,ok:boolean)=>
  <g transform={`translate(${x} ${y})`}>
   <rect x={-40} y={-80} width={560} height={240} rx={16} fill={C.surface} stroke={ok?C.edge:BAD} strokeWidth={ok?2:4}/>
   <T x={-8} y={-36} size={25} color={ok?C.muted:BAD}>{label}</T>
   <g transform="translate(60,-30) scale(0.42)">
    {run.prerequisites.map(([a,b])=><Arrow key={a+'-'+b} run={run} from={b} to={a} pos={pos} state="live" flash={!ok}/>)}
    {Object.keys(pos).map(k=>+k).filter(c=>c<run.numCourses).map(c=><Node key={c} x={pos[c][0]} y={pos[c][1]} n={c} state={e.done?.includes(c)?'done':e.remaining?.includes(c)?'cycle':e.queue?.includes(c)?'ready':'wait'} showIndeg={false}/>)}
   </g>
   <T x={445} y={140} size={32} anchor="middle" color={ok?C.teal:BAD} weight={700}>{ok?'能学成':'不能学成'}</T>
  </g>;
 return <>
  <T x={220} y={290} color={C.muted} size={26}>官方边界与补例</T>
  {mini(two,twoE,{0:[300,250],1:[700,250]},170,430,'官方示例 2 · 两门互相先修',false)}
  <g opacity={q}>{mini(emp,empE,{0:[180,250],1:[340,250],2:[500,250],3:[660,250]},720,430,'先修表为空 · 全部入度为零',true)}
  {mini(iso,isoE,{0:[300,250],1:[620,250],2:[300,90],3:[620,90]},1300,430,'补例 · 2、3 号是孤立课',true)}</g>
 </>;
}
function Close({shot,frame}:{shot:Shot;frame:number}){
 const p=actionProgress(shot,frame,'second',0,0.35);
 return <>
  {['先修项 → 从先修课指向目标课的边','入度为零的课 → 先进队列','学完一门 → 删出边，入度 −1','队列空且有课未学 → 有环'].map((line,j)=><T key={line} x={220} y={380+j*78} size={36} color={j===3?BAD:C.text}>{line}</T>)}
  <g opacity={p}>
   <T x={1300} y={380} size={42} color={C.gold}>拓扑排序</T><T x={1300} y={428} size={25} color={C.muted}>Kahn 入度做法</T>
   <T x={1300} y={545} size={42} color={C.gold} mono>O(n + e)</T><T x={1300} y={598} size={27} color={C.muted}>每课进出一次 · 每边删一次</T>
   <T x={1300} y={700} size={42} color={C.gold} mono>O(n + e)</T><T x={1300} y={753} size={27} color={C.muted}>入度数组与邻接表</T>
  </g>
 </>;
}
const slugOf=(s:Shot)=>({ '01':'input','02':'graph','03':'indegree','04':'learn','05':'why','06':'cycle','07':'blocked','08':'edge','09':'close' } as Record<string,string>)[s.id]??s.id;
const titles:Record<string,string>={input:'课程表：能不能把全部课程学完？',graph:'先修表 → 课程先修图',indegree:'哪门课现在就能学？',learn:'学完一门，解锁下一门',why:'为什么删边就能解锁？',cycle:'成环补例：三门课互相等',blocked:'队列空了 → 先修要求无解',edge:'边界：双向环、空表、孤立课',close:'入度为零就能学，队列空就是有环'};
const labels:Record<number,string>={6:'成环补例',8:'官方边界与补例'};
function splitSubtitle(text:string){
 const chunks=text.match(/[^，；：。！？]+[，；：。！？]?/g)??[text];const lines:string[]=[];let line='';
 for(const c of chunks){if(line.length+c.length>44&&line){lines.push(line);line='';}line+=c;}
 if(line)lines.push(line);return lines.flatMap(l=>l.match(/.{1,44}/g)??[]);
}
function Scene({shot,hideSubtitles}:{shot:Shot;hideSubtitles:boolean}){
 const frame=useCurrentFrame(),n=Number(shot.id);
 if(shot.codeCardFrom!==undefined&&frame>=shot.codeCardFrom)return <CodeCard/>;
 const run=n>=6&&n<=7?TRACE.cycle:TRACE.main,state=current(shot,frame,run);
 const body=n===1?<Input shot={shot} frame={frame}/>:n===2?<Graph shot={shot} frame={frame}/>:n===5?<Why shot={shot} frame={frame}/>:n===8?<EdgeCases shot={shot} frame={frame}/>:n===9?<Close shot={shot} frame={frame}/>:<Board run={run} {...state}/>;
 return <AbsoluteFill style={{background:C.bg}}><LeetcodeBackdrop/><LeetcodeHeader slug="course-schedule" identity={{number:207,method:'拓扑排序'}} detail={shot.chapterTitle}/>
 <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
 <T x={130} y={215} size={42} weight={600}>{titles[slugOf(shot)]??shot.id}</T>
 <T x={1785} y={215} size={22} color={C.gold} anchor="end">{labels[n]??'四门课教学示例'}</T>
 {body}
 {!hideSubtitles&&(shot.subtitles??[]).map((s,i)=>{
 if(frame<s.from||frame>(s.to??s.from+(s.duration??90)))return null;
 const lines=splitSubtitle(s.text),top=1020-lines.length*39;
 return <g data-subtitle={true} key={i}><rect x={150} y={top-32} width={1620} height={lines.length*39+25} rx={12} fill="#0B1220"/>
 {lines.map((l,j)=><T key={j} x={960} y={top+j*39} size={27} anchor="middle">{l}</T>)}</g>;
 })}
 </svg></AbsoluteFill>;
}
export function Main({hideSubtitles=false}:{hideSubtitles?:boolean}){
 return <AbsoluteFill>{shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><Scene shot={s} hideSubtitles={hideSubtitles}/></Sequence>)}
 {__HAS_VOICE_AUDIO__&&!STORYBOARD.meta.pendingAudio&&<Audio src={staticFile('audio/voice.wav')}/>}</AbsoluteFill>;
}
