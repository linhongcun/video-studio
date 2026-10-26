import React from 'react';
import model from '../../model.json';
import {C,FONT,MONO} from './theme';
import type {Stage} from './types';
export const M:any=model;
export const item=(key:string)=>{const found=M.items.find((v:any)=>v.key===key);if(!found)throw new Error('Unknown model element '+key);return found;};
export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const ease=(n:number)=>{const t=clamp(n);return t*t*(3-2*t);};
export const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
export const progress=(f:number,a:number,b:number)=>ease((f-a)/Math.max(1,b-a));
export const T=({x,y,size=36,color=C.text,anchor='start',mono=false,weight=500,maxWidth,children,...props}:any)=><text x={x} y={y} fill={color} fontSize={size} fontFamily={mono?MONO:FONT} textAnchor={anchor} fontWeight={weight} data-max-width={maxWidth} {...props}>{children}</text>;
export const Head=({chapter,title,sub}:any)=><>
 <T x={115} y={73} size={24} color={C.teal} weight={700}>布隆过滤器</T>
 <T x={315} y={73} size={24} color={C.muted}>{chapter}</T>
 <T x={1805} y={73} size={25} color={C.muted} anchor="end">IT小村 · 工程算法 02</T>
 <T x={115} y={153} size={49} weight={750} maxWidth={1690}>{title}</T>
 <T x={118} y={211} size={29} color={C.muted} maxWidth={1680}>{sub}</T>
</>;
export const Note=({children,color=C.muted}:any)=><T x={960} y={925} size={25} anchor="middle" color={color} maxWidth={1740}>{children}</T>;
export const Pill=({x=960,y=840,w=1340,label,color=C.teal,size=36,opacity=1}:any)=><g opacity={opacity}>
 <rect x={x-w/2} y={y-43} width={w} height={86} rx={18} fill={C.surface} stroke={color} strokeWidth={2}/>
 <T x={x} y={y+12} size={size} anchor="middle" color={color} weight={650} maxWidth={w-40}>{label}</T>
</g>;
export const Arrow=({x1,y1,x2,y2,color=C.muted,opacity=1}:any)=>{
 const a=Math.atan2(y2-y1,x2-x1),back=14;return <g opacity={opacity}><line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={3}/><path d={`M${x2-back*Math.cos(a-.45)} ${y2-back*Math.sin(a-.45)}L${x2} ${y2}L${x2-back*Math.cos(a+.45)} ${y2-back*Math.sin(a+.45)}`} fill="none" stroke={color} strokeWidth={3}/></g>;
};
export const X=(position:number)=>310+position*185;
export const TOP=548;
export const BitRow=({ones=[],focus=[],zeroFocus=[],label='8个位 · 教学示例',showCount=8}:any)=><g data-bit-row="true">
 <T x={118} y={510} size={28} color={C.muted}>{label}</T>
 <T x={118} y={645} size={28} color={C.muted}>位值</T>
 <T x={118} y={762} size={28} color={C.muted}>位置</T>
 {Array.from({length:M.bitCount},(_,i)=>{const one=ones.includes(i),active=focus.includes(i),zero=zeroFocus.includes(i),color=zero?C.red:active?C.gold:one?C.teal:C.edge;return <g key={i} opacity={i<showCount?1:0} data-bit-index={i} data-bit-value={one?1:0}>
  <rect x={X(i)-75} y={TOP} width={150} height={150} rx={20} fill={one?'#173C41':C.surface} stroke={color} strokeWidth={active||zero?4:2}/>
  <T x={X(i)} y={654} size={78} mono anchor="middle" color={one?C.teal:zero?C.red:C.muted} weight={750}>{one?'1':'0'}</T>
  <T x={X(i)} y={762} size={36} mono anchor="middle" color={active||zero?color:C.muted}>{i}</T>
 </g>;})}
</g>;
export const HashFlow=({element='A',position,phase=0,formal=true,ruleLabel,slot=0,mode='read',showPosition=true,color=C.gold}:any)=>{
 const inputP=ease(phase/.38),outputP=ease((phase-.42)/.58),endX=position===undefined?950:X(position);
 const path=`M950 416Q950 486 ${endX} ${TOP}`;
 const point=(t:number)=>({x:(1-t)*(1-t)*950+2*(1-t)*t*950+t*t*endX,y:(1-t)*(1-t)*416+2*(1-t)*t*486+t*t*TOP});
 const dot=point(outputP);
 return <g data-algorithm-flow={mode} data-flow-element={element} data-flow-position={position} data-flow-slot={slot}>
  <T x={263} y={361} size={28} anchor="end" color={C.muted}>元素</T>
  <rect x={330} y={279} width={220} height={137} rx={21} fill={C.surface} stroke={C.text} strokeWidth={2}/>
  <T x={440} y={383} size={76} mono anchor="middle" weight={750} data-element-text="true">{element}</T>
  <Arrow x1={583} y1={347} x2={698} y2={347} color={phase>0?color:C.edge}/>
  {phase>0&&phase<.38&&<circle cx={mix(589,690,inputP)} cy={347} r={10} fill={C.text}/>}
  <rect x={730} y={279} width={440} height={137} rx={21} fill={C.surface} stroke={phase>0?color:C.edge} strokeWidth={2}/>
  <T x={950} y={317} size={27} anchor="middle" color={C.muted}>{ruleLabel??(formal?'固定哈希':'固定计算')}</T>
  {showPosition&&<T x={950} y={389} size={48} anchor="middle" mono color={color} weight={700} data-position-text="true">位置 {position}</T>}
  {phase>.42&&<g data-active-route="true"><path d={path} fill="none" stroke={color} strokeWidth={3} opacity={.42}/>{outputP<1&&<circle cx={dot.x} cy={dot.y} r={10} fill={C.text} stroke={color} strokeWidth={2}/>}</g>}
 </g>;
};
export const Result=({kind,label,color=C.teal,opacity=1}:any)=><g data-result-kind={kind} opacity={opacity}><Pill label={label} color={color}/></g>;
export const Members=({keys=['A','B'],label='演示中已加入',opacity=1}:any)=><g opacity={opacity} data-members={JSON.stringify(keys)}>
 <T x={1490} y={323} size={26} anchor="middle" color={C.muted}>{label}</T>
 <T x={1490} y={390} size={45} anchor="middle" mono color={C.blue}>{keys.length?keys.join('  /  '):'暂为空'}</T>
</g>;
