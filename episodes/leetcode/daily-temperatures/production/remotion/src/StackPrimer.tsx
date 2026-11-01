import React from 'react';
import {Shot,MAIN,TraceEvent} from './data';
import operations from '../../research/stack-primer-operations.json';
import {C,FONT,MONO} from './theme';

const clip=(p:number)=>Math.max(0,Math.min(1,p));
const smooth=(p:number)=>{p=clip(p);return p*p*(3-2*p);};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const position=(i:number)=>580+i*235;
const stagingX=1370, rowY=826;
const X=(i:number)=>245+i*195;
const Y=(v:number)=>620-(v-28)*31;
const Text=({x,y,children,size=28,color=C.text,anchor='start',opacity=1,mono=false,weight=500}:any)=><text x={x} y={y} fontFamily={mono?MONO:FONT} fontSize={size} fill={color} textAnchor={anchor} opacity={opacity} fontWeight={weight}>{children}</text>;
const clock=(s:Shot,i:number,p:number)=>{
 const first=s.cueFrames?.sentences?.[i]??(i?s.durationInFrames*.5:0);
 const last=s.cueFrames?.sentences?.[i+1]??s.durationInFrames-10;
 return first+(last-first)*p;
};
type ConceptEvent={id:number;operation:string;before:number[];after:number[];day:number|null;removed:number|null;temperature?:number};
type RowProps={before:number[];after:number[];day:number|null;operation:string;progress:number;named:boolean;stagedDay?:number|null;topFocus?:number|null};

// Same date markers and original chart anchors. The only movement lane is the
// dedicated row at y826; it never passes through date labels or answer positions.
const StackRow=({before,after,day,operation,progress,named,stagedDay=null,topFocus=null}:RowProps)=>{
 const p=progress;
 const ids=Array.from(new Set([...before,...after,...(stagedDay!==null?[stagedDay]:[])]));
 // The top marker belongs to a record already resident in the stack.
 // An arriving card does not become the top until it reaches its final slot;
 // a removed card is in transit, so pop points directly to the remaining top.
 const topEntries=operation==='append'&&p<1?before:after;
 const top=topEntries.length>0?position(topEntries.length-1):null;
 return <g data-stack-primer-operation={operation} data-stack-primer-pending={after.join(',')}>
  <Text x={120} y={819} size={27} color={C.muted}>{named?'栈':'保存位置'}</Text>
  <Text x={120} y={859} size={22} color={C.muted}>原来的日期</Text>
  <path d={`M 465 783 V 870 H ${position(Math.max(0,after.length-1))+112}`} fill="none" stroke={C.edge} strokeWidth={2}/>
  {(before.length>0||after.length>0)&&<>
   <Text x={460} y={758} size={26} color={C.blue} anchor="end">{named?'栈底':'最先放入'}</Text>
  </>}
  {top!==null&&<>
   <Text x={top} y={720} size={27} color={C.gold} anchor="middle">{named?'栈顶':'末尾操作'}</Text>
   <path d={`M ${top} 734 V 773 M ${top-8} 763 L ${top} 773 L ${top+8} 763`} fill="none" stroke={C.gold} strokeWidth={2.5}/>
  </>}
  {ids.map(item=>{
   const oldIndex=before.indexOf(item),newIndex=after.indexOf(item);
   const entering=operation==='append'&&item===day&&oldIndex<0;
   const leaving=operation==='pop'&&item===day;
   const parked=item===stagedDay&&newIndex<0&&!leaving;
   const from=entering?stagingX:oldIndex>=0?position(oldIndex):stagingX;
   const to=leaving||parked?stagingX:position(Math.max(0,newIndex));
   const xx=mix(from,to,p),highlight=entering||leaving||parked||topFocus===item;
   return <g key={item} transform={`translate(${xx} ${rowY})`} data-primer-day={item+1}>
    <path d={`M 0 -34 Q 0 -78 ${X(item)-xx} ${Y(MAIN.input[item])-rowY+20}`} stroke={C.blue} strokeWidth={1.2} strokeDasharray="5 5" opacity={.22} fill="none"/>
    <rect x={-101} y={-34} width={202} height={68} rx={16} fill={C.surface} stroke={highlight?C.gold:C.blue} strokeWidth={2}/>
    <Text x={0} y={10} size={26} anchor="middle" color={highlight?C.gold:C.text}>第{item+1}天 · {MAIN.input[item]}</Text>
   </g>;
  })}
  {after.length===0&&ids.length===0&&<Text x={580} y={836} color={C.muted}>还没有放入</Text>}
 </g>;
};

function conceptPlayback(s:Shot,f:number){
 const kind=s.visualType;
 const beats:([number,number,number])[]=kind==='stack-basics'?[[0,.12,1],[0,.39,2],[0,.68,3],[1,.36,4]]:[[0,.12,5]];
 let id=kind==='stack-basics'?0:4,start=0,next=s.durationInFrames-10;
 for(let i=0;i<beats.length;i++){
  const [sentence,fraction,event]=beats[i],frame=clock(s,sentence,fraction);
  if(f<frame){next=frame;break;}
  id=event;start=frame;next=i+1<beats.length?clock(s,beats[i+1][0],beats[i+1][1]):s.durationInFrames-10;
 }
 const progress=id===0||kind==='monotone'&&id===4?1:smooth((f-start)/Math.max(1,Math.min(24,(next-start)*.7)));
 return {event:operations.events[id] as ConceptEvent,progress};
}

