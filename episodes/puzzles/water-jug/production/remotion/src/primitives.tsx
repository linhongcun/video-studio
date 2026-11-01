import React from 'react';
import {C,FONT,MONO} from './theme';
export const T=({x,y,children,size=32,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
export const Head=({title,sub}:any)=><g><T x={120} y={90} size={25} color={C.muted}>趣味推理 P03 · 量出4升水</T><T x={120} y={174} size={50} weight={760}>{title}</T>{sub&&<T x={120} y={232} size={28} color={C.muted}>{sub}</T>}</g>;
export const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={914} size={29} color={color} anchor="middle" alpha={alpha} data-note="true">{children}</T>;
