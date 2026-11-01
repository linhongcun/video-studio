import React from 'react';
import {C,FONT,MONO} from './theme';
import model from '../../model.json';
export const M:any=model;
export const COLORS:Record<string,string>={A:C.blue,B:C.teal,C:'#B4A0FF',D:C.gold};
export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const ease=(n:number)=>{const t=clamp(n);return t*t*(3-2*t);};
export const progress=(f:number,a:number,b:number)=>ease((f-a)/Math.max(1,b-a));
export const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
export const T=({x,y,size=34,color=C.text,anchor='start',children,mono=false,weight=500,...props}:any)=><text x={x} y={y} fill={color} fontSize={size} fontFamily={mono?MONO:FONT} textAnchor={anchor} fontWeight={weight} {...props}>{children}</text>;
export const Head=({chapter,title,sub}:any)=><>
 <T x={115} y={73} size={24} color={C.teal}>{chapter}</T>
 <T x={1805} y={73} size={25} color={C.muted} anchor="end">IT小村 · 工程算法 EA01</T>
 <T x={115} y={153} size={49} weight={750}>{title}</T>
 <T x={118} y={211} size={29} color={C.muted}>{sub}</T>
</>;
export const Note=({children,color=C.muted}:any)=><T x={960} y={931} size={27} anchor="middle" color={color} data-note="true">{children}</T>;
export const Pill=({x,y,label,color=C.teal,w=160,size=29,opacity=1}:any)=><g opacity={opacity}>
 <rect x={x-w/2} y={y-31} width={w} height={55} rx={14} fill={C.surface} stroke={color} strokeWidth={2}/>
 <T x={x} y={y+7} size={size} color={color} anchor="middle" weight={650}>{label}</T>
</g>;
export const Arrow=({x1,y1,x2,y2,color=C.muted,opacity=1,dashed=false}:any)=>{
 const a=Math.atan2(y2-y1,x2-x1),back=13;
 return <g opacity={opacity}><line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={3} strokeDasharray={dashed?'9 9':undefined}/><path d={`M${x2-back*Math.cos(a-.45)} ${y2-back*Math.sin(a-.45)}L${x2} ${y2}L${x2-back*Math.cos(a+.45)} ${y2-back*Math.sin(a+.45)}`} fill="none" stroke={color} strokeWidth={3}/></g>;
};
export const Cache=({x,y,id,detail='',dim=false,opacity=1,w=220}:any)=><g opacity={opacity} data-cache={id}>
 <rect x={x-w/2} y={y-68} width={w} height={136} rx={20} fill={C.surface} stroke={dim?C.edge:COLORS[id]} strokeWidth={3}/>
 <T x={x} y={y-15} size={34} color={COLORS[id]} anchor="middle" weight={700}>{id}缓存</T>
 {detail&&<T x={x} y={y+35} size={25} color={C.muted} anchor="middle">{detail}</T>}
</g>;
export const Panel=({x=1190,y=315,width=595,title,children}:any)=><g>
 <line x1={x} x2={x+width} y1={y+38} y2={y+38} stroke={C.edge} strokeWidth={2}/>
 <T x={x} y={y} size={28} color={C.muted}>{title}</T>
 {children}
