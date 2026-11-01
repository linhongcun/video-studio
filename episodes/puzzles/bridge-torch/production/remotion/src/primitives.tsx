import React from 'react';
import {C,FONT,MONO} from './theme';
import {Shot} from './data';
import {clamp,ease} from './crossings';
export const T=({x,y,children,size=32,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
export const Head=({title,sub,color=C.text}:any)=><g><T x={120} y={90} size={25} color={C.muted}>趣味推理 P02 · 四人过桥</T><T x={120} y={174} size={50} weight={760} color={color}>{title}</T>{sub&&<T x={120} y={230} size={28} color={C.muted}>{sub}</T>}</g>;
export const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={911} size={30} anchor="middle" color={color} alpha={alpha} data-note="true">{children}</T>;
export const sentenceStart=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?s.durationInFrames*.5:0));
export const sentenceProgress=(s:Shot,f:number,i=0,a=.08,b=.84)=>{
 const from=sentenceStart(s,i),end=sentenceStart(s,i+1)||s.durationInFrames;
 const to=i+1<(s.cueFrames?.sentences?.length??2)?end:s.durationInFrames;
 return clamp((f-(from+(to-from)*a))/Math.max(1,(to-from)*(b-a)));
};
export const fade=(f:number,from:number,to:number)=>ease((f-from)/(to-from));
