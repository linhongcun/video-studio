// EP.05 cdn-v1: web-page world map. Natural Earth 1:110m land (public domain), equirectangular projection.
// Everything (view, dots, lines, packets, labels, frames) comes from props / storyboard element fields.
import React from 'react';
import {Easing, interpolate, interpolateColors} from 'remotion';
import {FONT, P} from '../theme';
import {colorToken, stateAt, UIProps} from './ui';
import {BrowserChrome} from './BrowserChrome';
import {browserHeaderHeight} from './browserLayout';
import {LAND_PATH} from './worldLand';
import {CITIES} from './worldCities';

export type LonLat = {lon: number; lat: number};
/** A dot id, a CITIES key (e.g. "上海"), or explicit coordinates. */
export type MapPointRef = string | LonLat;
/** centerLon also sets the projection's central meridian (150 = Pacific-centred, so 上海→美国西海岸 does not wrap). */
export type MapView = {centerLon: number; centerLat: number; lonSpan: number};
export type MapViewKey = MapView & {frame: number; easing?: 'linear' | 'inOutCubic'};
export type ColorKey = {frame: number; color: string; fadeFrames?: number};
export type MapDot = {
  id: string; lon?: number; lat?: number; city?: string;
  label?: string; labelPos?: 'top' | 'bottom' | 'left' | 'right'; labelColor?: string; labelSize?: number; labelAppearFrame?: number; labelDx?: number; labelDy?: number;
  color?: string; size?: number; ring?: boolean;
  appearFrame?: number; appearFrames?: number; disappearFrame?: number;
  pulse?: boolean; pulsePeriod?: number; pulseStartFrame?: number; pulseEndFrame?: number;
  colorKeyframes?: ColorKey[]; highlightFrame?: number; dimFrame?: number; dimOpacity?: number; undimFrame?: number;
};
export type MapPacket = {startFrame: number; travelFrames?: number; mode?: 'go' | 'return' | 'roundtrip'; repeat?: number; everyFrames?: number; color?: string; size?: number};
export type MapLine = {
  id: string; from: MapPointRef; to: MapPointRef;
  startFrame?: number; drawFrames?: number; color?: string; width?: number; dashed?: boolean; bulge?: number;
  label?: string; labelColor?: string; labelSize?: number; labelAt?: number; labelDx?: number; labelDy?: number; labelAppearFrame?: number;
  colorKeyframes?: ColorKey[]; dimFrame?: number; dimOpacity?: number; disappearFrame?: number; packets?: MapPacket[];
};
export type MapLabel = {
  id: string; text: string; at: MapPointRef; dx?: number; dy?: number; anchor?: 'center' | 'left' | 'right';
  appearFrame?: number; disappearFrame?: number; color?: string; size?: number; weight?: number; background?: string; strike?: boolean; strikeFrame?: number;
};
export type WorldMapProps = {
  view?: MapView; viewKeyframes?: MapViewKey[]; landColor?: string; landStroke?: string; oceanColor?: string; graticule?: boolean;
  dots?: MapDot[]; lines?: MapLine[]; labels?: MapLabel[];
};

export const DEFAULT_VIEW: MapView = {centerLon: 150, centerLat: 18, lonSpan: 360};
const ease = Easing.inOut(Easing.cubic);
const clampOpt = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const wrap = (d: number) => ((d + 540) % 360 + 360) % 360 - 180;
const fadeIn = (frame: number, start = 0, dur = 8) => interpolate(frame, [start, start + dur], [0, 1], clampOpt);
const visible = (frame: number, a?: number, b?: number) => frame >= (a ?? 0) && (b === undefined || frame < b);
const tok = (c: string | undefined, fallback: string) => colorToken(c) ?? fallback;

