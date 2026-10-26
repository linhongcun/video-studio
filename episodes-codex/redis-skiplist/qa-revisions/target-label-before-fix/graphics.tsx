import React from 'react';
import rawModel from '../../model.json';
import {C,FONT,MONO} from './theme';
import type {NodeRecord,Snapshot,Link} from './types';
export const M:any=rawModel;
export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const ease=(n:number)=>{const t=clamp(n);return t*t*(3-2*t);};
export const progress=(f:number,a:number,b:number)=>ease((f-a)/Math.max(1,b-a));
export const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
const allValues=[...M.existingValues,M.newNode.value].sort((a:number,b:number)=>a-b);
const column=new Map(allValues.map((v:number,i:number)=>[v,285+i*175]));
export const X=(id:string)=>id===M.head?138:Number(column.get(Number((M.before.nodes[id]??M.after.nodes[id])?.value)));
export const Y=(level:number)=>level===0?660:385;
export const HALF_W=52,HALF_H=46;
export const value=(id:string)=>id===M.head?'起点':String((M.before.nodes[id]??M.after.nodes[id]).value);
export const snapshotAt=(writes:number):Snapshot=>writes<=0?M.insertion.allocated:M.insertion.pointerWrites[Math.min(writes,4)-1].snapshot;
export const links=(snapshot:Snapshot):Link[]=>Object.values(snapshot.nodes).flatMap(n=>n.forward.flatMap((to,level)=>to===null?[]:[{from:n.id,to,level}]));
for(const snap of [M.before,M.insertion.allocated,...M.insertion.pointerWrites.map((w:any)=>w.snapshot),M.after]){
 for(const link of links(snap)){
  if(!snap.nodes[link.to]||snap.nodes[link.to].height<=link.level)throw Error('Invalid model link '+JSON.stringify(link));
  if(!(X(link.to)>X(link.from)))throw Error('Non-forward teaching link '+JSON.stringify(link));
 }
}
export const T=({x,y,size=34,color=C.text,anchor='start',mono=false,weight=500,maxWidth,children,...props}:any)=><text x={x} y={y} fill={color} fontSize={size} fontFamily={mono?MONO:FONT} textAnchor={anchor} fontWeight={weight} data-max-width={maxWidth} {...props}>{children}</text>;
export const Head=({chapter,title,sub}:any)=><>
 <T x={115} y={73} size={24} color={C.teal} weight={700}>Redis 跳表</T>
 <T x={315} y={73} size={24} color={C.muted}>{chapter}</T>
 <T x={1805} y={73} size={25} color={C.muted} anchor="end">IT小村 · 工程算法 03</T>
 <T x={115} y={153} size={49} weight={750} maxWidth={1690}>{title}</T>
 <T x={118} y={211} size={29} color={C.muted} maxWidth={1680}>{sub}</T>
</>;
export const Note=({children,color=C.muted}:any)=><T x={960} y={925} size={25} anchor="middle" color={color} maxWidth={1740}>{children}</T>;
export const Pill=({x=960,y=842,w=1410,label,color=C.teal,size=35,opacity=1}:any)=><g opacity={opacity}>
 <rect x={x-w/2} y={y-43} width={w} height={86} rx={18} fill={C.surface} stroke={color} strokeWidth={2}/>
 <T x={x} y={y+12} size={size} anchor="middle" color={color} weight={650} maxWidth={w-42}>{label}</T>
</g>;
export const Result=({kind,label,color=C.teal,opacity=1,...attrs}:any)=><g data-result-kind={kind} opacity={opacity} {...attrs}><Pill label={label} color={color}/></g>;
export const Target=({newNode=false}:any)=><g data-target-value={M.target}>
 <rect x={1515} y={246} width={245} height={56} rx={13} fill={C.surface} stroke={C.gold} strokeWidth={1.5}/>
 <T x={1637} y={283} size={28} anchor="middle" color={C.gold} weight={650}>{newNode?'待接新节点':'目标'} {M.target}</T>
