import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
import {useLayoutAudit} from './LayoutAudit';

export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=>{
 const dx=width/5,dy=height/5,bw=dx*.68,bh=Math.min(58,dy*.63);
 return <svg data-cover-diagram="true" style={{position:'absolute',left:x,top:y,width,height}} viewBox={`0 0 ${width} ${height}`}>
  {['甲','乙','丙','丁','戊'].flatMap((g,r)=>Array.from({length:5},(_,c)=>{
   const candidate=(r===0&&c<3)||(r===1&&c<2)||(r===2&&c===0),champion=r===0&&c===0,color=champion?C.teal:candidate?C.gold:C.muted;
   return <g key={`${g}${c}`} opacity={candidate?1:.28}>
    <rect x={dx*(c+.5)-bw/2} y={dy*(r+.5)-bh/2} width={bw} height={bh} rx={10} fill={C.surface} stroke={color} strokeWidth={candidate?3:1.5}/>
    <text x={dx*(c+.5)} y={dy*(r+.5)+bh*.22} textAnchor="middle" fontFamily={FONT} fontSize={Math.min(33,bh*.6)} fontWeight={700} fill={color}>{g}{c+1}</text>
   </g>;
  }))}
 </svg>;
};
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 84% 65%, #194B7060, transparent 60%)'}}/>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:100,fontSize:28,color:C.muted}}>IT小村 / 趣味推理 P01</div>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>每场最多5匹 · 不能计时</div>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:310,width:840,fontSize:106,fontWeight:800,lineHeight:1.25,letterSpacing:-2}}>25匹马，<br/><span style={{color:C.gold}}>怎样找前三？</span></div>
 <Diagram x={120} y={650} width={840} height={440}/>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:1150,width:840,fontSize:31,color:C.muted}}>每一步排除，都要有依据</div>
</div>;
export const Cover:React.FC<{size?:string;auditLayout?:boolean}>=({size='16x9',auditLayout=false})=>{
 useLayoutAudit(auditLayout,size,0);
 if(size==='3x4')return <AbsoluteFill data-cover-root="true" data-canvas-width={1080} data-canvas-height={1440}><Portrait/></AbsoluteFill>;
 if(size==='4x3')return <AbsoluteFill data-cover-root="true" data-canvas-width={1440} data-canvas-height={1080} style={{background:C.bg}}><div data-layout-text="true" style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div></AbsoluteFill>;
 const spec=(covers.sizes as Record<string,any>)[size];
 return <AbsoluteFill data-cover-root="true" data-canvas-width={1920} data-canvas-height={1080} style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 84% 48%, #194B7059, transparent 60%)'}}/>
  <div data-layout-text="true" style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / 趣味推理 P01</div>
  <div data-layout-text="true" style={{position:'absolute',left:180,top:230,fontSize:40,color:C.muted}}>每场最多5匹 · 不能计时</div>
  <div data-layout-text="true" style={{position:'absolute',left:180,top:332,width:860,fontSize:111,fontWeight:800,lineHeight:1.22,letterSpacing:-2}}>25匹马，<br/><span style={{color:C.gold}}>怎样找前三？</span></div>
  <div data-layout-text="true" style={{position:'absolute',left:180,top:748,width:840,fontSize:34,color:C.muted}}>每一步排除，都要有依据</div>
  <Diagram x={1120} y={275} width={650} height={520}/>
  <div data-layout-text="true" style={{position:'absolute',left:1120,top:856,width:650,textAlign:'center',fontSize:27,color:C.muted}}>只知道名次，够了吗？</div>
 </AbsoluteFill>;
};
