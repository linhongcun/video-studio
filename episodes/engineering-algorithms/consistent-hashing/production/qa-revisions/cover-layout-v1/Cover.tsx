import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
import {COLORS,T,point,arc} from './graphics';
import {useLayoutAudit} from './LayoutAudit';
export const coverSizes:Record<string,{width:number;height:number}>=Object.fromEntries(Object.entries(covers.sizes).map(([key,s]:any)=>[key,{width:s.width,height:s.height}]));
const Diagram=({x,y,w,h}:any)=>{
 const cx=420,cy=230,r=154;
 return <svg x={x} y={y} width={w} height={h} viewBox="0 0 840 520">
  <circle cx={cx} cy={cy} r={r} fill="none" stroke={C.edge} strokeWidth={7}/>
  <path d={arc(50,70,r,cx,cy)} fill="none" stroke={COLORS.D} strokeWidth={15}/>
  {[[20,'A'],[50,'B'],[85,'C'],[70,'D']].map(([n,id]:any)=>{const p=point(n,r,cx,cy),lab=point(n,r+63,cx,cy);return <g key={id}>
   <circle cx={p.x} cy={p.y} r={27} fill={C.bg} stroke={COLORS[id]} strokeWidth={4}/><T x={p.x} y={p.y+11} size={33} anchor="middle" color={COLORS[id]} weight={750}>{id}</T>
   <T x={lab.x} y={lab.y+9} size={28} anchor="middle" color={COLORS[id]}>{n}</T>
  </g>;})}
  <T x={cx} y={cy-5} size={29} anchor="middle" color={C.muted}>旧位置不动</T><T x={cx} y={cy+43} size={29} anchor="middle" color={COLORS.D}>D只接这一段</T>
  <T x={cx} y={482} size={28} anchor="middle" color={C.muted}>示例位置 · 只展示归属变化</T>
 </svg>;
};
const Title=({x,y,size}:any)=><g>{covers.titleLines.map((line:string,i:number)=><T key={line} x={x} y={y+i*size*1.2} size={size} color={i===2?C.gold:C.text} weight={800}>{line}</T>)}</g>;
const Portrait=()=> <svg width={1080} height={1440} viewBox="0 0 1080 1440">
 <T x={120} y={130} size={27} color={C.muted}>IT小村 / 工程算法 EA01</T>
 <T x={120} y={222} size={31} color={C.muted}>{covers.eyebrow}</T>
 <Title x={120} y={365} size={104}/>
 <Diagram x={120} y={672} w={840} h={420}/>
 <T x={120} y={1180} size={29} color={C.muted}>{covers.footer}</T>
</svg>;
export const Cover=({size='16x9',auditLayout=false}:any)=>{
 useLayoutAudit(auditLayout,size,0);const spec=(covers.sizes as any)[size];
 return <AbsoluteFill data-cover-root="true" data-canvas-width={spec.width} data-canvas-height={spec.height} style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 55%, #174B6355, transparent 65%)'}}/>
  {size==='3x4'?<Portrait/>:size==='4x3'?<div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div>:<svg width={1920} height={1080} viewBox="0 0 1920 1080">
   <T x={180} y={134} size={30} color={C.muted}>IT小村 / 工程算法 EA01</T>
   <T x={180} y={276} size={36} color={C.muted}>{covers.eyebrow}</T>
   <Title x={180} y={430} size={112}/>
   <T x={180} y={852} size={31} color={C.muted}>{covers.footer}</T>
   <Diagram x={1030} y={270} w={730} h={570}/>
  </svg>}
 </AbsoluteFill>;
};
