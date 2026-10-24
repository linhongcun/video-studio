import React from 'react';
import solution from '../../solution.json';
import {C,FONT,MONO} from './theme';
const words=new Set(['class','def','if','return','for','in','range','int']);
const split=(s:string)=>s.split(/(\b(?:class|def|if|return|for|in|range|int)\b)/g);
/** Full static appendix, using exactly the executable source lines. */
export const CodeCard=()=> <g data-code-card="complete-python-solution">
 <text x={120} y={101} fill={C.muted} fontSize={24} fontFamily={FONT}>爬楼梯 · 两个滚动计数</text>
 <text x={120} y={184} fill={C.text} fontSize={54} fontWeight={760} fontFamily={FONT}>完整 Python 解法</text>
 <text x={120} y={245} fill={C.muted} fontSize={28} fontFamily={FONT}>可直接提交 · 暂停查看完整代码</text>
 {solution.lines.map((line,index)=><text key={index} x={180} y={345+index*48} fill={C.text} fontSize={36} fontFamily={MONO} xmlSpace="preserve" data-code-line={index+1}>
  {split(line).map((word,i)=><tspan key={i} fill={words.has(word)?C.gold:C.text}>{word}</tspan>)}
 </text>)}
 <text x={960} y={930} fill={C.muted} fontSize={29} textAnchor="middle" fontFamily={FONT}>本题每项只依赖前两项 · 时间 O(n) · 额外空间 O(1)</text>
</g>;
