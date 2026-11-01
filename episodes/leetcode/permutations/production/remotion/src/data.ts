import storyboard from '@storyboard';
import lesson from './lesson.json';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;from:number;durationInFrames:number;visualType:string;chapterId:string;cueFrames?:{sentences:number[];labels?:Record<string,number>};subtitles?:Subtitle[];codeCardFrom?:number;[key:string]:any};
export type TraceEvent={index:number;action:string;candidate:number|null;candidateIndex:number|null;path:number[];used:boolean[];answers:number[][];depth:number};
let offset=0;
export const shots:Shot[]=storyboard.scenes.flatMap((s:any)=>s.shots).map((s:any)=>{const sh={...s,id:String(s.id).padStart(2,'0'),from:offset};offset+=sh.durationInFrames;return sh;});
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:offset};
export const STORYBOARD=storyboard;
export const EVENTS=lesson.events as TraceEvent[];
export const INPUT=lesson.input;
export const event=(i:number):TraceEvent=>{const e=EVENTS[i];if(e?.index!==i)throw new Error(`Missing observed permutation event ${i}`);return e;};
export type Motion={previous:TraceEvent;next:TraceEvent;progress:number;moving:boolean};
export const still=(i:number):Motion=>({previous:event(i),next:event(i),progress:1,moving:false});
const weight=(action:string)=>action==='choose'||action==='unchoose'?3:action==='save-copy'?4:action==='skip-used'?1:0.6;
/** Playback of recorded snapshots only; no permutation algorithm lives in TypeScript. */
export const playback=(from:number,to:number,progress:number):Motion=>{
 if(from===to||progress<=0)return still(from);
 if(progress>=1)return still(to);
 const list=EVENTS.slice(from+1,to+1);const total=list.reduce((sum,e)=>sum+weight(e.action),0);let distance=progress*total;
 for(const item of list){const w=weight(item.action);if(distance<w){const p=Math.min(1,distance/w*1.4);return{previous:event(item.index-1),next:item,progress:p,moving:p<1};}distance-=w;}
 return still(to);
};
export const PHASES:Record<string,[[number,number],[number,number]]>={
 '05':[[0,2],[2,6]],'06':[[6,12],[12,12]],'07':[[12,14],[14,14]],'08':[[14,14],[14,17]],'09':[[17,20],[20,22]],'10':[[22,29],[29,54]],'11':[[54,72],[72,82]],
};
export const shotMotion=(shot:Shot,frame:number):Motion=>{
 const phases=PHASES[shot.id];if(!phases)return still(shot.id==='13'?14:82);
 const second=shot.cueFrames?.sentences?.[1]??Math.round(shot.durationInFrames/2);
 const start=frame<second?0:second;const end=frame<second?second:shot.durationInFrames;
 const pair=phases[frame<second?0:1];return playback(pair[0],pair[1],Math.max(0,Math.min(1,(frame-start-4)/Math.max(1,end-start-22))));
};
