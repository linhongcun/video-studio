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
 const second=s.cueFrames?.sentences?.[1]??clock(s,1,0);
 // No data-structure name is shown here: these are still the problem's
 // waiting dates. Sentence-prefix cues are acoustic anchors, not word ASR.
 // Reveal the relationship after the sentence has explained which dates stay.
 // This fraction is an editorial beat inside the real sentence envelope.
 const relationOpacity=clip((f-clock(s,1,.61))/8);
 const relationPhase=clip((f-clock(s,1,.20))/Math.max(1,clock(s,1,.65)-clock(s,1,.20)));
 const focusedDay=f<second?null:[2,3,4][Math.min(2,Math.floor(relationPhase*3))];
 const ids=Array.from(new Set([...e.before,...e.after]));
 // Point at the most recent resident waiting date; arriving records become
 // the endpoint only when they land. No stack operation is assumed here.
 const resident=e.id===1||p===1?e.after:e.before;
 const top=resident.length?position(resident.length-1):null;
 return <g data-concept-source="research/stack-primer-operations.json" data-concept-event={e.id} data-problem-fit-intro="pending-dates">
  <Text x={120} y={819} size={27} color={C.muted}>等待的日期</Text>
  <Text x={120} y={859} size={22} color={C.muted}>走到第5天 · 保留原日期</Text>
  <path d={`M 465 783 V 870 H ${position(e.after.length-1)+112}`} fill="none" stroke={C.edge} strokeWidth={2}/>
  {top!==null&&<>
   <Text x={top} y={720} size={27} color={C.gold} anchor="middle">最近留下的日子</Text>
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
  {f<second&&<Text x={1370} y={760} size={26} color={C.gold} anchor="middle">较凉，尚未等到答案</Text>}
  <g opacity={relationOpacity}>
   <Text x={960} y={268} size={34} color={C.gold} anchor="middle">35 ≥ 31 ≥ 30</Text>
  </g>
  <Text x={960} y={902} size={28} color={C.muted} anchor="middle">{f<second?'第3、4、5天尚未解决，按日期留下 · 先不写天数':'更暖就解决低温日，较凉就留下 · 接着看新来的32'}</Text>
 </g>;
};
