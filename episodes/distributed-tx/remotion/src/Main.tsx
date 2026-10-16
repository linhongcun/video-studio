// 第二十一期 v4：shot.background 整屏底色（每段一种底色）；章节卡为带 label 的 rect。
// 第二十期《两个订单，怎么撞成同一个号了？》：沿用 EP.19 渲染器（camera.pushIn + 单条整轨 voice.wav）。
//   camera.pushIn{fromScale,toScale,startFrame,endFrame,origin,easing}：镜头元素层（不含字幕、水印）在 startFrame..endFrame 内从 fromScale 推到 toScale，origin 为缩放中心。
//   配音改为单条整轨 public/audio/voice.wav（build_voice.py 按分镜停顿插好静音），第 0 帧起播；不再按镜头切音频。
//   实物图不再走 public/assets 的 staticFile，全部用本期 ../assets/*.svg 内联（OBJ_ASSETS 清空）。
// 第十八期《刚改的昵称，怎么又变回去了？》：沿用 EP.17 渲染器，新增（字段名照 storyboard.json；EP.13–17 分镜里都没有这些字段，旧期渲染不变）：
//   dbRole="replica" + replicaOf=<主库 layerGroup> + delayFrames=N：从库图层。若本镜头没有给从库节点单独写动画（未预烘焙），
//     （按整组判断）就按 asset 对上主库同组节点，把主库的全部关键帧和 appear/disappearFrame 整体推后 N 帧，并把 x/y/w/h 按两节点外框比例映射；
//     若分镜已给从库节点写了动画（Miyazaki 的 gen.py 目前就是预烘焙好的），原样使用，不再重复推后。
//     可选 clipTo=<元素 id>：把该节点裁进那个元素（tv-frame 时裁进屏幕内框 64,116,384×238 / 512）。
//   knollDraw="signalLine" + signal{fromXY,toXY,dotStart,dotFrames,dotStopAt,dotKeep}：两端点之间的信号线（dashed=虚线，drawProgress 描出）。
//   knollDraw="signalDot" + signalOf=<信号线 id>：圆点在 dotStart 起 dotFrames 帧内沿线走完；dotStopAt（0–1 比例或 [x,y] 坐标）非空时
//     走到该处停住并 8 帧淡出（信号断了）；dotKeep=false 时到达终点 4 帧淡出。圆点上分镜写的 x/y/opacity 动画被忽略，以 signal 为准。
//   nickname=true 的文字节点：手机昵称框内水平垂直居中，思源黑体（无则回退 Noto Sans CJK SC，同一字形），字号不小于 28px。
//   动画属性新增 w / h（如球飞远变小），只在分镜写了时生效。
// 第十七期《两个人抢同一件货，听谁的？》：沿用 EP.16 渲染器；实物图全部 staticFile 直出；动画属性 rotation 与 rotate 同义（dead-2 时钟旋转）。
// 第十六期《没封箱的包裹，别人看得见吗？》：沿用 EP.15 渲染器；字幕严格按 storyboard 数字 from/to（不按字数重分）；空字幕不画框；水印第 0 帧常显。
// 第九期《双十一下单那么多，为什么不丢单？》新增 arrow.headless（只画线段、不画箭头，用于划掉号单）。
// 第三期《输入网址后，怎么找到服务器？》：沿用第二期 storyboard 驱动渲染器（元素 / 动画 / 字幕 / 配音）。
// 第三期新增：drain（沙漏流沙）、strike（矩形划掉）、arrow.dash（虚线箭头）、PNG 图片（recap-2 第一期画面 ep1Frame）、
//   字幕直接用 storyboard 的 from/to（Miyazaki 已按 MiMo 真实句子起点对齐），箭头标签在开始描绘时才出现（与检查帧一致）。
// 第一期的逐镜头修正表（OVERRIDES / PINNED / ANIM_OVERRIDES / SFX / ARROW_TARGET）已清空；如需按镜头修正，填下方空表并在 README 记录原因。
// image 元素把 ../assets/*.svg 内联渲染（见 sync_assets.mjs），以支持对 SVG 内 <g id> 的局部动画：
//   tamperStrip  0→1  #tamper-strip 从左向右展开（封条贴上）
//   tamperAlarm  0→1  #tamper-strip 变危险色并抖动（封条被破坏）
//   drawCheck    0→1  #check 描线画出，#badge 由暗变亮（逐层验证通过）
//   badgeDanger  0→1  #badge 内亮色转危险色、勾淡出、抖动（校验失败）
//   glowPlaintext 0→1 #plaintext 发出危险色光晕（明文暴露）
// 元素属性 tint="danger"|"#RRGGBB"：把 SVG 里所有亮色填充/描边换成该色并加同色光晕（如第 4 章被调包的假公钥）。
import React from 'react';
import {ChannelBranding} from '../../../_shared/branding/ChannelBranding';
import {AbsoluteFill, Audio, Img, Easing, Sequence, interpolate, interpolateColors, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import sb from '../../storyboard.json';
import timing from './timing.json';
import ASSETS from './assets.gen';

const P: Record<string, string> = {bg: '#0B1020', panel: '#111827', panel2: '#1F2937', primary: '#22D3EE', secondary: '#3B82F6', text: '#E5E7EB', text2: '#9CA3AF', muted: '#6B7280', success: '#22C55E', accent: '#F59E0B', danger: '#F87171',
  ...((sb as any).meta?.palette ?? {})};
const FONT = '"Noto Sans CJK SC","Noto Sans SC",sans-serif';
const NICK_FONT = '"Source Han Sans SC","Source Han Sans CN","思源黑体","Noto Sans CJK SC","Noto Sans SC",sans-serif';
const MONO = '"DejaVu Sans Mono","Noto Sans Mono CJK SC",monospace';

// —— 制作侧逐镜头修正（键 "shotId:elementId"）；第二期目前为空 ——
const OVERRIDES: Record<string, Record<string, any>> = {};
const PINNED: Record<string, boolean> = {}; // 不随配音缩放的动画
const ANIM_OVERRIDES: Record<string, any[]> = {};
const SFX: Record<string, {f: number; src: string; v: number}[]> = {};

const FPS = 30;
const OBJ_ASSETS = new Set<string>();
const shots: any[] = ((sb as any).scenes ?? []).flatMap((s: any) => s.shots.map((sh: any) => ({...sh, sceneId: s.id})));
let acc = 0;
const plan = shots.map((sh) => {
  // 没有配音实测（timing.json 为空）时按分镜原时长排，便于出静帧预览
  const t = (timing as any)[sh.id] ?? {duration: sh.durationInFrames, audioFrames: sh.durationInFrames - 30, noAudio: true};
  const p = {sh, from: acc, dur: t.duration, audioFrames: t.audioFrames, scale: t.duration / sh.durationInFrames, noAudio: !!t.noAudio};
  acc += t.duration;
  return p;
});
export const totalFrames = Math.max(1, acc);

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

// 去掉分镜里给制作看的括注，如“服务器（第一期）”“咖啡店笔记本（复用第一期浏览器窗口）”
const clean = (s?: string) => (s ?? '').replace(/（[^）]*(第一期|复用|新)[^）]*）/g, '');
const color = (c?: string | null) => (c && P[c] ? P[c] : c ?? undefined);

// —— SVG 资产内联 ——
const lum = (hex: string) => {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((x) => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
};
// 给亮色（非底色/面板色）的 fill / stroke 打上 class，并把原色存进 CSS 变量，便于整体换色或渐变到危险色
const svgCache: Record<string, string> = {};
function prepSvg(src: string) {
  if (svgCache[src]) return svgCache[src];
  let s = src.replace(/<svg([^>]*?)\swidth="[^"]*"\s+height="[^"]*"/, '<svg$1 width="100%" height="100%"');
  s = s.replace(/<(rect|circle|path|text|ellipse|polygon|line|polyline)\b([^>]*?)(\/?)>/g, (m, tag, attrs, close) => {
    const cls: string[] = [], vars: string[] = [];
    const f = /\sfill="(#[0-9A-Fa-f]{6})"/.exec(attrs), st = /\sstroke="(#[0-9A-Fa-f]{6})"/.exec(attrs);
    if (f && lum(f[1]) > 0.05) { cls.push('vs-f'); vars.push(`--vs-f:${f[1]}`); }
    if (st && lum(st[1]) > 0.05) { cls.push('vs-s'); vars.push(`--vs-s:${st[1]}`); }
    if (/\sid="check"/.test(attrs)) attrs += ' pathLength="1"';
    return cls.length ? `<${tag}${attrs} class="${cls.join(' ')}" style="${vars.join(';')}"${close}>` : `<${tag}${attrs}${close}>`;
  });
  // 圆形徽章（如 hash-check 的 #badge）里预埋一个 ✕，badgeDanger 时与勾交替
  s = s.replace(/(<g id="badge">[\s\S]*?<circle[^>]*cx="([\d.]+)"[^>]*cy="([\d.]+)"[^>]*r="([\d.]+)"[^>]*\/>)/, (m, all, cx, cy, r) => {
    const [x, y, d] = [+cx, +cy, +r * 0.38];
    return `${all}<path class="vs-x" d="M${x - d} ${y - d} L${x + d} ${y + d} M${x + d} ${y - d} L${x - d} ${y + d}" fill="none" stroke="${P.bg}" stroke-width="${+r * 0.22}" stroke-linecap="round" opacity="0"/>`;
  });
  return (svgCache[src] = s);
}
const ANIM_PROPS_UNUSED = ['tamperStrip', 'tamperAlarm', 'drawCheck', 'badgeDanger', 'glowPlaintext'];

const SvgImage: React.FC<{e: any; scope: string; v: (p: string, d: any) => any; has: (p: string) => boolean; frame: number}> = ({e, scope, v, has, frame}) => {
  const raw = ASSETS[e.asset];
  if (!raw) return <div style={{width: '100%', height: '100%', border: `3px dashed ${P.muted}`, borderRadius: 12, color: P.text2, fontFamily: MONO, fontSize: 20, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{e.asset}</div>;
  let svg = prepSvg(raw);
  const par = e.fit === 'cover' ? 'xMidYMid slice' : e.fit === 'fill' ? 'none' : 'xMidYMid meet';
  svg = svg.replace('<svg', `<svg preserveAspectRatio="${par}" style="overflow:visible"`);
  const S = `[data-vs="${scope}"]`;
  const css: string[] = [];
  const D = P.danger;
  let shake = 0, glow: string | null = null;
  const tint = e.tint ? color(e.tint === 'danger' ? 'danger' : e.tint) : null;
  if (tint) {
    css.push(`${S} .vs-f{fill:${tint}!important} ${S} .vs-s{stroke:${tint}!important}`);
    glow = `drop-shadow(0 0 18px ${tint}88)`;
  }
  if (has('tamperStrip')) {
    const p = v('tamperStrip', 1);
    css.push(`${S} #tamper-strip{transform-box:fill-box;transform-origin:left center;transform:scaleX(${p})}`);
  }
  if (has('tamperAlarm')) {
    const p = v('tamperAlarm', 0);
    css.push(`${S} #tamper-strip .vs-f{fill:color-mix(in srgb,${D} ${p * 100}%,var(--vs-f))}`);
    shake = Math.max(shake, p > 0 && p < 1 ? 1 : 0);
  }
  if (has('drawCheck')) {
    const p = v('drawCheck', 1);
    css.push(`${S} #check{stroke-dasharray:1;stroke-dashoffset:${1 - p}}`, `${S} #badge{opacity:${0.35 + 0.65 * Math.min(1, p * 1.5)}}`);
  }
  if (has('badgeDanger')) {
    const p = v('badgeDanger', 0);
    css.push(`${S} #badge .vs-f{fill:color-mix(in srgb,${D} ${p * 100}%,var(--vs-f))}`, `${S} #badge #check{opacity:${1 - p}}`, `${S} .vs-x{opacity:${p}}`);
    if (p > 0) glow = `drop-shadow(0 0 ${24 * p}px ${D}aa)`;
    shake = Math.max(shake, p > 0 && p < 1 ? 1 : 0);
  }
  if (has('drain')) {
    const p = v('drain', 0);
    css.push(`${S} #sand-top{transform-box:fill-box;transform-origin:center bottom;transform:scaleY(${1 - p})}`,
      `${S} #sand-bottom{transform-box:fill-box;transform-origin:center bottom;transform:scaleY(${0.25 + 0.75 * p})}`,
      `${S} #stream{opacity:${p > 0 && p < 1 ? 1 : 0}}`);
  }
  if (has('glowPlaintext')) {
    const p = v('glowPlaintext', 0);
    const pulse = p >= 1 ? 0.75 + 0.25 * Math.sin(frame / 6) : p;
    css.push(`${S} #plaintext{filter:drop-shadow(0 0 ${14 * pulse}px ${D}) drop-shadow(0 0 ${4 * pulse}px ${D})}`);
  }
  // 抖动：状态切换的那几帧左右晃，切换完成后停住
  const dx = shake ? Math.sin(frame * 2.2) * 8 : 0;
  return (
    <div data-vs={scope} style={{width: '100%', height: '100%', transform: dx ? `translateX(${dx}px)` : undefined, filter: glow ?? undefined}}>
      {css.length > 0 && <style>{css.join('\n')}</style>}
      <div style={{width: '100%', height: '100%'}} dangerouslySetInnerHTML={{__html: svg}} />
    </div>
  );
};

// —— 服务器卡片：与浏览器卡片同一套样式（深色面板、4px 描边、16 圆角、同色外发光），不带窗口圆点（Nolan）——
const ServerCard: React.FC<{color?: string; label?: string; fontSize?: number}> = ({color = P.primary, label = '服务器', fontSize = 36}) => (
  <div style={{width: '100%', height: '100%', background: '#111827', border: `4px solid ${color}`, borderRadius: 16, boxSizing: 'border-box', boxShadow: `0 0 24px ${color}33`,
    position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '28px 28px 24px', gap: 14}}>
    {[0, 1, 2].map((i) => (
      <div key={i} style={{width: '100%', height: 38, background: `${color}1f`, border: `2px solid ${color}66`, borderRadius: 8, boxSizing: 'border-box', display: 'flex', alignItems: 'center', padding: '0 14px', gap: 10}}>
        <div style={{width: 12, height: 12, borderRadius: 6, background: P.success, boxShadow: `0 0 8px ${P.success}`, opacity: 0.85}} />
        <div style={{flex: 1}} />
        {[0, 1, 2].map((j) => <div key={j} style={{width: 20, height: 5, background: `${color}88`, borderRadius: 3}} />)}
      </div>
    ))}
    <div style={{marginTop: 10, color: P.text, fontFamily: FONT, fontSize, fontWeight: 700, lineHeight: 1.2, whiteSpace: 'nowrap'}}>{label}</div>
  </div>
);
// —— 第二期威胁图标（窃听 / 篡改 / 伪装）——
const Eye: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 100 100" width="100%" height="100%"><path d="M6 50 Q50 10 94 50 Q50 90 6 50Z" fill={`${color}22`} stroke={color} strokeWidth={6} strokeLinejoin="round" /><circle cx={50} cy={50} r={16} fill={color} /><circle cx={50} cy={50} r={6} fill={P.bg} /></svg>
);
const Pencil: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 100 100" width="100%" height="100%"><g transform="rotate(45 50 50)"><rect x={38} y={8} width={24} height={64} rx={4} fill={color} /><rect x={38} y={8} width={24} height={12} rx={4} fill={P.text2} /><path d="M38 72 L50 94 L62 72Z" fill="#FCD9B6" /><path d="M46 86 L50 94 L54 86Z" fill={P.bg} /></g></svg>
);
const Mask: React.FC<{color: string}> = ({color}) => (
  <svg viewBox="0 0 100 100" width="100%" height="100%"><path d="M8 34 Q50 22 92 34 Q92 72 62 74 Q50 60 38 74 Q8 72 8 34Z" fill={`${color}22`} stroke={color} strokeWidth={6} strokeLinejoin="round" /><ellipse cx={32} cy={46} rx={10} ry={7} fill={color} /><ellipse cx={68} cy={46} rx={10} ry={7} fill={color} /></svg>
);
const ICONS: Record<string, React.FC<{color: string}>> = {eye: Eye, pencil: Pencil, mask: Mask};

const Arrow: React.FC<{e: any; progress: number}> = ({e, progress}) => {
  const c = color(e.color);
  const yy = e.y + e.h - 10;
  const rev = e.direction === 'l';
  const both = e.direction === 'lr';
  const [x1, x2] = rev ? [e.x + e.w, e.x] : [e.x, e.x + e.w];
  const xe = x1 + (x2 - x1) * progress;
  const small = e.h <= 30;
  const hl = 18;
  const head = (x: number, dir: number) => `${x},${yy} ${x - dir * hl},${yy - 10} ${x - dir * hl},${yy + 10}`;
  const fs = e.fontSize ?? (small ? 20 : 30);
  return (
    <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1920} height={1080}>
      <line x1={x1} y1={yy} x2={xe} y2={yy} stroke={c} strokeWidth={small ? 3 : 5} strokeLinecap="round" strokeDasharray={e.dash ? '18 14' : undefined} />
      {!e.headless && progress > 0.02 && <polygon points={head(xe, rev ? -1 : 1)} fill={c} />}
      {!e.headless && both && progress > 0.98 && <polygon points={head(x1, -1)} fill={c} />}
      {e.label && <text x={(x1 + x2) / 2} y={yy - 14} textAnchor="middle" fill={c} fontFamily={FONT} fontSize={fs} fontWeight={600} opacity={progress > 0 ? 1 : 0}>{e.label}</text>}
    </svg>
  );
};

// —— EP.18 信号线 / 圆点 ——
const SignalLine: React.FC<{e: any; opacity: number; progress: number}> = ({e, opacity, progress}) => {
  const {fromXY: [x1, y1], toXY: [x2, y2]} = e.signal;
  const c = color(e.color) ?? P.primary;
  return (
    <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity}} width={1920} height={1080}>
      <line x1={x1} y1={y1} x2={x1 + (x2 - x1) * progress} y2={y1 + (y2 - y1) * progress} stroke={c} strokeWidth={5} strokeLinecap="round" strokeDasharray={e.dash ? '18 14' : undefined} opacity={0.9} />
    </svg>
  );
};
// dotStopAt：0–1 为沿线比例；[x,y] 为坐标，投影到线上换成比例
function stopFraction(sg: any): number | null {
  const st = sg.dotStopAt;
  if (st == null) return null;
  if (Array.isArray(st)) {
    const [x1, y1] = sg.fromXY, [x2, y2] = sg.toXY, dx = x2 - x1, dy = y2 - y1;
    return Math.max(0, Math.min(1, ((st[0] - x1) * dx + (st[1] - y1) * dy) / (dx * dx + dy * dy || 1)));
  }
  return Math.max(0, Math.min(1, +st));
}
const SignalDot: React.FC<{e: any; frame: number}> = ({e, frame}) => {
  const sg = e._signal;
  if (!sg) return null;
  const [x1, y1] = sg.fromXY, [x2, y2] = sg.toXY;
  const start = sg._dotStart, frames = Math.max(1, sg._dotFrames);
  const stop = stopFraction(sg);
  const end = stop ?? 1;
  const tRaw = (frame - start) / frames;
  const t = Math.max(0, Math.min(end, tRaw));
  const reachF = start + end * frames;
  let op = interpolate(frame, [start, start + 4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (stop != null) op *= interpolate(frame, [reachF, reachF + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  else if (!sg.dotKeep) op *= interpolate(frame, [reachF, reachF + 4], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (op <= 0.001) return null;
  const d = e.w ?? 24, c = color(e.color) ?? P.accent;
  // 断信号：停住后圆点略微放大、变暗，像信号灭掉
  const lost = stop != null && frame > reachF ? Math.min(1, (frame - reachF) / 8) : 0;
  return <div style={{position: 'absolute', left: x1 + (x2 - x1) * t - d / 2, top: y1 + (y2 - y1) * t - d / 2, width: d, height: d, borderRadius: d / 2, background: c, opacity: op,
    transform: `scale(${1 + 0.4 * lost})`, boxShadow: `0 0 ${16 * (1 - lost)}px ${c}`}} />;
};

// —— EP.18 从库：未预烘焙时由主库同组节点推后 delayFrames 生成 ——
const TV_SCREEN = {x: 64, y: 116, w: 384, h: 238, vb: 512};
function expandShot(sh: any, anims: any[]) {
  const els: any[] = sh.elements;
  // 整组判断：从库组里只要有一个节点有自己的动画，就视为分镜已预烘焙，整组原样使用
  const animated = new Set(anims.map((a: any) => a.elementId));
  const bakedGroups = new Set(els.filter((x) => x.dbRole === 'replica' && animated.has(x.id)).map((x) => x.layerGroup));
  const outAnims = [...anims];
  const outEls = els.map((e: any) => {
    let r = e;
    if (e.dbRole === 'replica' && e.replicaOf && e.delayFrames != null && !bakedGroups.has(e.layerGroup)) {
      const siblings = els.filter((x) => x.layerGroup === e.layerGroup);
      const mains = els.filter((x) => x.layerGroup === e.replicaOf && x.dbRole === 'main');
      const idx = siblings.filter((x) => x.asset === e.asset).indexOf(e);
      const m = mains.filter((x) => x.asset === e.asset)[idx];
      if (m) {
        const N = +e.delayFrames, sx = e.w / m.w, sy = e.h / m.h;
        const map: Record<string, (v: number) => number> = {x: (v) => e.x + (v - m.x) * sx, y: (v) => e.y + (v - m.y) * sy, w: (v) => v * sx, h: (v) => v * sy};
        for (const a of anims.filter((a: any) => a.elementId === m.id))
          outAnims.push({...a, elementId: e.id, keyframes: a.keyframes.map((k: any) => ({...k, frame: k.frame + N, value: map[a.property] && typeof k.value === 'number' ? map[a.property](k.value) : k.value}))});
        r = {...e, appearFrame: m.appearFrame == null ? e.appearFrame : m.appearFrame > 0 ? m.appearFrame + N : m.appearFrame, disappearFrame: m.disappearFrame == null ? null : m.disappearFrame + N, _derivedFrom: m.id};
      }
    }
    if (r.knollDraw === 'signalDot') {
      const line = els.find((x) => x.id === r.signalOf);
      if (line?.signal) r = {...r, _signal: line.signal};
    }
    if (r.clipTo) {
      const t = els.find((x) => x.id === r.clipTo);
      if (t) {
        let box = {x: t.x, y: t.y, w: t.w, h: t.h};
        if (/tv-frame/.test(t.asset ?? '')) { const k = Math.min(t.w, t.h) / TV_SCREEN.vb, ox = t.x + (t.w - TV_SCREEN.vb * k) / 2, oy = t.y + (t.h - TV_SCREEN.vb * k) / 2; box = {x: ox + TV_SCREEN.x * k, y: oy + TV_SCREEN.y * k, w: TV_SCREEN.w * k, h: TV_SCREEN.h * k}; }
        r = {...r, _clip: box};
      }
    }
    return r;
  });
  return {elements: outEls, anims: outAnims};
}

const Element: React.FC<{e: any; anims: any[]; frame: number; fps: number; scope: string}> = ({e: e0, anims, frame, fps, scope}) => {
  let e = e0;
  const has = (p: string) => anims.some((a) => a.elementId === e.id && a.property === p);
  const v = (p: string, d: any) => animValue(anims, e.id, p, frame, fps, d);
  const opacity = v('opacity', 1);
  const scale = v('scale', 1);
  const rotate = v('rotate', v('rotation', 0));
  const x = v('x', e.x), y = v('y', e.y);
  if (has('w') || has('h')) e = {...e, w: v('w', e.w), h: v('h', e.h)};
  const stroke = color(v('strokeColor', e.stroke));
  const fill = color(v('fillColor', e.color));
  if (opacity <= 0.001) return null;
  if (e.knollDraw === 'signalLine') return <SignalLine e={e} opacity={opacity} progress={has('drawProgress') ? v('drawProgress', 1) : 1} />;
  if (e.knollDraw === 'signalDot') return <SignalDot e={e} frame={frame} />;
  if (e.type === 'arrow') return <div style={{position: 'absolute', inset: 0, opacity}}><Arrow e={e} progress={Math.max(0, has('drawProgress') ? v('drawProgress', 1) : 1)} /></div>;
  if (e.type === 'line' && e.dash)
    return <div style={{position: 'absolute', left: x, top: y, width: Math.max(4, e.w), height: Math.max(4, e.h), borderTop: e.h <= 4 ? `4px dashed ${fill ?? P.text2}` : undefined, borderLeft: e.h > 4 ? `4px dashed ${fill ?? P.text2}` : undefined, opacity: opacity * 0.9}} />;
  if (e.type === 'line')
    return <div style={{position: 'absolute', left: x - 2, top: y, width: Math.max(4, e.w), height: Math.max(4, e.h), background: fill, opacity: opacity * 0.9, borderRadius: 2}} />;
  const base: React.CSSProperties = {position: 'absolute', left: x, top: y, width: e.w, height: e.h, opacity, transform: `scale(${scale}) rotate(${rotate}deg)`};
  if (e.type === 'image' && e.id === 'ep1Frame')
    return <div style={{...base, border: `2px solid ${color(e.stroke) ?? P.text2}`, boxSizing: 'border-box', overflow: 'hidden', borderRadius: 8}}><Img src={staticFile('img/ep1-connect.png')} style={{width: '100%', height: '100%', objectFit: 'cover'}} /></div>;
  // EP.16 实物图（public/assets 下的透明 SVG）：staticFile 直出；tagText 只是分镜备注，不渲染（标签另有 rect 节点）
  if (e.type === 'image' && OBJ_ASSETS.has(e.asset)) return <div style={base}><Img src={staticFile(e.asset)} style={{width: '100%', height: '100%', objectFit: 'contain'}} /></div>;
  if (e.type === 'image') return <div style={base}><SvgImage e={e} scope={scope} v={v} has={has} frame={frame} /></div>;
  if (e.type === 'rect' && e.id === 'server')
    return <div style={base}><ServerCard color={stroke ?? fill ?? P.primary} label={clean(e.label) || '服务器'} fontSize={e.fontSize ?? 36} /></div>;
  if (e.type === 'rect') {
    const isBrowser = /浏览器窗口/.test(`${e.label ?? ''}${e.note ?? ''}`);
    let label = clean(e.label);
    if (has('charsVisible')) label = label.slice(0, Math.round(v('charsVisible', label.length)));
    const lines = label.split('\n');
    const fs = e.fontSize ?? 36;
    const solid = fill && fill !== P.panel && !e.stroke;
    return (
      <div style={{...base, background: fill, border: stroke ? `4px ${e.dash ? 'dashed' : 'solid'} ${stroke}` : undefined, borderRadius: e.radius ?? 8, boxSizing: 'border-box',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 2, boxShadow: stroke && stroke !== P.muted ? `0 0 24px ${stroke}33` : undefined}}>
        {isBrowser && (
          <>
            <div style={{position: 'absolute', top: 14, left: 18, display: 'flex', gap: 10}}>
              {['#EF4444', '#F59E0B', '#22C55E'].map((c) => <div key={c} style={{width: 14, height: 14, borderRadius: 7, background: c, opacity: 0.8}} />)}
            </div>
            {label && <div style={{position: 'absolute', bottom: -(fs + 18), width: '100%', textAlign: 'center', color: P.text2, fontFamily: FONT, fontSize: fs}}>{label}</div>}
          </>
        )}
        {has('strike') && v('strike', 0) > 0 && (
          <div style={{position: 'absolute', left: '6%', top: '50%', height: 5, width: `${88 * v('strike', 0)}%`, background: P.danger, borderRadius: 3, boxShadow: `0 0 10px ${P.danger}88`}} />
        )}
        {!isBrowser && lines.map((l, i) => (
          <span key={i} style={{fontFamily: e.font === 'monospace' ? MONO : FONT, color: solid ? '#fff' : (lines.length > 1 && i === 0 ? stroke ?? P.text : P.text),
            fontSize: lines.length > 1 && i === 0 ? fs : lines.length > 1 ? Math.round(fs * (fs > 40 ? 0.5 : 0.85)) : fs, fontWeight: i === 0 ? 700 : 500, lineHeight: 1.25, whiteSpace: 'pre'}}>{l}</span>
        ))}
      </div>
    );
  }
  if (e.type === 'icon') {
    if (e.id === 'server') return <div style={base}><ServerCard color={stroke ?? fill ?? P.primary} label={clean(e.label) || '服务器'} fontSize={e.fontSize ?? 36} /></div>;
    const I = ICONS[e.id];
    const caption = null;
    return (
      <div style={base}>
        {I ? <I color={fill ?? P.primary} /> : <div style={{width: '100%', height: '100%', border: `3px dashed ${P.muted}`, borderRadius: 12, color: P.text2, fontFamily: FONT, fontSize: 22, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{clean(e.label)}</div>}
        {caption && <div style={{position: 'absolute', top: e.h + 4, left: -40, right: -40, textAlign: 'center', color: P.text2, fontFamily: FONT, fontSize: 22}}>{caption}</div>}
      </div>
    );
  }
  if (e.type === 'text' && e.nickname) {
    let text: string = e.text;
    if (has('charsVisible')) text = text.slice(0, Math.round(v('charsVisible', text.length)));
    return (
      <div style={{...base, display: 'flex', alignItems: 'center', justifyContent: 'center', color: fill ?? P.text, fontFamily: NICK_FONT, fontSize: Math.max(28, e.fontSize ?? 28), fontWeight: 700, whiteSpace: 'nowrap', lineHeight: 1}}>
        {text}
      </div>
    );
  }
  if (e.type === 'text') {
    let text: string = e.text;
    if (has('charsVisible')) text = text.slice(0, Math.round(v('charsVisible', text.length)));
    const pill = !!e.stroke;
    return (
      <div style={{...base, color: fill, fontSize: e.fontSize, fontFamily: e.font === 'monospace' ? MONO : FONT, fontWeight: e.fontSize >= 40 ? 800 : 600,
        textAlign: e.align ?? 'left', lineHeight: `${e.h - (pill ? 8 : 0)}px`, whiteSpace: 'pre', border: pill ? `4px solid ${stroke}` : undefined, borderRadius: pill ? e.h / 2 : undefined,
        background: pill ? `${stroke}1a` : undefined, boxSizing: 'border-box'}}>
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

const isFade = (t?: string) => t === 'fade' || t === 'crossfade';

const Shot: React.FC<{p: any; prevTr: any}> = ({p, prevTr}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {sh, dur, audioFrames, scale, noAudio} = p;
  const ov = ANIM_OVERRIDES[sh.id] ?? [];
  const src = [...sh.animations.filter((a: any) => !ov.some((o) => o.elementId === a.elementId && o.property === a.property)), ...ov];
  const anims = src.map((a: any) => PINNED[`${sh.id}:${a.elementId}`] ? a : {...a, keyframes: a.keyframes.map((k: any) => ({...k, frame: Math.round(k.frame * scale)}))});
  // EP.16 统一 z 排序：有 z 用 z；没有 z 的节点继承文档顺序里前一个节点的 z（+0.5，同值按原顺序稳定），所以 box 之后的标签仍在 box 之上
  const ex = expandShot({...sh, elements: sh.elements.map((e: any) => e.signal ? {...e, signal: {...e.signal, _dotStart: Math.round((e.signal.dotStart ?? 0) * scale), _dotFrames: Math.round((e.signal.dotFrames ?? 1) * scale)}} : e)}, anims);
  let lastZ = -1;
  const elements = ex.elements.filter((e: any) => e.role !== 'subtitle')
    .map((e: any, i: number) => { const z = typeof e.z === 'number' ? e.z : lastZ + 0.5; if (typeof e.z === 'number') lastZ = e.z; return {...e, _z: z, _i: i, dash: e.dash ?? e.dashed, ...(OVERRIDES[`${sh.id}:${e.id}`] ?? {})}; })
    .filter((e: any) => (e.appearFrame == null || frame >= e.appearFrame) && (e.disappearFrame == null || frame < e.disappearFrame))
    .sort((a: any, b: any) => a._z - b._z || a._i - b._i);
  const tr = sh.transition ?? {type: 'none', durationInFrames: 0};
  const td = isFade(tr.type) ? tr.durationInFrames : 0;
  const out = td ? interpolate(frame, [dur - td, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  const inn = isFade(prevTr?.type) ? interpolate(frame, [0, prevTr.durationInFrames || 8], [0, 1], {extrapolateRight: 'clamp'}) : 1;
  const subs = sh.subtitles?.length && typeof sh.subtitles[0].from === 'number' ? sh.subtitles : subtitleTimes(sh, audioFrames);
  // EP.16：空字幕条目（如开场 0–44 封面大字期间）不画底框
  const cam = sh.camera?.pushIn;
  const camScale = cam ? interpolate(frame, [cam.startFrame * scale, Math.max(cam.startFrame * scale + 1, cam.endFrame * scale)], [cam.fromScale, cam.toScale], {easing: ease(cam.easing ?? 'easeInOut'), extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  const cur = subs.find((s: any) => frame >= s.from && frame <= s.to && (s.text ?? '').trim() !== '');
  return (
    <AbsoluteFill>
      {sh.background ? <AbsoluteFill style={{background: sh.background, opacity: out * inn}} /> : null}
      <AbsoluteFill style={{opacity: out * inn, transform: camScale !== 1 ? `scale(${camScale})` : undefined, transformOrigin: cam ? `${cam.origin[0]}px ${cam.origin[1]}px` : undefined}}>
        {elements.map((e: any) => e._clip
          ? <div key={e.id} style={{position: 'absolute', inset: 0, clipPath: `inset(${e._clip.y}px ${1920 - e._clip.x - e._clip.w}px ${1080 - e._clip.y - e._clip.h}px ${e._clip.x}px)`}}><Element e={e} anims={ex.anims} frame={frame} fps={fps} scope={`${sh.id}-${e.id}`} /></div>
          : <Element key={e.id} e={e} anims={ex.anims} frame={frame} fps={fps} scope={`${sh.id}-${e.id}`} />)}
      </AbsoluteFill>
      {cur && (
        <div style={{position: 'absolute', left: 160, width: 1600, top: 900, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <span style={{fontFamily: FONT, fontSize: 42, fontWeight: 600, color: P.text, background: 'rgba(0,0,0,0.55)', padding: '8px 26px', borderRadius: 10, whiteSpace: 'nowrap'}}>{cur.text}</span>
        </div>
      )}
      {(SFX[sh.id] ?? []).map((s, i) => (
        <Sequence key={i} from={Math.round(s.f * scale)} layout="none"><Audio src={staticFile(`sfx/${s.src}`)} volume={s.v} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};

const Grid = () => <AbsoluteFill style={{backgroundImage: 'radial-gradient(#1E293B 1.5px, transparent 1.5px)', backgroundSize: '48px 48px', opacity: 0.6}} />;

// 供静帧/调试定位：镜头 id → 全局起始帧
export const shotStart: Record<string, number> = Object.fromEntries(plan.map((p) => [p.sh.id, p.from]));

export const Main: React.FC = () => (
  <AbsoluteFill style={{background: P.bg}}>
    <Grid />
    {plan.map((p, i) => (
      <Sequence key={p.sh.id} from={p.from} durationInFrames={p.dur} name={p.sh.id}>
        <Shot p={p} prevTr={i ? plan[i - 1].sh.transition : null} />
      </Sequence>
    ))}
    <Audio src={staticFile('audio/voice.wav')} />
    <ChannelBranding mainFrames={totalFrames} watermarkFadeIn={false} />
  </AbsoluteFill>
);
