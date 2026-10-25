import React from 'react';
import {C} from './theme';
import {T} from './primitives';
import {World,Focus,fullFocus,GROUND,detailY,overviewY,eggPose,trialView,LANES} from './egg-model';
export const Egg=({x,y,broke=false,holder=false,id=1,scale=1}:any)=><g transform={`translate(${x} ${y}) scale(${scale})`} data-egg={id} data-broken={broke?'true':'false'}>
 {broke?<g fill={C.red} stroke={C.red} strokeWidth={2}><path d="M-22 12 L-9 4 L-5 15 L-18 22Z"/><path d="M-4 18 L5 3 L11 16 L6 24Z"/><path d="M13 17 L22 9 L29 20 L18 24Z"/></g>:<><path d="M0 -27 C-13 -27 -22 -3 -22 9 C-22 36 22 36 22 9 C22 -3 13 -27 0 -27Z" fill="#F5E7CD" stroke="#CDBB99" strokeWidth={2}/><T x={0} y={14} size={25} anchor="middle" color="#463D30" weight={750}>{id}</T></>}
 {holder&&<path d="M-30 38 Q0 53 30 38 M-15 45L-15 56" fill="none" stroke={C.muted} strokeWidth={7} strokeLinecap="round"/>}
</g>;
const floorStatus=(f:number,w:World)=>f<=w.safe?C.teal:f>=w.breaking?C.red:C.edge;
export const Building=({world,focus=fullFocus,view=null,selected=null,planned=[],label='楼层总览',extraFloors=[],showUnknown=true}: {world:World;focus?:Focus;view?:ReturnType<typeof trialView>|null;selected?:number|null;planned?:number[];label?:string;extraFloors?:number[];showUnknown?:boolean})=>{
 const active=view?.trial.floor??selected,knownBreak=world.breaking<=100?world.breaking:null;
 const focusLow=Math.max(0,Math.round(focus.low)),focusHigh=Math.min(100,Math.round(focus.high));
 const localFloors=focus.amount>.8&&focus.high-focus.low<=12.01?Array.from({length:focusHigh-focusLow+1},(_,i)=>focusLow+i):[];
 const labels=Array.from(new Set([0,100,world.safe,knownBreak,active,...extraFloors,...(focus.amount>.5?localFloors:[])].filter((x):x is number=>x!==null&&x!==undefined)));
 return <g data-world={world.id} data-world-state={JSON.stringify(world)} data-focus={JSON.stringify(focus)}>
  <T x={310} y={310} size={25} color={C.muted} anchor="middle">{label}</T>
  <rect x={250} y={350} width={120} height={460} fill={C.surface} stroke={C.edge} rx={6}/>
  {Array.from({length:101},(_,f)=><line key={f} x1={250} x2={370} y1={overviewY(f)} y2={overviewY(f)} stroke={floorStatus(f,world)} strokeWidth={f%10===0?2:1} opacity={f%10===0?.8:.32}/>)}
  {focus.amount>.05&&<rect x={236} y={overviewY(focus.high)} width={148} height={overviewY(focus.low)-overviewY(focus.high)} rx={5} fill={C.gold} fillOpacity={.08*focus.amount} stroke={C.gold} strokeOpacity={focus.amount} strokeWidth={2}/>}
  <T x={228} y={359} size={24} color={C.muted} anchor="end">100</T><T x={228} y={818} size={24} color={C.muted} anchor="end">0</T>
  {[world.safe,knownBreak].filter((x):x is number=>x!==null&&x!==0&&x!==100).map(f=><line key={f} x1={370} x2={410} y1={overviewY(f)} y2={overviewY(f)} stroke={f===world.safe?C.teal:C.red} strokeWidth={3}/>)}
  <T x={310} y={857} size={24} color={C.teal} anchor="middle">已知安全：{world.safe}楼</T><T x={310} y={894} size={24} color={knownBreak===null?C.muted:C.red} anchor="middle">已知会碎：{knownBreak===null?'尚未知':knownBreak+'楼'}</T>
  <T x={905} y={310} size={25} color={C.muted} anchor="middle">{focus.amount<.05?'100层楼 · 每大格10层':focus.amount<.98?'同一楼体 · 正在展开':'局部展开 · 其余楼层压缩'}</T>
  <rect x={780} y={318} width={260} height={492} rx={4} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
  {Array.from({length:101},(_,f)=>{const y=detailY(f,focus),previous=f>0?detailY(f-1,focus):y+20,space=previous-y,coarse=f%10===0,band=f>=10?detailY(f-10,focus)-y:0,windowHeight=space>22?Math.min(17,space-12):coarse&&band>=30?Math.min(18,band-14):0;return space>=10||coarse?<g key={f}><line x1={780} x2={1040} y1={y} y2={y} stroke={floorStatus(f,world)} strokeWidth={coarse?2.5:1.5}/>{windowHeight>0&&f>0&&<><rect x={824} y={y+7} width={46} height={windowHeight} fill={C.edge}/><rect x={944} y={y+7} width={46} height={windowHeight} fill={C.edge}/></>}</g>:null;})}
  {focus.amount>.5&&focus.high<99&&<path d="M779 333l12 -7 12 7 12 -7 M1006 333l12 -7 12 7 12 -7" fill="none" stroke={C.muted} strokeWidth={3} opacity={focus.amount}/>}
  {planned.map(f=><g key={f} data-plan-floor={f}><line x1={772} x2={1050} y1={detailY(f,focus)} y2={detailY(f,focus)} stroke={C.gold} strokeWidth={2} strokeDasharray="8 8"/><circle cx={790} cy={detailY(f,focus)} r={5} fill={C.gold}/></g>)}
  {labels.filter(f=>f>=focus.low&&f<=focus.high||focus.amount<.1).map(f=><g key={f} data-floor-label={f}><T x={extraFloors.includes(f)?650:750} y={detailY(f,focus)+9} size={25} color={f===active?C.gold:f<=world.safe?C.teal:f>=world.breaking?C.red:C.muted} anchor="end" weight={f===active?750:500}>{f}楼</T></g>)}
  {focus.amount>.5&&focus.low>1&&<g opacity={focus.amount}><path d="M779 796l12 -7 12 7 12 -7 M1006 796l12 -7 12 7 12 -7" fill="none" stroke={C.muted} strokeWidth={3}/><T x={907} y={838} size={21} color={C.muted} anchor="middle">中间楼层省略</T></g>}
  {active!==null&&<g data-selected-floor={active}><line x1={1040} x2={1090} y1={detailY(active,focus)} y2={detailY(active,focus)} stroke={C.gold} strokeWidth={4}/><line x1={1090} x2={1340} y1={detailY(active,focus)} y2={detailY(active,focus)} stroke={C.gold} strokeDasharray="7 9" strokeWidth={2}/><T x={1355} y={detailY(active,focus)+9} size={24} color={C.gold}>投下</T></g>}
  <line x1={740} x2={1390} y1={GROUND} y2={GROUND} stroke={C.muted} strokeWidth={4}/><T x={725} y={864} size={25} color={C.muted} anchor="end">楼下地面</T>
  {([1,2] as const).map(id=>{const p=eggPose(id,world,view,focus);return <g key={id} data-egg-actor={id} data-x={p.x} data-y={p.y} data-holder={p.holder?'true':'false'}><Egg {...p} id={id}/>{p.broke&&<T x={p.x} y={808} size={22} color={C.red} anchor="middle">第{id}枚已碎</T>}</g>;})}
  {view&&<T x={1240} y={280} size={25} color={view.landed?(view.trial.broke?C.red:C.teal):C.muted} anchor="middle" data-trial-status="true">{view.phase==='carry'?`带到${view.trial.floor}楼`:view.phase==='ready'?`准备从${view.trial.floor}楼投下`:view.phase==='fall'?'正在下落':view.trial.broke?'落地：碎了':'落地：没碎'}</T>}
 </g>;
};
