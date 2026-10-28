import React from 'react';
import {LeetcodeHeader} from '../../../../_shared/leetcode-video/Frame';
import solution from '../../../solution.json';
import {C,FONT,MONO} from './theme';
const keywords=new Set(['class','def','for','in','if','return','int','list','continue','False','True']);
const split=(s:string)=>s.split(/(\b(?:class|def|for|in|if|return|int|list|continue|False|True)\b)/g);
/** Every source line uses fixed 36px; no fit-to-box or adaptive shrinking. */
export const CodeCard=()=> <g data-code-card="complete-python-solution" data-code-font-size="36" data-code-line-height="35">
 <foreignObject x={0} y={0} width={1920} height={84}><LeetcodeHeader slug="permutations" compact identity={{number:46,method:'全排列 · 回溯'}}/></foreignObject>
 <text x={130} y={139} fill={C.text} fontFamily={FONT} fontSize={44} fontWeight={750}>完整 Python 解法</text>
 <text x={130} y={186} fill={C.muted} fontFamily={FONT} fontSize={25}>完整22行 · 暂停查看 · 不改输入</text>
 {solution.lines.map((line,i)=><text key={i} x={155} y={231+i*35} fill={C.text} fontFamily={MONO} fontSize={36} xmlSpace="preserve" data-code-line={i+1}>{split(line).map((word,j)=><tspan key={j} fill={keywords.has(word)?C.gold:C.text}>{word}</tspan>)}</text>)}
 <text x={960} y={1041} fill={C.muted} fontFamily={FONT} fontSize={23} textAnchor="middle">排满保存 path.copy() · 返回后撤销选择 · 答案副本保持</text>
</g>;
