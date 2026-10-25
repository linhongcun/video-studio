import type {Shot} from './data';

export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??Number(s.javaCardFrom??s.durationInFrames)-15);
 return Math.round(a+(b-a)*ratio);
};
type Window=[number,number,number];
const WINDOWS:Record<string,Record<string,Window>>={
 'product-update':{click:[0,.04,.21],state:[0,.24,.39],summary:[0,.45,.62],record:[0,.67,.9]},
 'observer-brief':{register:[0,.03,.25],state:[0,.29,.4],summary:[0,.45,.62],record:[0,.69,.88],roles:[1,.03,.9]},
 'mq-practice':{local:[0,.04,.55],mq:[1,0,.26],queues:[1,.3,.7]},
 'publish-route':{publish:[1,.03,.25],route:[1,.3,.68]},
 'independent-consume':{summary:[0,.02,.2],summaryApply:[0,.23,.32],summaryAck:[0,.35,.48],record:[0,.15,.34],recordApply:[0,.37,.47],recordAck:[0,.54,.71],extend:[1,.08,.75]},
 'offline-backlog':{summary:[0,.3,.5],summaryApply:[0,.52,.64],summaryAck:[0,.66,.84],durable:[1,.03,.65]},
 'recover-idempotent':{recover:[0,.01,.1],record:[0,.14,.27],recordApply:[0,.3,.4],lostAck:[0,.4,.49],disconnect:[0,.51,.56],requeue:[0,.57,.64],redeliver:[0,.72,.93],dedup:[1,.02,.42],recordAck:[1,.55,.79]},
 'consistency-boundary':{gap:[0,.16,.62],outbox:[1,.02,.4],delay:[1,.48,.91]},
 'scope-choice':{mq:[0,.03,.83],local:[1,.04,.85]},
 'practice-recap':{publish:[0,.03,.32],route:[0,.35,.58],response:[0,.62,.88],reliability:[1,.03,.9]},
};
export const beat=(s:Shot,f:number,key:string)=>{
 const window=WINDOWS[s.visualType]?.[key];
 if(!window)throw new Error('Unknown motion beat: '+s.visualType+'/'+key);
 const [sentence,start,end]=window,a=at(s,sentence,start),b=at(s,sentence,end),p=Math.max(0,Math.min(1,(f-a)/Math.max(1,b-a)));
 return p*p*(3-2*p);
};
const first=(s:Shot,key:string,limit=.99)=>{
 for(let f=0;f<s.durationInFrames;f++)if(beat(s,f,key)>=limit)return f;
 return s.durationInFrames-1;
};
const EVENT_NAMES:Record<string,Record<string,string>>={
 'product-update':{click:'product-mark-paid-click',state:'product-order-state-paid',summary:'product-summary-updated',record:'product-record-appended'},
 'observer-brief':{register:'local-observers-registered',state:'local-source-paid',summary:'local-summary-notified',record:'local-record-notified'},
 'mq-practice':{mq:'explicit-cross-service-mq-example',queues:'two-independent-subscription-queues-visible'},
 'publish-route':{publish:'paid-event-published-to-exchange',route:'event-routed-to-both-queues'},
 'independent-consume':{summary:'summary-received',summaryApply:'summary-effect-applied',summaryAck:'summary-acknowledged',record:'record-received',recordApply:'one-record-appended',recordAck:'record-acknowledged',extend:'new-subscriber-without-producer-call'},
 'offline-backlog':{summary:'summary-consumes-while-record-offline',summaryApply:'summary-updated-record-still-pending',summaryAck:'summary-acked-record-retained',durable:'durability-assumptions-visible'},
 'recover-idempotent':{recover:'record-service-recovered',record:'backlog-delivered',recordApply:'record-first-effect-applied',lostAck:'first-confirmation-lost',disconnect:'connection-loss-detected',requeue:'unacknowledged-event-requeued',redeliver:'same-event-redelivered',dedup:'duplicate-effect-skipped',recordAck:'redelivery-acknowledged'},
 'consistency-boundary':{gap:'state-commit-publish-gap',outbox:'separate-outbox-design-example',delay:'asynchronous-result-delay'},
 'scope-choice':{mq:'cross-service-selection',local:'local-event-framework-selection'},
 'practice-recap':{publish:'recap-publish',route:'recap-subscribe',response:'recap-individual-response',reliability:'recap-delivery-idempotency-consistency'},
};
export const events=(s:Shot):[string,number][]=>[
 ...(s.javaCardFrom!=null?[['java-card-start',Number(s.javaCardFrom)],['java-card-final',s.durationInFrames-1]] as [string,number][]:[]),
 ...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),
 ...Object.entries(EVENT_NAMES[s.visualType]??{}).flatMap(([key,name])=>[[name+'-mid',first(s,key,.5)],[name,first(s,key)]] as [string,number][]),
];
