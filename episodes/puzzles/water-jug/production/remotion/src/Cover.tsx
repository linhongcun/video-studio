import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
import {useLayoutAudit} from './LayoutAudit';
export const coverSizes:Record<string,{width:number;height:number}>=Object.fromEntries(Object.entries(covers.sizes).map(([k,v]:any)=>[k,{width:v.width,height:v.height}]));
const Diagram=({x,y,width,height}:any)=><svg style={{position:'absolute',left:x,top:y,width,height}} viewBox="0 0 840 440">
 {[{x:220,cap:3,water:2,color:C.teal},{x:620,cap:5,water:5,color:C.blue}].map(v=><g key={v.x}><text x={v.x} y={340-v.cap*49} fill={v.color} fontSize={32} textAnchor="middle" fontFamily={FONT}>容量{v.cap}升</text><rect x={v.x-105} y={360-v.cap*49} width={210} height={v.cap*49} rx={12} fill={C.surface} stroke={v.color} strokeWidth={3}/><rect x={v.x-100} y={360-v.water*49+3} width={200} height={v.water*49-6} rx={7} fill="#66CFFF" opacity={.69}/><text x={v.x} y={422} fill={v.color} fontSize={49} fontFamily={MONO} textAnchor="middle">{v.water} 升</text></g>)}
 <text x={420} y={42} textAnchor="middle" fontSize={37} fill={C.gold} fontFamily={FONT}>先造出1升空位</text><path d="M 337 213 H 353 V 262 H 337" stroke={C.gold} strokeWidth={3} fill="none"/><text x={425} y={249} fill={C.gold} fontSize={29} fontFamily={FONT} textAnchor="middle">空1升</text><path d="M 505 310 H 342 M 363 291 L 342 310 L 363 329" stroke={C.gold} strokeWidth={4} fill="none"/>
</svg>;
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,fontFamily:FONT,color:C.text}}>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / 趣味推理 P03</div>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>3升和5升的壶</div>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:310,width:840,fontSize:108,fontWeight:800,lineHeight:1.22,letterSpacing:-3}}>没有刻度<br/><span style={{color:C.gold}}>量出4升？</span></div>
 <Diagram x={120} y={650} width={840} height={440}/>
 <div data-layout-text="true" style={{position:'absolute',left:120,top:1150,width:840,fontSize:29,color:C.muted}}>容量差留2升 · 再造1升空位</div>
</div>;
export const Cover:React.FC<{size?:string;auditLayout?:boolean}>=({size='16x9',auditLayout=false})=>{
 useLayoutAudit(auditLayout,size,0);const spec=(covers.sizes as any)[size];
 return <AbsoluteFill data-cover-root="true" data-canvas-width={spec.width} data-canvas-height={spec.height} style={{background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
 {size==='3x4'?<Portrait/>:size==='4x3'?<div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div>:<><div data-layout-text="true" style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / 趣味推理 P03</div><div data-layout-text="true" style={{position:'absolute',left:180,top:230,fontSize:42,color:C.muted}}>3升和5升的壶</div><div data-layout-text="true" style={{position:'absolute',left:180,top:332,width:870,fontSize:113,fontWeight:800,lineHeight:1.22,letterSpacing:-3}}>没有刻度<br/><span style={{color:C.gold}}>量出4升？</span></div><div data-layout-text="true" style={{position:'absolute',left:180,top:748,width:840,fontSize:32,color:C.muted}}>容量差留2升 · 再造1升空位</div><Diagram x={1100} y={300} width={660} height={440}/></>}
 </AbsoluteFill>;
};
