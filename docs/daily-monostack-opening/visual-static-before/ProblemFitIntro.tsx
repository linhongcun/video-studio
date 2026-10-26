import React from 'react';
import {Shot,MAIN} from './data';
import operations from '../../research/stack-primer-operations.json';
import {C,FONT,MONO} from './theme';

const clip=(p:number)=>Math.max(0,Math.min(1,p));
const smooth=(p:number)=>{p=clip(p);return p*p*(3-2*p);};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const position=(i:number)=>580+i*235;
const stagingX=1370,rowY=826;
const X=(i:number)=>245+i*195;
const Y=(v:number)=>620-(v-28)*31;
const Text=({x,y,children,size=28,color=C.text,anchor='start',opacity=1,mono=false,weight=500}:any)=><text x={x} y={y} fontFamily={mono?MONO:FONT} fontSize={size} fill={color} textAnchor={anchor} opacity={opacity} fontWeight={weight}>{children}</text>;
const clock=(s:Shot,i:number,p:number)=>{
 const first=s.cueFrames?.sentences?.[i]??(i?s.durationInFrames*.5:0);
 const last=s.cueFrames?.sentences?.[i+1]??s.durationInFrames-10;
 return first+(last-first)*p;
};
type AppendEvent={id:number;operation:string;before:number[];after:number[];day:number|null};

// This is a view of the existing, actually executed append snapshots. The 35
// record is already resident; 31 and 30 arrive in the same first sentence.
// There is no illustrative pop/restore and no second solution implementation.
function pendingDates(s:Shot,f:number){
 const beats:[number,number,number][]=[[0,.27,2],[0,.61,3]];
 let id=1,start=0,next=s.durationInFrames-10;
 for(let i=0;i<beats.length;i++){
  const [sentence,fraction,event]=beats[i],frame=clock(s,sentence,fraction);
  if(f<frame){next=frame;break;}
  id=event;start=frame;next=i+1<beats.length?clock(s,beats[i+1][0],beats[i+1][1]):s.durationInFrames-10;
 }
 const progress=id===1?1:smooth((f-start)/Math.max(1,Math.min(24,(next-start)*.7)));
 return {event:operations.events[id] as AppendEvent,progress};
}

export const ProblemFitIntro=({shot:s,frame:f}:{shot:Shot;frame:number})=>{
 const {event:e,progress:p}=pendingDates(s,f);
 const first=s.cueFrames?.sentences?.[0]??clock(s,0,0);
 const second=s.cueFrames?.sentences?.[1]??clock(s,1,0);
 // Labels use the shared sentence-onset cues. These are not word-level ASR
 // timestamps. The equality reveal is an editorial beat within sentence two.
 const topNamed=f>=(s.cueFrames?.labels?.['末尾就是栈顶']??first);
 const bottomNamed=f>=(s.cueFrames?.labels?.['末尾就是栈顶']??first);
 const relationNamed=f>=(s.cueFrames?.labels?.['本题让温度']??second);
 const relationOpacity=f<second?0:clip((f-second)/8);
 const equalOpacity=clip((f-clock(s,1,.76))/10);
 const relationPhase=clip((f-clock(s,1,.20))/Math.max(1,clock(s,1,.65)-clock(s,1,.20)));
 const focusedDay=f<second?null:[2,3,4][Math.min(2,Math.floor(relationPhase*3))];
 const ids=Array.from(new Set([...e.before,...e.after]));
 // An in-transit record is not yet the top. Keep pointing at the last
 // resident record, then change directly to the new top on landing.
 const resident=e.id===1||p===1?e.after:e.before;
 const top=resident.length?position(resident.length-1):null;
 return <g data-concept-source="research/stack-primer-operations.json" data-concept-event={e.id} data-problem-fit-intro="pending-dates">
  <Text x={120} y={819} size={27} color={C.muted}>{topNamed?'栈':'等待的日期'}</Text>
  <Text x={120} y={859} size={22} color={C.muted}>保留原来的日子</Text>
  <path d={`M 465 783 V 870 H ${position(e.after.length-1)+112}`} fill="none" stroke={C.edge} strokeWidth={2}/>
  {bottomNamed&&<Text x={460} y={758} size={26} color={C.blue} anchor="end">栈底</Text>}
  {top!==null&&<>
   <Text x={top} y={720} size={27} color={C.gold} anchor="middle">{topNamed?'栈顶':'末尾操作'}</Text>
   <path d={`M ${top} 734 V 773 M ${top-8} 763 L ${top} 773 L ${top+8} 763`} fill="none" stroke={C.gold} strokeWidth={2.5}/>
  </>}
  {ids.map(day=>{
   const entering=e.id>1&&day===e.day&&!e.before.includes(day);
   const target=position(e.after.indexOf(day));
   const xx=entering?mix(stagingX,target,p):target;
   const highlight=entering&&p<1||day===focusedDay;
   return <g key={day} transform={`translate(${xx} ${rowY})`} data-fit-pending-day={day+1} data-resident={!entering||p===1}>
    <path d={`M 0 -34 Q 0 -78 ${X(day)-xx} ${Y(MAIN.input[day])-rowY+20}`} stroke={C.blue} strokeWidth={1.2} strokeDasharray="5 5" opacity={.22} fill="none"/>
    <rect x={-101} y={-34} width={202} height={68} rx={16} fill={C.surface} stroke={highlight?C.gold:C.blue} strokeWidth={2}/>
    <Text x={0} y={10} size={26} anchor="middle" color={highlight?C.gold:C.text}>第{day+1}天 · {MAIN.input[day]}</Text>
   </g>;
  })}
  {f<second&&<Text x={1370} y={760} size={26} color={C.gold} anchor="middle">从同一个末尾放入或取出</Text>}
  <g opacity={relationOpacity}>
   <Text x={960} y={268} size={34} color={C.gold} anchor="middle">{relationNamed?'单调：35 ≥ 31 ≥ 30':'35 ≥ 31 ≥ 30'}</Text>
  </g>
  <g opacity={equalOpacity} data-equal-temperature-relation="separate-example" data-editorial-beat="sentence-two-late">
   <rect x={1410} y={690} width={340} height={187} rx={18} fill={C.surface} stroke={C.edge}/>
   <Text x={1580} y={722} size={23} color={C.muted} anchor="middle">相等关系 · 另例</Text>
   {[0,1].map(i=><g key={i}>
    <line x1={1485+i*190} x2={1485+i*190} y1={785} y2={831} stroke={C.teal} strokeWidth={18} opacity={.25}/>
    <circle cx={1485+i*190} cy={785} r={8} fill={C.bg} stroke={C.teal} strokeWidth={3}/>
    <Text x={1485+i*190} y={768} size={32} color={C.teal} anchor="middle" mono>{operations.equalityRelation.values[i]}</Text>
   </g>)}
   <Text x={1580} y={802} size={31} color={C.teal} anchor="middle">=</Text>
   <Text x={1580} y={858} size={23} color={C.muted} anchor="middle">相等也没有升高</Text>
  </g>
  <Text x={960} y={902} size={28} color={C.muted} anchor="middle">这些日子还在等待；新一天从栈顶开始检查</Text>
 </g>;
};
