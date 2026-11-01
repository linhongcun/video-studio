import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const s=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w;
 const title=["点了两次", "只扣一次？"],tag="同一次支付，保留同一个编号";
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 15%, #17556D88, transparent 65%)'}}/>
  <div data-cover-text style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,color:C.muted,fontSize:27}}>IT小村 / 扛住高峰 · EP.12</div>
  <div data-cover-text style={{position:'absolute',left:x,top:portrait?235:205,width:w,fontSize:wide?104:portrait?94:78,fontWeight:800,lineHeight:1.35,letterSpacing:-3}}>{title[0]}<br/><span style={{color:C.gold}}>{title[1]}</span></div>
  <div data-cover-text style={{position:'absolute',left:x,top:portrait?580:490,fontSize:wide?35:27,color:C.muted}}>{tag}</div>
  <div style={{position:'absolute',left:x,top:portrait?735:590,width:w,height:portrait?370:240,borderTop:`2px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,display:'flex',alignItems:'center',justifyContent:'space-around'}}>
   <div style={{fontSize:wide?39:29,color:C.blue}}>7042 →</div><div style={{textAlign:"center"}}><div style={{fontSize:25,color:C.muted}}>同一笔支付</div><div style={{fontFamily:MONO,fontSize:wide?100:80,color:C.teal}}>−30</div></div><div style={{fontSize:wide?39:29,color:C.gold}}>只扣一次</div>
  </div>
  <div data-cover-text style={{position:'absolute',left:x,top:portrait?1240:875,fontSize:portrait?25:21,color:C.muted}}>教学示例 · 因果动作讲清原理</div>
 </AbsoluteFill>;
};
