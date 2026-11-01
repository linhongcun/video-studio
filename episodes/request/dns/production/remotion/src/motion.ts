import type {Shot} from './data';
export const mechanismWindows=(s:Shot):[string,number,number][]=>{
 const b=s.cueFrames?.sentences?.[1]??Math.floor(s.durationInFrames/2);
 switch(s.id){
  case '04':return [['local-cache-check',35,65],['local-hit-return',100,135]];
  case '05':return [['client-to-recursive',70,110],['recursive-cache-check',125,155]];
  case '06':case '07':case '08':return [['recursive-query',18,70],['referral-or-answer',b+12,b+72]];
  case '09':return [['address-back-to-client',18,78]];
  case '10':return [['ttl-countdown',65,175]];
  case '11':return [['repeat-client-query',75,110],['cached-answer-return',130,185]];
  default:return [];
 }
};
export const events=(s:Shot):[string,number][]=>mechanismWindows(s).flatMap(([n,a,b])=>[[n+'-start',a],[n+'-mid',Math.round((a+b)/2)],[n+'-end',b]] as [string,number][]);
