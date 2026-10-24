import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??s.durationInFrames-15);
 return Math.round(a+(b-a)*ratio);
};
export const events=(s:Shot):[string,number][]=>{
 const p=(i:number,r:number)=>at(s,i,r);
 const chosen:Record<string,[string,number][]>= {
  hook:[['campaign-change-request',p(0,.45)],['checkout-change-scope',p(1,.5)]],
  monolith:[['amount-arrives',p(0,.8)],['ordinary-result',p(1,.75)]],
  'new-rule':[['member-rule-added',p(0,.35)],['campaign-rule-added',p(0,.7)],['three-branches',p(1,.7)]],
  extract:[['extraction-start',p(0,.15)],['rules-separated',p(1,.55)]],
  contract:[['same-input-contract',p(0,.8)],['common-output-contract',p(1,.7)]],
  strategy:[['delegation-visible',p(1,.65)]],
  select:[['member-selected',p(0,.65)],['selection-remains-external',p(1,.65)]],
  call:[['amount-at-checkout',p(0,.8)],['only-member-called',p(1,.8)]],
  return:[['member-calculated',p(0,.65)],['ninety-returned',p(1,.78)]],
  switch:[['independent-reset',0],['campaign-selected',p(0,.4)],['eighty-returned',p(1,.85)]],
  change:[['campaign-rate-changed',p(0,.75)],['seventy-five-returned',p(1,.85)]],
  compare:[['only-campaign-changed',p(0,.7)],['contract-and-registration-remain',p(1,.7)]],
  add:[['new-function-added',p(0,.75)],['new-option-registered',p(1,.3)],['newcomer-returns-ninety',p(1,.88)]],
  code:[['delegation-line-focused',p(0,.7)],['selection-argument-focused',p(1,.65)]],
  boundary:[['simple-branch-enough',p(0,.7)],['separation-cost-visible',p(1,.7)]],
  recap:[['selection-call-return-recap',p(0,.8)],['final-message',p(1,.8)]],
 };
 return [...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),...(chosen[s.visualType]??[])];
};
