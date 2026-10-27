import React from 'react';
import solution from '../../solution.json';
import {C,FONT,MONO} from './theme';
export const CodeCard=()=> <svg width={1920} height={1080} viewBox="0 0 1920 1080" data-code-card="full-python-static-150-frames">
 <rect width={1920} height={1080} fill={C.bg}/>
 <text x={130} y={102} fontFamily={FONT} fontSize={45} fontWeight={750} fill={C.text}>完整 Python 解法</text>
 <text x={1785} y={100} textAnchor="end" fontFamily={FONT} fontSize={28} fill={C.gold}>请暂停阅读 · LC.547</text>
 <rect x={110} y={143} width={1700} height={842} rx={24} fill={C.surface} stroke={C.edge}/>
 {solution.lines.map((line,i)=><g key={i}><text x={155} y={188+i*33} fontSize={20} fontFamily={MONO} fill={C.muted} textAnchor="end">{i+1}</text><text x={194} y={188+i*33} xmlSpace="preserve" fontSize={33} fontFamily={MONO} fill={line.includes('parent[rb] = ra')?C.gold:line.includes('count -= 1')||line.trim()==='return count'?C.teal:C.text}>{line}</text></g>)}
 <text x={130} y={1030} fontFamily={FONT} fontSize={27} fill={C.muted}>按大小合并 · 路径减半 · 根不同才减少组数</text>
 </svg>;
