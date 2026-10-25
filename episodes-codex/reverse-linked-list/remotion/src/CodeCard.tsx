import React from 'react';
import solution from '../../solution.json';
import {C,FONT,MONO} from './theme';
const words=new Set(['class','def','while','return','None']);
const split=(s:string)=>s.split(/(\b(?:class|def|while|return|None)\b)/g);
/** Independent static appendix: no scene animation, subtitle or progressive reveal. */
export const CodeCard=()=> <g data-code-card="complete-python-solution">
 <text x={120} y={101} fill={C.muted} fontSize={27} fontFamily={FONT}>反转链表 · 迭代解法</text>
 <text x={120} y={184} fill={C.text} fontSize={54} fontWeight={760} fontFamily={FONT}>完整 Python 解法</text>
 <text x={120} y={246} fill={C.muted} fontSize={30} fontFamily={FONT}>平台已定义节点类型 · 可直接提交 · 暂停查看完整代码</text>
 {solution.lines.map((line,index)=><text key={index} x={210} y={326+index*45} fill={C.text} fontSize={39} fontFamily={MONO} xmlSpace="preserve" data-code-line={index+1}>
  {split(line).map((word,i)=><tspan key={i} fill={words.has(word)?C.gold:C.text}>{word}</tspan>)}
 </text>)}
 <text x={960} y={940} fill={C.muted} fontSize={30} textAnchor="middle" fontFamily={FONT}>只修改原节点的 next · 时间 O(n) · 额外空间 O(1)</text>
</g>;
