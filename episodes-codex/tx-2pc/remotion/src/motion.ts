import type {Shot} from './data';
export const at=(s:Shot,i:number,p:number)=>{
 const a=Number(s.cueFrames?.sentences?.[i]??0);
 const b=Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-15);
 return Math.round(a+(b-a)*p);
};
export const events=(s:Shot):[string,number][]=>{
 const p=(i:number,r:number)=>at(s,i,r);
 return ({
  'hook':[['stock-operation-fails',p(0,.57)]],
  'prepare-request':[['order-work-ready',p(0,.58)],['stock-work-ready',p(1,.24)]],
  'prepared-votes':[['order-state-durable',p(0,.3)],['stock-state-durable',p(0,.72)],['order-ready-reply-arrives',p(1,.36)],['stock-ready-reply-arrives',p(1,.75)]],
  'durable-decision':[['commit-decision-durable',p(1,.57)]],
  'send-decision':[['final-commands-depart',p(1,.12)]],
  'apply-separately':[['order-commits-first',p(0,.63)],['stock-commits-later',p(1,.64)]],
  'success':[['all-completions-received',p(0,.65)]],
  'reject-before-decision':[['order-prepared',p(0,.18)],['stock-rejects',p(0,.76)],['abort-decision-durable',p(1,.6)]],
  'abort':[['abort-command-arrives',p(0,.72)],['pending-order-discarded',p(1,.37)],['abort-finished',p(1,.73)]],
  'in-doubt':[['coordinator-unreachable',p(0,.6)]],
  'recover-decision':[['old-decision-recovered',p(0,.57)],['order-recovery-complete',p(1,.4)],['stock-recovery-complete',p(1,.7)]],
  'resource-boundary':[['other-modification-waits',p(0,.64)]],
 }as Record<string,[string,number][]>)[s.visualType]??[];
};
export const eventAt=(s:Shot,n:string)=>events(s).find(([q])=>q===n)?.[1]??0;
