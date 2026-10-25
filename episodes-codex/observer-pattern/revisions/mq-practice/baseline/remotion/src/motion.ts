import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??Number(s.javaCardFrom??s.durationInFrames)-15);
 return Math.round(a+(b-a)*ratio);
};
type Window=[number,number,number];
const WINDOWS:Record<string,Record<string,Window>>={
 'product-update':{click:[0,.04,.21],state:[0,.24,.39],summary:[0,.45,.62],record:[0,.67,.9]},
 'observer-roles':{expand:[0,.04,.16],source:[0,.17,.41],summary:[0,.43,.65],record:[0,.68,.91],contract:[1,0,.35]},
 'register-interest':{separate:[0,.05,.9],summary:[1,.04,.4],record:[1,.46,.83]},
 'common-notification':{contract:[1,.04,.43],responses:[1,.52,.92]},
 'change-before-notify':{state:[1,.04,.3],notify:[1,.55,.94]},
 'each-reacts':{summary:[0,.02,.24],summaryResponse:[0,.27,.38],record:[0,.48,.71],recordResponse:[0,.74,.91],sequential:[1,.05,.5]},
 'separate-responsibilities':{summary:[0,.03,.35],record:[0,.41,.8],dependency:[1,.08,.8]},
 'unsubscribe-summary':{close:[0,.51,.92],cancel:[1,.03,.74],stopped:[1,.79,.97]},
 'notify-remaining':{state:[0,.06,.3],notify:[0,.46,.93],response:[1,.03,.33]},
 'change-membership':{review:[0,.05,.87],scope:[1,.07,.86]},
 'lifecycle-and-delivery':{lifecycle:[0,.06,.9],boundary:[1,.05,.88]},
 'idea-recap':{direct:[0,.04,.9],roles:[1,.03,.9]},
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
  'observer-roles':()=>[after('same-product-objects-expand','expand'),after('source-role-explained','source'),after('summary-concrete-role-explained','summary'),after('record-concrete-role-explained','record'),['common-observer-contract-start',at(s,1,0)],after('common-observer-contract-visible','contract')],
  'register-interest':()=>[['explicit-before-payment-replay',at(s,1,0)],['second-sentence-start',at(s,1,0)],after('summary-registration-start','summary',0,true),after('summary-in-membership','summary'),after('record-registration-start','record',0,true),after('record-in-membership','record')],
  'common-notification':()=>[after('common-fact-contract-visible','contract'),after('receivers-own-responses','responses')],
  'change-before-notify':()=>[after('order-state-updated-first','state'),after('first-notification-start','notify',0,true),after('notification-awaits-summary-receipt','notify')],
  'each-reacts':()=>[after('summary-notification-received','summary'),after('summary-display-updated','summaryResponse'),after('record-notification-start','record',0,true),after('record-notification-received','record'),after('first-change-record-appended','recordResponse'),after('sequential-example-caveat','sequential')],
  'separate-responsibilities':()=>[after('summary-owns-display','summary',.2),after('record-owns-history','record',.2),after('source-keeps-list-and-contract','dependency',.2)],
  'unsubscribe-summary':()=>[after('product-close-summary-click','close'),after('summary-withdrawal-start','cancel',0,true),after('summary-removed-from-membership','cancel'),after('summary-stopped-last-value-preserved','stopped')],
  'notify-remaining':()=>[after('same-order-now-shipped','state'),after('only-record-notification-start','notify',0,true),after('record-received-shipped','notify'),after('second-change-record-appended','response')],
  'change-membership':()=>[after('two-delivery-recipient-sets-reviewed','review'),after('contract-unchanged-membership-and-response-scope','scope',.2,true)],
  'lifecycle-and-delivery':()=>[after('subscription-lifecycle-cost','lifecycle',.4),['reliability-boundary-start',at(s,1,0)],after('no-crash-replay-guarantee','boundary')],
  'idea-recap':()=>[after('single-stable-receiver-direct-alternative','direct',.4),['recap-start',at(s,1,0)],after('source-change-highlight','roles',.28),after('current-members-highlight','roles',.55),after('independent-response-highlight','roles')],
 };
 return [...(s.javaCardFrom!=null?[['java-card-start',Number(s.javaCardFrom)],['java-card-final',s.durationInFrames-1]] as [string,number][]:[]),...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),...(chosen[s.visualType]?.()??[])];
};
