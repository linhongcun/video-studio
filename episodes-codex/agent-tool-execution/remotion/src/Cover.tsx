import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
import {Text} from './objects';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 const c=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=c.content.x,w=c.content.w;
 const top=portrait?245:210,subtitle=portrait?570:wide?520:470,panelY=portrait?760:605,panelH=portrait?300:205,gap=wide?50:30,colW=(w-gap)/2;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 8%,#18547088,transparent 67%)'}}/>
  <Text x={x} y={c.watermarkZone.y} w={w} size={wide?28:24} color={C.muted}>IT小村 / Agent 开发 · 工具调用</Text>
  <Text x={x} y={top} w={w} size={wide?106:portrait?95:76} weight={800}>AI 说要查，</Text>
  <Text x={x} y={top+(wide?140:portrait?133:110)} w={w} size={wide?106:portrait?95:76} color={C.teal} weight={800}>谁在执行？</Text>
  <Text x={x} y={subtitle} w={w} size={wide?36:portrait?31:27} color={C.muted}>调用请求，不等于执行结果</Text>
  <div style={{position:'absolute',left:x,top:panelY,width:w,height:panelH,display:'flex',gap}}>
   {[["模型提出","查询请求",C.blue],["应用程序","真正执行",C.gold]].map(([name,value,color])=><div key={name} style={{position:'relative',width:colW,borderTop:`3px solid ${color}`,borderBottom:`2px solid ${C.edge}`,background:`linear-gradient(180deg,${color}10,transparent)`}}><Text x={12} y={portrait?40:24} w={colW-24} size={wide?29:26} color={C.muted} center>{name}</Text><Text x={12} y={portrait?127:93} w={colW-24} size={wide?53:portrait?44:36} weight={650} color={color} center>{value}</Text></div>)}
  </div>
  <Text x={x} y={portrait?1155:859} w={w} size={wide?26:portrait?26:22} color={C.muted}>跟着一次订单查询，看清谁真正动手</Text>
 </AbsoluteFill>;
};
