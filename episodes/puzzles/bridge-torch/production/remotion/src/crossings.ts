export const PEOPLE=[1,2,5,10] as const;
export type Person=typeof PEOPLE[number];
export type Side=0|1;
export type Move={people:Person[];to:Side;minutes:number};
export type State={sides:Record<Person,Side>;torchSide:Side;holder:Person;total:number};
export const GREEDY:Move[]=[{people:[1,2],to:1,minutes:2},{people:[1],to:0,minutes:1},{people:[1,5],to:1,minutes:5},{people:[1],to:0,minutes:1},{people:[1,10],to:1,minutes:10}];
export const OPTIMAL:Move[]=[{people:[1,2],to:1,minutes:2},{people:[1],to:0,minutes:1},{people:[5,10],to:1,minutes:10},{people:[2],to:0,minutes:2},{people:[1,2],to:1,minutes:2}];
export const initial=():State=>({sides:{1:0,2:0,5:0,10:0},torchSide:0,holder:1,total:0});
export const after=(moves:Move[],count:number):State=>{
 const s=initial();
 for(const move of moves.slice(0,count)){
  if(move.people.length<1||move.people.length>2)throw Error('Bridge capacity');
  if(move.minutes!==Math.max(...move.people))throw Error('Pair must use slower duration');
  if(move.to===s.torchSide||move.people.some(p=>s.sides[p]!==s.torchSide))throw Error('People and torch must depart together');
  for(const p of move.people)s.sides[p]=move.to;
  s.torchSide=move.to;s.holder=move.people[0];s.total+=move.minutes;
 }
 return s;
};
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const ease=(v:number)=>{v=clamp(v);return v*v*(3-2*v);};
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const bankX=(side:Side)=>side?1620:300;
export const slotY=(p:Person)=>370+PEOPLE.indexOf(p)*110;
export const slot=(p:Person,side:Side)=>({x:bankX(side),y:slotY(p)});
// Motion has a visible hand-off, departure, crossing, arrival and settled hold.
export const stages={handoff:.12,depart:.24,align:.36,cross:.68,slot:.80,arrive:.90};
export const personPosition=(person:Person,state:State,move:Move|undefined,progress:number)=>{
 const start=slot(person,state.sides[person]);
 if(!move||!move.people.includes(person))return start;
 const n=move.people.indexOf(person),bridgeY=move.people.length===1?560:480+n*160;
 const x1=move.to?525:1395,x2=move.to?1395:525,end=slot(person,move.to);
 if(progress<stages.handoff)return start;
 if(progress<stages.depart){const p=ease((progress-stages.handoff)/(stages.depart-stages.handoff));return{x:mix(start.x,x1,p),y:start.y};}
 if(progress<stages.align){const p=ease((progress-stages.depart)/(stages.align-stages.depart));return{x:x1,y:mix(start.y,bridgeY,p)};}
 if(progress<stages.cross){const p=ease((progress-stages.align)/(stages.cross-stages.align));return{x:mix(x1,x2,p),y:bridgeY};}
 if(progress<stages.slot){const p=ease((progress-stages.cross)/(stages.slot-stages.cross));return{x:x2,y:mix(bridgeY,end.y,p)};}
 if(progress<stages.arrive){const p=ease((progress-stages.slot)/(stages.arrive-stages.slot));return{x:mix(x2,end.x,p),y:end.y};}
 return end;
};
const torchOffset=(side:Side)=>side?-120:120;
export const torchPosition=(state:State,move:Move|undefined,progress:number)=>{
 const old=slot(state.holder,state.torchSide),oldTorch={x:old.x+torchOffset(state.torchSide),y:old.y};
 if(!move)return oldTorch;
 const carrier=move.people[0],from=slot(carrier,state.torchSide),next={x:from.x+torchOffset(state.torchSide),y:from.y};
 if(progress<stages.handoff){const p=ease(progress/stages.handoff);return{x:mix(oldTorch.x,next.x,p),y:mix(oldTorch.y,next.y,p)};}
 const at=personPosition(carrier,state,move,progress);
 // Keep the one torch beside its carrier. Its offset turns only while stopped at the bank.
 const landing=ease((progress-stages.cross)/(stages.slot-stages.cross));
 const angle=mix(move.to?0:-Math.PI,move.to?-Math.PI:0,landing);
 return{x:at.x+120*Math.cos(angle),y:at.y+120*Math.sin(angle)};
};
