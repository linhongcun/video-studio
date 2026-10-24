import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const s=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 15%, #204A7888, transparent 65%)'}}/>
  <div style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,color:C.muted,fontSize:27}}>IT小村 / 分布式 · EP.20</div>
  <div style={{position:'absolute',left:x,top:portrait?235:205,width:w,fontSize:wide?108:portrait?94:78,fontWeight:800,lineHeight:1.35,letterSpacing:-3}}>两个订单，<br/>怎么<span style={{color:C.red}}>同一个号？</span></div>
  <div style={{position:'absolute',left:x,top:portrait?580:490,fontSize:wide?35:27,color:C.muted}}>各自生成，为什么会撞号？</div>
  <div style={{position:'absolute',left:x,top:portrait?735:590,width:w,height:portrait?370:240,borderTop:`2px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,display:'flex',alignItems:'center',justifyContent:'space-around'}}>
   {[{name:'订单甲',color:C.gold},{name:'订单乙',color:C.blue}].map(q=><div key={q.name} style={{textAlign:'center'}}><div style={{fontSize:wide?32:27,color:q.color}}>{q.name}</div><div style={{fontFamily:MONO,fontSize:wide?126:104,color:C.red}}>42</div></div>)}
  </div>
  <div style={{position:'absolute',left:x,top:portrait?1240:875,fontSize:portrait?25:21,color:C.muted}}>示例数据 · 时间、机器编号、序号共同区分</div>
 </AbsoluteFill>;
};
