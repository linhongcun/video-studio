import type {Shot} from './data';
export const at=(s:Shot,i:number,r:number)=>{const a=s.cueFrames?.sentences??[9,Math.floor(s.durationInFrames/2)];return Math.round(Number(a[i]??0)+(Number(a[i+1]??s.durationInFrames-15)-Number(a[i]??0))*r);};
export const events=(s:Shot):[string,number][]=>{
 const p=(i:number,r:number)=>at(s,i,r);
 const edge=(i:number,a:number,b:number,t:number)=>{for(let f=0;f<s.durationInFrames;f++){const r=Math.max(0,Math.min(1,(f-p(i,a))/Math.max(1,p(i,b)-p(i,a))));if(r*r*(3-2*r)>t)return f;}return s.durationInFrames-1;};
 const e:Record<string,[string,number][]>={
  '01':[['chat-order-query-start',9],['chat-order-query-complete',39],['chat-policy-query-start',57],['chat-policy-query-complete',90],['chat-ai-question-visible',120],['chat-preview-last-frame',236]],
  '02':[['request-reaches-program',edge(0,.05,.3,.99)],['permission-check-complete',p(0,.38)],['query-starts-at-source',edge(0,.4,.7,.99)],['result-reaches-model',edge(1,.04,.85,.99)]],
  '03':[['order-time-known',edge(0,.05,.4,.6)],['usage-unknown-visible',edge(0,.45,.8,.4)],['policy-gap-visible',edge(1,.05,.65,.2)],['policy-query-selected',edge(1,.05,.65,.8)]],
  '04':[['policy-request-reaches-program',p(0,.4)],['policy-query-executed',p(0,.8)],['policy-result-reaches-model',edge(1,.05,.85,.99)]],
  '05':[['policy-time-visible',edge(0,.05,.42,.5)],['policy-usage-visible',edge(0,.48,.85,.5)],['both-conditions-required',edge(1,.05,.65,.5)]],
  '06':[['time-condition-checked',edge(0,.05,.7,.55)],['usage-gap-highlighted',edge(1,.05,.7,.2)],['next-action-switches-to-question',edge(1,.05,.7,.75)]],
  '07':[['question-reaches-user',edge(0,.05,.8,.99)],['waiting-for-user',p(1,.05)]],
  '08':[['user-statement-reaches-program',edge(0,.05,.8,.99)],['all-inputs-reach-model',edge(1,.05,.8,.99)]],
  '09':[['recommendation-visible',edge(0,.08,.7,.7)]],
  '10':[['request-executed',p(0,.8)],['feedback-reaches-model',edge(1,.05,.8,.99)]],
  '11':[['usage-gap-revisited',edge(0,.05,.7,.5)],['question-selected-again',edge(1,.05,.7,.75)]],
 };
 return [...Object.entries(s.cueFrames?.labels??{}).map(([k,v])=>['label:'+k,Number(v)] as [string,number]),...(e[s.id]??[])];
};
