import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';

export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const gold='#FFCC70',teal='#56E4D3',blue='#7DB5FF';
const heights=[2,3,10,5,7,8,9];
const Diagram:React.FC<{x:number;y:number;width:number;height:number}>=({x,y,width,height})=>{
 const px=(i:number)=>45+i*(width-90)/6;
 const base=height-56,unit=(height-110)/10;
 return <svg data-cover-diagram="true" style={{position:'absolute',left:x,top:y,width,height,overflow:'visible'}} viewBox={`0 0 ${width} ${height}`}>
  <defs><linearGradient id="cover-water" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor={blue} stopOpacity=".42"/><stop offset="100%" stopColor={blue} stopOpacity=".12"/></linearGradient></defs>
  <path d={`M ${px(2)} ${base-9*unit} H ${px(6)} V ${base} H ${px(2)} Z`} fill="url(#cover-water)"/>
  <line x1={px(0)-30} y1={base} x2={px(6)+30} y2={base} stroke={C.edge} strokeWidth="2"/>
  <line x1={px(2)} y1={base-9*unit} x2={px(6)} y2={base-9*unit} stroke={blue} strokeWidth="2" strokeDasharray="8 7"/>
  {heights.map((h,i)=>{const selected=i===2||i===6,color=i===2?teal:i===6?gold:C.edge;return <g key={i}>
   <line x1={px(i)} y1={base} x2={px(i)} y2={base-h*unit} stroke={color} strokeWidth={selected?10:7} strokeLinecap="round"/>
   <text x={px(i)} y={base-h*unit-22} textAnchor="middle" fill={selected?color:C.muted} fontFamily={MONO} fontSize="27" fontWeight={selected?700:400}>{h}</text>
  </g>})}
  <path d={`M ${px(2)} ${base+24} v 9 M ${px(2)} ${base+29} H ${px(6)} M ${px(6)} ${base+24} v 9`} fill="none" stroke={C.muted} strokeWidth="2"/>
  <text x={(px(2)+px(6))/2} y={base+57} textAnchor="middle" fill={C.muted} fontFamily={FONT} fontSize="24">宽 4</text>
 </svg>;
};
const Portrait=()=> <div style={{position:'absolute',left:0,top:0,width:1080,height:1440,background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 62%, #194B7060, transparent 62%)'}}/>
 <div style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / LeetCode 11 · 双指针</div>
 <div style={{position:'absolute',left:120,top:214,fontSize:39,color:C.muted,letterSpacing:2}}>盛最多水的容器</div>
 <div style={{position:'absolute',left:120,top:310,width:840,fontSize:109,fontWeight:800,lineHeight:1.18,letterSpacing:-3}}>为什么<br/><span style={{color:gold}}>移动短边？</span></div>
 <Diagram x={120} y={650} width={840} height={460}/>
 <div style={{position:'absolute',left:120,top:1150,width:840,fontSize:29,color:C.muted}}>示例 · 看懂每一次排除的理由</div>
</div>;
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const spec=(covers.sizes as Record<string,any>)[size];
 if(size==='3x4')return <AbsoluteFill><Portrait/></AbsoluteFill>;
 if(size==='4x3')return <AbsoluteFill style={{background:C.bg}}><div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div></AbsoluteFill>;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
  <div style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / LeetCode 11 · 双指针</div>
  <div style={{position:'absolute',left:180,top:220,fontSize:42,color:C.muted,letterSpacing:3}}>盛最多水的容器</div>
  <div style={{position:'absolute',left:180,top:306,width:840,fontSize:119,fontWeight:800,lineHeight:1.18,letterSpacing:-3}}>为什么<br/><span style={{color:gold}}>移动短边？</span></div>
  <div style={{position:'absolute',left:180,top:700,width:820,fontSize:32,color:C.muted}}>看懂每一次排除的理由</div>
  <Diagram x={1100} y={350} width={660} height={450}/>
  <div style={{position:'absolute',left:1100,top:856,width:660,textAlign:'center',fontSize:26,color:C.muted}}>示例 · 宽 × 短边 = 面积</div>
 </AbsoluteFill>;
};
