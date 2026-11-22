import solution from '../../solution.json';
import {C, FONT, MONO} from '../../../../../_shared/leetcode-video/theme';

function lineColor(line: string): string {
  if (line.includes('while queue and fresh > 0') || line.includes('return minutes')) return C.gold;
  if (line.includes('deque') || line.includes('queue')) return C.teal;
  if (line.includes('fresh') || line.includes('minutes')) return '#FDBA74';
  return C.text;
}

export const CodeCard = () => (
  <svg width={1920} height={1080} viewBox="0 0 1920 1080" data-code-card="complete-python-solution">
    <rect width={1920} height={1080} fill={C.bg} />
    <text x={120} y={118} fontFamily={FONT} fontSize={40} fontWeight={750} fill={C.text}>
      完整 Python 解法
    </text>
    <text x={1800} y={118} textAnchor="end" fontFamily={FONT} fontSize={26} fill={C.gold}>
      请暂停阅读 · LC.994
    </text>
    <rect x={110} y={152} width={1700} height={784} rx={22} fill={C.surface} stroke={C.edge} strokeWidth={2} />
    {solution.lines.map((line, i) => (
      <g key={i}>
        <text x={156} y={196 + i * 27.5} textAnchor="end" fontFamily={MONO} fontSize={19} fill={C.muted}>
          {i + 1}
        </text>
        <text
          data-code-line={i}
          x={190}
          y={196 + i * 27.5}
          xmlSpace="preserve"
          fontFamily={MONO}
          fontSize={24}
          fill={lineColor(line)}
        >
          {line}
        </text>
      </g>
    ))}
    <text x={120} y={1000} fontFamily={FONT} fontSize={26} fill={C.muted}>
      全部烂橘入队（第 0 层） · 每轮锁定 len(queue) · 入队即改 2 去重 · fresh &gt; 0 防多算最后一层
    </text>
  </svg>
);
