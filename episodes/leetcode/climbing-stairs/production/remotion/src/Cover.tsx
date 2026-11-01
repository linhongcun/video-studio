import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
import {Staircase,Hop,Walker,foot,StairGeometry} from './Staircase';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=>{
 const g:StairGeometry={x:width*.08,baseY:height*.83,width:width*.27,rise:height*.18,steps:3};
 const top=foot(g,3);
 return <svg data-cover-diagram="literal-stairs" style={{position:'absolute',left:x,top:y,width,height}} viewBox={`0 0 ${width} ${height}`}>
  <text x={width*.43} y={height*.085} textAnchor="middle" fontFamily={MONO} fontSize={Math.min(43,width*.062)} fill={C.gold}>5 + 8 = 13</text>
  <Staircase geometry={g} counts={[5,8,13]} focus={{1:C.gold,2:C.teal,3:C.teal}} labelOffset={3} showOrigin={false} terminalLabel="终点" countSize={Math.min(31,width*.041)} numberSize={Math.min(23,width*.032)}/>
  <Hop geometry={g} from={2} to={3} progress={1} color={C.teal} showWalker={false}/><Hop geometry={g} from={1} to={3} progress={1} color={C.gold} showWalker={false}/><Walker x={top.x} y={top.y} color={C.teal} scale={.95}/>
  <text x={width*.5} y={height*.975} textAnchor="middle" fontFamily={FONT} fontSize={Math.min(26,width*.034)} fill={C.muted}>第4–6阶 · 前两阶的方法数相加</text>
 </svg>;
};
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 62%, #194B7060, transparent 62%)'}}/>
 <div style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / LeetCode 70</div>
 <div style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>爬楼梯</div>
 <div style={{position:'absolute',left:120,top:310,width:840,fontSize:104,fontWeight:800,lineHeight:1.22,letterSpacing:-3}}>为什么只记<br/><span style={{color:C.gold}}>前两个数？</span></div>
 <Diagram x={120} y={650} width={840} height={460}/>
 <div style={{position:'absolute',left:120,top:1150,width:840,fontSize:29,color:C.muted}}>最后一步分两类 · 滚动保留两数</div>
</div>;
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 if(size==='3x4')return <AbsoluteFill><Portrait/></AbsoluteFill>;
 if(size==='4x3')return <AbsoluteFill style={{background:C.bg}}><div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div></AbsoluteFill>;
 const spec=(covers.sizes as Record<string,any>)[size];
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
  <div style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / LeetCode 70</div>
  <div style={{position:'absolute',left:180,top:220,fontSize:42,color:C.muted}}>爬楼梯</div>
  <div style={{position:'absolute',left:180,top:306,width:840,fontSize:111,fontWeight:800,lineHeight:1.2,letterSpacing:-3}}>为什么只记<br/><span style={{color:C.gold}}>前两个数？</span></div>
  <div style={{position:'absolute',left:180,top:700,width:820,fontSize:32,color:C.muted}}>从最后一步，推出前两项相加</div>
  <Diagram x={1100} y={350} width={660} height={450}/>
  <div style={{position:'absolute',left:1100,top:856,width:660,textAlign:'center',fontSize:27,color:C.muted}}>每次只上1或2阶 · 恰好到终点</div>
 </AbsoluteFill>;
};
