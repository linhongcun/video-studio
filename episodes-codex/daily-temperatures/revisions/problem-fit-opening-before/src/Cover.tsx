import React from 'react';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
import {MAIN} from './data';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const CoverGraph=({x,y,w,h}:any)=>{
 // Day 3..7 of the same main teaching sample; no decorative temperature data.
 const values=MAIN.input.slice(2,7),days=[3,4,5,6,7];
 const px=(i:number)=>x+35+i*(w-70)/4;
 const py=(v:number)=>y+95+(36-v)*(h-165)/6;
 return <g data-cover-temperature-days="3,4,5,6,7">
  <path d={`M ${px(0)} ${py(35)-35} V ${y+18} H ${px(4)} V ${py(36)-35}`} stroke={C.teal} strokeWidth={4} fill="none"/>
  <text x={x+w/2} y={y-3} textAnchor="middle" fontFamily={FONT} fontSize={34} fontWeight={700} fill={C.teal}>等 4 天</text>
  {values.slice(0,-1).map((v,i)=><line key={i} x1={px(i)} y1={py(v)} x2={px(i+1)} y2={py(values[i+1])} stroke={C.blue} strokeWidth={5}/>)}
  {values.map((v,i)=><g key={i}>
   <line x1={px(i)} x2={px(i)} y1={py(v)} y2={y+h-43} stroke={C.blue} strokeWidth={20} opacity={.15}/>
   <circle cx={px(i)} cy={py(v)} r={10} fill={C.bg} stroke={i===0||i===4?C.teal:C.blue} strokeWidth={4}/>
   <text x={px(i)} y={py(v)-22} textAnchor="middle" fill={i===0||i===4?C.teal:C.text} fontFamily={MONO} fontWeight={700} fontSize={35}>{v}</text>
   <text x={px(i)} y={y+h-4} textAnchor="middle" fill={C.muted} fontFamily={FONT} fontSize={25}>第{days[i]}天</text>
  </g>)}
 </g>;
};
export const Cover=({size='16x9'}:{size?:keyof typeof coverSizes})=>{
 const cfg=(covers.sizes as any)[size];
 const region=cfg.contentRegion;
 return <svg {...coverSizes[size]} viewBox={`0 0 ${cfg.width} ${cfg.height}`}>
  <rect width="100%" height="100%" fill={C.bg}/>
  <rect x={region[0]-20} y={region[1]-45} width={region[2]+40} height={region[3]+75} rx={30} fill={C.surface} opacity={.54}/>
  {cfg.elements.map((e:any)=>e.type==='temperature-graph'?<CoverGraph key={e.id} {...e}/>:<g key={e.id}>
   {e.text.split('\n').map((line:string,i:number)=><text key={i} x={e.x} y={e.y+e.fontSize+i*(e.fontSize*1.16)} fill={e.id==='title'&&i===1?C.gold:e.id==='series'?C.muted:C.text} fontFamily={FONT} fontSize={e.fontSize} fontWeight={e.id==='title'?800:550}>{line}</text>)}
  </g>)}
  <text x={cfg.watermarkZone[0]+cfg.watermarkZone[2]} y={cfg.watermarkZone[1]+31} textAnchor="end" fontFamily={FONT} fontSize={23} fill={C.muted}>LC.739</text>
 </svg>;
};
