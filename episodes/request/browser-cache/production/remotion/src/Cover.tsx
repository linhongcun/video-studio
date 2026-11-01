import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{const s=covers.sizes[size],p=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w,yy=p?740:600;return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 10%,#17556D88,transparent 65%)'}}/>
 <div style={{position:'absolute',left:x,top:100,color:C.muted,fontSize:27}}>IT小村 / 浏览器与网络 · EP.07</div>
 <div style={{position:'absolute',left:x,top:p?235:205,width:w,fontSize:wide?108:p?94:78,fontWeight:800,lineHeight:1.35,letterSpacing:-2}}>同一张图片，<br/><span style={{color:C.teal}}>这次不用等？</span></div>
 <div style={{position:'absolute',left:x,top:p?575:490,fontSize:wide?35:27,color:C.muted}}>浏览器缓存：能直接复用，少传一次</div>
 <svg style={{position:'absolute',left:x,top:yy}} width={w} height={p?370:240} viewBox="0 0 810 240">
  <rect x={5} y={20} width={260} height={180} rx={16} fill={C.surface} stroke={C.teal} strokeWidth={2}/><path d="M25 180 L95 75 L165 180 Z" fill="#2B8D94"/><path d="M95 180 L185 80 L245 180 Z" fill={C.teal}/><circle cx={205} cy={65} r={19} fill={C.gold}/>
  <path d="M300 110H510M485 90L515 110L485 130" fill="none" stroke={C.teal} strokeWidth={4}/>
  <rect x={550} y={20} width={250} height={180} rx={16} fill={C.surface} stroke={C.blue} strokeWidth={2}/><text x={675} y={100} textAnchor="middle" fill={C.teal} fontSize={34}>页面图片</text><text x={675} y={150} textAnchor="middle" fill={C.muted} fontSize={24}>直接复用</text>
  <text x={135} y={235} textAnchor="middle" fill={C.muted} fontSize={22}>本地副本</text>
 </svg>
 <div style={{position:'absolute',left:x,top:p?1240:875,fontSize:p?25:21,color:C.muted}}>过程示意 · 请求匹配、规则允许，才可复用</div>
 </AbsoluteFill>};
