import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(Number(s.javaCardFrom??s.durationInFrames)/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??Number(s.javaCardFrom??s.durationInFrames)-15);
 return Math.round(a+(b-a)*ratio);
};
type Window=[number,number,number];
const WINDOWS:Record<string,Record<string,Window>>={
 'product-reminder':{click:[0,.4,.75],accepted:[1,.01,.13]},
 'roles-and-target':{roles:[1,.02,.94]},
 'introduce-adapter':{relations:[1,.02,.9]},
 'submit-through-target':{request:[1,.05,.78]},
 'convert-and-delegate':{convert:[0,.08,.8],delegate:[1,.08,.75]},
 'map-acceptance':{produced:[0,.02,.2],received:[0,.25,.7],mapped:[1,.06,.45],returned:[1,.52,.89]},
 'accepted-ui':{display:[0,.04,.22]},
 'rejection-and-unknown':{unknown:[1,.38,.78]},
 'maintenance-scope':{scope:[1,.05,.83]},
 'idea-recap':{roles:[0,.03,.94]},
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
  'product-reminder':()=>[after('send-button-pressed','click',.5),after('request-submitting','click'),after('accepted-only-after-return','accepted')],
  'incompatible-contracts':()=>[['explicit-before-integration-view',0],['contract-differences-explained',at(s,1,0)]],
  'roles-and-target':()=>[['transition-before-role-detail',0],after('client-role','roles',.15),after('target-is-contract','roles',.5),after('sdk-role','roles',.85)],
  'introduce-adapter':()=>[after('adapter-implements-target','relations',.2),after('adapter-holds-sdk','relations',.7)],
  'submit-through-target':()=>[['same-request-replay-established',0],['runtime-replay-after-explanation',at(s,1,0)],after('request-departure','request',0,true),after('adapter-receives-request','request')],
  'convert-and-delegate':()=>[after('input-mapping-start','convert',0,true),after('input-mapping-complete','convert'),after('sdk-delegation-start','delegate',0,true),after('sdk-request-arrives','delegate')],
  'map-acceptance':()=>[after('sdk-queued-receipt-produced','produced'),after('receipt-departure','received',0,true),after('adapter-receives-receipt','received'),after('acceptance-meaning-mapped','mapped'),after('business-result-departure','returned',0,true),after('same-reference-back-at-client','returned')],
  'accepted-ui':()=>[after('same-result-on-original-ui','display')],
  'rejection-and-unknown':()=>[['rules-transition-no-new-request',0],['explicit-rejection-rule',at(s,1,0)],after('unknown-is-not-rejection','unknown',.2)],
  'maintenance-scope':()=>[after('adapter-change-scope','scope',.2)],
  'cost-and-simple-option':()=>[['same-contract-direct-option',0],['extra-conversion-cost',at(s,1,0)]],
  'idea-recap':()=>[after('target-recap','roles',.15),after('adapter-recap','roles',.5),after('sdk-recap','roles',.85),['return-to-same-product-result',at(s,1,0)]],
 };
 return [...(s.javaCardFrom!=null?[['java-card-start',Number(s.javaCardFrom)],['java-card-final',s.durationInFrames-1]] as [string,number][]:[]),...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),...(chosen[s.visualType]?.()??[])];
};
