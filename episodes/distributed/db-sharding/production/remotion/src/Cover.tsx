import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{const s=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w;return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 10%, #17556D88, transparent 64%)'}}/>
 <div style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,fontSize:27,color:C.muted}}>IT小村 / 分布式 · EP.19</div>
 <div style={{position:'absolute',left:x,top:portrait?230:205,width:w,fontSize:wide?106:portrait?92:76,fontWeight:800,lineHeight:1.35,letterSpacing:-3}}>订单<span style={{color:C.gold}}>太多</span>，<br/>一个库<span style={{color:C.teal}}>装不下？</span></div>
 <div style={{position:'absolute',left:x,top:portrait?570:495,fontSize:wide?34:27,color:C.muted}}>按什么分，才能找到数据？</div>
 <div style={{position:'absolute',left:x,top:portrait?735:610,width:w,display:'flex',alignItems:'center',justifyContent:'space-between'}}>{['A库','B库','C库'].map((t,i)=><div key={t} style={{width:'28%',borderTop:`3px solid ${[C.teal,C.blue,C.gold][i]}`,paddingTop:30,textAlign:'center',fontSize:wide?48:37,color:[C.teal,C.blue,C.gold][i]}}>{t}<div style={{fontSize:wide?27:21,color:C.muted,marginTop:25}}>一部分订单</div></div>)}</div>
 <div style={{position:'absolute',left:x,top:portrait?1240:875,fontSize:portrait?25:21,color:C.muted}}>示例数据 · 规则决定路由，资源与分布决定收益</div>
 </AbsoluteFill>};
