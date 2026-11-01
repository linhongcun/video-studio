import React from 'react';
import {C,FONT,MONO} from './theme';
import {Shot} from './data';
export const clamp=(x:number,a=0,b=1)=>Math.min(b,Math.max(a,x));
export const ease=(x:number)=>{const p=clamp(x);return p*p*(3-2*p);};
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const T=({x,y,children,size=32,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
export const Head=({title,sub,color=C.text}:any)=><g><T x={120} y={82} size={25} color={C.muted}>Agent Skills · 工作方法如何按需进入任务</T><T x={120} y={166} size={49} weight={760} color={color}>{title}</T>{sub&&<T x={120} y={225} size={29} color={C.muted}>{sub}</T>}</g>;
export const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={914} size={30} anchor="middle" color={color} alpha={alpha} data-note="true">{children}</T>;
export const sentenceStart=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?s.durationInFrames*.5:0));
export const sentenceProgress=(s:Shot,f:number,i=0,a=.08,b=.82)=>{const from=sentenceStart(s,i),to=i+1<(s.cueFrames?.sentences?.length??2)?sentenceStart(s,i+1):s.durationInFrames;return clamp((f-(from+(to-from)*a))/Math.max(1,(to-from)*(b-a)));};
export const fade=(f:number,from:number,span=22)=>ease((f-from)/span);
export const Box=({x,y,w,h,title,color=C.edge,fill=C.surface,children,alpha=1,caption}:any)=><g opacity={alpha} data-box="true"><rect x={x} y={y} width={w} height={h} rx={22} fill={fill} stroke={color} strokeWidth={2}/>{title&&<T x={x+26} y={y+52} size={31} color={color===C.edge?C.text:color} weight={700}>{title}</T>}{caption&&<T x={x+26} y={y+h-24} size={25} color={C.muted}>{caption}</T>}{children}</g>;
export const Pill=({x,y,w=300,text,color=C.teal,alpha=1,size=29}:any)=><g opacity={alpha}><rect x={x} y={y} width={w} height={62} rx={13} fill={C.bg} stroke={color} strokeWidth={2}/><T x={x+w/2} y={y+42} size={size} color={color===C.edge?C.muted:color} anchor="middle">{text}</T></g>;
export const Arrow=({x1,y1,x2,y2,color=C.edge,alpha=1,dashed=false}:any)=>{const a=Math.atan2(y2-y1,x2-x1),l=15;return <g opacity={alpha}><path d={`M ${x1} ${y1} L ${x2} ${y2}`} stroke={color} strokeWidth={3} strokeDasharray={dashed?'9 9':undefined} fill="none"/><path d={`M ${x2-l*Math.cos(a-.55)} ${y2-l*Math.sin(a-.55)} L ${x2} ${y2} L ${x2-l*Math.cos(a+.55)} ${y2-l*Math.sin(a+.55)}`} stroke={color} strokeWidth={3} fill="none"/></g>;};
export const Packet=({p,from,to,text,color=C.teal,w=320}:any)=>{const t=ease(p),alpha=clamp(p/.08)*clamp((1-p)/.08);return <g data-motion-packet="true"><Pill x={mix(from[0],to[0],t)-w/2} y={mix(from[1],to[1],t)-31} w={w} text={text} color={color} alpha={alpha}/></g>;};

export const DotPacket=({p,from,to,color=C.blue}:any)=>{const t=ease(p),alpha=clamp(p/.06)*clamp((1-p)/.06);return <g data-motion-packet="true" opacity={alpha}><circle cx={mix(from[0],to[0],t)} cy={mix(from[1],to[1],t)} r={13} fill={color}/><circle cx={mix(from[0],to[0],t)} cy={mix(from[1],to[1],t)} r={22} fill="none" stroke={color} strokeWidth={2} opacity={.3}/></g>;};
