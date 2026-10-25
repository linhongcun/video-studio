import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(Number(s.javaCardFrom??s.durationInFrames)/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??Number(s.javaCardFrom??s.durationInFrames)-15);
 return Math.round(a+(b-a)*ratio);
};
type Window=[number,number,number];
const WINDOWS:Record<string,Record<string,Window>>={
 'product-reminder':{click:[0,.4,.75],accepted:[1,.01,.13]},
 'adapter-structure':{relations:[1,.02,.94]},
 'submit-through-target':{request:[1,.05,.78]},
 'convert-and-delegate':{convert:[0,.06,.43],delegate:[0,.55,.93]},
 'return-and-feedback':{produced:[0,.02,.14],received:[0,.16,.35],mapped:[0,.4,.65],returned:[0,.7,.94],display:[1,.03,.2]},
 'external-upgrade':{requestChange:[1,.04,.46],receiptChange:[1,.56,.94]},
 'boundary-change':{requestUpdate:[0,.04,.3],receiptUpdate:[0,.34,.61],assemblyUpdate:[0,.65,.94]},
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
  'product-reminder':()=>[after('product-click','click',.5),after('product-submitting','click'),after('product-accepted','accepted')],
  'business-first':()=>[['own-business-contract',0],['upgrade-isolation-benefit',at(s,1,0)]],
  'adapter-structure':()=>[after('business-target','relations',.15),after('adapter-implements-target','relations',.5),after('adapter-holds-service','relations',.85)],
  'submit-through-target':()=>[['same-submission-replay-intro',0],['request-view-after-replay-intro',at(s,1,0)],after('business-request-departure','request',0,true),after('adapter-receives-request','request')],
  'convert-and-delegate':()=>[after('request-conversion-start','convert',0,true),after('request-conversion-complete','convert'),after('delegate-to-service-start','delegate',0,true),after('service-receives-request','delegate')],
  'return-and-feedback':()=>[after('service-receipt-produced','produced'),after('service-receipt-departure','received',0,true),after('adapter-receives-receipt','received'),after('business-result-mapped','mapped'),after('business-result-departure','returned',0,true),after('result-arrives-at-business','returned'),['same-result-back-on-ui',at(s,1,0)],after('ui-accepted','display')],
  'external-upgrade':()=>[['keep-completed-product-during-transition',0],['later-development-view',at(s,1,0)],after('external-request-format-change-start','requestChange',0,true),after('external-request-format-v2','requestChange'),after('receipt-wrapper-change-start','receiptChange',0,true),after('receipt-wrapper-halfway','receiptChange',.5),after('external-nested-receipt-v2','receiptChange')],
  'boundary-change':()=>[after('adapter-request-mapping-updated','requestUpdate'),after('adapter-return-mapping-updated','receiptUpdate'),after('creation-and-wiring-updated','assemblyUpdate'),['business-contract-and-workflow-stable',at(s,1,0)]],
  'cost-and-corruption':()=>[['business-rules-and-integration-boundary',0],['maintenance-and-capability-limit',at(s,1,0)]],
  'idea-recap':()=>[['business-first-contract-recap',0],['two-benefits-recap',at(s,1,0)]],
 };
 return [...(s.javaCardFrom!=null?[['java-card-start',Number(s.javaCardFrom)],['java-card-final',s.durationInFrames-1]] as [string,number][]:[]),...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),...(chosen[s.visualType]?.()??[])];
};
