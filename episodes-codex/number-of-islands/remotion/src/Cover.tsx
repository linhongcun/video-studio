import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
import {IslandMap} from './IslandMap';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=>{
 const cell=Math.min((width-70)/5,(height-70)/4),g={x:(width-5*cell)/2,y:(height-4*cell)/2,cell};
 return <svg data-cover-diagram="literal-sea-land-map" style={{position:'absolute',left:x,top:y,width,height}} viewBox={`0 0 ${width} ${height}`}>
  <IslandMap geometry={g} previewComponents showState={false} showCoordinates={false} showGrid={false} showNeighbor={false}/>
  <text x={g.x+cell*3.75} y={g.y+cell*1.13} fill={C.text} fontFamily={FONT} fontSize={Math.min(69,cell*.65)} textAnchor="middle" fontWeight="750"><tspan fontFamily={MONO}>3</tspan>座岛</text>
  <text x={g.x+cell*3.75} y={g.y+cell*1.58} fill="#9BC3CC" fontFamily={FONT} fontSize={Math.min(27,cell*.235)} textAnchor="middle">整片相连，只数一次</text>
 </svg>;
};
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 62%, #174E6760, transparent 62%)'}}/>
 <div style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / LeetCode 200</div>
 <div style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>岛屿数量</div>
 <div style={{position:'absolute',left:120,top:310,width:840,fontSize:104,fontWeight:800,lineHeight:1.22,letterSpacing:-3}}>同一座岛<br/><span style={{color:C.gold}}>怎样只数一次？</span></div>
 <Diagram x={120} y={650} width={840} height={460}/>
 <div style={{position:'absolute',left:120,top:1150,width:840,fontSize:29,color:C.muted}}>沿四邻找完整座，再继续扫描</div>
</div>;
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 if(size==='3x4')return <AbsoluteFill><Portrait/></AbsoluteFill>;
 if(size==='4x3')return <AbsoluteFill style={{background:C.bg}}><div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div></AbsoluteFill>;
 const spec=(covers.sizes as Record<string,any>)[size];
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #174E6759, transparent 60%)'}}/>
  <div style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / LeetCode 200</div>
  <div style={{position:'absolute',left:180,top:220,fontSize:42,color:C.muted}}>岛屿数量</div>
  <div style={{position:'absolute',left:180,top:306,width:840,fontSize:108,fontWeight:800,lineHeight:1.2,letterSpacing:-3}}>同一座岛<br/><span style={{color:C.gold}}>怎样只数一次？</span></div>
  <div style={{position:'absolute',left:180,top:700,width:820,fontSize:32,color:C.muted}}>先沿四邻归完整座，再寻找新岛</div>
  <Diagram x={1100} y={330} width={660} height={480}/>
  <div style={{position:'absolute',left:1100,top:856,width:660,textAlign:'center',fontSize:27,color:C.muted}}>地形不改 · 每座岛只从一个起点加数</div>
 </AbsoluteFill>;
};
