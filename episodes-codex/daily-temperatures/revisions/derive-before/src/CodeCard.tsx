import React from 'react';
import solution from '../../solution.json';
import {C,FONT,MONO} from './theme';
export const CodeCard=()=> <svg width={1920} height={1080} viewBox="0 0 1920 1080" data-code-card="full-python-static-150-frames">
 <rect width={1920} height={1080} fill={C.bg}/>
 <text x={130} y={110} fontFamily={FONT} fontSize={46} fontWeight={750} fill={C.text}>完整 Python 解法</text>
 <text x={1785} y={108} textAnchor="end" fontFamily={FONT} fontSize={30} fill={C.gold}>请暂停阅读 · LC.739</text>
 <rect x={110} y={160} width={1700} height={760} rx={24} fill={C.surface} stroke={C.edge}/>
 {solution.lines.map((line,i)=><g key={i}><text x={155} y={222+i*52} fontSize={22} fontFamily={MONO} fill={C.muted} textAnchor="end">{i+1}</text><text x={195} y={222+i*52} xmlSpace="preserve" fontSize={36} fontFamily={MONO} fill={line.trim().startsWith('while')?C.gold:line.includes('answer[previous]')?C.teal:C.text}>{line}</text></g>)}
 <text x={130} y={995} fontFamily={FONT} fontSize={28} fill={C.muted}>严格更暖才移出 · 日期差写回原位 · 没等到保持 0</text>
 </svg>;