</g>;
const oldBypass=(l:Link,detour:boolean)=>{const pred=M.search.predecessors[l.level];return detour&&pred!==undefined&&l.from===pred&&l.to===M.before.nodes[pred].forward[l.level];};
export const edgeGeometry=(l:Link,detour=false)=>{
 const x1=X(l.from)+HALF_W,x2=X(l.to)-HALF_W,y=Y(l.level),bend=oldBypass(l,detour)?(l.level===1?-110:110):0;
 const a={x:x1,y},b={x:mix(x1,x2,.32),y:y+bend},c={x:mix(x1,x2,.68),y:y+bend},d={x:x2,y};
 const point=(p:number)=>{const t=clamp(p),u=1-t;return{x:u*u*u*a.x+3*u*u*t*b.x+3*u*t*t*c.x+t*t*t*d.x,y:u*u*u*a.y+3*u*u*t*b.y+3*u*t*t*c.y+t*t*t*d.y};};
 const angle=Math.atan2(d.y-c.y,d.x-c.x),back=12;
 return{d:bend?`M${x1} ${y}C${b.x} ${b.y},${c.x} ${c.y},${x2} ${y}`:`M${x1} ${y}L${x2} ${y}`,
  arrow:`M${d.x-back*Math.cos(angle-.45)} ${d.y-back*Math.sin(angle-.45)}L${d.x} ${d.y}L${d.x-back*Math.cos(angle+.45)} ${d.y-back*Math.sin(angle+.45)}`,
  point,x1,x2,y,bend};
};
const sameLink=(a:Link|undefined,b:Link)=>a&&a.from===b.from&&a.to===b.to&&a.level===b.level;
export const Edge=({link,detour=false,color=C.edge,width=3,kind='actual',opacity=1}:any)=>{
 const g=edgeGeometry(link,detour);return <g opacity={opacity} data-edge-from={link.from} data-edge-to={link.to} data-edge-level={link.level} data-edge-kind={kind}>
  <path d={g.d} fill="none" stroke={color} strokeWidth={width} strokeDasharray={kind==='proposed'?'9 7':undefined}/>
  <path d={g.arrow} fill="none" stroke={color} strokeWidth={width}/>
 </g>;
};
export const MoveDot=({link,p,detour=false,kind='advance'}:any)=>{
 const g=edgeGeometry(link,detour),pt=g.point(p);return <g data-motion-kind={kind} data-motion-from={link.from} data-motion-to={link.to} data-motion-level={link.level} data-motion-progress={p}><circle cx={pt.x} cy={pt.y} r={9} fill={C.text} stroke={C.gold} strokeWidth={2}/></g>;
};
export const Drop=({node,p=0,moving=false}:any)=>{
 const x=X(node),y1=Y(1)+HALF_H+8,y2=Y(0)-HALF_H-8;
 return <g data-motion-kind="descend" data-motion-from={node} data-motion-to={node} data-motion-level={1} data-motion-to-level={0} data-motion-progress={p}>
  <path d={`M${x} ${y1}V${y2}`} fill="none" stroke={C.gold} strokeWidth={4}/>
  <path d={`M${x-10} ${y2-13}L${x} ${y2}L${x+10} ${y2-13}`} fill="none" stroke={C.gold} strokeWidth={4}/>
  {moving&&<circle cx={x} cy={mix(y1,y2,p)} r={9} fill={C.text} stroke={C.gold} strokeWidth={2}/>}
 </g>;
};
export const Cursor=({node,level=0,color=C.gold}:any)=><g data-cursor-node={node} data-cursor-level={level}><rect x={X(node)-HALF_W-7} y={Y(level)-HALF_H-7} width={2*HALF_W+14} height={2*HALF_H+14} rx={19} fill="none" stroke={color} strokeWidth={3}/></g>;
export const Graph=({snapshot=M.before,upperOpacity=1,activeLink,cursor,candidate,detour=false,newOpacity=1,skipped=[],hideLabels=false}:any)=>{
 const showUpper=upperOpacity>.001,upper=(Number(upperOpacity)),rec=snapshot as Snapshot;
 return <g data-skiplist-graph="true">
  {!hideLabels&&<><T x={115} y={305} size={28} color={C.muted} opacity={upper}>上层：少量节点的远链接</T><T x={115} y={580} size={28} color={C.muted}>{showUpper?'底层：仍保留全部节点':'按数值从小到大 · 教学示例'}</T></>}
  <g data-actual-links="true">{links(rec).filter(l=>l.level===0||showUpper).map(l=><Edge key={`${l.from}-${l.level}`} link={l} detour={detour} color={sameLink(activeLink,l)?C.gold:C.edge} width={sameLink(activeLink,l)?4:3} opacity={l.level===1?upper:1}/>)}</g>
  {Object.values(rec.nodes).map((n:NodeRecord)=>{
   const id=n.id,isNew=id===M.newNode.id,opacity=isNew?newOpacity:1,head=id===M.head;
   return <g key={id} opacity={opacity} data-node-id={id} data-node-value={n.value??'head'} data-node-height={upper>.04?n.height:1} data-node-source-height={n.height} data-node-inserted={head||rec.reachableBottom.includes(id)?'true':'false'}>
    {n.height>1&&showUpper&&<line x1={X(id)} y1={Y(1)+HALF_H+2} x2={X(id)} y2={Y(0)-HALF_H-2} stroke={isNew?C.blue:C.edge} strokeWidth={2.5} opacity={upper} data-level-stem="true"/>}
    {Array.from({length:n.height},(_,level)=>{if(level===1&&!showUpper)return null;const rejected=candidate?.node===id&&candidate?.level===level&&candidate?.reject;
     return <g key={level} opacity={level===1?upper:1} data-port-node={id} data-port-level={level} data-port-value={n.value??'head'} data-port-next={n.forward[level]??'null'}>
      <rect x={X(id)-HALF_W} y={Y(level)-HALF_H} width={HALF_W*2} height={HALF_H*2} rx={14} fill={isNew?'#1B304B':C.surface} stroke={rejected?C.red:skipped.includes(id)?C.blue:isNew?C.blue:C.edge} strokeWidth={rejected?3:2}/>
      <T x={X(id)} y={Y(level)+(head?9:16)} size={head?25:44} mono={!head} anchor="middle" color={rejected?C.red:isNew?C.blue:C.text} weight={700} data-value-glyph="true">{head?'起点':n.value}</T>
     </g>;
    })}
   </g>;
  })}
  {cursor&&<Cursor {...cursor}/>}
 </g>;
};
export const Comparison=({event,label,color=C.gold}:any)=><g data-comparison="true" data-current={event.current} data-candidate={event.candidate} data-target={M.target} data-can-advance={event.canAdvance?'true':'false'}><Result kind={event.canAdvance?'advance-test':'blocked-test'} label={label} color={color}/></g>;
export const Predecessors=({opacity=1}:any)=><g opacity={opacity}>
 <T x={X(M.search.predecessors[1])} y={310} size={25} anchor="middle" color={C.blue} data-predecessor-level={1} data-predecessor-node={M.search.predecessors[1]}>上层接在{value(M.search.predecessors[1])}后</T>
 <T x={X(M.search.predecessors[0])} y={580} size={25} anchor="middle" color={C.blue} data-predecessor-level={0} data-predecessor-node={M.search.predecessors[0]}>底层接在{value(M.search.predecessors[0])}后</T>
</g>;
