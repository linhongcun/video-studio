// v2 完整版：由 ../storyboard.json 驱动的通用渲染器（元素/动画/字幕/配音）。
// 复用第一期（速览版）的浏览器、地址栏、服务器机柜、信封、响应包、文件夹、齿轮；新增步骤条、URL 切分、HSTS 盾牌、缓存抽屉、
// DNS 树、握手时序图、CDN/负载均衡/反向代理、状态码翻牌、渲染流水线、<script> 方块等。
import React from 'react';
import {ChannelBranding} from '../../../_shared/branding/ChannelBranding';
import {AbsoluteFill, Audio, Easing, Sequence, interpolate, interpolateColors, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import sb from '../../storyboard.json';
import timing from './timing.json';

const P = {bg: '#0B1020', panel: '#111827', panel2: '#1F2937', primary: '#22D3EE', secondary: '#3B82F6', text: '#E5E7EB', text2: '#9CA3AF', muted: '#6B7280', success: '#22C55E', accent: '#F59E0B', danger: '#EF4444'};
const FONT = '"Noto Sans CJK SC","Noto Sans SC",sans-serif';
const MONO = '"DejaVu Sans Mono","Noto Sans Mono CJK SC",monospace';

// 制作侧覆盖（记录在 README）：connect-2 的 quic 与 tls13note 同在右下角重叠 → quic 移到左下
const OVERRIDES: Record<string, Record<string, any>> = {
  'connect-2:quic': {x: 120},
  // 导演验收修订：⇄ 改为 =，并补「一致 → 304」
  'response-2:etag': {text: 'If-None-Match: "v1" = ETag: "v1"  一致 → 304'},
};
// 这些动画按导演要求固定在镜头原始帧，不随配音缩放
const PINNED: Record<string, boolean> = {}; // v0.5.0：+44% 配音后所有动画等比压缩，tls13note 不再固定在 200 帧
// 动画覆盖（帧为原分镜帧，仍随配音缩放）：dns-2 的解析结果原定 190 帧才出现、只停留约 10 帧就随转场淡出 → 提前到 ask2 到达后
const ANIM_OVERRIDES: Record<string, any[]> = {
  'dns-2': [
    {elementId: 'ip', property: 'opacity', keyframes: [{frame: 150, value: 0}, {frame: 162, value: 1}], easing: 'easeOut'},
    {elementId: 'ipNote', property: 'opacity', keyframes: [{frame: 158, value: 0}, {frame: 170, value: 1}], easing: 'easeOut'},
  ],
  // server-2：信封到达源站后淡出，避免盖住机柜
  'server-2': [{elementId: 'packet', property: 'opacity', keyframes: [{frame: 140, value: 1}, {frame: 152, value: 0}], easing: 'easeOut'}],
};

const shots: any[] = (sb as any).scenes.flatMap((s: any) => s.shots.map((sh: any) => ({...sh, sceneId: s.id})));
let acc = 0;
const plan = shots.map((sh) => {
  const t = (timing as any)[sh.id];
  const p = {sh, from: acc, dur: t.duration, audioFrames: t.audioFrames, scale: t.duration / sh.durationInFrames};
  acc += t.duration;
  return p;
});
export const totalFrames = acc;

const SFX: Record<string, {f: number; src: string; v: number}[]> = {
  'intro-1': [{f: 50, src: 'click.wav', v: 0.18}],
  'url-1': [{f: 32, src: 'click.wav', v: 0.12}, {f: 62, src: 'click.wav', v: 0.12}],
  'cache-1': [{f: 213, src: 'ding.wav', v: 0.08}],
  'connect-1': [{f: 30, src: 'whoosh.wav', v: 0.06}],
  'connect-2': [{f: 140, src: 'ding.wav', v: 0.07}],
  'request-2': [{f: 382, src: 'whoosh.wav', v: 0.08}],
  'server-1': [{f: 30, src: 'whoosh.wav', v: 0.08}],
  'server-2': [{f: 20, src: 'whoosh.wav', v: 0.08}],
  'response-1': [{f: 10, src: 'click.wav', v: 0.12}],
  'response-2': [{f: 20, src: 'ding.wav', v: 0.07}],
  'recap-5': [{f: 130, src: 'ding.wav', v: 0.1}],
};

const ease = (n: string) => (n === 'linear' ? Easing.linear : n === 'easeInOut' ? Easing.inOut(Easing.cubic) : n === 'easeIn' ? Easing.in(Easing.cubic) : Easing.out(Easing.cubic));

function animValue(anims: any[], id: string, prop: string, frame: number, fps: number, def: any) {
  const list = anims.filter((x) => x.elementId === id && x.property === prop);
  if (!list.length) return def;
  const k = list.flatMap((a) => a.keyframes.map((kf: any) => ({...kf, easing: a.easing}))).sort((a: any, b: any) => a.frame - b.frame);
  if (typeof k[0].value === 'string') {
    if (frame <= k[0].frame) return k[0].value;
    for (let i = 0; i < k.length - 1; i++)
      if (frame <= k[i + 1].frame) return interpolateColors(frame, [k[i].frame, k[i + 1].frame], [k[i].value, k[i + 1].value]);
    return k[k.length - 1].value;
  }
  if (frame <= k[0].frame) return k[0].value;
  for (let i = 0; i < k.length - 1; i++) {
    const a = k[i], b = k[i + 1];
    if (frame <= b.frame) {
      if (b.easing === 'spring') {
        const s = spring({frame: frame - a.frame, fps, config: {damping: 12, stiffness: 140}, durationInFrames: Math.max(8, b.frame - a.frame + 10)});
        return a.value + (b.value - a.value) * s;
      }
      return interpolate(frame, [a.frame, b.frame], [a.value, b.value], {easing: ease(b.easing)});
    }
  }
  return k[k.length - 1].value;
}

const clean = (s?: string) => (s ?? '').replace(/（(新|第一期)）/g, '');

// —— 复用第一期 ——
const ServerRack: React.FC<{color?: string}> = ({color = P.secondary}) => (
  <div style={{width: '100%', height: '100%', background: P.panel, border: `4px solid ${color}`, borderRadius: 18, padding: 24, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 18}}>
    {[0, 1, 2, 3].map((i) => (
      <div key={i} style={{flex: 1, background: P.panel2, borderRadius: 8, display: 'flex', alignItems: 'center', padding: '0 20px', gap: 12}}>
        <div style={{width: 16, height: 16, borderRadius: 8, background: P.success, boxShadow: `0 0 10px ${P.success}`, opacity: 0.8}} />
        <div style={{flex: 1}} />
        {[0, 1, 2].map((j) => <div key={j} style={{width: 22, height: 6, background: '#374151', borderRadius: 3}} />)}
      </div>
    ))}
  </div>
);
const Gear: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="-50 -50 100 100" width="100%" height="100%">
    {Array.from({length: 8}).map((_, i) => <rect key={i} x={-7} y={-46} width={14} height={20} rx={3} fill={color} transform={`rotate(${i * 45})`} />)}
    <circle r={30} fill={color} /><circle r={12} fill={P.bg} />
  </svg>
);
const Folder: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 200 180" width="100%" height="100%">
    <path d="M10 40 h60 l15 15 h105 v115 h-180z" fill={color} opacity={0.9} />
    <rect x={60} y={10} width={80} height={100} rx={6} fill="#E5E7EB" />
  </svg>
);
const Envelope: React.FC<{color: string; big?: boolean}> = ({color, big}) => (
  <svg viewBox="0 0 200 140" width="100%" height="100%" preserveAspectRatio="none">
    <rect x={3} y={3} width={194} height={134} rx={10} fill={big ? 'rgba(59,130,246,0.12)' : color} stroke={big ? color : '#93C5FD'} strokeWidth={big ? 1.5 : 4} vectorEffect="non-scaling-stroke" />
    <path d="M6 10 L100 78 L194 10" fill="none" stroke={big ? 'rgba(147,197,253,0.35)' : '#DBEAFE'} strokeWidth={big ? 3 : 5} vectorEffect="non-scaling-stroke" />
  </svg>
);
const RespBox: React.FC<{color: string}> = ({color}) => (
  <div style={{width: '100%', height: '100%', borderRadius: 16, background: 'rgba(34,197,94,0.12)', border: `4px solid ${color}`, boxSizing: 'border-box', boxShadow: `0 0 40px ${color}55`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
    <span style={{writingMode: 'vertical-rl', fontFamily: FONT, fontSize: 30, color, letterSpacing: 6, fontWeight: 700}}>响应</span>
  </div>
);

// —— 新组件 ——
const Shield: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 100 110" width="100%" height="100%">
    <path d="M50 4 L92 20 V52 C92 80 72 98 50 106 C28 98 8 80 8 52 V20 Z" fill={`${color}22`} stroke={color} strokeWidth={5} />
    <path d="M30 56 L45 71 L72 40" fill="none" stroke={color} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" />
    <text x={50} y={96} textAnchor="middle" fontFamily={MONO} fontSize={13} fontWeight="bold" fill={color}>HSTS</text>
  </svg>
);
const Drawer: React.FC<{color: string}> = ({color}) => (
  <div style={{width: '100%', height: '100%', display: 'flex', flexDirection: 'column', gap: 10, padding: 14, boxSizing: 'border-box', background: P.panel, border: `4px solid ${color}`, borderRadius: 16}}>
    {[0, 1].map((i) => (
      <div key={i} style={{flex: 1, border: `3px solid ${color}88`, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{width: 70, height: 12, borderRadius: 6, background: color}} />
      </div>
    ))}
    <div style={{textAlign: 'center', fontFamily: FONT, fontSize: 28, color: P.text2}}>本地缓存</div>
  </div>
);
const CacheFile: React.FC<{e: any; frame: number}> = ({e, frame}) => {
  const left = Math.max(0, 3600 - Math.floor(frame * 2));
  return (
    <div style={{width: 'max-content', minWidth: '100%', height: '100%', background: '#E5E7EB', borderRadius: 10, boxSizing: 'border-box', padding: '14px 18px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', boxShadow: '0 8px 24px rgba(0,0,0,.4)'}}>
      <div style={{fontFamily: MONO, fontSize: 28, fontWeight: 700, color: P.bg}}>{clean(e.label)}</div>
      <div style={{fontFamily: MONO, fontSize: 28, color: '#047857', whiteSpace: 'nowrap'}}>⏱ max-age {left}s</div>
    </div>
  );
};
const Check: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 100 100" width="100%" height="100%"><circle cx={50} cy={50} r={44} fill={color} /><path d="M28 52 L44 68 L73 36" fill="none" stroke={P.bg} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" /></svg>
);
const Lock: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 100 100" width="100%" height="100%"><path d="M30 44 V30 a20 20 0 0 1 40 0 V44" fill="none" stroke={color} strokeWidth={9} /><rect x={20} y={42} width={60} height={50} rx={9} fill={color} /><circle cx={50} cy={64} r={7} fill={P.bg} /><rect x={47} y={64} width={6} height={16} fill={P.bg} /></svg>
);
const Cdn: React.FC<{color: string}> = ({color}) => (
  <div style={{width: '100%', height: '100%', position: 'relative'}}>
    <svg viewBox="0 0 320 200" width="100%" height="100%">
      <path d="M80 160 a50 50 0 0 1 8 -99 a70 70 0 0 1 132 -10 a55 55 0 0 1 20 109 z" fill={`${color}1f`} stroke={color} strokeWidth={5} />
      {[[120, 110], [170, 90], [215, 120]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={9} fill={color} />)}
      <path d="M120 110 L170 90 L215 120" stroke={color} strokeWidth={3} fill="none" />
    </svg>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 4, textAlign: 'center', fontFamily: FONT, fontSize: 28, fontWeight: 700, color}}>CDN 边缘节点</div>
  </div>
);

