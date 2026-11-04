import data from '../../model-data.json';
import {Shot} from './data';

export type Outcome='L'|'B'|'R';
export type Node={id:string;prefix:string;number:number;left:number[];right:number[];normalReferences:number[];candidates:string[];knownNormal:number[];partitions:Record<Outcome,string[]>;answers:Record<Outcome,string|null>|null};
export const model=data;
export const nodes=data.nodes as Node[];
export const node=(prefix:string)=>{const n=nodes.find(n=>n.prefix===prefix);if(!n)throw Error('Unknown model prefix '+prefix);return n;};
export const OUTCOMES:Outcome[]=['L','B','R'];
export const word=(o:Outcome)=>data.outcomes[o];
export const caseBall=(c:string)=>Number(c.slice(0,-1));
export const caseWord=(c:string,question=false)=>`${caseBall(c)}${c.endsWith('H')?'重':'轻'}${question?'？':''}`;
export const casesWord=(cases:string[],question=true)=>cases.map(c=>caseWord(c,question)).join(' · ');
export const allBalls=Array.from({length:data.rules.balls},(_,i)=>i+1);
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const tween=(f:number,a:number,b:number)=>{const p=clamp((f-a)/Math.max(1,b-a));return p*p*(3-2*p);};
export const timings=(s:Shot)=>{const [v,w]=s.voice;return {a:v.localStart,b:v.localEnd,c:w.localStart,e:w.localEnd};};
export const inWindow=(start:number,end:number,part:number)=>start+(end-start)*part;
export type Point={x:number;y:number};
export type Layout=Record<number,Point>;
export const rackLayout=():Layout=>Object.fromEntries([1,2,3,4,9,10,5,6,7,8,11,12].map((id,i)=>[id,{x:245+(i%6)*286,y:390+Math.floor(i/6)*170}]));
/** Separate the rows before crossing columns; all twelve identities stay visible. */
export const firstWeighingLayout=(f:number,a:number):Layout=>{
  const from=rackLayout(),to=boardLayout(node('').left,node('').right),layout={...from};
  for(const id of node('').left){const p=tween(f,a+4,a+30);layout[id]={x:from[id].x+(to[id].x-from[id].x)*p,y:from[id].y+(to[id].y-from[id].y)*p};}
  for(const id of node('').right){const p=tween(f,a+32,a+91);layout[id]=p<.2?{x:from[id].x,y:from[id].y+(600-from[id].y)*(p/.2)}:p<.8?{x:from[id].x+(to[id].x-from[id].x)*((p-.2)/.6),y:600}:{x:to[id].x,y:600+(to[id].y-600)*((p-.8)/.2)};}
  for(const id of [11,12]){const p=tween(f,a+94,a+112);layout[id]={x:from[id].x+(to[id].x-from[id].x)*p,y:from[id].y+(to[id].y-from[id].y)*p};}
  for(const id of [9,10]){const p=tween(f,a+114,a+133);layout[id]={x:from[id].x+(to[id].x-from[id].x)*p,y:from[id].y+(to[id].y-from[id].y)*p};}
  return layout;
};
export const boardLayout=(left:number[],right:number[],pending:number[]=[],slotsLeft=left,slotsRight=right):Layout=>{
  const off=allBalls.filter(id=>!left.includes(id)&&!right.includes(id)&&!pending.includes(id));
  return Object.fromEntries(allBalls.map(id=>{
    if(left.includes(id)){const i=slotsLeft.indexOf(id);return [id,{x:245+(i%4)*125,y:457+Math.floor(i/4)*113}];}
    if(right.includes(id)){const i=slotsRight.indexOf(id);return [id,{x:825+(i%4)*125,y:457+Math.floor(i/4)*113}];}
    if(pending.includes(id)){const i=pending.indexOf(id);return [id,{x:230+i*210,y:568}];}
    // A ball keeps its own off-pan slot, even when neighbours move onstage.
    const i=id-1;return [id,{x:1395+(i%4)*130,y:410+Math.floor(i/4)*105}];
  }));
};
export const lerpLayout=(a:Layout,b:Layout,p:number):Layout=>Object.fromEntries(allBalls.map(id=>[id,{x:a[id].x+(b[id].x-a[id].x)*p,y:a[id].y+(b[id].y-a[id].y)*p}]));
type Move={id:number;from:Point;to:Point;points:Point[]};
const near=(a:Point,b:Point)=>Math.hypot(a.x-b.x,a.y-b.y)<1;
/** One numbered ball moves at a time. Off-pan columns have a 72px clear lane. */
export const safeTransition=(from:Node,to:Node,f:number,start:number,end:number)=>{
  const initial=boardLayout(from.left,from.right),target=boardLayout(to.left,to.right),off=boardLayout([],[]),positions={...initial},sourcePan=[...from.left,...from.right],targetPan=[...to.left,...to.right],moves:Move[]=[];
  const add=(id:number,destination:Point,kind:'out'|'across'|'in')=>{
    const p=positions[id],lane=(kind==='in'?p.x:destination.x)-65,points=kind==='out'?[p,{x:p.x,y:730},{x:lane,y:730},{x:lane,y:destination.y},destination]:kind==='in'?[p,{x:lane,y:p.y},{x:lane,y:730},{x:destination.x,y:730},destination]:[p,{x:p.x,y:730},{x:destination.x,y:730},destination];
    moves.push({id,from:p,to:destination,points});positions[id]=destination;
  };
  for(const id of sourcePan.filter(id=>!targetPan.includes(id)))add(id,off[id],'out');
  const across=sourcePan.filter(id=>targetPan.includes(id)&&!near(initial[id],target[id])),arrivals=targetPan.filter(id=>!sourcePan.includes(id));
  while(across.length){const index=across.findIndex(id=>allBalls.every(other=>other===id||Math.hypot(positions[other].x-target[id].x,positions[other].y-target[id].y)>=60));
    if(index<0){const id=across.shift()!;add(id,off[id],'out');arrivals.push(id);}
    else{const [id]=across.splice(index,1);add(id,target[id],'across');}
  }
  for(const id of arrivals)add(id,target[id],'in');
  if(f<start)return {layout:initial,moving:false};
  if(f>=end||!moves.length)return {layout:target,moving:false};
  const progress=clamp((f-start)/(end-start))*moves.length,index=Math.min(moves.length-1,Math.floor(progress)),p=tween(progress-index,0,1),layout={...initial};
  for(let i=0;i<index;i++)layout[moves[i].id]=moves[i].to;
  const current=moves[index],lengths=current.points.slice(1).map((v,i)=>Math.hypot(v.x-current.points[i].x,v.y-current.points[i].y)),total=lengths.reduce((a,b)=>a+b,0);let distance=p*total;
  for(let i=0;i<lengths.length;i++){if(distance<=lengths[i]||i===lengths.length-1){const a=current.points[i],b=current.points[i+1],q=lengths[i]?distance/lengths[i]:1;layout[current.id]={x:a.x+(b.x-a.x)*q,y:a.y+(b.y-a.y)*q};break;}distance-=lengths[i];}
  return {layout,moving:true};
};
export const normalAfter=(cases:string[])=>allBalls.filter(id=>!cases.some(c=>caseBall(c)===id));
export const main=data.mainExample;
export const mirrorExample=data.traces.find(t=>t.ball===data.mainExample.ball&&t.kind!==data.mainExample.kind)!;
export const lightComparisonExample=data.traces.find(t=>t.case==='9L')!;