export const StackPrimer=({shot:s,frame:f}:{shot:Shot;frame:number})=>{
 const {event:e,progress}=conceptPlayback(s,f),basics=s.visualType==='stack-basics';
 const named=!basics||f>=(s.cueFrames?.labels?.['栈']??clock(s,1,0));
 const monotoneNamed=f>=(s.cueFrames?.labels?.['单调']??clock(s,1,0));
 const second=smooth((f-clock(s,1,.03))/Math.max(1,clock(s,1,.78)-clock(s,1,.03)));
 const restored=e.id===5&&progress===1;
 const removed=e.operation==='pop'?e.day:null;
 return <g data-concept-source="research/stack-primer-operations.json" data-concept-event={e.id}>
  <StackRow before={e.before} after={e.after} day={e.day} operation={e.operation} progress={progress} named={named} stagedDay={removed}/>
  {basics?<>
   <Text x={1370} y={760} size={26} color={C.gold} anchor="middle">{e.operation==='pop'?'只从末尾取出':e.id>0?'只从末尾加入':'右侧是操作端'}</Text>
   {e.operation==='pop'&&progress>.7&&<Text x={1370} y={715} size={23} color={C.gold} anchor="middle">刚取出 · 第5天</Text>}
   {named&&<Text x={960} y={268} size={31} color={C.teal} anchor="middle">后放的先取 · 后进先出</Text>}
  </>:<>
   <Text x={1370} y={760} size={25} color={C.gold} anchor="middle" opacity={monotoneNamed?0:1}>{restored?'仍是原来的日期顺序':'把第5天放回末尾'}</Text>
   <Text x={960} y={268} size={34} color={C.gold} anchor="middle" opacity={restored?1:0}>35 ≥ 31 ≥ 30</Text>
   {monotoneNamed&&<g opacity={clip(second*4)} data-equal-temperature-relation="separate-example">
    <rect x={1410} y={690} width={340} height={187} rx={18} fill={C.surface} stroke={C.edge}/>
    <Text x={1580} y={722} size={23} color={C.muted} anchor="middle">相等关系 · 另例</Text>
    {[0,1].map(i=><g key={i}><line x1={1485+i*190} x2={1485+i*190} y1={785} y2={831} stroke={C.teal} strokeWidth={18} opacity={.25}/><circle cx={1485+i*190} cy={785} r={8} fill={C.bg} stroke={C.teal} strokeWidth={3}/><Text x={1485+i*190} y={768} size={32} color={C.teal} anchor="middle" mono>{operations.equalityRelation.values[i]}</Text></g>)}
    <Text x={1580} y={802} size={31} color={C.teal} anchor="middle">=</Text>
    <Text x={1580} y={858} size={23} color={C.muted} anchor="middle">相等也没有升高</Text>
   </g>}
  </>}
  <Text x={960} y={902} size={28} color={C.muted} anchor="middle">保存规则示意 · 先不写天数</Text>
 </g>;
};

type ActualPlayback={event:TraceEvent;previous:TraceEvent;progress:number;eventFrame:number};
export const OrderPrimer=({playback:pb}:{playback:ActualPlayback})=>{
 const e=pb.event,old=pb.previous;
 const moving=e.type==='push'?'append':e.type==='pop'?'pop':'hold';
 const day=e.type==='push'?e.today:e.type==='pop'||e.type==='resolve'?e.previous??null:null;
 const staged=e.type==='pop'||e.type==='resolve'?e.previous??null:null;
 const before=e.type==='push'||e.type==='pop'?old.pending:e.pending;
 const reason=e.type==='compare'?e.reason:null;
 const note=e.id<16?'新来的32，先看末尾30':e.id<19?'32 > 30：先取出第5天':e.id<22?'32 > 31：再取出第4天':e.id<23?'32 < 35：保留35，停止取出':'把第6天32加入末尾，仍有35 ≥ 32';
 return <g data-algorithm-trace-event={e.id} data-source-line={e.sourceLine}>
  <StackRow before={before} after={e.pending} day={day} operation={moving} progress={pb.progress} named={false} stagedDay={staged} topFocus={reason?e.previous??null:null}/>
  {reason&&e.previous!==null&&e.previous!==undefined&&<>
   <Text x={1510} y={737} size={32} color={reason==='warmer'?C.teal:C.gold} anchor="middle" mono>32 {reason==='warmer'?'>':'<'} {MAIN.input[e.previous]}</Text>
   <Text x={1510} y={777} size={24} color={reason==='warmer'?C.teal:C.gold} anchor="middle">{reason==='warmer'?'更暖，可以取出':'不够暖，保留并停止'}</Text>
  </>}
  <Text x={960} y={902} size={28} color={e.id>=23?C.teal:C.gold} anchor="middle">{note}</Text>
 </g>;
};
