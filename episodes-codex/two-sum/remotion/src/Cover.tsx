import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=>{
 const cx=(i:number)=>width*(.2+.3*i),cy=height*.35,b=width*.17;
 return <svg data-cover-diagram="true" style={{position:'absolute',left:x,top:y,width,height}} viewBox={`0 0 ${width} ${height}`}>
  <text x={width*.5} y={height*.08} textAnchor="middle" fontFamily={FONT} fontSize={width*.046} fill={C.gold}>示例 · 目标 6</text>
  {[3,8,3].map((value,i)=><g key={i}>
   <rect x={cx(i)-b/2} y={cy-b/2} width={b} height={b} rx={12} fill={C.surface} stroke={i===1?C.edge:i===2?C.gold:C.teal} strokeWidth={i===1?2:3}/>
   <text x={cx(i)} y={cy+b*.25} textAnchor="middle" fontFamily={MONO} fontSize={b*.69} fill={i===2?C.gold:i===0?C.teal:C.text}>{value}</text>
   <text x={cx(i)} y={cy+b*.93} textAnchor="middle" fontFamily={MONO} fontSize={b*.31} fill={C.muted}>{i}</text>
  </g>)}
  <path d={`M ${cx(0)} ${cy+b*1.17} V ${height*.76} H ${cx(2)} V ${cy+b*1.17}`} fill="none" stroke={C.teal} strokeWidth={3}/>
  <text x={width*.5} y={height*.91} textAnchor="middle" fontFamily={FONT} fontSize={width*.043} fill={C.teal}>两个 3，两个不同下标</text>
 </svg>;
};
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 62%, #194B7060, transparent 62%)'}}/>
 <div style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / LeetCode 1</div>
 <div style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>两数之和</div>
 <div style={{position:'absolute',left:120,top:310,width:840,fontSize:103,fontWeight:800,lineHeight:1.22,letterSpacing:-3}}>为什么要先查，<br/><span style={{color:C.gold}}>再记录？</span></div>
 <Diagram x={120} y={650} width={840} height={460}/>
 <div style={{position:'absolute',left:120,top:1150,width:840,fontSize:29,color:C.muted}}>先查询，再记录 · 同一格不能用两次</div>
</div>;
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 if(size==='3x4')return <AbsoluteFill><Portrait/></AbsoluteFill>;
 if(size==='4x3')return <AbsoluteFill style={{background:C.bg}}><div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div></AbsoluteFill>;
 const spec=(covers.sizes as Record<string,any>)[size];
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
  <div style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / LeetCode 1</div>
  <div style={{position:'absolute',left:180,top:220,fontSize:42,color:C.muted}}>两数之和</div>
  <div style={{position:'absolute',left:180,top:306,width:840,fontSize:108,fontWeight:800,lineHeight:1.2,letterSpacing:-3}}>为什么要先查，<br/><span style={{color:C.gold}}>再记录？</span></div>
  <div style={{position:'absolute',left:180,top:700,width:820,fontSize:32,color:C.muted}}>先查询，才能避免同一格用两次</div>
  <Diagram x={1100} y={350} width={660} height={450}/>
 </AbsoluteFill>;
};