const ARROW_TARGET: Record<string, string> = {ask0: 'root', ask1: 'tld', ask2: 'auth'};

const Arrow: React.FC<{e: any; progress: number; endY?: number; target?: any}> = ({e, progress, endY, target}) => {
  const color = e.color;
  if (e.curve !== undefined) {
    // 304 → 缓存抽屉的回折弧线
    const x1 = e.x, y1 = e.y, x2 = e.x - 140, y2 = e.y + e.h;
    const cx = x1 + 40, cy = y2 + 10;
    const d = `M${x1} ${y1} Q${cx} ${cy} ${x2} ${y2}`;
    return (
      <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1920} height={1080}>
        <path d={d} fill="none" stroke={color} strokeWidth={5} strokeDasharray="1000" strokeDashoffset={1000 * (1 - progress)} pathLength={1000} />
        {progress > 0.95 && <polygon points={`${x2},${y2} ${x2 + 18},${y2 - 14} ${x2 + 20},${y2 + 8}`} fill={color} />}
        <text x={x1 + 30} y={y1 + e.h / 2 + 10} fill={color} fontFamily={FONT} fontSize={28} opacity={progress}>{e.label}</text>
      </svg>
    );
  }
  let x1: number, y1: number, x2: number, y2: number;
  if (e.direction === 'r' || e.direction === 'l') {
    const yy = e.y + e.h - 10;
    [x1, x2] = e.direction === 'r' ? [e.x, e.x + e.w] : [e.x + e.w, e.x];
    y1 = y2 = yy;
  } else {
    x1 = e.x; y1 = e.y; x2 = target ? target.x : e.x + e.w; y2 = endY ?? e.y + e.h;
    if (target) y2 = endY ?? target.y + target.h / 2;
  }
  const xe = x1 + (x2 - x1) * progress, ye = y1 + (y2 - y1) * progress;
  const ang = Math.atan2(y2 - y1, x2 - x1);
  const hl = 18;
  const lab = e.label;
  const small = e.h <= 30;
  return (
    <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1920} height={1080}>
      <line x1={x1} y1={y1} x2={xe} y2={ye} stroke={color} strokeWidth={small ? 3 : 5} strokeLinecap="round" />
      {progress > 0.02 && (
        <polygon points={`${xe},${ye} ${xe - hl * Math.cos(ang - 0.45)},${ye - hl * Math.sin(ang - 0.45)} ${xe - hl * Math.cos(ang + 0.45)},${ye - hl * Math.sin(ang + 0.45)}`} fill={color} />
      )}
      {lab && (e.direction === 'r' || e.direction === 'l') && (
        <text x={(x1 + x2) / 2} y={y1 - (small ? 6 : 12)} textAnchor="middle" fill={color} fontFamily={FONT} fontSize={small ? 20 : 30} fontWeight={600} opacity={Math.min(1, progress * 2)}>{lab}</text>
      )}
      {lab && !(e.direction === 'r' || e.direction === 'l') && (
        <text x={x1 + (x2 - x1) * 0.45} y={y1 + (y2 - y1) * 0.45 - 14} textAnchor="middle" fill={color} fontFamily={FONT} fontSize={28} fontWeight={600}>{lab}</text>
      )}
    </svg>
  );
};

