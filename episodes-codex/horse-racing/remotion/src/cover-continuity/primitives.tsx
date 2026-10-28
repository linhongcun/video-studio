import React from 'react';
import {PuzzleHeader} from '../../../../_shared/puzzles-video/Frame';
import {C,FONT,MONO} from './theme';
import {GROUPS,HORSES,Shot} from '../data';

export const clamp=(p:number)=>Math.max(0,Math.min(1,p));
export const ease=(p:number)=>{p=clamp(p);return p*p*(3-2*p);};
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const at=(s:Shot,i:number,p:number)=>{
 const start=Number(s.cueFrames?.sentences?.[i]??(i?Math.round(s.durationInFrames*.5):0));
 const end=Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-12);
 return start+(end-start)*p;
};
export const phase=(s:Shot,f:number,i=0,a=.08,b=.78)=>ease((f-at(s,i,a))/Math.max(1,at(s,i,b)-at(s,i,a)));
export const across=(s:Shot,f:number,a=.05,b=.8)=>clamp((f-at(s,0,a))/Math.max(1,at(s,1,b)-at(s,0,a)));
export const steps=(p:number,n:number)=>{const z=clamp(p)*n,i=Math.min(n-1,Math.floor(z));return {index:i,progress:ease(Math.min(1,(z-i)/.65))};};
export const T=({x,y,children,size=32,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
export const Head=({title,sub,kicker='25匹马赛跑',color=C.text}:any)=><PuzzleHeader number="P01" title={title} sub={sub} kicker={kicker} color={color}/>;
export const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={913} anchor="middle" size={31} color={color} alpha={alpha} data-note="true">{children}</T>;
export const CHAMPIONS=GROUPS.map(g=>g+'1');
export const RETAINED=['甲1','甲2','甲3','乙1','乙2','丙1'];
export const FINALISTS=['甲2','甲3','乙1','乙2','丙1'];
export const nodeXY=(id:string)=>{const row=GROUPS.indexOf(id[0]),col=Number(id[1])-1;return {x:420+col*180,y:360+row*103};};
export const Node=({id,x,y,alpha=1,color=C.text,fill=C.surface,scale=1,strokeWidth=1.8,label,tag}:any)=><g transform={`translate(${x} ${y}) scale(${scale})`} opacity={alpha} data-horse-id={id} data-horse-x={x} data-horse-y={y}>
 <rect x={-65} y={-35} width={130} height={70} rx={14} fill={fill} stroke={color} strokeWidth={strokeWidth}/>
 <T x={0} y={12} size={34} color={color} anchor="middle" weight={700}>{label??id}</T>
 {tag&&<T x={0} y={68} size={23} color={color} anchor="middle">{tag}</T>}
</g>;
type BoardProps={
 named?:boolean;knownRows?:number;rankHeaders?:boolean;groupLabels?:boolean;
 alpha?:Record<string,number>;colors?:Record<string,string>;positions?:Record<string,{x:number;y:number}>;
 scales?:Record<string,number>;outlines?:string[];proofTargets?:string[];unknownRows?:boolean;
 rowAlpha?:Record<string,number>;nodeLabel?:Record<string,string>;allAlpha?:number;
};
export const Board=({named=true,knownRows=5,rankHeaders=true,groupLabels=true,alpha={},colors={},positions={},scales={},outlines=[],rowAlpha={},nodeLabel={},allAlpha=1}:BoardProps)=>{
 return <g opacity={allAlpha} data-board="horse-groups">
  {rankHeaders&&[1,2,3,4,5].map((n,col)=><T key={n} x={420+col*180} y={294} anchor="middle" size={25} color={C.muted}>组内第{n}</T>)}
  {groupLabels&&GROUPS.map((g,row)=><T key={g} x={234} y={372+row*103} anchor="middle" size={31} color={C.muted} alpha={rowAlpha[g]??1}>{g}组</T>)}
  {HORSES.map(h=>{
   const pt=positions[h.id]??nodeXY(h.id),known=h.row<knownRows,color=colors[h.id]??(known?C.text:C.muted);
   return <Node key={h.id} id={h.id} {...pt} alpha={(alpha[h.id]??1)*(rowAlpha[h.group]??1)} color={color} scale={scales[h.id]??1} label={nodeLabel[h.id]??(named&&known?h.id:`${String(h.row*5+h.col+1).padStart(2,'0')}`)} strokeWidth={outlines.includes(h.id)?3.5:1.5}/>;
  })}
 </g>;
};
export const Arrow=({from,to,color=C.gold,progress=1,width=4,alpha=1,curve=0}:any)=>{
 const dx=to.x-from.x,dy=to.y-from.y,len=Math.sqrt(dx*dx+dy*dy),ux=dx/Math.max(1,len),uy=dy/Math.max(1,len),start={x:from.x+ux*74,y:from.y+uy*42},end={x:to.x-ux*74,y:to.y-uy*42};
 const mx=(start.x+end.x)/2-uy*curve,my=(start.y+end.y)/2+ux*curve;
 const tip={x:mix(start.x,end.x,progress),y:mix(start.y,end.y,progress)},angle=Math.atan2(dy,dx),p1={x:tip.x-13*Math.cos(angle-.5),y:tip.y-13*Math.sin(angle-.5)},p2={x:tip.x-13*Math.cos(angle+.5),y:tip.y-13*Math.sin(angle+.5)};
 return <g opacity={alpha}><path d={`M ${start.x} ${start.y} Q ${mx} ${my} ${end.x} ${end.y}`} fill="none" stroke={color} strokeWidth={width} pathLength={1} strokeDasharray="1" strokeDashoffset={1-clamp(progress)}/>{progress>.98&&<path d={`M ${p1.x} ${p1.y} L ${tip.x} ${tip.y} L ${p2.x} ${p2.y}`} fill="none" stroke={color} strokeWidth={width}/>}</g>;
};
export const FasterProof=({names,target,reveal=3,alpha=1,conclusion=true}:any)=>{
 const list=names.slice(0,Math.ceil(reveal));
 return <g opacity={alpha} data-proof-target={target} data-proof-count={list.length}>
  <rect x={1365} y={303} width={425} height={506} rx={22} fill={C.surface} stroke={C.edge}/>
  <T x={1578} y={351} size={28} color={C.gold} anchor="middle">已知比 {target} 更快</T>
  {list.map((name:string,i:number)=><g key={name} opacity={clamp(reveal-i)}><circle cx={1442} cy={410+i*92} r={19} fill={C.gold+'18'} stroke={C.gold}/><T x={1442} y={419+i*92} size={23} color={C.gold} anchor="middle">{i+1}</T><T x={1570} y={422+i*92} size={35} color={C.gold} anchor="middle">{name}</T><T x={1685} y={420+i*92} size={24} color={C.muted} anchor="middle">更快</T></g>)}
  {conclusion&&reveal>=3&&<T x={1578} y={770} size={31} color={C.red} anchor="middle">{target} 无缘前三</T>}
 </g>;
};
