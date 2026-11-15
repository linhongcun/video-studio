import solution from '../../solution.json';
import {C,FONT,MONO} from '../../../../../_shared/leetcode-video/theme';
export const CodeCard=()=> <svg width={1920} height={1080} viewBox="0 0 1920 1080" data-code-card="complete-python-solution">
<rect width={1920} height={1080} fill={C.bg}/>
<text x={130} y={120} fontFamily={FONT} fontSize={42} fontWeight={750} fill={C.text}>完整 Python 解法</text>
<text x={1785} y={120} textAnchor="end" fontFamily={FONT} fontSize={27} fill={C.gold}>请暂停阅读 · LC.15</text>
<rect x={110} y={160} width={1700} height={795} rx={24} fill={C.surface} stroke={C.edge}/>
{solution.lines.map((line,i)=><g key={i}>
<text x={160} y={201+i*32} textAnchor="end" fontFamily={MONO} fontSize={21} fill={C.muted}>{i+1}</text>
<text data-code-line={i} x={200} y={201+i*32} xmlSpace="preserve" fontFamily={MONO} fontSize={26} fill={line.includes('while')?C.gold:line.includes('ans')?C.teal:C.text}>{line}</text>
</g>)}
<text x={130} y={1020} fontFamily={FONT} fontSize={27} fill={C.muted}>固定值去重 · 和偏小移 L，偏大移 R · 命中后跳过两端等值段</text>
</svg>;
