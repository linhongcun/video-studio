import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';

export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const chars=[...'abcbadea'];
const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=>{
 const gap=width/8,box=gap*.79,center=(i:number)=>gap*(i+.5),cy=height*.39;
 return <svg data-cover-diagram="true" style={{position:'absolute',left:x,top:y,width,height}} viewBox={`0 0 ${width} ${height}`}>
  <rect x={center(0)-box*.65} y={cy-box*.78} width={gap*2+box*1.3} height={box*1.66} rx={14} fill={C.teal+'12'} stroke={C.teal} strokeWidth={3}/>
  {chars.map((char,i)=>{const repeated=i===1||i===3,color=repeated?C.red:i<3?C.teal:C.muted;return <g key={i}>
   <rect x={center(i)-box/2} y={cy-box/2} width={box} height={box} rx={10} fill={C.surface} stroke={color} strokeWidth={repeated?3:1.5}/>
   <text x={center(i)} y={cy+box*.23} textAnchor="middle" fontFamily={MONO} fontSize={box*.7} fill={color}>{char}</text>
   <text x={center(i)} y={cy+box*.99} textAnchor="middle" fontFamily={MONO} fontSize={Math.max(21,box*.28)} fill={C.muted}>{i}</text>
  </g>})}
  <path d={`M ${center(1)} ${cy-box*.95} Q ${center(2)} ${cy-box*2.05} ${center(3)} ${cy-box*.95}`} fill="none" stroke={C.red} strokeWidth={3}/>
  <text x={center(2)} y={cy-box*1.86} textAnchor="middle" fill={C.red} fontFamily={FONT} fontSize={Math.min(31,box*.42)}>重复</text>
  <path d={`M ${center(0)} ${cy+box*1.7} H ${center(2)-15} l -12 -9 m 12 9 l -12 9`} fill="none" stroke={C.gold} strokeWidth={4}/>
  <text x={width/2} y={cy+box*2.44} textAnchor="middle" fontFamily={FONT} fontSize={Math.min(31,box*.41)} fill={C.gold}>左边，要移到哪里？</text>
 </svg>;
};
const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 62%, #194B7060, transparent 62%)'}}/>
 <div style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / LeetCode 3 · 滑动窗口</div>
 <div style={{position:'absolute',left:120,top:214,fontSize:37,color:C.muted}}>无重复字符的最长子串</div>
 <div style={{position:'absolute',left:120,top:310,width:840,fontSize:105,fontWeight:800,lineHeight:1.2,letterSpacing:-3}}>重复了，<br/><span style={{color:C.gold}}>左边移几步？</span></div>
 <Diagram x={120} y={650} width={840} height={460}/>
 <div style={{position:'absolute',left:120,top:1150,width:840,fontSize:29,color:C.muted}}>示例 · 看懂每一次收缩的依据</div>
</div>;
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 if(size==='3x4')return <AbsoluteFill><Portrait/></AbsoluteFill>;
 if(size==='4x3')return <AbsoluteFill style={{background:C.bg}}><div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div></AbsoluteFill>;
 const spec=(covers.sizes as Record<string,any>)[size];
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
  <div style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / LeetCode 3 · 滑动窗口</div>
  <div style={{position:'absolute',left:180,top:220,fontSize:42,color:C.muted}}>无重复字符的最长子串</div>
  <div style={{position:'absolute',left:180,top:306,width:840,fontSize:111,fontWeight:800,lineHeight:1.2,letterSpacing:-3}}>重复了，<br/><span style={{color:C.gold}}>左边移几步？</span></div>
  <div style={{position:'absolute',left:180,top:700,width:820,fontSize:32,color:C.muted}}>让重复消失，再继续向右</div>
  <Diagram x={1100} y={350} width={660} height={450}/>
  <div style={{position:'absolute',left:1100,top:856,width:660,textAlign:'center',fontSize:26,color:C.muted}}>示例 · 一段连续、不重复的字符</div>
 </AbsoluteFill>;
};
