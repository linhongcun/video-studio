import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const s=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9';
 const x=s.content.x,w=s.content.w;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 87% 10%, #194B5C77, transparent 63%)'}}/>
  <div style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,fontSize:wide?31:27,color:C.muted,letterSpacing:3}}>IT小村 <span style={{color:C.edge,margin:'0 12px'}}>/</span> 数据库 · EP.16</div>
  <div style={{position:'absolute',left:x,top:portrait?230:205,width:w,fontSize:wide?110:portrait?98:82,fontWeight:800,lineHeight:1.35,letterSpacing:-3}}>扣了<span style={{color:C.gold}}>钱</span>，<br/>对方<span style={{color:C.red}}>没到账？</span></div>
  <div style={{position:'absolute',left:x,top:portrait?570:495,width:w,fontSize:wide?34:27,color:C.muted}}>两处修改，如何一起生效？</div>
  <div style={{position:'absolute',left:x,top:portrait?700:595,width:w,height:portrait?460:245,display:'flex',flexDirection:portrait?'column':'row',gap:portrait?25:30}}>
   <div style={{flex:1,border:`1px solid ${C.red}66`,background:'#2D202B',borderRadius:18,padding:portrait?28:26,boxSizing:'border-box'}}>
    <div style={{fontSize:wide?30:25,color:C.red,fontWeight:650,marginBottom:20}}>只完成扣款</div>
    <div style={{fontSize:wide?58:42,fontFamily:MONO,color:C.red,fontWeight:700}}>800 <span style={{fontSize:30,color:C.muted}}>/</span> 500</div>
    <div style={{fontSize:23,color:C.muted,marginTop:18}}>一边改了，另一边没改</div>
   </div>
   <div style={{flex:1,border:`1px solid ${C.teal}66`,background:'#102E33',borderRadius:18,padding:portrait?28:26,boxSizing:'border-box'}}>
    <div style={{fontSize:wide?30:25,color:C.teal,fontWeight:650,marginBottom:20}}>一笔事务 · 一起确认</div>
    <div style={{fontSize:wide?58:42,fontFamily:MONO,color:C.teal,fontWeight:700}}>800 <span style={{fontSize:30,color:C.muted}}>/</span> 700</div>
    <div style={{fontSize:23,color:C.muted,marginTop:18}}>两处修改一起生效</div>
   </div>
  </div>
  <div style={{position:'absolute',left:x,top:portrait?1240:875,fontSize:portrait?24:21,color:C.muted}}>同一数据库 · 示例数据 · 非真实转账</div>
 </AbsoluteFill>;
};
