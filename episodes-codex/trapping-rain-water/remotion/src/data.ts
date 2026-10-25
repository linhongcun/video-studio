import storyboard from '@storyboard';
import lesson from './lesson.json';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;from:number;durationInFrames:number;visualType:string;chapterId:string;cueFrames?:{sentences?:number[];labels?:Record<string,number>};subtitles?:Subtitle[];codeCardFrom?:number;[key:string]:any};
export type TraceEvent={index:number;stage:string;i:number;height:number[];left:number[];right:number[];highest:number;total:number;totalBefore:number;level:number|null;depth:number|null;water:number[]};
let offset=0;
export const SHOTS:Shot[]=(storyboard.scenes??[]).flatMap((scene:any)=>scene.shots??[]).map((shot:any)=>{const item={...shot,id:String(shot.id).padStart(2,'0'),from:offset};offset+=shot.durationInFrames;return item;});
export const STORYBOARD=storyboard;
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:offset};
export const DEMO=lesson;
export const HEIGHT=lesson.height;
export const EVENTS=lesson.events as TraceEvent[];
export const INITIAL:TraceEvent={index:0,stage:'initial',i:0,height:HEIGHT,left:HEIGHT.map(()=>0),right:HEIGHT.map(()=>0),highest:0,total:0,totalBefore:0,level:null,depth:null,water:HEIGHT.map(()=>0)};
/** Only select observed solution.py snapshots; this file does not compute maxima or solve water. */
export const event=(index:number):TraceEvent=>{
 if(index===0)return INITIAL;
 const value=EVENTS[index-1];
 if(value?.index!==index)throw new Error(`Missing observed source event ${index}`);
 return value;
};
export const FINAL=event(EVENTS.length);
export const clamp=(value:number)=>Math.max(0,Math.min(1,value));
export const span=(value:number,from:number,to:number)=>clamp((value-from)/Math.max(1,to-from));
export const sentence=(shot:Shot,index:number)=>shot.cueFrames?.sentences?.[index]??(index===0?0:Math.round(shot.durationInFrames/2));
/** A pedagogical preview is outlined; the real snapshot commits only after the whole column is shown. */
export const observedStep=(first:number,last:number,progress:number)=>{
 const p=clamp(progress),count=last-first+1;
 const position=Math.min(count-1,Math.floor(p*count));
 const fraction=p===1?1:p*count-position;
 const target=event(first+position);
 const committed=fraction>=.70;
 return {target,snapshot:committed?target:event(target.index-1),fraction,committed};
};
