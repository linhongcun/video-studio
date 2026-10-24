import React,{useLayoutEffect} from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import episode from '../../episode.json';
import {C,FONT,MONO} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{
 useLayoutEffect(()=>{document.querySelectorAll('[data-copyfit]').forEach((q:HTMLElement)=>{if(q.scrollWidth>q.clientWidth+2)console.error('COPYFIT overflow',q.textContent,q.scrollWidth,q.clientWidth)});},[]);
 const s=covers.sizes[size],portrait=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w,mq=episode.ep===10;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 90% 10%, #1A506A77, transparent 65%)'}}/>
 <div style={{position:'absolute',left:s.watermarkZone.x,top:s.watermarkZone.y,color:C.muted,fontSize:28}}>IT小村</div>
 <div style={{position:'absolute',left:x,top:portrait?150:120,color:C.muted,fontSize:27}}>扛住高峰 · EP.{episode.ep}</div>
 <div data-copyfit style={{position:'absolute',left:x,top:portrait?250:220,width:w,fontSize:wide?96:portrait?88:74,fontWeight:800,lineHeight:1.35}}>{episode.cover[0]}<br/><span style={{color:C.gold}}>{episode.cover[1]}</span></div>
 <div data-copyfit style={{position:'absolute',left:x,top:portrait?590:500,width:w,fontSize:wide?35:portrait?30:27,color:C.muted,lineHeight:1.4}}>{episode.tagline}</div>
 <div style={{position:'absolute',left:x,top:portrait?760:640,width:w,height:portrait?250:170,borderTop:`2px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`,display:'flex',alignItems:'center',justifyContent:'space-around'}}>
 {(mq?['已入队','处理中','待确认']:['有额度','才放行','无额度拒绝']).map((t,i)=><div key={t} style={{textAlign:'center',color:i===2?C.gold:C.teal}}><div style={{fontFamily:MONO,fontSize:wide?67:portrait?48:43,marginBottom:16}}>{mq?['7042','→','…'][i]:['2','→','0'][i]}</div><div style={{fontSize:wide?32:portrait?27:25}}>{t}</div></div>)}
 </div>
 <div style={{position:'absolute',left:x,top:portrait?1160:875,fontSize:portrait?25:21,color:C.muted}}>教学示例 · {mq?'提交不等于业务完成':'放行不等于业务成功'}</div>
 </AbsoluteFill>;
};
