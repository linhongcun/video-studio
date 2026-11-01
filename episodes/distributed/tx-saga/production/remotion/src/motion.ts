import type {Shot} from './data';
export const at=(s:Shot,i:number,r:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[i]??0),b=Number(starts[i+1]??s.durationInFrames-15);
 return Math.round(a+(b-a)*r);
};
export const events=(s:Shot):[string,number][]=>{
 const p=(i:number,r:number)=>at(s,i,r);
 return ({
  charge:[['charge-local-commit',p(0,.68)]],
  stock:[['stock-local-commit',p(0,.68)],['order-confirmed',p(1,.62)]],
  failure:[['charge-local-commit',p(0,.63)],['stock-business-rejected',p(1,.56)]],
  'already-committed':[['refund-planned',p(1,.45)]],
  compensation:[['refund-request-arrives',p(1,.68)]],
  refund:[['refund-local-commit',p(0,.67)],['original-and-refund-visible',p(1,.34)]],
  duplicate:[['duplicate-refund-recognized',p(0,.67)],['local-dedup-boundary',p(1,.44)]],
  'refund-failed':[['refund-attempt-failed',p(1,.5)]],
  recover:[['program-interrupted',p(0,.62)],['progress-restored',p(1,.22)],['repeated-failure-escalated',p(1,.72)]],
  boundary:[['intermediate-value-read',p(0,.68)],['suitable-business-boundary',p(1,.6)]],
 } as Record<string,[string,number][]>)[s.visualType]??[];
};
export const eventAt=(s:Shot,n:string)=>events(s).find(([k])=>k===n)?.[1]??0;
