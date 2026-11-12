import React from 'react';
import solution from '../../solution.json';
import {C,FONT,MONO} from './theme';
export const CodeCard=()=> <svg width={1920} height={1080} viewBox="0 0 1920 1080" data-code-card="full-python-static-150-frames">
 <rect width={1920} height={1080} fill={C.bg}/>
 <text x={130} y={164} fontFamily={FONT} fontSize={44} fontWeight={750} fill={C.text}>完整 Python 解法</text>
 <text x={1785} y={160} textAnchor="end" fontFamily={FONT} fontSize={27} fill={C.gold}>请暂停阅读 · LC.347</text>
 <rect x={110} y={200} width={1700} height={745} rx={24} fill={C.surface} stroke={C.edge}/>
 {solution.lines.map((line,i)=><g key={i}><text x={159} y={260+i*43} fontSize={22} fontFamily={MONO} fill={C.muted} textAnchor="end">{i+1}</text><text x={200} y={260+i*43} xmlSpace="preserve" fontSize={31} fontFamily={MONO} fill={line.includes('heappush')?C.gold:line.includes('heappop')?C.teal:C.text}>{line}</text></g>)}
 <text x={130} y={1015} fontFamily={FONT} fontSize={27} fill={C.muted}>先统计频次 · 超过 k 才删堆顶 · 返回数字，顺序不限</text>
 </svg>;
