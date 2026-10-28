import {PuzzleHeader} from '../../../../_shared/puzzles-video/Frame';
import React from 'react';
import {C,FONT,MONO} from './theme';
export const T=({x,y,children,size=32,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
export const Head=({title,sub}:any)=><PuzzleHeader number="P03" title={title} sub={sub}/>;
export const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={914} size={29} color={color} anchor="middle" alpha={alpha} data-note="true">{children}</T>;
