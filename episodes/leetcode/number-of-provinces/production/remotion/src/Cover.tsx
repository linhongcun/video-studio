import React from 'react';
import covers from '@covers';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const City=({x,y,label,color,scale=1}:any)=><g transform={`translate(${x} ${y}) scale(${scale})`} data-cover-city={label}>
 <ellipse cx={0} cy={20} rx={35} ry={9} fill={color} opacity={.12}/>
 <path d="M-28 13V-18H-11V-37H9V-12H27V13Z" fill={C.surface} stroke={color} strokeWidth={2.4} strokeLinejoin="round"/>
 <path d="M-20-10H-17M-20-1H-17M-4-27H0M-4-17H0M-4-7H0M17-3H21M17 6H21" stroke={color} strokeWidth={3} strokeLinecap="round"/>
 <text x={0} y={50} textAnchor="middle" fill={color} fontFamily={MONO} fontSize={26} fontWeight={750}>{label}</text>
 </g>;
const CityGroups=({x,y,w,h}:any)=>{
 const p=[[.11,.28],[.31,.15],[.51,.28],[.14,.80],[.43,.80],[.84,.77]];
 const px=(i:number)=>x+p[i][0]*w,py=(i:number)=>y+p[i][1]*h;
 const scale=Math.min(w/1000,h/340)*1.15;
 return <g data-cover-input="AB,BC,DE;F-isolated" data-connection-kind="direct-relationship-not-geographic-roads">
  <rect x={x} y={y-9} width={w*.64} height={h*.59} rx={30} fill={C.teal+'09'} stroke={C.teal} strokeOpacity={.35} strokeWidth={1.5}/>
  <rect x={x} y={y+h*.64} width={w*.60} height={h*.35} rx={30} fill={C.blue+'09'} stroke={C.blue} strokeOpacity={.35} strokeWidth={1.5}/>
  <rect x={x+w*.71} y={y+h*.53} width={w*.28} height={h*.46} rx={30} fill={C.gold+'09'} stroke={C.gold} strokeOpacity={.35} strokeWidth={1.5}/>
  {[[0,1],[1,2],[3,4]].map(([a,b])=><line key={`${a}-${b}`} x1={px(a)} y1={py(a)} x2={px(b)} y2={py(b)} stroke={a<3?C.teal:C.blue} strokeWidth={4} strokeOpacity={.8}/>)}
  {p.map((_,i)=><City key={i} x={px(i)} y={py(i)} label={'ABCDEF'[i]} scale={scale} color={i<3?C.teal:i<5?C.blue:C.gold}/>)}
  <text x={x+w*.32} y={y+h*.48+28} textAnchor="middle" fill={C.teal} fontFamily={FONT} fontSize={Math.max(22,26*scale)}>A 与 C 经 B 相连</text>
  <text x={x+w*.82} y={y+h*.22} textAnchor="middle" fill={C.text} fontFamily={FONT} fontSize={Math.max(24,31*scale)} fontWeight={650}>3 个省份</text>
  <text x={x+w*.82} y={y+h*.34} textAnchor="middle" fill={C.muted} fontFamily={FONT} fontSize={Math.max(18,22*scale)}>教学示例</text>
 </g>;
};
export const Cover=({size='16x9'}:{size?:keyof typeof coverSizes})=>{
 const cfg=(covers.sizes as any)[size],region=cfg.contentRegion;
 return <svg {...coverSizes[size]} viewBox={`0 0 ${cfg.width} ${cfg.height}`}>
  <rect width="100%" height="100%" fill={C.bg}/>
  <rect x={region[0]-20} y={region[1]-45} width={region[2]+40} height={region[3]+75} rx={30} fill={C.surface} opacity={.50}/>
  {cfg.elements.map((e:any)=>e.type==='city-groups'?<CityGroups key={e.id} {...e}/>:<g key={e.id}>
   {e.text.split('\n').map((line:string,i:number)=><text key={i} x={e.x} y={e.y+e.fontSize+i*(e.fontSize*1.16)} fill={e.id==='title'&&i===1?C.gold:e.id==='series'?C.muted:C.text} fontFamily={FONT} fontSize={e.fontSize} fontWeight={e.id==='title'?800:550}>{line}</text>)}
  </g>)}
  <text x={cfg.watermarkZone[0]+cfg.watermarkZone[2]} y={cfg.watermarkZone[1]+31} textAnchor="end" fontFamily={FONT} fontSize={23} fill={C.muted}>LC.547</text>
 </svg>;
};
