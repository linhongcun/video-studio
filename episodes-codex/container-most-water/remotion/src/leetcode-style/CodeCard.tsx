import React from 'react';
import solution from '../../../solution.json';
import {C,FONT,MONO} from './theme';
import {EpisodeHeader} from './EpisodeHeader';

const keywords=new Set(['class','def','while','if','else','return']);
const tokens=(line:string)=>line.split(/(\b(?:class|def|while|if|else|return)\b)/g);

/** Static reference card: every line stays visible for pause-and-read viewing. */
export const CodeCard=()=> <g data-code-card="complete-python-solution">
 <EpisodeHeader compact/>
 <text x={120} y={184} fill={C.text} fontSize={54} fontWeight={760} fontFamily={FONT}>完整 Python 解法</text>
 <text x={120} y={244} fill={C.muted} fontSize={27} fontFamily={FONT}>可直接提交 · 暂停查看完整代码</text>
 {solution.lines.map((line,index)=><text key={index} x={160} y={290+index*38} fill={C.text} fontSize={34} fontFamily={MONO} xmlSpace="preserve" data-code-line={index+1}>
  {tokens(line).map((part,i)=><tspan key={i} fill={keywords.has(part)?C.gold:C.text}>{part}</tspan>)}
 </text>)}
 <text x={960} y={944} fill={C.muted} fontSize={27} textAnchor="middle" fontFamily={FONT}>时间 O(n) · 额外空间 O(1)</text>
</g>;
