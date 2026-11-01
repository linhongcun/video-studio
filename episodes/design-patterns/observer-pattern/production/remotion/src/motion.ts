import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??Number(s.javaCardFrom??s.durationInFrames)-15);
 return Math.round(a+(b-a)*ratio);
};
type Window=[number,number,number];
const WINDOWS:Record<string,Record<string,Window>>={
 'product-update':{click:[0,.04,.21],state:[0,.24,.39],summary:[0,.45,.62],record:[0,.67,.9]},
 'why-observer':{cost:[0,.12,.75],separate:[1,.05,.55],receivers:[1,.6,.9]},
 'observer-roles':{expand:[0,.04,.16],source:[0,.17,.41],summary:[0,.43,.65],record:[0,.68,.91],contract:[1,0,.35]},
 'register-interest':{separate:[0,.05,.9],summary:[1,.04,.4],record:[1,.46,.83]},
 'notify-and-react':{state:[0,.06,.28],dispatch:[0,.4,.93],summary:[1,0,.17],summaryResponse:[1,.18,.26],record:[1,.32,.52],recordResponse:[1,.55,.66],responses:[1,.7,.93]},
 'unsubscribe-summary':{close:[0,.51,.92],cancel:[1,.03,.74],stopped:[1,.79,.97]},
 'notify-remaining':{state:[0,.06,.3],notify:[0,.46,.93],response:[1,.03,.33]},
 'benefits-and-cost':{review:[0,.04,.82],contract:[1,.02,.32],lifecycle:[1,.35,.63],direct:[1,.7,.93]},
 'mq-application':{mechanism:[0,.12,.85],publish:[1,.02,.3],subscribe:[1,.34,.66],responses:[1,.7,.93]},
 'observer-recap':{source:[0,.04,.4],responses:[0,.47,.9],relation:[1,.04,.92]},
};
export const beat=(s:Shot,f:number,key:string)=>{
 const window=WINDOWS[s.visualType]?.[key];if(!window)throw new Error('Unknown motion beat: '+s.visualType+'/'+key);
 const [sentence,start,end]=window,a=at(s,sentence,start),b=at(s,sentence,end),p=Math.max(0,Math.min(1,(f-a)/Math.max(1,b-a)));
 return p*p*(3-2*p);
};
const first=(s:Shot,key:string,limit=.99,strict=false)=>{
 for(let f=0;f<s.durationInFrames;f++)if(strict?beat(s,f,key)>limit:beat(s,f,key)>=limit)return f;
 return s.durationInFrames-1;
};
export const events=(s:Shot):[string,number][]=>{
 const after=(name:string,key:string,limit=.99,strict=false):[string,number]=>[name,first(s,key,limit,strict)];
 const chosen:Record<string,()=>[string,number][]>= {
  'product-update':()=>[after('product-mark-paid-click','click'),after('product-order-state-paid','state'),after('product-summary-updated','summary'),after('product-record-appended','record')],
  'why-observer':()=>[after('embedded-handling-maintenance-cost','cost',.5),after('source-and-response-responsibilities-separated','separate'),after('receivers-own-handling','receivers')],
  'observer-roles':()=>[after('same-product-objects-expand','expand'),after('source-role-explained','source'),after('summary-concrete-role-explained','summary'),after('record-concrete-role-explained','record'),['common-observer-contract-start',at(s,1,0)],after('common-observer-contract-visible','contract')],
  'register-interest':()=>[['explicit-before-payment-replay',at(s,1,0)],['second-sentence-start',at(s,1,0)],after('summary-registration-start','summary',0,true),after('summary-in-membership','summary'),after('record-registration-start','record',0,true),after('record-in-membership','record')],
  'notify-and-react':()=>[after('source-updated-before-notification','state'),after('summary-notification-start','dispatch',0,true),after('summary-notification-sent-partway','dispatch'),after('summary-received','summary'),after('summary-display-updated','summaryResponse'),after('record-notification-start','record',0,true),after('record-received','record'),after('record-appended-one-fact','recordResponse'),after('receivers-own-responses','responses')],
  'unsubscribe-summary':()=>[after('product-close-summary-click','close'),after('summary-withdrawal-start','cancel',0,true),after('summary-removed-from-membership','cancel'),after('summary-stopped-last-value-preserved','stopped')],
  'notify-remaining':()=>[after('same-order-now-shipped','state'),after('only-record-notification-start','notify',0,true),after('record-received-shipped','notify'),after('second-change-record-appended','response')],
  'benefits-and-cost':()=>[after('two-notifications-recipient-comparison','review'),after('unchanged-common-contract','contract'),after('subscription-lifecycle-cost','lifecycle'),after('simple-stable-contact-can-call-directly','direct')],
  'mq-application':()=>[after('one-brief-application-context','mechanism'),after('application-source-publishes-fact','publish'),after('application-two-independent-subscriptions','subscribe'),after('application-receivers-own-handling','responses')],
  'observer-recap':()=>[after('back-to-pattern-source','source'),after('recap-observers-own-response','responses'),after('recap-adjustable-subscription-relation','relation')],
 };
 return [...(s.javaCardFrom!=null?[['java-card-start',Number(s.javaCardFrom)],['java-card-final',s.durationInFrames-1]] as [string,number][]:[]),...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),...(chosen[s.visualType]?.()??[])];
};
