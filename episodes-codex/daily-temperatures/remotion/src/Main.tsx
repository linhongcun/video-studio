import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots,MAIN,EQUALITY,PLAYBACK,TraceCase,TraceEvent,Beat,STORYBOARD} from './data';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
import {StackPrimer,OrderPrimer} from './StackPrimer';
declare const __HAS_VOICE_AUDIO__:boolean;

const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const ease=(n:number)=>{n=clamp(n);return n*n*(3-2*n);};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const end=(s:Shot)=>s.codeCardFrom??s.durationInFrames-10;
const at=(s:Shot,sentence:number,fraction:number)=>{
 const starts=s.cueFrames?.sentences??[0,s.durationInFrames/2];
 const first=starts[sentence]??0,last=starts[sentence+1]??end(s);
 return first+(last-first)*fraction;
};
const phase=(s:Shot,f:number,sentence=0,a=.05,b=.85)=>ease((f-at(s,sentence,a))/Math.max(1,at(s,sentence,b)-at(s,sentence,a)));
const T=({x,y,size=30,color=C.text,children,anchor='start',weight=500,opacity=1,mono=false,...rest}:any)=> <text x={x} y={y} fontSize={size} fill={color} textAnchor={anchor} fontWeight={weight} opacity={opacity} fontFamily={mono?MONO:FONT} {...rest}>{children}</text>;
const Header=({title,detail,kicker}:any)=><g>
 <T x={120} y={65} size={24} color={C.muted}>{kicker}</T>
 <T x={120} y={148} size={50} weight={750}>{title}</T>
 {detail&&<T x={120} y={207} size={28} color={C.muted}>{detail}</T>}
 <T x={1795} y={65} size={24} color={C.muted} anchor="end">LC.739</T>
 </g>;
const Note=({children,color=C.muted,opacity=1}:any)=><T x={960} y={902} size={29} color={color} anchor="middle" opacity={opacity}>{children}</T>;
const xpos=(day:number,n:number)=>n===3?570+day*390:245+day*195;
const ypos=(temperature:number)=>620-(temperature-28)*31;
const slot=(index:number)=>580+index*235;

type Playback={event:TraceEvent;previous:TraceEvent;progress:number;eventFrame:number};
function playback(s:Shot,f:number,caseData:TraceCase,initial:number,beats:Beat[]):Playback{
 let id=initial,old=initial,frame=0,nextFrame=end(s);
 for(let i=0;i<beats.length;i++){
  const b=beats[i],start=at(s,b[0],b[1]);
  if(f<start){nextFrame=start;break;}
  old=id;id=b[2];frame=start;nextFrame=i+1<beats.length?at(s,beats[i+1][0],beats[i+1][1]):end(s);
 }
 return {event:caseData.events[id],previous:caseData.events[old],progress:ease((f-frame)/Math.max(1,Math.min(14,(nextFrame-frame)*.65))),eventFrame:frame};
}
const state=(c:TraceCase,id:number):Playback=>({event:c.events[id],previous:c.events[id],progress:1,eventFrame:0});

const WaitSpan=({c,from,to,progress=1,label,top=283,color=C.teal}:any)=>{
 const a=xpos(from,c.input.length),b=mix(a,xpos(to,c.input.length),clamp(progress));
 return <g opacity={clamp(progress*5)} data-wait-span={`${from+1}-${to+1}`}>
  <path d={`M ${a} ${ypos(c.input[from])-57} V ${top} H ${b}`} fill="none" stroke={color} strokeWidth={4}/>
  <path d={`M ${b-10} ${top-8} L ${b} ${top} L ${b-10} ${top+8}`} fill="none" stroke={color} strokeWidth={3}/>
  <T x={(a+xpos(to,c.input.length))/2} y={top-18} size={32} color={color} anchor="middle" opacity={clamp((progress-.5)*2)}>{label}</T>
 </g>;
};

