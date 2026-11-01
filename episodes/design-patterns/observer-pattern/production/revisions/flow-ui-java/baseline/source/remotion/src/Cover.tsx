import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
import {Text} from './objects';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const c=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=c.content.x,w=c.content.w;
 const top=portrait?240:210,panelY=portrait?755:590,panelH=portrait?300:210;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 84% 12%, #18547066, transparent 68%)'}}/>
  <Text x={x} y={c.watermarkZone.y} w={w} size={wide?28:24} color={C.muted}>IT小村 / 设计模式 · 观察者</Text>
  <Text x={x} y={top} w={w} size={wide?108:portrait?95:78} weight={800}>订单状态变了，</Text>
  <Text x={x} y={top+(wide?142:portrait?130:106)} w={w} size={wide?108:portrait?95:78} color={C.teal} weight={800}>谁该收到通知？</Text>
  <Text x={x} y={portrait?555:wide?510:469} w={w} size={wide?36:portrait?33:28} color={C.muted}>让接收方独立加入、离开</Text>
  <div style={{position:'absolute',left:x,top:panelY,width:w,height:panelH,borderTop:`3px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,background:`linear-gradient(180deg, ${C.teal}0B, transparent)`}}>
   <Text x={15} y={portrait?34:23} w={w-30} size={wide?31:27} color={C.muted} center>同一笔示例订单 · 两个接收方</Text>
   <Text x={15} y={portrait?113:85} w={w-30} size={wide?57:portrait?57:46} weight={750} center color={C.gold}>变化发生 · 各自响应</Text>
   <Text x={15} y={portrait?225:157} w={w-30} size={wide?28:portrait?31:25} center color={C.teal}>订阅 → 通知 → 取消订阅</Text>
  </div>
  <Text x={x} y={portrait?1155:859} w={w} size={wide?25:portrait?26:22} color={C.muted}>观察者模式 · 看懂对象怎样协作</Text>
 </AbsoluteFill>;
};
