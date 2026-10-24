import type {Shot} from './data';
export const at=(s:Shot,i:number,r:number)=>{const ss=s.cueFrames?.sentences??[0,s.durationInFrames/2];return Math.round(Number(ss[i]??0)+(Number(ss[i+1]??s.durationInFrames-15)-Number(ss[i]??0))*r)};
export const events=(s:Shot):[string,number][]=>{const p=(i:number,r:number)=>at(s,i,r);return ({
'hook':[['order-refused',p(1,.25)]],
'reserve-save':[['reservation-committed',p(0,.68)],['local-save-explained',p(1,.28)]],
'decide-confirm':[['confirm-decision-durable',p(1,.36)]],
'confirm-apply':[['reservation-to-sale-committed',p(0,.68)]],
'confirm-retry':[['reply-lost',p(0,.35)],['same-confirm-arrives',p(1,.3)],['confirmed-no-extra-effect',p(1,.65)]],
'cancel-reset':[['second-branch-reservation',p(1,.35)],['other-side-refused',p(1,.7)]],
'decide-cancel':[['cancel-decision-durable',p(0,.55)]],
'cancel-apply':[['reservation-released-committed',p(0,.68)]],
'cancel-retry':[['same-cancel-arrives',p(0,.68)],['cancelled-no-extra-effect',p(1,.5)]],
'recap':[['show-confirm-outcome',p(0,.68)],['switch-to-separate-cancel-outcome',p(1,.07)]],
} as Record<string,[string,number][]>)[s.visualType]??[]};
export const eventAt=(s:Shot,k:string)=>events(s).find(([n])=>n===k)?.[1]??0;
