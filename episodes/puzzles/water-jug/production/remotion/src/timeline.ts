import type {Shot} from './data';
const cue=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?s.durationInFrames/2:0));
export const operationWindow=(s:Shot)=>{
 const index=['fill-five','make-two','empty-small','save-two','refill-five','pour-one'].indexOf(s.visualType);if(index<0)return null;
 const start=index===2?cue(s,1)-8:cue(s,0)+12,end=index===2?s.durationInFrames-38:cue(s,1)+24;
 return{index,start,span:Math.max(120,end-start)};
};
export const operationProgress=(s:Shot,f:number)=>{
 const w=operationWindow(s);return w?{...w,progress:Math.max(0,Math.min(1,(f-w.start)/w.span))}:null;
};
