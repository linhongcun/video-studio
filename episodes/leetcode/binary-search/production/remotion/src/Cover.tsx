import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const values=[1,3,5,7,9,11,13,15];
const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=>{
 const gap=width/8,box=gap*.82,cx=(i:number)=>gap*(i+.5),cy=height*.42;
 return <svg data-cover-diagram="true" style={{position:'absolute',left:x,top:y,width,height}} viewBox={`0 0 ${width} ${height}`}>
  <text x={width/2} y={height*.09} textAnchor="middle" fontFamily={FONT} fontSize={Math.min(35,width*.043)} fill={C.gold}>目标：13</text>
  {values.map((n,i)=>{const excluded=i<=3;return <g key={n} opacity={excluded?.38:1}>
   <rect x={cx(i)-box/2} y={cy-box/2} width={box} height={box} rx={8} fill={C.surface} stroke={i===3?C.gold:i===6?C.teal:C.edge} strokeWidth={i===3||i===6?3:1.5}/>
   <text x={cx(i)} y={cy+box*.25} textAnchor="middle" fontFamily={MONO} fontSize={box*.63} fill={i===6?C.teal:C.text}>{n}</text>
   <text x={cx(i)} y={cy+box*.95} textAnchor="middle" fontFamily={MONO} fontSize={Math.max(20,box*.28)} fill={C.muted}>{i}</text>
  </g>})}
  <path d={`M ${cx(0)-box*.5} ${cy+box*1.3} v 12 H ${cx(3)+box*.5} v -12`} stroke={C.gold} strokeWidth={3} fill="none"/>
  <text x={(cx(0)+cx(3))/2} y={cy+box*2.2} textAnchor="middle" fontFamily={FONT} fontSize={Math.min(31,width*.038)} fill={C.gold}>都 ≤ 7 &lt; 13</text>
  <path d={`M ${cx(4)-box*.6} ${cy-box*.8} h ${3*gap+box*1.2} v ${box*2.45} H ${cx(4)-box*.6} Z`} fill="none" stroke={C.teal} strokeWidth={2}/>
  <text x={width/2} y={height*.94} textAnchor="middle" fontFamily={FONT} fontSize={Math.min(29,width*.035)} fill={C.muted}>示例 · 顺序让排除有依据</text>
 </svg>;
};
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 62%, #194B7060, transparent 62%)'}}/>
 <div style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / LeetCode 704</div>
 <div style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>二分查找</div>
 <div style={{position:'absolute',left:120,top:310,width:840,fontSize:103,fontWeight:800,lineHeight:1.22,letterSpacing:-3}}>为什么能<br/><span style={{color:C.gold}}>放心排除一半？</span></div>
 <Diagram x={120} y={650} width={840} height={460}/>
 <div style={{position:'absolute',left:120,top:1150,width:840,fontSize:29,color:C.muted}}>有序是前提 · 找不到也能正确停下</div>
</div>;
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 if(size==='3x4')return <AbsoluteFill><Portrait/></AbsoluteFill>;
 if(size==='4x3')return <AbsoluteFill style={{background:C.bg}}><div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div></AbsoluteFill>;
 const spec=(covers.sizes as Record<string,any>)[size];
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
  <div style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / LeetCode 704</div>
  <div style={{position:'absolute',left:180,top:220,fontSize:42,color:C.muted}}>二分查找</div>
  <div style={{position:'absolute',left:180,top:306,width:840,fontSize:111,fontWeight:800,lineHeight:1.2,letterSpacing:-3}}>为什么能<br/><span style={{color:C.gold}}>放心排除一半？</span></div>
  <div style={{position:'absolute',left:180,top:700,width:820,fontSize:32,color:C.muted}}>有序，才排得安全</div>
  <Diagram x={1100} y={350} width={660} height={450}/>
 </AbsoluteFill>;
};
