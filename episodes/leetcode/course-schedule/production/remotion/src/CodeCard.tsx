import solution from '../../solution.json';
import {C,FONT,MONO} from '../../../../../_shared/leetcode-video/theme';
export const CodeCard=()=> <svg width={1920} height={1080} viewBox="0 0 1920 1080" data-code-card="complete-python-solution">
<rect width={1920} height={1080} fill={C.bg}/>
<text x={130} y={140} fontFamily={FONT} fontSize={42} fontWeight={750} fill={C.text}>完整 Python 解法</text>
<text x={1785} y={140} textAnchor="end" fontFamily={FONT} fontSize={27} fill={C.gold}>请暂停阅读 · LC.207</text>
<rect x={110} y={185} width={1700} height={720} rx={24} fill={C.surface} stroke={C.edge}/>
{solution.lines.map((line,i)=><g key={i}>
<text x={160} y={236+i*38} textAnchor="end" fontFamily={MONO} fontSize={21} fill={C.muted}>{i+1}</text>
<text data-code-line={i} x={200} y={236+i*38} xmlSpace="preserve" fontFamily={MONO} fontSize={30} fill={line.includes('indegree')?C.gold:line.includes('queue')?C.teal:C.text}>{line}</text>
</g>)}
<text x={130} y={1010} fontFamily={FONT} fontSize={27} fill={C.muted}>先修项成边 · 入度为零进队列 · 学完删出边 · 学完门数判定</text>
</svg>;
