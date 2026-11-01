export type State=[number,number];
export type Operation={kind:'fill'|'pour'|'drain';from?:0|1;to?:0|1;title:string;stop:string};
export const CAPACITIES:State=[3,5];
export const OPERATIONS:Operation[]=[
 {kind:'fill',to:1,title:'装满大容器',stop:'大容器装满，停止加水'},
 {kind:'pour',from:1,to:0,title:'大容器倒向小容器',stop:'小容器满，停止互倒'},
 {kind:'drain',from:0,title:'倒空小容器',stop:'小容器空，停止倒出'},
 {kind:'pour',from:1,to:0,title:'把剩下的水转进小容器',stop:'大容器空，停止互倒'},
 {kind:'fill',to:1,title:'再次装满大容器',stop:'大容器装满，停止加水'},
 {kind:'pour',from:1,to:0,title:'只补满小容器的空位',stop:'小容器满，大容器留下4升'},
];
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const ease=(v:number)=>{v=clamp(v);return v*v*(3-2*v);};
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const TRANSFER={lead:.12,transfer:.25,complete:.82};
export const apply=(state:State,op:Operation):{state:State;amount:number}=>{
 const next:State=[...state];let amount=0;
 if(op.kind==='fill'){amount=CAPACITIES[op.to!]-next[op.to!];next[op.to!]+=amount;}
 if(op.kind==='drain'){amount=next[op.from!];next[op.from!]=0;}
 if(op.kind==='pour'){amount=Math.min(next[op.from!],CAPACITIES[op.to!]-next[op.to!]);next[op.from!]-=amount;next[op.to!]+=amount;}
 return{state:next,amount};
};
export const STATES:State[]=[[0,0]];
for(const op of OPERATIONS)STATES.push(apply(STATES[STATES.length-1],op).state);
export const operationAt=(index:number,progress:number)=>{
 const op=OPERATIONS[index],start=STATES[index],result=apply(start,op),fraction=ease((progress-TRANSFER.transfer)/(TRANSFER.complete-TRANSFER.transfer)),complete=progress>=TRANSFER.complete;
 const volume:State=[mix(start[0],result.state[0],fraction),mix(start[1],result.state[1],fraction)];
 return{index,op,start,end:result.state,volume,amount:result.amount,transferred:result.amount*fraction,complete,progress,phase:progress<TRANSFER.lead?'prepare':progress<TRANSFER.transfer?'lead':complete?'settled':'flowing',flowVisible:progress>=TRANSFER.lead&&!complete,flowReveal:clamp((progress-TRANSFER.lead)/(TRANSFER.transfer-TRANSFER.lead)),externalIn:op.kind==='fill'?result.amount*fraction:0,externalOut:op.kind==='drain'?result.amount*fraction:0,historyCount:index+1+(complete?1:0)};
};
export const BAR={centers:[690,1240],width:240,bottom:760,unit:80};
export const surface=(volume:number)=>BAR.bottom-volume*BAR.unit;
