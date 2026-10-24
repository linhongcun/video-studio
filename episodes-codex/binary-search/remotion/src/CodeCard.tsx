import React from 'react';
import solution from '../../solution.json';
import {C,FONT,MONO} from './theme';
const words=new Set(['class','def','while','if','else','return','int','list']);
const split=(s:string)=>s.split(/(\b(?:class|def|while|if|else|return|int|list)\b)/g);
/** Static, complete, exactly the same source as the executable and article. */
export const CodeCard=()=> <g data-code-card="complete-python-solution">
 <text x={120} y={101} fill={C.muted} fontSize={24} fontFamily={FONT}>二分查找 · 闭区间</text>
 <text x={120} y={184} fill={C.text} fontSize={54} fontWeight={760} fontFamily={FONT}>完整 Python 解法</text>
 <text x={120} y={242} fill={C.muted} fontSize={27} fontFamily={FONT}>可直接提交 · 暂停查看完整代码</text>
 {solution.lines.map((line,index)=><text key={index} x={160} y={300+index*40} fill={C.text} fontSize={35} fontFamily={MONO} xmlSpace="preserve" data-code-line={index+1}>
  {split(line).map((word,i)=><tspan key={i} fill={words.has(word)?C.gold:C.text}>{word}</tspan>)}
 </text>)}
 <text x={960} y={940} fill={C.muted} fontSize={27} textAnchor="middle" fontFamily={FONT}>升序、无重复 · 时间 O(log n) · 额外空间 O(1)</text>
</g>;
