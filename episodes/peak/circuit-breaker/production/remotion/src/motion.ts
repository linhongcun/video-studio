import type {Shot} from './data';

/** Visual-only windows: all important requests start after the camera lands. */
export const W={
 baselineRequest:[48,90], baselineWaiters:[90,135,180],
 observe:[45,155], failures:[65,110,155],
 blockedRequest:[48,92], unavailableReply:[128,168],
 orderSubmit:[176,216], waitingCaption:[210,260],
 failedProbe:[48,108], failedProbeReply:[167,222],
 newProbe:[58,103], newProbeReply:[118,160],
 restoredRequest1:[176,220], restoredRequest2:[196,240],
} as const;

export function events(s:Shot):[string,number][] {
 const id=Number(s.id);
 const window=(name:string,w:readonly number[]):[string,number][]=>[[`${name}-start`,w[0]],[`${name}-end`,w[1]]];
 if(id===1)return [['order-submit-visible',70],['blocked-optional-call-visible',177]];
 if(id===2)return [...window('unprotected-request',W.baselineRequest),...W.baselineWaiters.map((f,i)=>[`waiting-request-${i+1}`,f] as [string,number])];
 if(id===3)return [['shared-resource-full',60]];
 if(id===4)return [['observation-start',W.observe[0]],...W.failures.map((f,i)=>[`observed-failure-${i+1}`,f] as [string,number])];
 if(id===5)return [...window('blocked-request',W.blockedRequest),...window('unavailable-feedback',W.unavailableReply)];
 if(id===6)return window('business-order-submit',W.orderSubmit);
 if(id===7)return window('wait-then-probe-caption',W.waitingCaption);
 if(id===8)return [...window('limited-failing-probe',W.failedProbe),...window('failing-probe-reply',W.failedProbeReply)];
 if(id===9)return [...window('new-round-probe',W.newProbe),...window('successful-probe-reply',W.newProbeReply),...window('normal-request-1',W.restoredRequest1),...window('normal-request-2',W.restoredRequest2)];
 return [];
}
