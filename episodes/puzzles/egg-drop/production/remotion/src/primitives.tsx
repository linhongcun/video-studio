import React from 'react';
import {C,FONT,MONO} from './theme';
export const T=({x,y,children,size=32,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
export const Head=({title,sub}:any)=><g><T x={120} y={90} size={25} color={C.muted}>趣味推理 P05 · 两枚鸡蛋</T><T x={120} y={174} size={50} weight={760}>{title}</T>{sub&&<T x={120} y={232} size={28} color={C.muted}>{sub}</T>}</g>;
export const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={922} size={28} color={color} anchor="middle" alpha={alpha} data-note="true">{children}</T>;
export const Panel=({x=1460,y=340,title,lines=[],accent=C.gold}:any)=><g data-panel="true"><rect x={x} y={y} width={335} height={454} rx={20} fill={C.surface} stroke={C.edge}/><T x={x+28} y={y+50} size={24} color={accent} weight={700}>{title}</T>{lines.map((line:any,i:number)=><g key={i}><T x={x+28} y={y+98+i*94} size={22} color={C.muted}>{line.label}</T><T x={x+28} y={y+146+i*94} size={line.size??32} color={line.color??C.text} weight={650}>{line.value}</T></g>)}</g>;
