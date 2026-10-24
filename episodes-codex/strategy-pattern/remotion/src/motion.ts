import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??s.durationInFrames-15);
 return Math.round(a+(b-a)*ratio);
};
type Window=[number,number,number];
const WINDOWS:Record<string,Record<string,Window>>={
 question:{member:[0,.08,.72],campaign:[1,.08,.72]},
 'inline-rules':{activity:[0,.08,.75],motive:[1,.08,.75]},
 'member-method':{input:[1,.04,.32],result:[1,.42,.78]},
 'two-strategies':{campaign:[1,.08,.7]},
 'choose-function':{selected:[1,.05,.35],explained:[1,.42,.8]},
 'function-not-result':{emphasis:[0,.08,.75],parameter:[1,.06,.7]},
 'parameter-binding':{amount:[0,.06,.75],function:[1,.06,.7]},
 'execute-member':{invocation:[0,.06,.7],calculation:[1,.05,.42],returned:[1,.52,.85]},
 'switch-function':{cleared:[1,.03,.25],replaced:[1,.33,.65]},
 'execute-campaign':{invocation:[0,.06,.7],calculation:[1,.05,.42],returned:[1,.52,.85]},
 'pattern-recap':{responsibility:[0,.05,.75],definition:[1,.06,.7]},
 'when-to-use':{member:[1,.06,.38],campaign:[1,.45,.75]},
 'cost-recap':{direct:[0,.06,.7],cost:[1,.06,.75]},
};
export const beat=(s:Shot,f:number,key:string)=>{
 const window=WINDOWS[s.visualType]?.[key];
 if(!window)throw new Error('Unknown motion beat: '+s.visualType+'/'+key);
 const [sentence,start,end]=window,a=at(s,sentence,start),b=at(s,sentence,end);
 const p=Math.max(0,Math.min(1,(f-a)/Math.max(1,b-a)));
 return p*p*(3-2*p);
};
const first=(s:Shot,key:string,limit=.99,strict=false)=>{
 for(let f=0;f<s.durationInFrames;f++)if(strict?beat(s,f,key)>limit:beat(s,f,key)>=limit)return f;
 return s.durationInFrames-1;
};
export const events=(s:Shot):[string,number][]=>{
 const after=(name:string,key:string,limit=.99,strict=false):[string,number]=>[name,first(s,key,limit,strict)];
 const chosen:Record<string,()=>[string,number][]>= {
  question:()=>[after('member-example','member'),after('campaign-example','campaign')],
  'inline-rules':()=>[after('two-methods-inside-checkout','activity'),after('independent-maintenance-motive','motive')],
  'member-method':()=>[['second-sentence-start',at(s,1,0)],after('amount-enters-member','input'),after('member-example-returns-ninety','result')],
  'two-strategies':()=>[after('campaign-method-visible','campaign')],
  'choose-function':()=>[['new-call-shown',at(s,1,.03)],after('member-chosen-as-argument','selected'),after('function-explained','explained')],
  'function-not-result':()=>[after('member-function-emphasized','emphasis',.25,true),after('still-no-result','parameter')],
  'parameter-binding':()=>[after('amount-correspondence','amount'),after('pricing-binding-starts','function',0,true),after('pricing-points-to-member','function')],
  'execute-member':()=>[after('member-invocation-identified','invocation'),after('member-calculated','calculation'),after('ninety-returned','returned')],
  'switch-function':()=>[['second-sentence-start',at(s,1,0)],after('old-ninety-cleared','cleared'),after('pricing-replaced-by-campaign','replaced',.5,true)],
  'execute-campaign':()=>[after('campaign-invocation-identified','invocation'),after('campaign-calculated','calculation'),after('eighty-returned','returned')],
  'pattern-recap':()=>[after('checkout-responsibility','responsibility',.5,true),after('strategy-responsibility','definition',.35,true)],
  'when-to-use':()=>[after('member-maintenance-emphasis','member',.25,true),after('campaign-maintenance-emphasis','campaign',.25,true)],
  'cost-recap':()=>[['cost-discussion-starts',at(s,1,.03)],after('direct-conditions','direct'),after('reading-cost','cost')],
 };
 return [...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),...(chosen[s.visualType]?.()??[])];
};
