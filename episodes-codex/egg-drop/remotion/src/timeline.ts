import {clamp,mix,STAGES} from './egg-model';
export type Window={start:number;ready:number;release:number;land:number;commit:number;end:number};
export const cues=(s:any)=>{
 const q=s.cueFrames?.sentences??s.subtitles?.map((x:any)=>x.from)??[8,Math.round(s.durationInFrames*.5)];
 const a=typeof q[0]==='number'?q[0]:(q[0]?.frame??8),b=typeof q[1]==='number'?q[1]:(q[1]?.frame??Math.round(s.durationInFrames*.5));
 const voice=s.voice??[];
 return {first:a,second:b,firstEnd:voice[0]?.localEnd??b-16,secondEnd:voice[1]?.localEnd??s.durationInFrames-30,end:s.durationInFrames-1};
};
export const window=(start:number,end:number):Window=>({start,ready:Math.round(mix(start,end,.19)),release:Math.round(mix(start,end,.34)),land:Math.round(mix(start,end,.73)),commit:Math.round(mix(start,end,.86)),end});
export const spread=(count:number,start:number,end:number)=>Array.from({length:count},(_,i)=>window(Math.round(mix(start,end,i/count)),Math.round(mix(start,end,(i+1)/count))-2));
export const actionWindows=(s:any):Window[]=>{
 const c=cues(s),end=c.secondEnd-12;
 switch(s.visualType){
  case 'rules':return spread(2,c.first+12,c.firstEnd-8);
  case 'fixed-ten-plan':return [window(c.second+52,c.secondEnd-24)];
  case 'late-break-cost':return [window(Math.max(70,c.first+12),c.firstEnd-8)];
  case 'first-fourteen':return [{start:c.first+12,ready:Math.min(c.firstEnd-12,c.first+70),release:c.second+12,land:c.second+62,commit:c.second+79,end:Math.min(end,c.second+103)}];
  case 'next-twenty-seven':return [window(c.second+8,Math.min(end,Math.round(c.second+(c.secondEnd-c.second)*.44)))];
  case 'actual-first-egg':return [...spread(2,Math.max(32,c.first+12),c.firstEnd-8),window(c.second+8,Math.min(end,Math.round(c.second+(c.secondEnd-c.second)*.5)))];
  case 'actual-linear':return [window(Math.max(58,c.first+12),c.firstEnd-8),...spread(3,c.second+6,Math.min(end,Math.round(c.second+(c.secondEnd-c.second)*.78)))];
  case 'threshold-found':return [window(c.first+10,c.firstEnd-8)];
  default:return [];
 }
};
export const progress=(f:number,w:Window)=>{
 const points=[[w.start,0],[w.ready,STAGES.carry],[w.release,STAGES.release],[w.land,STAGES.land],[w.commit,STAGES.commit],[w.end,1]];
 if(f<=w.start)return 0;if(f>=w.end)return 1;
 for(let i=1;i<points.length;i++)if(f<=points[i][0])return mix(points[i-1][1],points[i][1],clamp((f-points[i-1][0])/(points[i][0]-points[i-1][0])));
 return 1;
};
