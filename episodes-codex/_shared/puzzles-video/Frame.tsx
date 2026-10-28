import React from 'react';
import {C, FONT} from './theme';

type HeaderProps = {
  number: string; title: string; sub?: string; kicker?: string; color?: string;
};

/** Static cover motifs stay at the edges; only the puzzle objects animate. */
export const PuzzleCanvas = () => <g data-puzzles-style="cover-continuity-v1" aria-hidden="true">
  <defs>
    <radialGradient id="puzzles-glow"><stop stopColor={C.violet} stopOpacity=".07"/><stop offset="1" stopColor={C.bg} stopOpacity="0"/></radialGradient>
  </defs>
  <rect width="1920" height="1080" fill={C.bg}/>
  <ellipse cx="1300" cy="430" rx="1000" ry="670" fill="url(#puzzles-glow)"/>
  {[{x:0,y:0},{x:1920,y:1080}].map(({x,y},i)=><g key={i} transform={`translate(${x} ${y}) rotate(${i?180:0})`} opacity=".18">
    {[80,132,184].map(r=><path key={r} d={`M 0 ${r} A ${r} ${r} 0 0 0 ${r} 0`} fill="none" stroke={r===132?C.coral:C.violet} strokeWidth="1"/>)}
    {[32,64,96,128,160].flatMap(px=>[32,64,96,128,160].map(py=><circle key={`${px}-${py}`} cx={px} cy={py} r="1.3" fill={C.violet}/>))}
  </g>)}
  <path d="M120 121H1800" stroke={C.edge} strokeWidth="1"/>
</g>;

/** Same P badge, typography and palette as the series covers. */
export const PuzzleHeader = ({number,title,sub,kicker,color=C.text}:HeaderProps) => <g fontFamily={FONT} data-puzzles-header={number}>
  <rect x="120" y="53" width="86" height="43" rx="11" fill={C.coral}/>
  <text x="163" y="83" textAnchor="middle" fill={C.bg} fontSize="27" fontWeight="800">{number}</text>
  <text x="224" y="85" fill={C.violet} fontSize="26" fontWeight="700">趣味推理</text>
  {kicker&&<text x="380" y="85" fill={C.muted} fontSize="23">{kicker}</text>}
  <text x="120" y="174" fill={color} fontSize="50" fontWeight="760">{title}</text>
  {sub&&<text x="120" y="232" fill={C.muted} fontSize="28" fontWeight="500">{sub}</text>}
</g>;
