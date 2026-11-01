import type {Shot} from './data';
export type ActionWindow={start:number;end:number};
export const actionWindows=(s:Shot):Record<string,ActionWindow>=>{
 const b=Number(s.cueFrames?.sentences?.[1]??s.durationInFrames/2);
 return ({
  '02':{'burst-first':{start:15,end:55},'burst-second':{start:70,end:110},'burst-third':{start:125,end:165}},
  '03':{'queue-appears':{start:80,end:115},'task-written':{start:120,end:165}},
  '04':{'save-receipt':{start:30,end:75},'page-response':{start:b+12,end:b+57}},
  '05':{'task-delivery':{start:b-10,end:b+55}},
  '06':{'business-work':{start:20,end:b}},
  '07':{'processing-ack':{start:b+5,end:b+70},'delivery-finishes':{start:b+70,end:b+100}},
  '08':{'next-task-delivery':{start:70,end:100},'half-work':{start:102,end:120},'connection-breaks':{start:b,end:b+20}},
  '09':{'requeue-same-task':{start:15,end:70},'redeliver-same-task':{start:b,end:b+65}},
  '10':{'ack-lost':{start:72,end:108},'redelivery-reuses-result':{start:b,end:b+55}},
  '11':{'burst-waits':{start:48,end:113},'backend-capacity':{start:b,end:b+80}},
 } as Record<string,Record<string,ActionWindow>>)[s.id]??{};
};
export const events=(s:Shot):[string,number][]=>Object.entries(actionWindows(s)).flatMap(([name,w])=>[[name+'-starts',w.start],[name+'-lands',w.end]] as [string,number][]);
