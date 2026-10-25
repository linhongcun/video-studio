import type {Shot} from './data';
export const at=(s:Shot,i:number,r:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.floor(s.durationInFrames/2)];
 const start=Number(starts[i]??0),end=Number(starts[i+1]??s.durationInFrames-15);
 return Math.round(start+(end-start)*r);
};
export const events=(s:Shot):[string,number][]=>{
 const p=(i:number,r:number)=>at(s,i,r);
 const map:Record<string,[string,number][] >={
  '01':[['assistant-preparing',24],['system-still-waiting',54]],
  '02':[['rewind-explained',p(0,.18)],['inputs-sent',p(0,.48)],['inputs-reach-model',p(0,.88)],['tool-description-focused',p(1,.35)]],
  '03':[['call-leaves-model',p(0,.12)],['call-reaches-program',p(0,.82)],['parameter-highlighted',p(1,.24)]],
  '04':[['tool-checked',p(0,.32)],['arguments-checked',p(0,.56)],['permission-checked',p(0,.80)],['query-code-receives-order',p(1,.72)]],
  '05':[['http-request-starts',p(0,.08)],['http-request-reaches-system',p(0,.78)],['order-result-created',p(1,.15)],['order-result-reaches-program',p(1,.79)]],
  '06':[['result-held-by-program',p(0,.15)],['result-return-starts',p(1,.10)],['result-reaches-model',p(1,.80)]],
  '07':[['reply-starts',p(0,.42)],['reply-reaches-chat',p(0,.82)],['query-evidence-visible',p(1,.10)]],
  '08':[['new-session-reset',0],['new-user-visible',p(1,.10)],['new-call-reaches-check',p(1,.80)]],
  '09':[['permission-denied',p(0,.55)],['no-http-call-confirmed',p(1,.10)]],
  '10':[['failure-leaves-program',p(0,.08)],['failure-reaches-model',p(0,.40)],['failure-reply-visible',p(0,.72)],['no-order-data-confirmed',p(1,.10)]],
  '11':[['execution-role-recalled',p(0,.55)],['execution-evidence-recalled',p(1,.25)]],
 };
 return [...Object.entries(s.cueFrames?.labels??{}).map(([t,v])=>['label:'+t,Number(v)] as [string,number]),...(map[s.id]??[])];
};
