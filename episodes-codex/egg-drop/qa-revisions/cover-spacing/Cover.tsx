import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
import {Egg} from './Building';
import {useLayoutAudit} from './LayoutAudit';

export const coverSizes:Record<string,{width:number;height:number}>=Object.fromEntries(
  Object.entries(covers.sizes).map(([key,value]:any)=>[key,{width:value.width,height:value.height}])
);

const Diagram=({x,y,width,height}:{x:number;y:number;width:number;height:number})=>{
  const floorY=(floor:number)=>450-floor*3.4;
  const intervals=[{low:0,high:14,label:'跨14层',color:C.gold},
    {low:14,high:27,label:'再跨13',color:C.blue},
    {low:27,high:39,label:'再跨12',color:C.teal}];
  return <svg data-cover-diagram="true" style={{position:'absolute',left:x,top:y,width,height}} viewBox="0 0 840 520">
    <text x={440} y={46} textAnchor="middle" fontFamily={FONT} fontSize={29} fill={C.muted}>每次向上跨，先留收尾次数</text>
    <rect x={320} y={110} width={180} height={340} rx={8} fill={C.surface} stroke={C.edge} strokeWidth={3}/>
    {Array.from({length:20},(_,i)=>{const floor=(i+1)*5;return <g key={floor}>
      <line x1={320} x2={500} y1={floorY(floor)} y2={floorY(floor)} stroke={C.edge} strokeWidth={1.5}/>
      {floor<100&&[350,430].map(wx=><rect key={wx} x={wx} y={floorY(floor)+5} width={35} height={7} fill={C.edge}/>)}
    </g>;})}
    <text x={284} y={120} textAnchor="end" fontFamily={MONO} fontSize={31} fill={C.muted}>100楼</text>
    {intervals.map(({low,high,label,color})=><g key={high}>
      <rect x={321.5} y={floorY(high)} width={177} height={floorY(low)-floorY(high)} fill={color} fillOpacity={.13}/>
      <line x1={308} x2={520} y1={floorY(high)} y2={floorY(high)} stroke={color} strokeWidth={3}/>
      <text x={284} y={floorY(high)+9} textAnchor="end" fontFamily={MONO} fontSize={32} fontWeight={650} fill={color}>{high}楼</text>
      <path d={`M545 ${floorY(high)+3}h12v${floorY(low)-floorY(high)-6}h-12`} fill="none" stroke={color} strokeWidth={2.5}/>
      <text x={583} y={(floorY(high)+floorY(low))/2+8} fontFamily={FONT} fontSize={24} fill={color}>{label}</text>
    </g>)}
    <line x1={300} x2={520} y1={450} y2={450} stroke={C.muted} strokeWidth={3}/>
    <text x={284} y={460} textAnchor="end" fontFamily={MONO} fontSize={28} fill={C.muted}>0</text>
    <text x={150} y={290} textAnchor="middle" fontFamily={FONT} fontSize={27} fill={C.muted}>两枚鸡蛋</text>
    <Egg x={110} y={360} id={1} scale={1.35}/><Egg x={195} y={360} id={2} scale={1.35}/>
    <text x={410} y={500} textAnchor="middle" fontFamily={FONT} fontSize={27} fill={C.muted}>计划试点 · 间隔逐次缩小</text>
  </svg>;
};

const Title=({x,y,width,size}:{x:number;y:number;width:number;size:number})=><div
  data-layout-text="true" data-cover-title="true"
  style={{position:'absolute',left:x,top:y,width,fontSize:size,fontWeight:800,lineHeight:1.16,letterSpacing:-2}}
>{covers.titleLines.map((line:string,index:number)=><div key={line} style={{color:index===2?C.gold:C.text,whiteSpace:'nowrap'}}>{line}</div>)}</div>;

const Portrait=()=> <div style={{position:'absolute',inset:0,width:1080,height:1440,fontFamily:FONT,color:C.text}}>
  <div data-layout-text="true" style={{position:'absolute',left:120,top:100,fontSize:27,color:C.muted}}>IT小村 / 趣味推理 P05</div>
  <div data-layout-text="true" style={{position:'absolute',left:120,top:190,fontSize:32,color:C.muted}}>{covers.eyebrow}</div>
  <Title x={120} y={275} width={840} size={104}/>
  <Diagram x={120} y={680} width={840} height={420}/>
  <div data-layout-text="true" style={{position:'absolute',left:120,top:1140,width:840,fontSize:29,color:C.muted}}>{covers.footer}</div>
</div>;

export const Cover:React.FC<{size?:string;auditLayout?:boolean}>=({size='16x9',auditLayout=false})=>{
  useLayoutAudit(auditLayout,size,0);
  const spec=(covers.sizes as any)[size];
  return <AbsoluteFill data-cover-root="true" data-canvas-width={spec.width} data-canvas-height={spec.height}
    style={{background:C.bg,color:C.text,fontFamily:FONT}}>
    <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 52%, #194B7059, transparent 60%)'}}/>
    {size==='3x4'?<Portrait/>:size==='4x3'?<div style={{position:'absolute',left:315,top:0,width:1080,height:1440,transform:'scale(.75)',transformOrigin:'top left'}}><Portrait/></div>:<>
      <div data-layout-text="true" style={{position:'absolute',left:spec.watermarkZone.x,top:spec.watermarkZone.y,fontSize:30,color:C.muted}}>IT小村 / 趣味推理 P05</div>
      <div data-layout-text="true" style={{position:'absolute',left:180,top:230,fontSize:40,color:C.muted}}>{covers.eyebrow}</div>
      <Title x={180} y={330} width={875} size={112}/>
      <div data-layout-text="true" style={{position:'absolute',left:180,top:806,width:875,fontSize:31,color:C.muted}}>{covers.footer}</div>
      <Diagram x={1090} y={250} width={680} height={610}/>
    </>}
  </AbsoluteFill>;
};
