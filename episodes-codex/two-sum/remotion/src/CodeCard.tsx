import React from 'react';
import solution from '../../solution.json';
import {C,FONT,MONO} from './theme';
const words=new Set(['class','def','for','in','if','return','int','list']);
const split=(s:string)=>s.split(/(\b(?:class|def|for|in|if|return|int|list)\b)/g);
/** Static display, derived from the exact executable solution. */
export const CodeCard=()=> <g data-code-card="complete-python-solution">
 <text x={120} y={101} fill={C.muted} fontSize={24} fontFamily={FONT}>两数之和 · 一遍哈希表</text>
 <text x={120} y={181} fill={C.text} fontSize={54} fontWeight={760} fontFamily={FONT}>完整 Python 解法</text>
 <text x={120} y={238} fill={C.muted} fontSize={27} fontFamily={FONT}>可直接提交 · 暂停查看完整代码</text>
 {solution.lines.map((line,index)=><text key={index} x={150} y={305+index*43} fill={C.text} fontSize={35} fontFamily={MONO} xmlSpace="preserve" data-code-line={index+1}>
  {split(line).map((word,i)=><tspan key={i} fill={words.has(word)?C.gold:C.text}>{word}</tspan>)}
 </text>)}
 <text x={960} y={940} fill={C.muted} fontSize={27} textAnchor="middle" fontFamily={FONT}>平均时间 O(n) · 额外空间 O(n) · 先查，再记录</text>
</g>;
