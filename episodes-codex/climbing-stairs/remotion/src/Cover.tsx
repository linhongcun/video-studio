import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=>{
 const gap=width/3,box=Math.min(170,gap*.72),cy=height*.48,cx=(i:number)=>gap*(i+.5);
 return <svg data-cover-diagram="true" style={{position:'absolute',left:x,top:y,width,height}} viewBox={`0 0 ${width} ${height}`}>
  {[5,8,13].map((n,i)=><g key={n}>
   <text x={cx(i)} y={cy-box*.83} textAnchor="middle" fontFamily={FONT} fontSize={Math.min(30,width*.038)} fill={C.muted}>第{i+4}阶</text>
   <rect x={cx(i)-box/2} y={cy-box/2} width={box} height={box} rx={22} fill={C.surface} stroke={i===2?C.gold:C.teal} strokeWidth={3}/>
   <text x={cx(i)} y={cy+box*.27} textAnchor="middle" fontFamily={MONO} fontSize={box*.65} fill={i===2?C.gold:C.teal}>{n}</text>
  </g>)}
  {[0,1].map((i)=><path key={i} d={`M ${cx(i)} ${cy+box*.53} C ${cx(i)} ${height*.91}, ${cx(2)} ${height*.91}, ${cx(2)} ${cy+box*.53}`} stroke={i?C.gold:C.teal} strokeWidth={3} fill="none"/>)}
  <text x={width/2} y={height*.08} textAnchor="middle" fontFamily={MONO} fontSize={Math.min(44,width*.06)} fill={C.gold}>5 + 8 = 13</text>
  <text x={width/2} y={height*.98} textAnchor="middle" fontFamily={FONT} fontSize={Math.min(28,width*.034)} fill={C.muted}>示例 · 方法数只依赖前两阶</text>
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
