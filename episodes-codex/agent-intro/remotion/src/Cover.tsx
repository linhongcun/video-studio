import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
import {Text} from './objects';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const c=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=c.content.x,w=c.content.w;
 const top=portrait?245:210,panelY=portrait?760:605,panelH=portrait?300:205;
 const gap=portrait?40:60,colW=(w-gap)/2;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 84% 12%, #18547088, transparent 68%)'}}/>
  <Text x={x} y={c.watermarkZone.y} w={w} size={wide?28:24} color={C.muted}>IT小村 / 智能体开发 · 概念入门</Text>
  <Text x={x} y={top} w={w} size={wide?108:portrait?98:78} weight={800}>AI 会回答，</Text>
  <Text x={x} y={top+(wide?140:portrait?130:104)} w={w} size={wide?108:portrait?98:78} color={C.teal} weight={800}>怎样才能办事？</Text>
  <Text x={x} y={portrait?555:wide?520:470} w={w} size={wide?37:portrait?32:28} color={C.muted}>从生成回复，到查询真实结果</Text>
  <div style={{position:'absolute',left:x,top:panelY,width:w,height:panelH,display:'flex',gap}}>
   {[["模型","提出下一步","查询订单",C.gold],["执行程序","调用工具","拿回结果",C.teal]].map(([name,a,b,color])=><div key={name} style={{width:colW,borderTop:`3px solid ${color}`,borderBottom:`2px solid ${C.edge}`,position:'relative',background:`linear-gradient(180deg, ${color}0B, transparent)`}}>
    <Text x={12} y={portrait?28:17} w={colW-24} size={wide?29:25} color={C.muted} center>{name}</Text>
    <Text x={12} y={portrait?93:65} w={colW-24} size={wide?47:portrait?48:35} weight={650} color={color} center>{a}</Text>
    <Text x={12} y={portrait?200:143} w={colW-24} size={wide?28:portrait?31:25} color={color} center>{b}</Text>
   </div>)}
  </div>
  <Text x={x} y={portrait?1155:859} w={w} size={wide?25:portrait?26:22} color={C.muted}>示例 · 查询与建议，不等于退款到账</Text>
 </AbsoluteFill>;
};