export function viewAt(props: WorldMapProps, frame: number): MapView {
  const keys = [...(props.viewKeyframes ?? [])].sort((a, b) => a.frame - b.frame);
  if (!keys.length) return props.view ?? DEFAULT_VIEW;
  if (frame <= keys[0].frame) return keys[0];
  for (let i = 1; i < keys.length; i++) if (frame <= keys[i].frame) {
    const a = keys[i - 1], b = keys[i];
    const t = (keys[i].easing === 'linear' ? (x: number) => x : ease)((frame - a.frame) / Math.max(1, b.frame - a.frame));
    // zoom in log space so the span change feels uniform
    return {centerLon: a.centerLon + wrap(b.centerLon - a.centerLon) * t, centerLat: a.centerLat + (b.centerLat - a.centerLat) * t, lonSpan: Math.exp(Math.log(a.lonSpan) + (Math.log(b.lonSpan) - Math.log(a.lonSpan)) * t)};
  }
  return keys[keys.length - 1];
}
/** Equirectangular projection into a W×H box. Returns pixels relative to the box. */
export function makeProjection(view: MapView, W: number, H: number) {
  const k = W / view.lonSpan;
  return {k, project: ({lon, lat}: LonLat) => ({x: W / 2 + wrap(lon - view.centerLon) * k, y: H / 2 - (lat - view.centerLat) * k})};
}
export function resolvePoint(ref: MapPointRef, dots: MapDot[] = []): LonLat {
  if (typeof ref !== 'string') return ref;
  const dot = dots.find(d => d.id === ref);
  if (dot) return dotLonLat(dot);
  if (CITIES[ref]) return CITIES[ref];
  // Node ids written as "n-<city>" (e.g. "n-东京") resolve to the dot placed at that city, else the CITIES entry.
  const m = /^n-(.+)$/.exec(ref);
  if (m) {
    const byCity = dots.find(d => d.city === m[1]);
    if (byCity) return dotLonLat(byCity);
    if (CITIES[m[1]]) return CITIES[m[1]];
  }
  throw new Error(`WorldMap: unknown point "${ref}" (not a dot id or CITIES key)`);
}
export function dotLonLat(d: MapDot): LonLat {
  if (typeof d.lon === 'number' && typeof d.lat === 'number') return {lon: d.lon, lat: d.lat};
  if (d.city && CITIES[d.city]) return CITIES[d.city];
  throw new Error(`WorldMap: dot ${d.id} needs lon/lat or a known city`);
}
const colorAt = (base: string, keys: ColorKey[] | undefined, frame: number) => {
  let c = base;
  for (const k of [...(keys ?? [])].sort((a, b) => a.frame - b.frame)) {
    if (frame < k.frame) break;
    c = interpolateColors(frame, [k.frame, k.frame + (k.fadeFrames ?? 10)], [c, tok(k.color, k.color)]);
  }
  return c;
};
const dimAt = (frame: number, dimFrame?: number, to = .3, undim?: number) => {
  if (dimFrame === undefined) return 1;
  const v = interpolate(frame, [dimFrame, dimFrame + 10], [1, to], clampOpt);
  return undim === undefined ? v : interpolate(frame, [undim, undim + 10], [v, 1], clampOpt);
};
/** Quadratic "great-circle-ish" arc: bows toward screen-up (north) by bulge × chord length. */
export function arc(a: {x: number; y: number}, b: {x: number; y: number}, bulge = .18) {
  const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2, dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1;
  let nx = -dy / len, ny = dx / len;
  if (ny > 0) {nx = -nx; ny = -ny;}
  const c = {x: mx + nx * len * bulge, y: my + ny * len * bulge};
  const at = (t: number) => ({x: (1 - t) ** 2 * a.x + 2 * (1 - t) * t * c.x + t * t * b.x, y: (1 - t) ** 2 * a.y + 2 * (1 - t) * t * c.y + t * t * b.y});
  let length = 0, prev = a;
  for (let i = 1; i <= 48; i++) {const p = at(i / 48); length += Math.hypot(p.x - prev.x, p.y - prev.y); prev = p;}
  return {d: `M${a.x},${a.y} Q${c.x},${c.y} ${b.x},${b.y}`, at, length};
}
const packetT = (p: MapPacket, frame: number): number | null => {
  const travel = p.travelFrames ?? 20, every = p.everyFrames ?? travel + 6, n = p.repeat ?? 1;
  for (let i = 0; i < n; i++) {
    const s = p.startFrame + i * every, total = p.mode === 'roundtrip' ? travel * 2 : travel;
    if (frame >= s && frame < s + total) {
      const q = (frame - s) / travel;
      return p.mode === 'return' ? 1 - q : p.mode === 'roundtrip' ? (q <= 1 ? q : 2 - q) : q;
    }
  }
  return null;
};

