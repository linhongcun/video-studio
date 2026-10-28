import React from 'react';
import {PuzzleHeader} from '../../../../_shared/puzzles-video/Frame';
import {C,FONT,MONO} from './theme';
import {Shot} from '../data';
import {clamp,ease} from '../crossings';
export const T=({x,y,children,size=32,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
export const Head=({title,sub,color=C.text}:any)=><PuzzleHeader number="P02" title={title} sub={sub} kicker="四人过桥" color={color}/>;
export const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={911} size={30} anchor="middle" color={color} alpha={alpha} data-note="true">{children}</T>;
export const sentenceStart=(s:Shot,i:number)=>Number(s.cueFrames?.sentences?.[i]??(i?s.durationInFrames*.5:0));
export const sentenceProgress=(s:Shot,f:number,i=0,a=.08,b=.84)=>{
 const from=sentenceStart(s,i),end=sentenceStart(s,i+1)||s.durationInFrames;
 const to=i+1<(s.cueFrames?.sentences?.length??2)?end:s.durationInFrames;
 return clamp((f-(from+(to-from)*a))/Math.max(1,(to-from)*(b-a)));
};
export const fade=(f:number,from:number,to:number)=>ease((f-from)/(to-from));