</g>;
export const point=(v:number,r=250,cx=660,cy=553)=>{const a=v*Math.PI*2/100-Math.PI/2;return{x:cx+Math.cos(a)*r,y:cy+Math.sin(a)*r};};
export const arc=(from:number,to:number,r=250,cx=660,cy=553)=>{
 const end=to<from?to+100:to,a=point(from,r,cx,cy),b=point(end,r,cx,cy);
 return `M${a.x} ${a.y}A${r} ${r} 0 ${end-from>50?1:0} 1 ${b.x} ${b.y}`;
};
type Segment={from:number;to:number;color:string;opacity?:number};
export const Ring=({nodes=M.nodesBefore,keys=[],focus,trace,segments=[],dOpacity=1,morph=1,showNodeLabels=true,showZero=true,centerText='编号空间',size=1}:any)=>{
 const cx=660,cy=553,r=250;
 const pos=(v:number,rad=r)=>{const p=point(v,rad,cx,cy);return{x:mix(235+v*8.6,p.x,morph),y:mix(550,p.y,morph)};};
 const path=Array.from({length:101},(_,i)=>{const p=pos(i);return `${i?'L':'M'}${p.x} ${p.y}`;}).join(' ');
 return <g data-ring="true">
  <path d={path} stroke={C.edge} strokeWidth={5} fill="none"/>
  {morph>.99&&segments.map((v:Segment,i:number)=><path key={i} d={arc(v.from,v.to,r+8)} stroke={v.color} strokeWidth={14} opacity={v.opacity??.8} fill="none" strokeLinecap="butt"/>)}
  {morph>.99&&<><T x={cx} y={cy-20} size={30} anchor="middle" color={C.muted}>{centerText}</T><T x={cx} y={cy+26} size={30} anchor="middle" mono color={C.muted}>0—99 · 示例</T></>}
  {showZero&&(morph>.99?<><line x1={cx} x2={cx} y1={cy-r-10} y2={cy-r-26} stroke={C.muted} strokeWidth={2}/><T x={cx} y={cy-r-42} size={25} anchor="middle" color={C.muted}>0 / 100</T></>:<><T x={235} y={514} size={25} anchor="middle" color={C.muted}>0</T><T x={1086} y={514} size={25} anchor="middle" color={C.muted}>99</T></>)}
  {morph>.99&&<><path d={arc(3,9,310)} fill="none" stroke={C.muted} strokeWidth={2}/><path d={`M${point(9,310).x-11} ${point(9,310).y-7}l11 7l-3 -14`} fill="none" stroke={C.muted} strokeWidth={2}/></>}
  {morph>.99&&keys.map((v:number)=>{const p=point(v,217),t=point(v,184);return <g key={v} opacity={focus===undefined||v===focus?1:.32} data-key-position={v}>
   <circle cx={p.x} cy={p.y} r={focus===v?9:5} fill={focus===v?C.text:C.muted}/>
   <T x={t.x} y={t.y+8} size={26} mono anchor="middle" color={focus===v?C.text:C.muted}>{v}</T>
  </g>;})}
  {trace&&morph>.99&&<g data-trace-from={trace.from} data-trace-to={trace.to}>
   <path d={arc(trace.from,trace.to,r)} fill="none" stroke={C.gold} strokeWidth={6} opacity={.23}/>
   {trace.progress>0&&<path d={arc(trace.from,mix(trace.from,trace.to,trace.progress),r)} fill="none" stroke={C.gold} strokeWidth={6}/>}
   <circle cx={point(mix(trace.from,trace.to,trace.progress)).x} cy={point(mix(trace.from,trace.to,trace.progress)).y} r={11} fill={C.text}/>
  </g>}
  {nodes.map((n:any)=>{const p=pos(n.position),lab=pos(n.position,318),op=n.id==='D'?dOpacity:1;return <g key={n.id+'-'+n.position} opacity={op} data-node={n.id} data-position={n.position}>
   <circle cx={p.x} cy={p.y} r={nodes.length>5?18:29} fill={C.bg} stroke={COLORS[n.id]} strokeWidth={4}/>
   <T x={p.x} y={p.y+(nodes.length>5?8:12)} size={nodes.length>5?23:35} anchor="middle" color={COLORS[n.id]} weight={700}>{n.id}</T>
   {showNodeLabels&&morph>.99&&<T x={lab.x} y={lab.y+10} size={29} anchor={n.position===50?'middle':n.position<50?'start':'end'} color={COLORS[n.id]}>{n.id} · {n.position}</T>}
  </g>;})}
 </g>;
};