export const WorldMapView: React.FC<{props: WorldMapProps; frame: number; width: number; height: number; uid?: string}> = ({props, frame, width: W, height: H, uid = 'map'}) => {
  const view = viewAt(props, frame), {k, project} = makeProjection(view, W, H);
  const dots = props.dots ?? [], lines = props.lines ?? [], labels = props.labels ?? [];
  const tx = W / 2 - (180 + view.centerLon) * k, ty = H / 2 - (90 - view.centerLat) * k;
  const grat: React.ReactNode[] = [];
  if (props.graticule !== false) {
    for (let lon = -180; lon < 180; lon += 30) {const x = W / 2 + wrap(lon - view.centerLon) * k; grat.push(<line key={`m${lon}`} x1={x} x2={x} y1={0} y2={H} />);}
    for (let lat = -60; lat <= 60; lat += 30) {const y = H / 2 - (lat - view.centerLat) * k; grat.push(<line key={`p${lat}`} x1={0} x2={W} y1={y} y2={y} />);}
  }
  const labelEls: React.ReactNode[] = [];
  const pushLabel = (key: string, x: number, y: number, text: string, o: {color?: string; size?: number; weight?: number; anchor?: string; background?: string; opacity: number; strike?: number; dataId?: string}) => {
    const size = o.size ?? 30, tr = o.anchor === 'left' ? 'translate(0,-50%)' : o.anchor === 'right' ? 'translate(-100%,-50%)' : 'translate(-50%,-50%)';
    labelEls.push(<div key={key} data-map-label={o.dataId ?? key} style={{position: 'absolute', left: x, top: y, transform: tr, opacity: o.opacity, whiteSpace: 'nowrap', fontFamily: FONT, fontSize: size, lineHeight: 1.2, fontWeight: o.weight ?? 700, color: tok(o.color, P.text), background: o.background ? tok(o.background, o.background) : `${P.bg}CC`, padding: '2px 10px', borderRadius: 8}}>
      <span style={{position: 'relative'}}>{text}{o.strike !== undefined && <span style={{position: 'absolute', left: -4, top: '52%', height: 4, width: `calc(${o.strike * 100}% + 8px)`, background: P.danger, borderRadius: 2}} />}</span>
    </div>);
  };
  return <div data-world-map={uid} style={{position: 'relative', width: W, height: H, overflow: 'hidden', background: tok(props.oceanColor, '#0E1630')}}>
    <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
      <defs>
        <filter id={`${uid}-glow`} x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        {lines.map(l => {
          const a = project(resolvePoint(l.from, dots)), b = project(resolvePoint(l.to, dots)), g = arc(a, b, l.bulge);
          const p = (l.drawFrames ?? 20) <= 1 ? (frame >= (l.startFrame ?? 0) ? 1 : 0) : interpolate(frame, [l.startFrame ?? 0, (l.startFrame ?? 0) + (l.drawFrames ?? 20)], [0, 1], {...clampOpt, easing: ease});
          return <mask key={l.id} id={`${uid}-m-${l.id}`} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}><path d={g.d} fill="none" stroke="#fff" strokeWidth={(l.width ?? 4) + 8} strokeLinecap="round" strokeDasharray={g.length + 2} strokeDashoffset={(g.length + 2) * (1 - p)} /></mask>;
        })}
      </defs>
      <g stroke={P.muted} strokeOpacity={.18} strokeWidth={1}>{grat}</g>
      <g transform={`translate(${tx},${ty}) scale(${k})`}>
        {[-360, 0, 360].map(off => <path key={off} transform={`translate(${off},0)`} d={LAND_PATH} fillRule="evenodd" fill={tok(props.landColor, P.panel2)} stroke={tok(props.landStroke, '#334155')} strokeWidth={1.2} vectorEffect="non-scaling-stroke" />)}
      </g>
      {lines.map(l => {
        if (!visible(frame, l.startFrame, l.disappearFrame)) return null;
        const a = project(resolvePoint(l.from, dots)), b = project(resolvePoint(l.to, dots)), g = arc(a, b, l.bulge);
        const color = colorAt(tok(l.color, P.secondary), l.colorKeyframes, frame), w = l.width ?? 4, op = dimAt(frame, l.dimFrame, l.dimOpacity);
        return <g key={l.id} data-map-line={l.id} opacity={op}>
          <path d={g.d} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round" strokeDasharray={l.dashed ? `${w * 3} ${w * 2.5}` : undefined} mask={`url(#${uid}-m-${l.id})`} />
          {(l.packets ?? []).map((pk, i) => {
            const t = packetT(pk, frame);
            if (t === null) return null;
            const s = pk.size ?? 9, c = tok(pk.color, '#FDE68A'), dir = pk.mode === 'return' ? -1 : 1;
            return <g key={i} data-map-packet={`${l.id}-${i}`} filter={`url(#${uid}-glow)`}>
              {[.06, .03].map((d, j) => {const q = g.at(Math.max(0, Math.min(1, t - d * dir))); return <circle key={j} cx={q.x} cy={q.y} r={s * (.45 + j * .2)} fill={c} opacity={.25 + j * .2} />;})}
              {(() => {const q = g.at(t); return <circle cx={q.x} cy={q.y} r={s} fill={c} />;})()}
            </g>;
          })}
        </g>;
      })}
      {dots.map(d => {
        if (!visible(frame, d.appearFrame, d.disappearFrame)) return null;
        const p = project(dotLonLat(d)), r = d.size ?? 12, a0 = d.appearFrame ?? 0, af = d.appearFrames ?? 10;
        const pop = interpolate(frame, [a0, a0 + af * .6, a0 + af], [0, 1.3, 1], clampOpt);
        const hl = d.highlightFrame === undefined ? 1 : interpolate(frame, [d.highlightFrame, d.highlightFrame + 10], [1, 1.6], clampOpt);
        const color = colorAt(tok(d.color, P.primary), d.colorKeyframes, frame), op = dimAt(frame, d.dimFrame, d.dimOpacity, d.undimFrame);
        const period = d.pulsePeriod ?? 45, ps = d.pulseStartFrame ?? a0 + af;
        const pulsing = d.pulse && frame >= ps && (d.pulseEndFrame === undefined || frame < d.pulseEndFrame);
        const ph = pulsing ? ((frame - ps) % period) / period : 0;
        return <g key={d.id} data-map-dot={d.id} opacity={op}>
          {pulsing && <circle cx={p.x} cy={p.y} r={r * hl * (1 + ph * 1.8)} fill="none" stroke={color} strokeWidth={3} opacity={(1 - ph) * .8} />}
          {d.highlightFrame !== undefined && frame >= d.highlightFrame && <circle cx={p.x} cy={p.y} r={r * hl * 1.6} fill={color} opacity={.18} />}
          <circle cx={p.x} cy={p.y} r={r * pop * hl} fill={d.ring ? P.bg : color} stroke={d.ring ? color : P.bg} strokeWidth={d.ring ? 4 : 3} filter={`url(#${uid}-glow)`} />
        </g>;
      })}
    </svg>
    {dots.map(d => {
      if (!d.label || !visible(frame, d.appearFrame, d.disappearFrame)) return null;
      const p = project(dotLonLat(d)), r = (d.size ?? 12) + 10, size = d.labelSize ?? 30, pos = d.labelPos ?? 'top';
      const x = pos === 'left' ? p.x - r : pos === 'right' ? p.x + r : p.x, y = pos === 'top' ? p.y - r - size * .6 : pos === 'bottom' ? p.y + r + size * .6 : p.y;
      const la = d.labelAppearFrame ?? (d.appearFrame ?? 0) + 4;
      pushLabel(`dot-${d.id}`, x + (d.labelDx ?? 0), y + (d.labelDy ?? 0), d.label, {color: d.labelColor ?? d.color, size, anchor: pos === 'left' ? 'right' : pos === 'right' ? 'left' : 'center', opacity: fadeIn(frame, la) * dimAt(frame, d.dimFrame, d.dimOpacity, d.undimFrame), dataId: d.id});
      return null;
    })}
    {lines.map(l => {
      if (!l.label || !visible(frame, l.startFrame, l.disappearFrame)) return null;
      const a = project(resolvePoint(l.from, dots)), b = project(resolvePoint(l.to, dots)), q = arc(a, b, l.bulge).at(l.labelAt ?? .5);
      const la = l.labelAppearFrame ?? (l.startFrame ?? 0) + (l.drawFrames ?? 20);
      pushLabel(`line-${l.id}`, q.x + (l.labelDx ?? 0), q.y + (l.labelDy ?? -34), l.label, {color: l.labelColor ?? l.color, size: l.labelSize ?? 28, opacity: fadeIn(frame, la) * dimAt(frame, l.dimFrame, l.dimOpacity), dataId: l.id});
      return null;
    })}
    {labels.map(lb => {
      if (!visible(frame, lb.appearFrame, lb.disappearFrame)) return null;
      const p = project(resolvePoint(lb.at, dots));
      const strike = lb.strike ? (lb.strikeFrame === undefined ? 1 : interpolate(frame, [lb.strikeFrame, lb.strikeFrame + 10], [0, 1], clampOpt)) : undefined;
      pushLabel(`label-${lb.id}`, p.x + (lb.dx ?? 0), p.y + (lb.dy ?? 0), lb.text, {color: lb.color, size: lb.size, weight: lb.weight, anchor: lb.anchor, background: lb.background, opacity: fadeIn(frame, lb.appearFrame ?? 0), strike: strike && strike > 0 ? strike : undefined});
      return null;
    })}
    {labelEls}
  </div>;
};

