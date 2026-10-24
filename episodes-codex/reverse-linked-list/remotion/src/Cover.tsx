import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=><svg data-cover-diagram="true" style={{position:'absolute',left:x,top:y,width,height}} viewBox="0 0 840 400">
 <defs><marker id="cover-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M 1 1 L 8 4.5 L 1 8" fill="none" stroke={C.teal} strokeWidth="2.5"/></marker><marker id="cover-saved" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M 1 1 L 8 4.5 L 1 8" fill="none" stroke={C.blue} strokeWidth="2.5"/></marker></defs>
 <text x="440" y="50" textAnchor="middle" fontFamily={FONT} fontSize="34" fill={C.blue}>保存的入口 · nxt</text>
 <path d="M 440 75 V 105 H 520 V 190 H 503" stroke={C.blue} strokeWidth="3" fill="none" markerEnd="url(#cover-saved)"/>
 {[1,2,3].map((n,i)=><g key={n}><text x={220+i*220} y="145" textAnchor="middle" fontFamily={FONT} fontSize="25" fill={C.muted}>原节点 {n}</text><rect x={160+i*220} y="175" width="120" height="104" rx="17" fill={C.surface} stroke={n===1?C.gold:n===2?C.blue:C.edge} strokeWidth="3"/><text x={220+i*220} y="247" textAnchor="middle" fontFamily={MONO} fontSize="62" fill={C.text}>{n}</text></g>)}
 <text x="50" y="240" textAnchor="middle" fontFamily={MONO} fontSize="30" fill={C.muted}>None</text><text x="804" y="240" textAnchor="middle" fontFamily={MONO} fontSize="26" fill={C.muted}>None</text>
 <path d="M 154 227 H 91" stroke={C.teal} strokeWidth="4" fill="none" markerEnd="url(#cover-arrow)"/>
 <path d="M 500 227 H 593 M 720 227 H 761" stroke={C.teal} strokeWidth="3" fill="none" markerEnd="url(#cover-arrow)"/>
 <text x="420" y="353" textAnchor="middle" fontFamily={FONT} fontSize="31" fill={C.gold}>示例 · 先保存 2，再改 1 的连接</text>
</svg>;
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 62%, #194B7060, transparent 62%)'}}/>
 <div style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / LeetCode 206</div>
 <div style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>反转链表</div>
 <div style={{position:'absolute',left:120,top:305,width:840,fontSize:104,fontWeight:800,lineHeight:1.15,letterSpacing:-2}}>为什么要先<br/><span style={{color:C.gold}}>保存下一个</span><br/>节点？</div>
 <Diagram x={120} y={725} width={840} height={400}/>
 <div style={{position:'absolute',left:120,top:1155,width:840,fontSize:29,color:C.muted}}>原节点不动 · 只改变 next 引用</div>
</div>;
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 if(size==='3x4')return <AbsoluteFill><Portrait/></AbsoluteFill>;
 if(size==='4x3')return <AbsoluteFill style={{background:C.bg}}><div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div></AbsoluteFill>;
 const spec=(covers.sizes as Record<string,any>)[size];
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
  <div style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / LeetCode 206</div>
  <div style={{position:'absolute',left:180,top:220,fontSize:42,color:C.muted}}>反转链表</div>
  <div style={{position:'absolute',left:180,top:305,width:820,fontSize:108,fontWeight:800,lineHeight:1.15,letterSpacing:-2}}>为什么要先<br/><span style={{color:C.gold}}>保存下一个</span><br/>节点？</div>
  <div style={{position:'absolute',left:180,top:765,width:820,fontSize:33,color:C.muted}}>连接改掉了，下一步的入口还在</div>
  <Diagram x={1040} y={365} width={750} height={410}/>
 </AbsoluteFill>;
};
