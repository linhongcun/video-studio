import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C,FONT} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
export const Cover:React.FC<{size?:string}>=({size='16x9'})=>{const s=covers.sizes[size],p=size==='3x4',wide=size==='16x9',x=s.content.x,w=s.content.w,yy=p?740:600;return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT}}>
 <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 10%,#17556D88,transparent 65%)'}}/>
 <div style={{position:'absolute',left:x,top:100,color:C.muted,fontSize:27}}>IT小村 / 浏览器与网络 · EP.06</div>
 <div style={{position:'absolute',left:x,top:p?235:205,width:w,fontSize:wide?108:p?94:78,fontWeight:800,lineHeight:1.35,letterSpacing:-2}}>一台忙不过来，<br/><span style={{color:C.teal}}>请求交给谁？</span></div>
 <div style={{position:'absolute',left:x,top:p?575:490,fontSize:wide?35:27,color:C.muted}}>负载均衡，把请求分给可用实例</div>
 <svg style={{position:'absolute',left:x,top:yy}} width={w} height={p?370:240} viewBox="0 0 810 240">
  <path d="M125 120H365M455 120L660 42M455 120H660M455 120L660 198" fill="none" stroke={C.teal} strokeWidth={4}/>
  <rect x={0} y={78} width={150} height={84} rx={16} fill={C.surface} stroke={C.blue} strokeWidth={2}/><text x={75} y={132} textAnchor="middle" fill={C.text} fontSize={28}>请求</text>
  <rect x={330} y={78} width={160} height={84} rx={16} fill={C.surface} stroke={C.teal} strokeWidth={2}/><text x={410} y={132} textAnchor="middle" fill={C.teal} fontSize={28}>分配入口</text>
  {[42,120,198].map((y,i)=><g key={i}><rect x={650} y={y-32} width={155} height={64} rx={13} fill={C.surface} stroke={C.blue} strokeWidth={2}/><text x={727} y={y+10} textAnchor="middle" fill={C.text} fontSize={25}>{'应用'+['甲','乙','丙'][i]}</text></g>)}
 </svg>
 <div style={{position:'absolute',left:x,top:p?1240:875,fontSize:p?25:21,color:C.muted}}>过程示意 · 增加实例，按规则分配请求</div>
 </AbsoluteFill>};