/** Storyboard component: bare map filling its element box (e.g. lower half of a shop page, shot 1/17/18). */
export const WorldMap: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame);
  return <div data-component="WorldMap" style={{width: '100%', height: '100%', borderRadius: e.radius ?? 12, overflow: 'hidden', border: e.border === false ? undefined : `2px solid ${P.muted}55`, boxSizing: 'border-box'}}>
    <WorldMapView props={e as WorldMapProps} frame={frame} width={e.w - (e.border === false ? 0 : 4)} height={e.h - (e.border === false ? 0 : 4)} uid={e.id} />
  </div>;
};

export type WorldMapPageProps = WorldMapProps & {url?: string; title?: string; pageTitle?: string; pageTitleColor?: string; badges?: string[]; showPadlock?: boolean};
/** Storyboard component: full-screen browser page (same chrome as cookie-v1 BrowserChrome) whose page is a title row + the map. */
export const WorldMapPage: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), header = browserHeaderHeight(e), titleH = e.pageTitle ? 72 : 0;
  const mapW = e.w - 6, mapH = e.h - header - 6 - titleH;
  return <div data-component="WorldMapPage" style={{position: 'relative', width: '100%', height: '100%'}}>
    <BrowserChrome e={{...e, page: 'worldMap', pageBlank: false}} frame={frame} source={original} siblings={[]} />
    <div style={{position: 'absolute', left: 3, top: 3 + header, width: mapW, height: titleH + mapH, fontFamily: FONT}}>
      {titleH > 0 && <div data-map-page-title style={{height: titleH, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 28px', boxSizing: 'border-box', background: P.bg, borderBottom: `1px solid ${P.muted}55`}}>
        <div style={{fontSize: 40, fontWeight: 800, color: tok(e.pageTitleColor, P.text), whiteSpace: 'nowrap'}}>{e.pageTitle}</div>
        <div style={{display: 'flex', gap: 12}}>{(e.badges ?? []).map((b: string) => <div key={b} data-badge={b} style={{fontSize: 28, fontWeight: 700, padding: '4px 14px', borderRadius: 8, background: '#7C2D12', color: '#FDE68A', whiteSpace: 'nowrap'}}>{b}</div>)}</div>
      </div>}
      <WorldMapView props={e as WorldMapProps} frame={frame} width={mapW} height={mapH} uid={e.id} />
      {!titleH && (e.badges ?? []).length > 0 && <div style={{position: 'absolute', right: 20, top: 16, display: 'flex', gap: 12}}>{e.badges.map((b: string) => <div key={b} data-badge={b} style={{fontSize: 28, fontWeight: 700, padding: '4px 14px', borderRadius: 8, background: '#7C2D12', color: '#FDE68A'}}>{b}</div>)}</div>}
    </div>
  </div>;
};