type WeatherProps={c?:TraceCase;pb?:Playback;allVisible?:boolean;showAnswers?:boolean;showZeros?:boolean;showPending?:boolean;stackNamed?:boolean;current?:number;focus?:number[];scan?:number;span?:{from:number;to:number;p:number;label:string};zeroReveal?:number;cost?:number;mutedAnswers?:boolean};
function Weather({c=MAIN,pb=state(MAIN,34),allVisible=false,showAnswers=true,showZeros=false,showPending=false,stackNamed=true,current,focus=[],scan=-1,span,zeroReveal=2,cost=-1,mutedAnswers=false}:WeatherProps){
 const e=pb.event,old=pb.previous,p=pb.progress,n=c.input.length;
 const today=current??e.today;
 const currentX=mix(xpos(old.today<0?today:old.today,n),xpos(today,n),p);
 const compare=e.type==='compare'&&e.previous!==null&&e.previous!==undefined;
 const solving=(e.type==='resolve'||e.type==='pop')&&e.previous!==undefined;
 const previous=(compare||solving)?e.previous:-1;
 const beforePending=old.pending;
 const movingPush=e.type==='push'&&old.id!==e.id;
 const movingPop=e.type==='pop'&&old.id!==e.id;
 const pendingIds=Array.from(new Set([...e.pending,...(movingPop?[e.previous!]:[])]));
 return <g data-trace-event={e.id} data-source-line={e.sourceLine}>
  <T x={120} y={293} size={24} color={C.muted}>气温</T>
  {[30,32,34,36].map(t=><g key={t}><line x1={195} x2={1730} y1={ypos(t)} y2={ypos(t)} stroke={C.edge} strokeWidth={1}/><T x={178} y={ypos(t)+9} size={22} color={C.muted} anchor="end" mono>{t}</T></g>)}
  <T x={120} y={644} size={19} color={C.muted}>基准28</T>
  <line x1={195} x2={1730} y1={620} y2={620} stroke={C.edge} strokeWidth={2}/>
  {c.input.slice(0,-1).map((v,i)=><line key={i} x1={xpos(i,n)} y1={ypos(v)} x2={xpos(i+1,n)} y2={ypos(c.input[i+1])} stroke={C.blue} strokeWidth={5} opacity={allVisible||i<today?.65:.16}/>)}
  {today>=0&&!allVisible&&<g data-current-day={today+1}>
   <line x1={currentX} x2={currentX} y1={318} y2={639} stroke={C.gold} strokeWidth={2} strokeDasharray="7 7" opacity={.55}/>
   <T x={currentX} y={305} size={25} color={C.gold} anchor="middle">当天</T>
  </g>}
  {c.input.map((temperature,i)=>{
   const active=i===today||focus.includes(i)||i===scan||i===previous;
   const seen=allVisible||i<=today;
   const color=i===scan?C.gold:i===previous?C.teal:active?C.gold:C.blue;
   const revealZero=showZeros&&(c.actual[i]!==0||i<(n-2+zeroReveal));
   const answer=e.answer[i];
   const showAnswer=showAnswers&&(answer>0||revealZero);
   return <g key={i} data-day={i+1} data-answer={showAnswer?answer:'pending'} opacity={seen?1:.32}>
    {active&&<rect x={xpos(i,n)-63} y={342} width={126} height={352} rx={20} fill={color+'0C'} stroke={color} strokeWidth={1.5} strokeOpacity={.5}/>}
    <line x1={xpos(i,n)} x2={xpos(i,n)} y1={ypos(temperature)} y2={620} stroke={color} opacity={.17} strokeWidth={26}/>
    <circle cx={xpos(i,n)} cy={ypos(temperature)} r={active?13:10} fill={C.bg} stroke={color} strokeWidth={active?5:3}/>
    <T x={xpos(i,n)} y={ypos(temperature)-27} size={active?39:35} anchor="middle" color={active?color:C.text} weight={650} mono>{temperature}</T>
    <T x={xpos(i,n)} y={671} size={26} anchor="middle" color={active?color:C.muted}>第{i+1}天</T>
    {showAnswers&&<>
     <T x={xpos(i,n)} y={739} size={showAnswer?40:30} anchor="middle" color={mutedAnswers?C.muted:showAnswer?C.teal:C.edge} mono opacity={e.type==='resolve'&&e.previous===i?Math.max(.2,p):1}>{showAnswer?answer:'·'}</T>
     {showAnswer&&<line x1={xpos(i,n)-33} x2={xpos(i,n)+33} y1={754} y2={754} stroke={C.teal} strokeOpacity={.4}/>}
    </>}
    {cost>=0&&<g opacity={cost>=i?1:.16}><T x={xpos(i,n)} y={806} size={25} anchor="middle" color={C.blue}>加入 1</T>{c.actual[i]>0&&<T x={xpos(i,n)} y={848} size={25} anchor="middle" color={C.teal}>移出 1</T>}</g>}
   </g>;
  })}
  {showAnswers&&<T x={122} y={735} size={23} color={C.muted}>等几天</T>}
  {scan>=0&&<g><circle cx={xpos(scan,n)} cy={ypos(c.input[scan])} r={23} fill="none" stroke={C.gold} strokeWidth={3}/><T x={xpos(scan,n)} y={ypos(c.input[scan])+53} color={C.gold} size={24} anchor="middle">查看</T></g>}
  {span&&<WaitSpan c={c} from={span.from} to={span.to} progress={span.p} label={span.label}/>}
  {solving&&e.previous!==undefined&&<WaitSpan c={c} from={e.previous} to={e.today} progress={e.type==='pop'?p:1} label={e.type==='resolve'?`等 ${e.distance} 天`:'写回原来的天'} top={265}/>}
  {showPending&&<g data-pending={e.pending.join(',')}>
   <T x={120} y={826} size={26} color={C.muted}>{stackNamed?'单调栈':'待解决区'}</T>
   <T x={120} y={863} size={20} color={C.muted}>保留原日期</T>
   {pendingIds.map(day=>{
    const actualSlot=e.pending.indexOf(day),oldSlot=beforePending.indexOf(day),isPop=movingPop&&day===e.previous;
    const isPush=movingPush&&day===e.today;
    const targetX=isPop?xpos(day,n):slot(Math.max(0,actualSlot));
    const targetY=isPop?730:826;
    // A new pending marker appears at its slot. Its filled label must never
    // travel through the original date labels or already committed answers.
    const sourceX=isPush?targetX:slot(Math.max(0,oldSlot>=0?oldSlot:actualSlot));
    const sourceY=isPush?targetY:826;
    const xx=mix(sourceX,targetX,p),yy=mix(sourceY,targetY,p);
    const alpha=isPop?1-p*.9:isPush?p:1;
    return <g key={day} opacity={alpha} data-pending-day={day+1} transform={`translate(${xx} ${yy})`}>
     <path d={`M 0 -34 Q 0 -78 ${xpos(day,n)-xx} ${ypos(c.input[day])-yy+20}`} stroke={C.blue} strokeWidth={1.2} fill="none" strokeDasharray="5 5" opacity={.22}/>
     <rect x={-101} y={-34} width={202} height={68} rx={16} fill={C.surface} stroke={isPush?C.gold:C.blue} strokeWidth={2}/>
     <T x={0} y={10} size={26} anchor="middle" color={isPush?C.gold:C.text}>第{day+1}天 · {c.input[day]}</T>
    </g>;
   })}
   {e.pending.length===0&&!movingPop&&<T x={580} y={836} color={C.gold}>空：没有旧天可比较</T>}
   {e.pending.length>0&&<T x={1425} y={835} size={24} color={C.muted}>末尾先检查 ←</T>}
  </g>}
  {compare&&e.previous!==undefined&&e.previous!==null&&<g>
   <rect x={1300} y={232} width={480} height={62} rx={14} fill={C.surface} stroke={e.reason==='warmer'?C.teal:C.gold}/>
   <T x={1540} y={273} size={27} anchor="middle" color={e.reason==='warmer'?C.teal:C.gold}>
    {e.temperature} {e.reason==='warmer'?'>':e.reason==='equal'?'=':'<'} {c.input[e.previous]} · {e.reason==='warmer'?'可以解决':e.reason==='equal'?'相等，不移出':'不够暖，停止'}
   </T>
  </g>}
 </g>;
}