const Element: React.FC<{e: any; all: any[]; anims: any[]; frame: number; fps: number}> = ({e, all, anims, frame, fps}) => {
  const v = (p: string, d: any) => animValue(anims, e.id, p, frame, fps, d);
  const opacity = v('opacity', 1);
  const scale = v('scale', 1);
  const rotate = v('rotate', 0);
  const rotY = v('rotateY', 0);
  const x = v('x', e.x), y = v('y', e.y);
  const stroke = v('strokeColor', e.stroke);
  const fill = v('fillColor', e.color);
  if (opacity <= 0.001) return null;
  if (e.type === 'arrow') {
    const tgt = ARROW_TARGET[e.id] ? all.find((o) => o.id === ARROW_TARGET[e.id]) : undefined;
    const endY = anims.some((a) => a.elementId === e.id && a.property === 'y') ? v('y', e.y) : undefined;
    const prog = anims.some((a) => a.elementId === e.id && a.property === 'drawProgress') ? v('drawProgress', 1)
      : endY !== undefined ? Math.min(1, (frame - (anims.find((a) => a.elementId === e.id && a.property === 'y').keyframes[0].frame)) / 15) : 1;
    return <div style={{position: 'absolute', inset: 0, opacity}}><Arrow e={e} progress={Math.max(0, prog)} endY={endY} target={tgt} /></div>;
  }
  if (e.type === 'line')
    return <div style={{position: 'absolute', left: x - 2, top: y, width: Math.max(4, e.w), height: Math.max(4, e.h), background: e.color, opacity: opacity * 0.9, borderRadius: 2}} />;
  const base: React.CSSProperties = {position: 'absolute', left: x, top: y, width: e.w, height: e.h, opacity, transform: `perspective(900px) scale(${scale}) rotate(${e.id === 'gear' ? 0 : rotate}deg) rotateY(${rotY}deg)`};
  if (e.type === 'rect') {
    const isBrowser = (e.label ?? '').startsWith('浏览器窗口');
    const label = isBrowser ? '' : clean(e.label);
    const lines = label.split('\n');
    const fs = e.fontSize ?? 32;
    const solid = fill && fill !== P.panel && !e.stroke;
    return (
      <div style={{...base, background: fill, border: stroke ? `4px solid ${stroke}` : undefined, borderRadius: e.radius ?? 8, boxSizing: 'border-box',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 2, boxShadow: stroke && stroke !== P.muted ? `0 0 24px ${stroke}33` : undefined}}>
        {isBrowser && (
          <>
            <div style={{position: 'absolute', top: 14, left: 18, display: 'flex', gap: 10}}>
              {['#EF4444', '#F59E0B', '#22C55E'].map((c) => <div key={c} style={{width: 14, height: 14, borderRadius: 7, background: c, opacity: 0.8}} />)}
            </div>
            <div style={{position: 'absolute', bottom: -44, width: '100%', textAlign: 'center', color: P.text2, fontFamily: FONT, fontSize: 28}}>浏览器</div>
          </>
        )}
        {lines.map((l, i) => (
          <span key={i} style={{fontFamily: e.font === 'monospace' ? MONO : FONT, color: solid ? '#fff' : (lines.length > 1 && i === 0 ? stroke ?? P.text : P.text),
            fontSize: lines.length > 1 && i === 0 ? fs : lines.length > 1 ? Math.round(fs * (fs > 40 ? 0.5 : 0.85)) : fs, fontWeight: i === 0 ? 700 : 500, lineHeight: 1.25, whiteSpace: 'pre'}}>{l}</span>
        ))}
      </div>
    );
  }
  if (e.type === 'icon') {
    const label = clean(e.label);
    let inner: React.ReactNode = null, caption: string | null = null;
    if (e.id === 'hsts') inner = <Shield color={e.color} />;
    else if (e.id === 'drawer') inner = <Drawer color={e.color} />;
    else if (e.id === 'cacheFile') inner = <CacheFile e={e} frame={frame} />;
    else if (e.id === 'check') inner = <Check color={e.color} />;
    else if (e.id === 'lock') inner = <Lock color={e.color} />;
    else if (e.id === 'cdn') inner = <Cdn color={e.color} />;
    else if (e.id === 'server') { inner = <ServerRack color={e.color} />; caption = label.includes('源站') ? '源站服务器' : '服务器'; }
    else if (e.id === 'folder') { inner = <Folder color={e.color} />; caption = label; }
    else if (e.id === 'gear') { inner = <Gear color={e.color} />; caption = label; }
    const capSmall = e.h < 100;
    return (
      <div style={{...base}}>
        <div style={{width: '100%', height: '100%', transform: e.id === 'gear' ? `rotate(${rotate}deg)` : undefined}}>{inner}</div>
        {caption && <div style={{position: 'absolute', top: e.h + (capSmall ? 2 : 4), left: -40, right: -40, textAlign: 'center', color: P.text2, fontFamily: FONT, fontSize: 28}}>{caption}</div>}
      </div>
    );
  }
  if (e.type === 'packet') {
    const resp = e.id === 'respPacket';
    return <div style={base}>{resp ? <RespBox color={e.color} /> : <Envelope color={e.color} big={e.w > 300} />}</div>;
  }
  if (e.type === 'text') {
    let text: string = e.text;
    if (anims.some((a) => a.elementId === e.id && a.property === 'charsVisible')) text = text.slice(0, Math.round(v('charsVisible', text.length)));
    const pill = !!e.stroke;
    return (
      <div style={{...base, color: e.color, fontSize: e.fontSize, fontFamily: e.font === 'monospace' ? MONO : FONT, fontWeight: e.fontSize >= 40 ? 800 : 600,
        textAlign: e.align ?? 'left', lineHeight: `${e.h - (pill ? 8 : 0)}px`, whiteSpace: 'pre', border: pill ? `4px solid ${e.stroke}` : undefined, borderRadius: pill ? e.h / 2 : undefined,
        background: pill ? `${e.stroke}1a` : undefined, boxSizing: 'border-box'}}>
        {text}
      </div>
    );
  }
  return null;
};

