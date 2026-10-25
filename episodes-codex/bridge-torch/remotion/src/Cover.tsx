import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
import {useLayoutAudit} from './LayoutAudit';
export const coverSizes:Record<string,{width:number;height:number}>=Object.fromEntries(Object.entries(covers.sizes).map(([k,v]:any)=>[k,{width:v.width,height:v.height}]));
const Diagram=({x,y,width,height}:any)=><svg style={{position:'absolute',left:x,top:y,width,height}} viewBox="0 0 840 440">
 <rect x={0} y={120} width={210} height={240} rx={24} fill={C.surface} stroke={C.edge}/><rect x={630} y={120} width={210} height={240} rx={24} fill={C.surface} stroke={C.edge}/><path d="M 210 177 H 630 M 210 303 H 630" stroke={C.edge} strokeWidth={8}/>
 {[1,2,5,10].map((p,i)=><g key={p}><rect x={i<2?25:655} y={145+(i%2)*110} width={160} height={80} rx={16} fill={C.bg} stroke={i<2?C.teal:C.gold} strokeWidth={3}/><text x={i<2?105:735} y={199+(i%2)*110} textAnchor="middle" fontSize={38} fill={i<2?C.teal:C.gold} fontFamily={FONT}>{p}分钟</text></g>)}
 <text x={420} y={70} textAnchor="middle" fontSize={40} fill={C.muted} fontFamily={FONT}>一把手电 · 两人同行</text><path d="M 292 240 H 548 M 526 219 L 548 240 L 526 261" stroke={C.gold} strokeWidth={5} fill="none"/>
 <text x={420} y={412} textAnchor="middle" fontSize={52} fill={C.gold} fontFamily={MONO}>19 → 17 分钟</text>
</svg>;
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,fontFamily:FONT,color:C.text}}>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / 趣味推理 P02</div>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>四人过桥</div>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:310,width:840,fontSize:101,fontWeight:800,lineHeight:1.22,letterSpacing:-3}}>最快的人接送<br/><span style={{color:C.gold}}>反而更慢？</span></div>
 <Diagram x={120} y={650} width={840} height={440}/>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:1150,width:840,fontSize:29,color:C.muted}}>慢者同行 · 快者分担返回</div>
</div>;
export const Cover:React.FC<{size?:string;auditLayout?:boolean}>=({size='16x9',auditLayout=false})=>{
 useLayoutAudit(auditLayout,size,0);const spec=(covers.sizes as any)[size];
 return <AbsoluteFill data-cover-root="true" data-canvas-width={spec.width} data-canvas-height={spec.height} style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
  {size==='3x4'?<Portrait/>:size==='4x3'?<div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div>:<>
  <div data-layout-text="true" style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / 趣味推理 P02</div>
  <div data-layout-text="true" style={{position:'absolute',left:180,top:230,fontSize:42,color:C.muted}}>四人过桥</div>
  <div data-layout-text="true" style={{position:'absolute',left:180,top:332,width:870,fontSize:106,fontWeight:800,lineHeight:1.22,letterSpacing:-3}}>最快的人接送<br/><span style={{color:C.gold}}>反而更慢？</span></div>
  <div data-layout-text="true" style={{position:'absolute',left:180,top:748,width:840,fontSize:32,color:C.muted}}>慢者同行 · 快者分担返回</div>
  <Diagram x={1100} y={300} width={660} height={440}/>
  </>}
 </AbsoluteFill>;
};
