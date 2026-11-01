import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{const s=covers.sizes[size],p=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w;return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 15%, #18566A88, transparent 65%)'}}/>
 <div style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,color:C.muted,fontSize:27}}>IT小村 / 数据库 · EP.18</div>
 <div style={{position:'absolute',left:x,top:p?235:205,width:w,fontSize:wide?108:p?94:78,fontWeight:800,lineHeight:1.35,letterSpacing:-3}}>昵称刚改好，<br/>怎么<span style={{color:C.red}}>又变回去了？</span></div>
 <div style={{position:'absolute',left:x,top:p?580:490,fontSize:wide?35:27,color:C.muted}}>保存成功，为什么读到旧名字</div>
 <div style={{position:'absolute',left:x,top:p?735:590,width:w,height:p?370:240,borderTop:`2px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,display:'flex',alignItems:'center',justifyContent:'space-around'}}>
  <div style={{textAlign:'center'}}><div style={{fontSize:25,color:C.muted}}>主库</div><div style={{fontSize:wide?84:64,color:C.teal,fontWeight:700,marginTop:18}}>青禾</div></div><div style={{fontSize:wide?48:34,color:C.gold}}>→</div><div style={{textAlign:'center'}}><div style={{fontSize:25,color:C.muted}}>从库尚未更新</div><div style={{fontSize:wide?84:64,color:C.red,fontWeight:700,marginTop:18}}>阿青</div></div>
 </div>
 <div style={{position:'absolute',left:x,top:p?1240:875,fontSize:p?25:21,color:C.muted}}>同一条昵称记录 · 示例数据</div>
 </AbsoluteFill>;};