function subtitleTimes(sh: any, audioFrames: number) {
  const n = (s: string) => s.replace(/[\s，。：？！；、,.:?!;—“”"()（）]/g, '').length || 1;
  const total = sh.subtitles.reduce((a: number, s: any) => a + n(s.text), 0);
  let t = 0;
  return sh.subtitles.map((s: any, i: number) => {
    const from = Math.round((t / total) * audioFrames);
    t += n(s.text);
    const to = i === sh.subtitles.length - 1 ? audioFrames + 8 : Math.round((t / total) * audioFrames) - 1;
    return {text: s.text, from, to};
  });
}

const Shot: React.FC<{p: any; prevType: string}> = ({p, prevType}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {sh, dur, audioFrames, scale} = p;
  // 动画相对帧按配音缩放；PINNED 的保持原帧
  const ov = ANIM_OVERRIDES[sh.id] ?? [];
  const src = [...sh.animations.filter((a: any) => !ov.some((o) => o.elementId === a.elementId && o.property === a.property)), ...ov];
  const anims = src.map((a: any) => PINNED[`${sh.id}:${a.elementId}`] ? a : {...a, keyframes: a.keyframes.map((k: any) => ({...k, frame: Math.round(k.frame * scale)}))});
  const elements = sh.elements.filter((e: any) => e.role !== 'subtitle').map((e: any) => ({...e, ...(OVERRIDES[`${sh.id}:${e.id}`] ?? {})}));
  const tr = sh.transition ?? {type: 'none', durationInFrames: 0};
  const td = tr.type === 'fade' ? tr.durationInFrames : 0;
  const out = td ? interpolate(frame, [dur - td, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  const inn = prevType === 'fade' ? interpolate(frame, [0, 8], [0, 1], {extrapolateRight: 'clamp'}) : 1;
  const subs = subtitleTimes(sh, audioFrames);
  const cur = subs.find((s: any) => frame >= s.from && frame <= s.to);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{opacity: out * inn}}>
        {elements.map((e: any) => <Element key={e.id} e={e} all={elements} anims={anims} frame={frame} fps={fps} />)}
      </AbsoluteFill>
      {cur && (
        <div style={{position: 'absolute', left: 160, width: 1600, top: 900, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <span style={{fontFamily: FONT, fontSize: 42, fontWeight: 600, color: P.text, background: 'rgba(0,0,0,0.55)', padding: '8px 26px', borderRadius: 10, whiteSpace: 'nowrap'}}>{cur.text}</span>
        </div>
      )}
      <Audio src={staticFile(`audio/${sh.id}.wav`)} />
      {(SFX[sh.id] ?? []).map((s, i) => (
        <Sequence key={i} from={Math.round(s.f * scale)} layout="none"><Audio src={staticFile(`sfx/${s.src}`)} volume={s.v} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};

const Grid = () => <AbsoluteFill style={{backgroundImage: 'radial-gradient(#1E293B 1.5px, transparent 1.5px)', backgroundSize: '48px 48px', opacity: 0.6}} />;

export const Main: React.FC = () => (
  <AbsoluteFill style={{background: P.bg}}>
    <Grid />
    {plan.map((p, i) => (
      <Sequence key={p.sh.id} from={p.from} durationInFrames={p.dur} name={p.sh.id}>
        <Shot p={p} prevType={i ? plan[i - 1].sh.transition?.type : 'none'} />
      </Sequence>
    ))}
    <ChannelBranding mainFrames={totalFrames} />
  </AbsoluteFill>
);
