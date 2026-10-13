// 「IT小村」专用封面（非截帧）。版式完全由 cover 节点驱动（episodes/<slug>/storyboard.json 的 cover，或 covers/cover-spec.json[slug]，
// 格式见 Miyazaki 的 cover-spec：title.lines / badge / series / watermark / subject / overlay / sizes{16x9,3x4}）。
// 合成：Cover169 1920x1080、Cover43 1440x1080（= 16:9 居中 1440 裁切）、Cover34 1080x1440。坐标 px，左上原点；文字 top = 字体 ascender 线（对齐 PIL anchor 'la'）。
import React from 'react';
import {AbsoluteFill} from 'remotion';

const FONT = '"Source Han Sans SC","Noto Sans CJK SC","Noto Sans SC",sans-serif';
const LH = 1.448; // Noto/Source Han CJK：ascender 1.16 + descender 0.288 → 行框顶 = ascender 线
const PANEL = '#111827';

export type Asset = {svg: string; bbox: [number, number, number, number]}; // bbox = SVG 用户坐标里的可见内容框
export type CoverProps = {spec: any; size: '16x9' | '3x4'; offsetX?: number; assets: Record<string, Asset>; textWidths?: Record<string, number>};

const fit = (a: Asset, w: number, h: number) => { const k = Math.min(w / a.bbox[2], h / a.bbox[3]); return {w: Math.floor(a.bbox[2] * k), h: Math.floor(a.bbox[3] * k), k}; };
const Svg: React.FC<{a: Asset; x: number; y: number; w: number; h: number; rotate?: number}> = ({a, x, y, w, h, rotate}) => {
  const svg = a.svg.replace(/<svg[^>]*>/, (m) => m.replace(/\s(width|height|viewBox|preserveAspectRatio)="[^"]*"/g, '').replace('<svg', `<svg width="${w}" height="${h}" viewBox="${a.bbox.join(' ')}" preserveAspectRatio="none"`));
  return <div style={{position: 'absolute', left: x, top: y, width: w, height: h, transform: rotate ? `rotate(${rotate}deg)` : undefined}} dangerouslySetInnerHTML={{__html: svg}} />;
};
const Text: React.FC<{x: number; y: number; fs: number; color: string; align?: 'left' | 'center' | 'right'; stroke?: string; children: React.ReactNode}> = ({x, y, fs, color, align = 'left', stroke, children}) => (
  <div style={{position: 'absolute', top: y, left: align === 'left' ? x : undefined, right: align === 'right' ? `calc(100% - ${x}px)` : undefined,
    ...(align === 'center' ? {left: x, transform: 'translateX(-50%)'} : {}), fontFamily: FONT, fontWeight: 700, fontSize: fs, lineHeight: LH, color, whiteSpace: 'nowrap',
    ...(stroke ? {WebkitTextStroke: `8px ${stroke}`, paintOrder: 'stroke fill'} : {})}}>{children}</div>
);

function Subject({spec, s, assets, P}: {spec: any; s: any; assets: Record<string, Asset>; P: any}) {
  const subj: any[] = spec.subject ?? [];
  const A = (name: string) => assets[subj.find((x) => x.asset.endsWith(name))?.asset ?? ''];
  const els: React.ReactNode[] = [];
  if (spec.overlay?.type === 'sign') { // 窗口 + 屏内状态牌 + 前景小票（第十一期）
    const win = assets[subj.find((x) => x.role === 'main').asset]; const f = fit(win, s.w, s.h * 0.9);
    const wx = Math.min(s.x + Math.floor((s.w - f.w) / 2) + 60, s.x + s.w - f.w), wy = s.y;
    els.push(<Svg key="win" a={win} x={wx} y={wy} w={f.w} h={f.h} />);
    const k = f.w / win.bbox[2]; const sx0 = wx + Math.floor((120 - win.bbox[0]) * k), sy0 = wy + Math.floor((180 - win.bbox[1]) * k), sw = Math.floor(272 * k), sh = Math.floor(130 * k);
    const fs = Math.floor(sh * 0.55);
    els.push(<div key="sign" style={{position: 'absolute', left: sx0, top: sy0, width: sw + 1, height: sh + 1, boxSizing: 'border-box', border: `8px solid ${P.badgeFill === undefined ? '#F59E0B' : '#F59E0B'}`, borderRadius: Math.floor(16 * k), background: PANEL,
      display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT, fontWeight: 700, fontSize: fs, lineHeight: 1, color: '#FFFFFF'}}>{spec.overlay.text}</div>);
    const front = subj.find((x) => x.role === 'front');
    if (front) { const t = assets[front.asset]; const g = fit(t, s.w * 0.36, s.h * 0.5); const r = 8 * Math.PI / 180;
      const W2 = g.w * Math.cos(r) + g.h * Math.sin(r), H2 = g.w * Math.sin(r) + g.h * Math.cos(r); const tx = s.x, ty = s.y + s.h - g.h - 20;
      els.push(<Svg key="tk" a={t} x={tx + W2 / 2 - g.w / 2} y={ty + H2 / 2 - g.h / 2} w={g.w} h={g.h} rotate={8} />); }
  } else if (subj.some((x) => x.role === 'end')) { // 横杆小票队列 + 队尾（第九期）
    const end = assets[subj.find((x) => x.role === 'end').asset]; const ce = fit(end, s.w * 0.3, s.h * 0.6); const cx = s.x + s.w - ce.w;
    els.push(<Svg key="end" a={end} x={cx} y={s.y + s.h - ce.h} w={ce.w} h={ce.h} />);
    const ry = s.y + 10, rx1 = s.x + s.w - 64;
    els.push(<div key="rail" style={{position: 'absolute', left: s.x, top: ry, width: rx1 - s.x + 1, height: 25, borderRadius: 12, background: '#9CA3AF'}} />);
    els.push(<svg key="arrow" style={{position: 'absolute', left: 0, top: 0}} width="100%" height="100%"><polygon points={`${rx1 + 6},${ry - 24} ${rx1 + 62},${ry + 12} ${rx1 + 6},${ry + 48}`} fill="#22D3EE" /></svg>);
    const main = subj.find((x) => x.role === 'main'); const n = main.count ?? 1; const sw = (cx - 20 - s.x) / n; const a = assets[main.asset];
    for (let j = 0; j < n; j++) { const g = fit(a, sw * 0.86, s.h * 0.8); const x0 = Math.floor(s.x + j * sw + (sw - g.w) / 2);
      els.push(<div key={`h${j}`} style={{position: 'absolute', left: x0 + Math.floor(g.w / 2) - 5, top: ry + 24, width: 11, height: 27, background: '#9CA3AF'}} />);
      els.push(<Svg key={`s${j}`} a={a} x={x0} y={ry + 50} w={g.w} h={g.h} />); }
  } else { const a = assets[subj[0].asset]; const g = fit(a, s.w, s.h);
    els.push(<Svg key="m" a={a} x={s.x + Math.floor((s.w - g.w) / 2)} y={s.y + Math.floor((s.h - g.h) / 2)} w={g.w} h={g.h} />); }
  return <>{els}</>;
}

export const Cover: React.FC<CoverProps> = ({spec, size, offsetX = 0, assets}) => {
  const L = spec.sizes[size]; const P = spec.palette;
  const t = L.title, b = L.badge, r = L.series, w = L.watermark;
  return (
    <AbsoluteFill style={{background: P.bg, overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: -offsetX, top: 0, width: L.width, height: L.height}}>
        <Subject spec={spec} s={L.subject} assets={assets} P={P} />
        {spec.title.lines.map((line: string, i: number) => (
          <Text key={i} x={t.x} y={t.y + i * t.lh} fs={t.fs} color={i ? P.title2 : P.title1} align={t.align === 'center' ? 'center' : 'left'} stroke={P.bg}>{line}</Text>
        ))}
        <div style={{position: 'absolute', left: b.x, top: b.y, width: b.w + 1, height: b.h + 1, borderRadius: b.h / 2, background: P.badgeFill, display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: FONT, fontWeight: 700, fontSize: b.fs, lineHeight: LH, color: P.badgeText}}>{spec.badge.text}</div>
        <Text x={r.x} y={r.y} fs={r.fs} color={P.series}>{spec.series.text}</Text>
        <Text x={w.x} y={w.y} fs={w.fs} color={P.watermark} align="right">{spec.watermark?.text ?? 'IT小村'}</Text>
      </div>
    </AbsoluteFill>
  );
};
