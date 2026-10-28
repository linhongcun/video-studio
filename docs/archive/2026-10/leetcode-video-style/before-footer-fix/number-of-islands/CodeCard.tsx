import React from 'react';
import {LeetcodeHeader} from '../../../../_shared/leetcode-video/Frame';
import solution from '../../../solution.json';
import {C,FONT,MONO} from './theme';
const words=new Set(['class','def','for','in','if','return','int','list','while','and','or','not','continue']);
const split=(s:string)=>s.split(/(\b(?:class|def|for|in|if|return|int|list|while|and|or|not|continue)\b)/g);
/** All 26 source lines are displayed explicitly; no adaptive font reduction. */
export const CodeCard=()=> <g data-code-card="complete-python-solution" data-code-font-size="30" data-code-line-height="29">
 <foreignObject x={0} y={0} width={1920} height={84}><LeetcodeHeader slug="number-of-islands" compact identity={{number:200,method:'岛屿数量 · 迭代深度优先搜索'}}/></foreignObject>
 <text x={120} y={158} fill={C.text} fontSize={48} fontWeight={760} fontFamily={FONT}>完整 Python 解法</text>
 <text x={120} y={211} fill={C.muted} fontSize={25} fontFamily={FONT}>完整26行 · 暂停查看 · 不改输入地图</text>
 {solution.lines.map((line,index)=><text key={index} x={150} y={253+index*29} fill={C.text} fontSize={30} fontFamily={MONO} xmlSpace="preserve" data-code-line={index+1}>
  {split(line).map((word,i)=><tspan key={i} fill={words.has(word)?C.gold:C.text}>{word}</tspan>)}
 </text>)}
 <text x={960} y={1053} fill={C.muted} fontSize={22} textAnchor="middle" fontFamily={FONT}>四邻扩展 · 先标记再入栈 · 只在新岛起点增加计数</text>
</g>;
