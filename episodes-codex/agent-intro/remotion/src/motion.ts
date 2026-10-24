import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??s.durationInFrames-15);
 return Math.round(a+(b-a)*ratio);
};
export const events=(s:Shot):[string,number][]=>{
 const p=(i:number,r:number)=>at(s,i,r);
 const edge=(i:number,a:number,b:number,threshold:number)=>{
  const start=p(i,a),end=p(i,b);
  for(let f=0;f<s.durationInFrames;f++){const raw=Math.max(0,Math.min(1,(f-start)/Math.max(1,end-start)));if(raw*raw*(3-2*raw)>threshold)return f;}
  return s.durationInFrames-1;
 };
 const t=Number(s.id);
 const chosen:Record<number,[string,number][]>={
  7:[['request-to-program',p(1,.38)],['program-to-tool',p(1,.8)]],
  8:[['request-arrives-at-program',edge(0,.05,.75,.99)],['order-number-checked',p(1,.2)],['permission-checked',p(1,.45)],['query-arrives',edge(1,.5,.85,.99)]],
  9:[['result-arrives-at-program',p(0,.85)],['usage-remains-unknown',edge(1,.04,.55,.25)]],
  10:[['result-reaches-model',edge(0,.02,.72,.99)],['next-action-selected',edge(1,.05,.65,.45)]],
  11:[['policy-query-reaches-tool',edge(0,.04,.8,.99)],['policy-result-returned',edge(1,.05,.8,.99)]],
  12:[['both-policy-conditions-visible',edge(0,.04,.75,.6)],['only-time-condition-checked',edge(1,.04,.7,.2)]],
  13:[['question-arrives-at-user',p(0,.8)],['waiting-for-user',edge(1,.05,.65,.2)]],
  15:[['user-statement-arrives',edge(0,.05,.75,.99)]],
  16:[['recommendation-settled',p(0,.65)],['refund-still-not-executed',edge(1,.06,.6,.3)]],
  17:[['predefined-branches-visible',p(1,.7)]],
  18:[['dynamic-action-selected',edge(1,.08,.7,.3)]],
  19:[['actual-refund-state-checked',edge(1,.04,.7,.3)]],
 };
 return [...Object.entries(s.cueFrames?.labels??{}).map(([name,frame])=>['label:'+name,Number(frame)] as [string,number]),...(chosen[t]??[]),...Object.entries(s.cueFrames?.events??{}).map(([name,frame])=>[name,Number(frame)] as [string,number])];
};
export const eventAt=(s:Shot,name:string,fallbackSentence=0,fallbackRatio=.5)=>Number(s.cueFrames?.events?.[name]??at(s,fallbackSentence,fallbackRatio));
