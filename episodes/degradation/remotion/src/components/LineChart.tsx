import React from 'react';
import {animatedValue, progress} from '../animation';
import {ShotElement} from '../storyboard';
import {colorToken, stateAt, UIProps} from './ui';

type Point = [number, number];
type Series = {id: string; color: string; width: number; points: Point[]};
const REVEAL_FRAMES = 6;

/** Only false-to-true transitions start a reveal; unrelated state keys do not. */
const revealAt = (original: ShotElement, frame: number, shown: (e: ShotElement) => boolean) => {
  let state = original, visible = shown(state), start: number | undefined;
  for (const key of [...(original.stateKeyframes ?? [])].sort((a, b) => a.frame - b.frame)) {
    if (key.frame > frame) break;
    state = {...state, ...key};
    const next = shown(state);
    if (next && !visible) start = key.frame;
    visible = next;
  }
  return !visible ? 0 : start === undefined ? 1 : progress(frame, start, REVEAL_FRAMES);
};

/** Element-local SVG: authored domains determine all data and axis geometry. */
export const LineChart: React.FC<UIProps> = ({e: original, source, frame, shot}) => {
  const e = stateAt(original, frame), initial = source ?? original;
  const [x0, x1] = e.domain.x, [y0, y1] = e.domain.y;
  // Inset by half the widest stroke so round caps and the axis line stay inside the element box (cover safe areas).
  const pad = Math.max((e.axisWidth ?? 0) / 2, ...(e.series as Series[]).map(series => series.width / 2));
  const pw = e.w - pad * 2, ph = e.h - pad * 2;
  const point = ([x, y]: Point) => `${pad + (x - x0) / (x1 - x0) * pw},${pad + ph - (y - y0) / (y1 - y0) * ph}`;
  const spread = shot ? Number(animatedValue(shot, e.id, 'spread', frame, e.spread ?? 0)) : e.spread ?? 0;
  const areaPoints = e.area?.from.map((from: Point, i: number) => point([
    from[0] + (e.area.to[i][0] - from[0]) * spread,
    from[1] + (e.area.to[i][1] - from[1]) * spread,
  ])).join(' ');
  return <svg data-line-chart width="100%" height="100%" viewBox={`0 0 ${e.w} ${e.h}`} preserveAspectRatio="none" style={{display: 'block', overflow: 'visible'}}>
    {e.areaShown && e.area && <polygon data-chart-area points={areaPoints} fill={colorToken(e.area.color)} opacity={e.area.opacity * revealAt(initial, frame, state => !!state.areaShown)} />}
    <path data-chart-axes d={`M${pad} ${pad}V${pad + ph}H${pad + pw}`} fill="none" stroke={colorToken(e.axisColor)} strokeWidth={e.axisWidth} />
    {(e.series as Series[]).filter(series => (e.visibleSeries ?? []).includes(series.id)).map(series => {
      const reveal = revealAt(initial, frame, state => (state.visibleSeries ?? []).includes(series.id));
      return <polyline key={series.id} data-chart-series={series.id} points={series.points.map(point).join(' ')} fill="none" stroke={colorToken(series.color)} strokeWidth={series.width} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={reveal < 1 ? 1 : undefined} strokeDashoffset={reveal < 1 ? 1 - reveal : undefined} opacity={reveal === 0 ? 0 : 1} />;
    })}
  </svg>;
};
