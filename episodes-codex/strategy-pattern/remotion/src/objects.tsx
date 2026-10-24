import React,{useLayoutEffect,useRef} from 'react';
import {C,FONT,MONO} from './theme';
import {clamp,ease,lerp} from './primitives';
export {clamp,ease,lerp};

export const Text:React.FC<{children:React.ReactNode;x:number;y:number;w:number;size?:number;color?:string;alpha?:number;center?:boolean;weight?:number;h?:number;mono?:boolean}>=({children,x,y,w,size=32,color=C.text,alpha=1,center=false,weight=550,h,mono=false})=>{
 const ref=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{const e=ref.current;if(e&&e.clientWidth>0&&(e.scrollWidth>e.clientWidth+2||(h&&e.scrollHeight>e.clientHeight+2)))console.error('COPYFIT overflow',String(children),e.scrollWidth,e.clientWidth,e.scrollHeight,e.clientHeight);},[children,w,size,h]);
 return <div ref={ref} data-fit style={{position:'absolute',left:x,top:y,width:w,height:h,color,opacity:alpha,fontFamily:mono?MONO:FONT,fontSize:size,fontWeight:weight,lineHeight:1.4,whiteSpace:'pre-line',textAlign:center?'center':'left',boxSizing:'border-box'}}>{children}</div>;
};
export const Heading=({children,color=C.text,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><Text x={130} y={171} w={1660} size={49} color={color} alpha={alpha} weight={750}>{children}</Text>;
export const Note=({children,color=C.muted,alpha=1}:{children:React.ReactNode;color?:string;alpha?:number})=><Text x={180} y={826} w={1560} size={30} center color={color} alpha={alpha}>{children}</Text>;
export const Reset=({children,alpha=1}:{children:React.ReactNode;alpha?:number})=><Text x={130} y={252} w={1650} size={24} color={C.gold} alpha={alpha}>{children}</Text>;
export const Frame=({x,y,w,h,label,color=C.edge,alpha=1,children}:{x:number;y:number;w:number;h:number;label?:string;color?:string;alpha?:number;children?:React.ReactNode})=><div style={{position:'absolute',left:x,top:y,width:w,height:h,opacity:alpha,background:C.bg,border:`2px solid ${color}`,borderRadius:18,boxSizing:'border-box'}}>
 {label&&<Text x={24} y={16} w={w-48} size={27} color={color===C.edge?C.muted:color}>{label}</Text>}{children}
</div>;
export const Rule=({x=1310,y=352,w=440,name,formula,active=false,color=C.teal,alpha=1,changed=false,detail}:{key?:React.Key;x?:number;y?:number;w?:number;name:string;formula:string;active?:boolean;color?:string;alpha?:number;changed?:boolean;detail?:string})=><div style={{position:'absolute',left:x,top:y,width:w,height:102,borderLeft:`4px solid ${active?color:C.edge}`,background:changed?`${C.gold}15`:active?`${color}11`:C.bg,opacity:alpha,boxSizing:'border-box'}}>
 <Text x={22} y={12} w={170} size={30} color={active?color:C.text} weight={650}>{name}</Text>
 <Text x={198} y={14} w={w-215} size={30} color={changed?C.gold:active?color:C.muted} center>{formula}</Text>
 <Text x={22} y={61} w={w-44} size={detail?26:20} color={detail?color:C.muted}>{detail??'金额 → 应付金额'}</Text>
</div>;
export const Token=({text,x,y,w=250,color=C.gold,alpha=1}:{text:string;x:number;y:number;w?:number;color?:string;alpha?:number})=><div style={{position:'absolute',left:x-w/2,top:y-31,width:w,height:62,background:C.bg,border:`2px solid ${color}`,borderRadius:12,opacity:alpha,boxSizing:'border-box'}}><Text x={12} y={8} w={w-24} size={30} color={color} center>{text}</Text></div>;
export const Path=({points,p=1,color=C.teal,alpha=1,dashed=false}:{points:[number,number][];p?:number;color?:string;alpha?:number;dashed?:boolean})=>{
 let lengths:number[]=[],total=0;for(let i=1;i<points.length;i++){total+=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);lengths.push(total);}
 const dist=total*clamp(p);let path=`M ${points[0][0]} ${points[0][1]}`;
 for(let i=1;i<points.length;i++){const prev=i===1?0:lengths[i-2],len=lengths[i-1]-prev,q=clamp((dist-prev)/Math.max(1,len));if(q<=0)break;path+=` L ${lerp(points[i-1][0],points[i][0],q)} ${lerp(points[i-1][1],points[i][1],q)}`;if(q<1)break;}
 const last=points[points.length-1],pre=points[points.length-2],ang=Math.atan2(last[1]-pre[1],last[0]-pre[0]);
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:alpha}}><path d={path} fill="none" stroke={color} strokeWidth={3} strokeDasharray={dashed?'9 8':undefined}/>{p>=.995&&<path d={`M ${last[0]-15*Math.cos(ang-.5)} ${last[1]-15*Math.sin(ang-.5)} L ${last[0]} ${last[1]} L ${last[0]-15*Math.cos(ang+.5)} ${last[1]-15*Math.sin(ang+.5)}`} fill="none" stroke={color} strokeWidth={3}/>}</svg>;
};
export const Travel=({points,p,text,color=C.gold,w=220,alpha=1,endInset=0}:{points:[number,number][];p:number;text:string;color?:string;w?:number;alpha?:number;endInset?:number})=>{
 let total=0;const lengths:number[]=[];for(let i=1;i<points.length;i++){total+=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);lengths.push(total);}let x=points[0][0],y=points[0][1],dist=clamp(p)*Math.max(0,total-endInset);
 for(let i=1;i<points.length;i++){const prev=i===1?0:lengths[i-2],q=clamp((dist-prev)/Math.max(1,lengths[i-1]-prev));x=lerp(points[i-1][0],points[i][0],q);y=lerp(points[i-1][1],points[i][1],q);if(q<1)break;}
 const tokenAlpha=endInset?alpha*(1-clamp((p-.9)/.1)):alpha;
 return <><Path points={points} color={color} p={p} alpha={alpha}/><Token text={text} x={x} y={y} w={w} color={color} alpha={tokenAlpha}/></>;
};
export const Result=({amount,waiting=false,x=625,y=630,w=480,alpha=1,color=C.teal}:{amount:string;waiting?:boolean;x?:number;y?:number;w?:number;alpha?:number;color?:string})=><div style={{position:'absolute',left:x,top:y,width:w,height:120,borderTop:`2px solid ${waiting?C.edge:color}`,opacity:alpha}}><Text x={0} y={14} w={w} size={23} center color={C.muted}>应付金额</Text><Text x={0} y={48} w={w} size={51} center color={waiting?C.muted:color} weight={750}>{waiting?'等待返回':amount+' 元'}</Text></div>;
export const Code=({lines,x=300,y=330,w=1320,size=34,active=-1}:{lines:string[];x?:number;y?:number;w?:number;size?:number;active?:number})=><div style={{position:'absolute',left:x,top:y,width:w,padding:24,boxSizing:'border-box',borderLeft:`3px solid ${C.teal}`,background:C.surface}}>{lines.map((l,i)=><div key={i} style={{fontFamily:MONO,whiteSpace:'pre',fontSize:size,lineHeight:'1.6',color:i===active?C.gold:C.text,background:i===active?`${C.gold}10`:'transparent'}}>{l||' '}</div>)}</div>;
