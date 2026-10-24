import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={ '16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const s=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9';
 const x=s.content.x,w=s.content.w,headingTop=portrait?235:205;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 10%, #1B536166, transparent 64%)'}}/>
  <div style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,fontSize:wide?31:27,color:C.muted,letterSpacing:3}}>IT小村 <span style={{color:C.edge,margin:'0 12px'}}>/</span> 数据库 · EP.15</div>
  <div style={{position:'absolute',left:x,top:headingTop,width:w,fontSize:wide?110:portrait?98:82,fontWeight:800,lineHeight:1.35,letterSpacing:-3}}>加个<span style={{color:C.teal}}>索引</span>，<br/>为啥就<span style={{color:C.gold}}>快了？</span></div>
  <div style={{position:'absolute',left:x,top:portrait?570:495,width:w,fontSize:wide?34:27,color:C.muted}}>同一笔订单，换一条查找路径。</div>
  <div style={{position:'absolute',left:x,top:portrait?715:595,width:w,height:portrait?445:245,display:'flex',flexDirection:portrait?'column':'row',gap:portrait?26:30}}>
   <div style={{flex:1,border:`1px solid ${C.edge}`,background:C.surface,borderRadius:18,padding:portrait?28:26,boxSizing:'border-box'}}>
    <div style={{fontSize:wide?30:25,color:C.gold,fontWeight:650,marginBottom:24}}>全表扫描</div>
    <div style={{display:'flex',gap:8,alignItems:'center'}}>{Array.from({length:6},(_,i)=><div key={i} style={{height:portrait?42:53,flex:1,borderRadius:4,border:`1px solid ${i===4?C.gold:C.edge}`,background:i===4?'#64502E':'#233247'}}/>)}</div>
    <div style={{fontSize:23,color:C.muted,marginTop:22}}>逐行检查</div>
   </div>
   <div style={{flex:1,border:`1px solid ${C.teal}66`,background:'#102B31',borderRadius:18,padding:portrait?28:26,boxSizing:'border-box'}}>
    <div style={{fontSize:wide?30:25,color:C.teal,fontWeight:650,marginBottom:24}}>索引</div>
    <div style={{display:'flex',alignItems:'center',gap:16,height:portrait?42:53}}><div style={{fontFamily:MONO,fontSize:wide?43:32,fontWeight:700,color:C.teal}}>7042</div><div style={{color:C.teal,fontSize:36}}>→</div><div style={{fontSize:wide?28:23}}>订单记录</div></div>
    <div style={{fontSize:23,color:C.muted,marginTop:22}}>先定位，再读取</div>
   </div>
  </div>
  <div style={{position:'absolute',left:x,top:portrait?1240:875,fontSize:portrait?24:21,color:C.muted}}>示例数据 · 结构示意 · 非性能实测</div>
 </AbsoluteFill>;
};
