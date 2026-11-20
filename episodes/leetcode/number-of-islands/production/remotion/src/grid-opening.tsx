import React from 'react';
import {AbsoluteFill, Composition, registerRoot, useCurrentFrame} from 'remotion';
import {LeetcodeHeader} from '../../../../../_shared/leetcode-video/Frame';
import {GRID, VIDEO, shots} from './data';
import type {Cell} from './data';
import {center, IslandMap, MAP, NeighborArrow} from './leetcode-style/IslandMap';
import {C, FONT, MONO} from './leetcode-style/theme';

const firstShot = shots[0];
const land: Cell = [0, 0];
const sea: Cell = [0, 2];
const landAt = 46;
const seaAt = 100;
const mapAt = 153;
const neighborsAt = 196;
const fade = (frame: number, from: number, length: number) =>
  Math.min(1, Math.max(0, (frame - from) / length));

const Opening = () => {
  const frame = useCurrentFrame();
  const mapReveal = fade(frame, mapAt, 24);
  const adjacent = frame >= neighborsAt;
  const target = frame >= seaAt ? sea : land;
  const mapping = frame >= landAt && !adjacent;
  const label = frame >= seaAt ? '第一行第三列：0 → 海水' : '第一行第一列：1 → 陆地';
  const subtitle = firstShot.subtitles?.find(({from, to, duration}) =>
    frame >= from && frame < (to === undefined ? from + (duration ?? 0) : to + 1),
  );
  const subtitleStyle: React.CSSProperties = {
    position: 'absolute', left: 210, right: 210, bottom: 69, textAlign: 'center',
    fontSize: 31, lineHeight: 1.45, fontWeight: 500, color: C.text,
    textShadow: '0 2px 5px #0F172A', whiteSpace: 'pre-wrap',
  };

  return <AbsoluteFill style={{background: C.bg, fontFamily: FONT}}>
    <LeetcodeHeader slug="number-of-islands" detail="LeetCode 200 · 岛屿数量"/>
    <svg width={VIDEO.width} height={VIDEO.height} fontFamily={FONT} fill={C.text}>
      <text x={120} y={182} fontSize={51} fontWeight={760}>这张网格里有几座岛？</text>
      <text x={120} y={242} fontSize={27} fill={C.muted}>4 行 5 列 · 每个数字对应地图上的同一格</text>
      <text x={MAP.x} y={284} fontSize={27} fontWeight={700}>
        {adjacent ? '同一张海陆地图' : '输入网格'}
      </text>
      <IslandMap showState={false} showNeighbor={false} focusCells={mapping ? [target] : []}/>
      {GRID.flatMap((row, r) => row.map((value, col) => {
        const cell: Cell = [r, col];
        const key = cell.join(',');
        const selected = mapping && r === target[0] && col === target[1];
        const revealed = Math.max(mapReveal, key === land.join(',') ? fade(frame, landAt, 12) :
          key === sea.join(',') ? fade(frame, seaAt, 12) : 0);
        const {x, y} = center(cell);
        return <g key={key} opacity={1 - revealed} data-input-cell={key} data-value={value}>
          <rect x={x-MAP.cell/2} y={y-MAP.cell/2} width={MAP.cell} height={MAP.cell}
            fill="#14263B" stroke={selected ? C.gold : '#36516A'} strokeWidth={selected ? 4 : 2}/>
          <text x={x} y={y+16} fontFamily={MONO} textAnchor="middle" fontSize={46}
            fontWeight={700} fill={selected ? C.gold : C.text}>{value}</text>
        </g>;
      }))}
      {adjacent && <>
        <NeighborArrow from={land} to={[0, 1]} alpha={fade(frame, neighborsAt, 10)}/>
        <NeighborArrow from={land} to={[1, 0]} alpha={fade(frame, neighborsAt+12, 10)}/>
      </>}
      <rect x={1050} y={319} width={730} height={151} rx={24} fill={C.surface} stroke={C.gold} strokeWidth={2}/>
      <text x={1090} y={373} fontSize={29} fill={C.muted}>题目要求返回</text>
      <text x={1090} y={422} fontSize={32}>一个整数：岛屿的数量</text>
      <text x={1698} y={431} fontFamily={MONO} fontSize={86} textAnchor="end" fill={C.gold}>?</text>
      <rect x={1050} y={507} width={730} height={342} rx={23} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
      <text x={1090} y={573} fontSize={36} fontWeight={700} fill={C.gold}>
        {adjacent ? '只沿上下左右相连' : mapping ? label : '先读每一格的数字'}
      </text>
      <text x={1090} y={639} fontSize={30}>
        {adjacent ? '共享边缘的陆地才能连起来' : '第几行、第几列，对应地图上的同一格'}
      </text>
      <text x={1090} y={694} fontSize={30}>
        {adjacent ? '整片相连的陆地才算一座岛' : '整个输入用同一规则画成地图'}
      </text>
      <rect x={1090} y={747} width={46} height={36} rx={9} fill="#74AF76" stroke="#CDB783" strokeWidth={3}/>
      <text x={1155} y={775} fontSize={30}>1 陆地</text>
      <rect x={1370} y={747} width={46} height={36} rx={9} fill="#10394F" stroke="#69ADBD" strokeWidth={2}/>
      <text x={1435} y={775} fontSize={30}>0 海水</text>
      <text x={120} y={1045} fontSize={20} fill={C.muted} opacity={.65}>LeetCode 200 · 原题海陆示例</text>
    </svg>
    {subtitle && <div data-subtitle="true" style={subtitleStyle}>{subtitle.text}</div>}
  </AbsoluteFill>;
};

const Root = () => <Composition id="GridOpening" component={Opening}
  {...VIDEO} durationInFrames={firstShot.durationInFrames}/>;
registerRoot(Root);