const HEADS:Record<string,[string,string]>={
 'stack-basics':['同一端，加入和取出','只演示这些日期怎样保存；先不计算等待天数'],
 monotone:['这些待解决日的温度，怎样排列？','先把刚取出的第5天放回；原输入没有排序'],
 problem:['每天要等多久，才会更暖？','连续八天的气温 · 只看未来第一个严格更高的温度'],
 output:['返回等待天数','日期之间的距离，就是这一天的答案'],
 repeat:['每天往后找，重复在哪里？','先查看，再留下还没等到答案的天'],
 order:['新来的一天，先解决最近的等待','更早留下的温度 ≥ 最近留下的温度'],
 name:['按温度有序，保留未解决的天','较早较高的在左，最近的一天在末尾'],
 'first-days':['从第一天开始执行','同一教学输入重新开始 · 所有答案最初为 0'],
 cooler:['更暖就解决，较凉就继续等','第3天解决第2天；第4、5天暂时没有答案'],
 multiple:['一天，可以解决不止一天','第6天的32依次比较30、31、35'],
 warmer:['第7天的36，让两天等到答案','每次移出一个下标，写回它自己的日期位置'],
 finish:['日期走完，剩下的答案保留零','第7天、第8天都没有未来更暖的日子'],
 equality:['另一个小例子：相等不算更暖','新输入 · 30，30，31 · 状态从头开始'],
 earliest:['为什么一定是“第一个”？','回到八天主例 · 此前都没有更暖，直到第7天出现36'],
 cost:['每个下标，只加入一次','找到答案后移出最多一次；无需每天重查所有未来'],
 closing:['严格更暖才解决，日期差写回原位','原来的日子保留，答案也回到原来的位置'],
};
function Scene({shot:s}:{shot:Shot}){
 const f=useCurrentFrame(),t=s.visualType,p=phase(s,f),q=phase(s,f,1);
 const title=t==='stack-basics'&&f>=(s.cueFrames?.labels?.['栈']??at(s,1,0))?['栈：后放的先取','左侧是栈底；右侧是栈顶，加入和取出都在这里']:t==='monotone'&&f>=(s.cueFrames?.labels?.['单调']??at(s,1,0))?['单调：从栈底到栈顶不升','这里选择温度不升的顺序，允许相等']:HEADS[t]??['每日温度',''];
 const chapter=({problem:'先看题目要什么',derive:'为什么这样保存',walk:'按天走完整过程',code:'写回程序'} as any)[s.chapterId];
 if(s.codeCardFrom!==undefined&&f>=s.codeCardFrom)return <CodeCard/>;
 const pbCfg=PLAYBACK[t];
 let body:React.ReactNode=null;
 if(pbCfg){
  const c=pbCfg.caseName==='equality'?EQUALITY:MAIN;
  const pb=playback(s,f,c,pbCfg.initial,pbCfg.beats);
  const finishing=pb.event.type==='finish';
  const notes:Record<string,string>={
   'first-days':pb.event.id<=1?'空栈先加入；没有旧天可比较':'温度更暖 → 移出旧天 → 原位写1 → 留下今天',
   cooler:pb.event.id<12?'第2天等1天，写回第2天':'较凉，无法解决更高的旧气温；留下自己',
   multiple:pb.event.id<19?'先解决第5天：6 − 5 = 1':'再解决第4天：6 − 4 = 2；遇35停止',
   warmer:pb.event.id<27?'第6天：7 − 6 = 1':'第3天：7 − 3 = 4，答案是天数',
   finish:finishing?'剩余第7、8天：没有未来更暖 → 保持0':'第8天33 < 第7天36，不能解决',
   equality:pb.event.id<4?'30 = 30，没有严格更暖；两天都要保留':'31更暖，先解决第2天，再解决第1天',
  };
  body=<><Weather c={c} pb={pb} showPending showZeros={finishing}/><Note color={finishing?C.teal:C.gold}>{notes[t]}</Note></>;
 } else if(t==='stack-basics'||t==='monotone'){
  body=<><Weather allVisible current={4} focus={[2,3,4]} showAnswers={false}/><StackPrimer shot={s} frame={f}/></>;
 } else if(t==='problem'){
  const scanning=Math.min(3,Math.floor(q*4)),look=[3,4,5,6][scanning];
  body=<><Weather allVisible current={2} focus={[2]} showAnswers={false} scan={look}/><Note color={C.gold}>第三天之后，哪一天第一次比35更高？</Note></>;
 } else if(t==='output'){
  body=<><Weather allVisible current={2} focus={[2,6]} pb={state(MAIN,34)} span={{from:2,to:6,p:p,label:'7 − 3 = 4 天'}} showZeros={q>.3} zeroReveal={q>.65?2:1}/><Note color={C.teal}>第3天的答案是4；末两天没有未来更暖，填0</Note></>;
 } else if(t==='repeat'){
  const from=q>.01?3:2,step=Math.min(from===2?3:1,Math.floor((q>.01?q:p)*(from===2?4:2))),look=(from===2?[3,4,5,6]:[4,5])[step];
  body=<><Weather allVisible current={from} focus={q>.6?[2,3,4]:[from]} scan={look} showAnswers={false}/><g opacity={p}><path d={`M ${xpos(3,8)} 778 H ${xpos(6,8)}`} stroke={C.gold} strokeWidth={3} strokeDasharray="8 8"/><T x={930} y={830} anchor="middle" color={C.gold}>又看到了同样的后几天</T></g><Note>按日期前进，把问题留给新来的一天</Note></>;
 } else if(t==='order'){
  const pb=playback(s,f,MAIN,15,[[0,.10,16],[0,.26,17],[0,.42,18],[0,.56,19],[0,.72,20],[0,.85,21],[1,.10,22],[1,.55,23]]);
  body=<><Weather pb={state(MAIN,23)} current={5} focus={pb.event.previous!==null&&pb.event.previous!==undefined?[pb.event.previous]:[]} allVisible showAnswers={false}/><OrderPrimer playback={pb}/></>;
 } else if(t==='name'){
  const named=f>=(s.cueFrames?.labels?.['单调栈']??at(s,1,0));
  body=<><Weather pb={state(MAIN,23)} current={5} showPending stackNamed={named} showAnswers={false} allVisible focus={[2,5]}/><T x={1410} y={788} size={32} color={C.gold} opacity={p}>35 ≥ 32</T><Note color={named?C.teal:C.gold}>{named?'单调栈 · 存下标，末尾先检查，解决后移出':'只动末尾，并保持温度从底到顶不升'}</Note></>;
 } else if(t==='earliest'){
  const look=[3,4,5,6][Math.min(3,Math.floor(q*4))];
  body=<><Weather pb={state(MAIN,34)} allVisible current={2} focus={[2]} scan={look} span={q>.8?{from:2,to:6,p:clamp((q-.8)*5),label:'此前没解决，第一次更暖就是现在'}:undefined}/><Note color={C.teal}>第4、5、6天都不更暖 → 第7天第一次满足</Note></>;
 } else if(t==='cost'){
  body=<><Weather pb={state(MAIN,34)} allVisible showAnswers={false} cost={Math.min(7,Math.floor(p*8))}/><Note color={C.teal}>{q>.25?'时间 O(n) · 额外空间 O(n)':'本例：8次加入，6次移出；每一天都只处理一次入栈'}</Note></>;
 } else if(t==='closing'){
  body=<><Weather pb={state(MAIN,34)} allVisible showZeros span={{from:2,to:6,p:p,label:'today − previous'}}/><Note color={C.teal}>answer[previous] = today - previous</Note></>;
 }
 const sub=(s.subtitles??[]).find(v=>f>=v.from&&f<(v.to!==undefined?v.to+1:v.from+(v.duration??0)));
 return <svg width={1920} height={1080} viewBox="0 0 1920 1080">
  <rect width={1920} height={1080} fill={C.bg}/>
  <Header title={title[0]} detail={title[1]} kicker={chapter}/>
  {body}
  <T x={1795} y={906} size={20} color={C.muted} anchor="end">教学示例 · 未指定单位</T>
 </svg>;
}
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=>{
 const f=useCurrentFrame();
 const shot=shots.find(s=>f>=s.from&&f<s.from+s.durationInFrames)??shots[shots.length-1];
 const local=f-shot.from;
 const card=shot.codeCardFrom!==undefined&&local>=shot.codeCardFrom;
 const sub=(shot.subtitles??[]).find(v=>local>=v.from&&local<(v.to!==undefined?v.to+1:v.from+(v.duration??0)));
 const pending=Boolean((STORYBOARD.meta as any).pendingAudio);
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
  {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&!pending&&<Audio src={staticFile('audio/voice.wav')}/>}
  {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><Scene shot={s}/></Sequence>)}
  {!hideSubtitles&&!card&&sub&&<div style={{position:'absolute',left:110,right:110,bottom:33,minHeight:67,display:'flex',alignItems:'center',justifyContent:'center',padding:'9px 22px',borderRadius:14,background:'#07111EEB',color:C.text,fontSize:32,lineHeight:1.5,textAlign:'center'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
