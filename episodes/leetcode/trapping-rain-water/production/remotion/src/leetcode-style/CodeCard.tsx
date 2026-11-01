import React from 'react';
import solution from '../../../solution.json';
import {C,FONT,MONO} from './theme';
import {EpisodeHeader} from './EpisodeHeader';
import {Terrain} from './Terrain';
import {FINAL} from '../data';
const keywords=new Set(['class','def','for','in','return','int','list']);
const split=(value:string)=>value.split(/(\b(?:class|def|for|in|return|int|list)\b)/g);
/** Nineteen complete source lines; fixed 35px font and 38px spacing, no copyfit. */
export const CodeCard=()=> <g data-code-card="complete-python-solution" data-code-font-size="35" data-code-line-height="38">
 <EpisodeHeader compact/>
 <text x={150} y={160} fontFamily={FONT} fontSize={51} fontWeight={760} fill={C.text}>完整 Python 解法</text>
 <text x={150} y={212} fontFamily={FONT} fontSize={26} fill={C.muted}>完整19行 · 暂停查看 · 不修改输入</text>
 <g transform="translate(1460 5) scale(.25)"><Terrain x={0} baseline={780} water={FINAL.water} showColumns={false} showHeights={false}/></g>
 {solution.lines.map((line,index)=><text key={index} x={175} y={263+index*38} fill={C.text} fontSize={35} fontFamily={MONO} xmlSpace="preserve" data-code-line={index+1}>{split(line).map((token,j)=><tspan key={j} fill={keywords.has(token)?C.gold:C.text}>{token}</tspan>)}</text>)}
 <text x={150} y={1039} fill={C.muted} fontSize={23} fontFamily={FONT}>含当前柱的左右最高值 → 较小值定水位 → 减柱高 → 相加</text>
</g>;
