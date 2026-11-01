import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const s=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 15%, #17556D88, transparent 65%)'}}/>
  <div style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,color:C.muted,fontSize:27}}>IT小村 / 数据库 · EP.17</div>
  <div style={{position:'absolute',left:x,top:portrait?235:205,width:w,fontSize:wide?108:portrait?94:78,fontWeight:800,lineHeight:1.35,letterSpacing:-3}}>最后 <span style={{color:C.gold}}>1</span> 件，<br/>怎么<span style={{color:C.red}}>都成功了？</span></div>
  <div style={{position:'absolute',left:x,top:portrait?580:490,fontSize:wide?35:27,color:C.muted}}>同一条库存，两次购买请求</div>
  <div style={{position:'absolute',left:x,top:portrait?735:590,width:w,height:portrait?370:240,borderTop:`2px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,display:'flex',alignItems:'center',justifyContent:'space-around'}}>
   <div style={{fontSize:wide?36:29,color:C.gold}}>请求甲</div><div style={{textAlign:'center'}}><div style={{fontSize:24,color:C.muted}}>库存</div><div style={{fontFamily:MONO,fontSize:wide?126:104,color:C.teal}}>1</div></div><div style={{fontSize:wide?36:29,color:C.blue}}>请求乙</div>
  </div>
  <div style={{position:'absolute',left:x,top:portrait?1240:875,fontSize:portrait?25:21,color:C.muted}}>示例数据 · 先加锁读取，再检查库存</div>
 </AbsoluteFill>;
};
