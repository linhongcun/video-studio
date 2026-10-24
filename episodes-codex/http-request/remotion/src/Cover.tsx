import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import config from '../../production.json';
import {C,FONT} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const s=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 15%, #17556D88, transparent 65%)'}}/>
 <div style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,color:C.muted,fontSize:27}}>IT小村</div>
 <div style={{position:'absolute',left:x,top:portrait?235:205,width:w,fontSize:wide?102:portrait?83:76,fontWeight:800,lineHeight:1.4,letterSpacing:-2}}>{config.cover[0]}<br/><span style={{color:C.teal}}>{config.cover[1]}</span></div>
 <div style={{position:'absolute',left:x,top:portrait?580:495,width:w,fontSize:wide?34:26,color:C.muted,lineHeight:1.5}}>{config.strap}</div>
 <div style={{position:'absolute',left:x,top:portrait?780:620,width:w,height:200,display:'flex',alignItems:'center',justifyContent:'space-between',gap:16,borderTop:`2px solid ${C.teal}`,borderBottom:`1px solid ${C.edge}`}}>
 {config.coverDiagram.map((t,i)=><React.Fragment key={t}><div style={{fontSize:wide?47:portrait?35:30,fontWeight:650,color:i===1?C.gold:C.text}}>{t}</div>{i<2&&<div style={{fontSize:40,color:C.teal}}>→</div>}</React.Fragment>)}
 </div>
 <div style={{position:'absolute',left:x,top:portrait?1110:875,fontSize:25,color:C.muted}}>浏览器与网络 · EP.{String(config.ep).padStart(2,'0')}</div>
 </AbsoluteFill>;
};
