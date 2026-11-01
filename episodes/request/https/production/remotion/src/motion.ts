import type {Shot} from './data';
// Complete mechanism windows, measured in unchanged real-shot local frames.
// Navigation QA uses these landmarks; it does not substitute for seeing clips.
export const mechanismWindows=(s:Shot):[string,number,number][]=>{
 const b=Number(s.cueFrames?.sentences?.[1]??s.durationInFrames/2);
 const windows:Record<string,[string,number,number][] >={
  '04':[['identity-request',105,160],['identity-question',b+12,b+82]],
  '05':[['domain-check',15,50],['validity-check',65,100],['trust-check',b+12,b+47]],
  '06':[['blocked-at-identity',90,145],['certificate-warning',150,195]],
  '07':[['public-data-out',115,170],['public-data-back-and-derive',b+12,b+82]],
  '08':[['encrypt',15,50],['ciphertext-travel',65,150],['decrypt-and-verify',150,185]],
  '09':[['response-travel',25,110],['response-accepted',120,155]],
  '10':[['ciphertext-travel',95,165],['ciphertext-modified',125,150],['record-rejected',175,205]],
 };
 return windows[s.id]??[];
};
export const events=(s:Shot):[string,number][]=>mechanismWindows(s).flatMap(([name,a,b])=>[[`${name}-start`,a],[`${name}-mid`,Math.round((a+b)/2)],[`${name}-end`,b]] as [string,number][]);
