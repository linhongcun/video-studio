import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const c=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=c.content.x,w=c.content.w;
 const panelY=portrait?760:605,panelH=portrait?300:205;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 84% 12%, #18547088, transparent 68%)'}}/>
  <div style={{position:'absolute',left:x,top:c.watermarkZone.y,color:C.muted,fontSize:wide?28:24}}>IT小村 / 分布式 · Saga</div>
  <div style={{position:'absolute',left:x,top:portrait?245:210,width:w,fontWeight:800,fontSize:wide?105:portrait?94:78,lineHeight:1.28,letterSpacing:-2}}>扣款成功<br/><span style={{color:C.teal}}>缺货怎么办？</span></div>
  <div style={{position:'absolute',left:x,top:portrait?555:470,fontSize:wide?37:portrait?32:28,color:C.muted}}>用新退款，处理已经保存的扣款</div>
  <div style={{position:'absolute',left:x,top:panelY,width:w,height:panelH,display:'flex',gap:portrait?40:60}}>
   {[['扣款已保存','800','原扣款 −200',C.teal],['本单库存','0','缺货拒绝',C.red]].map(([name,value,state,color])=><div key={name}style={{flex:1,borderTop:`3px solid ${color}`,borderBottom:`2px solid ${C.edge}`,textAlign:'center',paddingTop:portrait?28:15,background:`linear-gradient(180deg, ${color}0B, transparent)`}}>
    <div style={{fontSize:wide?29:25,color:C.muted}}>{name}</div><div style={{fontSize:wide?65:portrait?72:51,fontFamily:MONO,fontWeight:700,color,marginTop:8}}>{value}</div><div style={{fontSize:wide?30:portrait?31:25,color,marginTop:portrait?18:8}}>{state}</div>
   </div>)}
  </div><div style={{position:'absolute',left:x,top:portrait?1155:859,color:C.muted,fontSize:wide?25:portrait?26:22}}>示例 · 原扣款保留，新退款补偿</div>
 </AbsoluteFill>;
};
