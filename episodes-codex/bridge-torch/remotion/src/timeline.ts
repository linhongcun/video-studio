import type {Shot} from './data';
const sentence=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?s.durationInFrames*.5:0));
export const crossingWindow=(s:Shot)=>{
 const second=sentence(s,1);
 // The first 12% is a stable preparation/hand-off. Actual departure starts after sentence 2.
 if(s.visualType==='fastest-first')return{start:second-8,end:s.durationInFrames-24,count:2,index:0,strategy:'greedy' as const};
 if(s.visualType==='fastest-middle')return{start:sentence(s,0)+10,end:Math.min(s.durationInFrames-24,second+28),count:2,index:2,strategy:'greedy' as const};
 if(s.visualType==='nineteen')return{start:sentence(s,0)+12,end:second+24,count:1,index:4,strategy:'greedy' as const};
 const index=['quick-pair-out','one-returns','slow-pair-out','two-returns','quick-pair-finish'].indexOf(s.visualType);
 if(index>=0)return{start:sentence(s,0)+16,end:second+24,count:1,index,strategy:'optimal' as const};
 return null;
};
export const crossingAt=(s:Shot,f:number)=>{
 const window=crossingWindow(s);if(!window)return null;
 const span=Math.max(window.count*85,window.end-window.start),raw=Math.max(0,Math.min(1,(f-window.start)/span))*window.count,part=Math.min(window.count-1,Math.floor(raw));
 return{...window,span,index:window.index+part,progress:Math.max(0,Math.min(1,raw-part))};
};
