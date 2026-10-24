import React from 'react';
import solution from '../../solution.json';
import {C,FONT,MONO} from './theme';

const keywords=new Set(['class','def','for','in','while','return']);
const split=(line:string)=>line.split(/(\b(?:class|def|for|in|while|return)\b)/g);

/** Complete program is static from the first card frame through the final frame. */
export const CodeCard=()=>{
 const rows=solution.lines;
 const lineHeight=Math.min(39,600/Math.max(1,rows.length-1));
 const size=Math.min(34,lineHeight*.9);
 return <g data-code-card="complete-python-solution">
  <text x={120} y={101} fill={C.muted} fontSize={24} fontFamily={FONT}>无重复字符的最长子串 · 滑动窗口</text>
  <text x={120} y={184} fill={C.text} fontSize={54} fontWeight={760} fontFamily={FONT}>完整 Python 解法</text>
  <text x={120} y={242} fill={C.muted} fontSize={27} fontFamily={FONT}>可直接提交 · 暂停查看完整代码</text>
  {rows.map((line,index)=><text key={index} x={160} y={291+index*lineHeight} fill={C.text} fontSize={size} fontFamily={MONO} xmlSpace="preserve" data-code-line={index+1}>
   {split(line).map((part,i)=><tspan key={i} fill={keywords.has(part)?C.gold:C.text}>{part}</tspan>)}
  </text>)}
  <text x={960} y={958} fill={C.muted} fontSize={27} textAnchor="middle" fontFamily={FONT}>平均时间 O(n) · 集合只保存当前窗口的字符</text>
 </g>;
};

