import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??s.durationInFrames-15);
 return Math.round(a+(b-a)*ratio);
};
type Window=[number,number,number];
const WINDOWS:Record<string,Record<string,Window>>={
 'same-task':{member:[0,.05,.55],campaign:[0,.58,.94]},
 'mixed-pricing':{details:[0,.05,.72],maintenance:[1,.06,.72]},
 'separate-pricing':{separate:[1,.05,.83],retained:[1,.86,.98]},
 'shared-contract':{contract:[0,.06,.75],examples:[1,.06,.75]},
 'choose-strategy':{selection:[1,.06,.7]},
 'member-delegation':{request:[0,.1,.85],calculation:[1,.02,.22],returned:[1,.28,.68],used:[1,.73,.96]},
 'swap-strategy':{cleared:[0,.45,.75],selection:[0,.78,.98],request:[1,.04,.3],calculation:[1,.34,.46],returned:[1,.51,.78],used:[1,.83,.97]},
 'stable-collaboration':{steps:[0,.04,.9],contract:[1,.06,.75]},
 'maintenance-boundary':{scope:[1,.05,.78]},
 'cost-boundary':{reading:[0,.04,.94],direct:[1,.08,.75]},
 'idea-recap':{roles:[0,.04,.95],idea:[1,.06,.8]},
};
export const beat=(s:Shot,f:number,key:string)=>{
 const window=WINDOWS[s.visualType]?.[key];
 if(!window)throw new Error('Unknown motion beat: '+s.visualType+'/'+key);
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
  'same-task':()=>[after('member-task-example','member'),after('campaign-task-example','campaign')],
  'mixed-pricing':()=>[after('pricing-details-inside-flow','details',.1,true),after('maintenance-enters-common-flow','maintenance',.2,true)],
  'separate-pricing':()=>[['second-sentence-start',at(s,1,0)],after('pricing-separation-starts','separate',0,true),after('pricing-separation-complete','separate'),after('pricing-duty-retained','retained')],
  'shared-contract':()=>[after('common-contract-visible','contract'),after('same-task-different-results','examples')],
  'choose-strategy':()=>[['selection-role-appears',at(s,1,.03)],after('member-selected-without-pricing','selection',.5,true)],
  'member-delegation':()=>[after('original-amount-delivered','request'),after('member-pricing-calculated','calculation'),after('ninety-returned','returned'),after('common-flow-continues','used',.3,true)],
  'swap-strategy':()=>[after('old-ninety-cleared','cleared'),after('campaign-selected','selection'),after('original-hundred-delivered','request'),after('campaign-pricing-calculated','calculation'),after('eighty-returned','returned'),after('same-flow-continues','used',.3,true)],
  'stable-collaboration':()=>[after('common-steps-reviewed','steps'),after('flow-depends-on-contract','contract',.2,true),after('algorithm-details-remain-outside','contract',.4)],
  'maintenance-boundary':()=>[['second-sentence-start',at(s,1,0)],after('member-internal-maintenance-scope','scope',.2,true)],
  'cost-boundary':()=>[after('collaboration-reading-cost','reading',.65),['simple-direct-alternative',at(s,1,.04)]],
  'idea-recap':()=>[after('strategy-role','roles',.33),after('settlement-role','roles',.66,true),after('design-idea-recap','idea')],
 };
 return [...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),...(chosen[s.visualType]?.()??[])];
};
