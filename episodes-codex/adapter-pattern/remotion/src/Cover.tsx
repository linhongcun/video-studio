import React,{useLayoutEffect} from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
import {Text} from './objects';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const copy=covers.copy,c=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=c.content.x,w=c.content.w;
 const top=portrait?240:210,panelY=portrait?755:590,panelH=portrait?300:210;
 useLayoutEffect(()=>{if(size==='4x3'){for(const e of Array.from(document.querySelectorAll('[data-cover] [data-fit]'))){const b=e.getBoundingClientRect();if(b.left<314.5||b.right>1125.5||b.bottom>918)console.error('COPYFIT cover4x3 safe-region',e.textContent,b.left,b.right,b.bottom);}}},[size]);
 return <AbsoluteFill data-cover style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 84% 12%, #18547066, transparent 68%)'}}/>
  <Text x={x} y={c.watermarkZone.y} w={w} size={wide?28:24} color={C.muted}>IT小村 / 设计模式 · 适配器</Text>
  <Text x={x} y={top} w={w} size={wide?108:portrait?95:78} weight={800}>{copy.headline[0]}</Text>
  <Text x={x} y={top+(wide?142:portrait?130:106)} w={w} size={wide?108:portrait?95:78} color={C.teal} weight={800}>{copy.headline[1]}</Text>
  <Text x={x} y={portrait?565:wide?505:469} w={w} size={wide?36:portrait?33:28} color={C.muted}>{copy.subtitle}</Text>
  <div style={{position:'absolute',left:x,top:panelY,width:w,height:panelH,borderTop:`3px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,background:`linear-gradient(180deg, ${C.teal}0B, transparent)`}}>
   <Text x={15} y={portrait?30:20} w={w-30} size={wide?31:27} color={C.muted} center>{copy.panelTitle}</Text>
   <Text x={15} y={portrait?107:78} w={w-30} size={wide?57:portrait?48:43} weight={750} center color={C.gold}>{copy.panelRoute}</Text>
   <Text x={15} y={portrait?225:157} w={w-30} size={wide?28:portrait?31:25} center color={C.teal}>{copy.panelDetail}</Text>
  </div>
  <Text x={x} y={portrait?1155:859} w={w} size={wide?25:portrait?26:22} color={C.muted}>{copy.footer}</Text>
 </AbsoluteFill>;
};
