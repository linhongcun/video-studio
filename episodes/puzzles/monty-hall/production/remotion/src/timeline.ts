import type {Shot} from './data';
import type {Progress} from './monty-model';
const clamp=(p:number)=>Math.max(0,Math.min(1,p));
const part=(f:number,a:number,b:number)=>clamp((f-a)/Math.max(1,b-a));
const cue=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?s.durationInFrames/2:0));
const sentenceEnd=(s:Shot,i:number)=>Number(s.voice?.[i]?.localEnd??(i?s.durationInFrames-24:cue(s,1)-14));
export const gameProgress=(s:Shot,f:number):Progress=>{
 const type=s.visualType,first=cue(s,0),second=cue(s,1);
 if(type==='hook'||type==='host-rules')return{pick:0,host:0,swap:0,reveal:0};
 if(type==='example-open'){const pick=part(f,first+8,first+35),host=part(f,first+47,Math.max(first+95,Math.floor(sentenceEnd(s,0)-5)));return{pick,host,swap:0,reveal:0};}
 if(type==='example-switch'||type==='right-switch-loses'){
  const start=first+8,revealEnd=Math.floor(sentenceEnd(s,0)-5),available=revealEnd-start,swapEnd=start+available*.64,revealStart=swapEnd+8;
  return{pick:1,host:1,swap:part(f,start,swapEnd),reveal:part(f,revealStart,revealEnd)};
 }
 if(type==='initially-right')return{pick:1,host:part(f,second+10,Math.min(s.durationInFrames-35,second+95)),swap:0,reveal:0};
 if(type==='initially-wrong-three'){
  const start=second+8,end=Math.min(s.durationInFrames-30,Math.floor(sentenceEnd(s,1)-5)),available=end-start,hostEnd=start+available*.24,swapStart=hostEnd+10,swapEnd=start+available*.76,revealStart=swapEnd+9;
  return{pick:1,host:part(f,start,hostEnd),swap:part(f,swapStart,swapEnd),reveal:part(f,revealStart,end)};
 }
 return{pick:1,host:1,swap:1,reveal:1};
};
export const morphProgress=(s:Shot,f:number)=>part(f,cue(s,0)+12,Math.max(cue(s,0)+90,cue(s,1)+8));
export const focusProgress=(s:Shot,f:number)=>part(f,cue(s,0)+8,Math.min(cue(s,1)-15,cue(s,0)+65));
export const additionProgress=(s:Shot,f:number)=>part(f,cue(s,1),s.durationInFrames-35);
