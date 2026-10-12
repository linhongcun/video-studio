import React from 'react';
import {AbsoluteFill, Audio, Easing, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import sb from './storyboard.json';
import timing from './timing.json';

const P = sb.meta.palette;
const FONT = '"Noto Sans CJK SC","Noto Sans SC",sans-serif';
const MONO = '"DejaVu Sans Mono",monospace';
const shots: any[] = sb.scenes.flatMap((s: any) => s.shots);
let acc = 0;
const plan = shots.map((sh) => {
  const t = (timing as any)[sh.id];
  const p = {sh, from: acc, dur: t.duration, audioFrames: t.audioFrames};
  acc += t.duration;
  return p;
});
export const totalFrames = acc;

// 轻音效：按镜头相对帧
const SFX: Record<string, {f: number; src: string; v: number}[]> = {
  's1-1': [{f: 50, src: 'click.wav', v: 0.25}],
  's2-2': [{f: 15, src: 'whoosh.wav', v: 0.12}],
  's3-1': [{f: 10, src: 'click.wav', v: 0.15}],
  's4-1': [{f: 15, src: 'ding.wav', v: 0.12}],
  's4-2': [{f: 30, src: 'whoosh.wav', v: 0.12}],
  's5-2': [{f: 40, src: 'ding.wav', v: 0.1}],
};

const ease = (name: string) =>
  name === 'linear' ? Easing.linear : name === 'easeInOut' ? Easing.inOut(Easing.cubic) : Easing.out(Easing.cubic);

function animValue(anims: any[], id: string, prop: string, frame: number, fps: number, def: number) {
  const a = anims.find((x) => x.elementId === id && x.property === prop);
  if (!a) return def;
  const k = a.keyframes;
  if (a.easing === 'spring') {
    // 首段用 spring 过冲，其余线性插值
    const f0 = k[0].frame;
    if (frame <= f0) return k[0].value;
    const last = k[k.length - 1];
    const s = spring({frame: frame - f0, fps, config: {damping: 11, stiffness: 140}});
    return k[0].value + (last.value - k[0].value) * s;
  }
  return interpolate(frame, k.map((x: any) => x.frame), k.map((x: any) => x.value), {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease(a.easing),
  });
}

const ServerRack: React.FC<{e: any}> = ({e}) => (
  <div style={{width: '100%', height: '100%', background: e.color, border: `4px solid ${e.stroke}`, borderRadius: 18, padding: 28, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 24}}>
    {[0, 1, 2, 3].map((i) => (
      <div key={i} style={{flex: 1, background: '#1F2937', borderRadius: 8, display: 'flex', alignItems: 'center', paddingLeft: 80, gap: 14}}>
        {[0, 1, 2, 3, 4].map((j) => <div key={j} style={{width: 120 / 5, height: 6, background: '#374151', borderRadius: 3}} />)}
      </div>
    ))}
  </div>
);

const Icon: React.FC<{e: any}> = ({e}) => {
  if (e.icon === 'server-rack') return <ServerRack e={e} />;
  if (e.icon === 'gear')
    return (
      <svg viewBox="-50 -50 100 100" width="100%" height="100%">
        {Array.from({length: 8}).map((_, i) => (
          <rect key={i} x={-7} y={-46} width={14} height={20} rx={3} fill={e.color} transform={`rotate(${i * 45})`} />
        ))}
        <circle r={30} fill={e.color} />
        <circle r={12} fill={P.bg} />
      </svg>
    );
  if (e.icon === 'folder-html')
    return (
      <svg viewBox="0 0 200 180" width="100%" height="100%">
        <path d="M10 40 h60 l15 15 h105 v115 h-180z" fill={e.color} opacity={0.85} />
        <rect x={60} y={10} width={80} height={100} rx={6} fill="#E5E7EB" />
        <text x={100} y={70} textAnchor="middle" fontSize={22} fontFamily={MONO} fill="#0B1020" fontWeight="bold">HTML</text>
      </svg>
    );
  return null;
};

const Packet: React.FC<{e: any}> = ({e}) =>
  e.shape === 'envelope' ? (
    <svg viewBox="0 0 200 140" width="100%" height="100%" preserveAspectRatio="none">
      <rect x={3} y={3} width={194} height={134} rx={12} fill={e.color} stroke="#93C5FD" strokeWidth={4} />
      <path d="M6 10 L100 78 L194 10" fill="none" stroke="#DBEAFE" strokeWidth={5} />
    </svg>
  ) : (
    <div style={{width: '100%', height: '100%', borderRadius: 16, background: 'rgba(34,211,238,0.12)', border: `4px solid ${e.color}`, boxSizing: 'border-box', boxShadow: `0 0 40px ${e.color}55`}} />
  );

const Arrow: React.FC<{e: any; progress: number}> = ({e, progress}) => {
  const left = e.direction === 'left';
  const w = e.width * progress;
  const h = Math.max(e.height, 4);
  return (
    <svg width={e.width + 40} height={40} style={{position: 'absolute', left: e.x - 20, top: e.y - 20, overflow: 'visible'}}>
      <line x1={left ? e.width + 20 : 20} x2={left ? e.width + 20 - w : 20 + w} y1={20} y2={20} stroke={e.color} strokeWidth={h} strokeDasharray={e.dashed ? '18 14' : undefined} strokeLinecap="round" />
      {progress > 0.02 && (
        <polygon points={left ? `${e.width + 20 - w},20 ${e.width + 40 - w},6 ${e.width + 40 - w},34` : `${20 + w},20 ${w},6 ${w},34`} fill={e.color} />
      )}
    </svg>
  );
};

const Element: React.FC<{e: any; anims: any[]; frame: number; fps: number}> = ({e, anims, frame, fps}) => {
  const v = (p: string, d: number) => animValue(anims, e.id, p, frame, fps, d);
  const opacity = v('opacity', e.id === 'enterFlash' ? 0 : 1);
  const scale = v('scale', 1);
  const rotate = v('rotate', 0);
  const x = v('x', e.x);
  const y = v('y', e.y);
  if (e.type === 'arrow') return <div style={{opacity}}><Arrow e={e} progress={v('progress', 1)} /></div>;
  const base: React.CSSProperties = {position: 'absolute', left: x, top: y, width: e.width, height: e.height, opacity, transform: `scale(${scale}) rotate(${rotate}deg)`};
  if (e.type === 'rect') {
    const isBrowser = e.label === '浏览器窗口';
    return (
      <div style={{...base, background: e.color, border: e.stroke ? `4px solid ${e.stroke}` : undefined, borderRadius: e.radius ?? 6, boxSizing: 'border-box',
        boxShadow: e.id.startsWith('led') ? `0 0 16px ${e.color}` : undefined, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'visible'}}>
        {isBrowser && (
          <div style={{position: 'absolute', top: 14, left: 18, display: 'flex', gap: 10}}>
            {['#EF4444', '#F59E0B', '#22C55E'].map((c) => <div key={c} style={{width: 14, height: 14, borderRadius: 7, background: c, opacity: 0.8}} />)}
          </div>
        )}
        {isBrowser && <div style={{position: 'absolute', bottom: -52, width: '100%', textAlign: 'center', color: P.muted, fontFamily: FONT, fontSize: 30}}>浏览器</div>}
        {e.icon === 'image' && (
          <svg viewBox="0 0 100 60" width="60%" height="60%"><polygon points="10,55 40,20 60,42 72,30 92,55" fill={P.primary} opacity={0.6} /><circle cx={75} cy={14} r={7} fill={P.accent} /></svg>
        )}
        {e.text && <span style={{color: e.textColor ?? P.text, fontFamily: FONT, fontSize: e.fontSize ?? 36, fontWeight: 700}}>{e.text}</span>}
      </div>
    );
  }
  if (e.type === 'icon')
    return (
      <div style={base}>
        <Icon e={e} />
        {e.icon === 'server-rack' && <div style={{position: 'absolute', bottom: -52, width: '100%', textAlign: 'center', color: P.muted, fontFamily: FONT, fontSize: 30}}>服务器</div>}
      </div>
    );
  if (e.type === 'packet') return <div style={base}><Packet e={e} /></div>;
  if (e.type === 'code')
    return (
      <pre style={{...base, margin: 0, background: e.color, color: e.textColor, fontFamily: MONO, fontSize: e.fontSize, borderRadius: 8, padding: '10px 16px', boxSizing: 'border-box', whiteSpace: 'pre'}}>{e.text}</pre>
    );
  if (e.type === 'text') {
    let text: string = e.text;
    if (e.typewriter) text = text.slice(0, Math.round(v('charsVisible', text.length)));
    return (
      <div style={{...base, color: e.color, fontSize: e.fontSize, fontFamily: e.font === 'monospace' ? MONO : FONT, fontWeight: e.fontWeight ?? (e.fontSize > 40 ? 800 : 600),
        textAlign: e.align ?? 'left', lineHeight: `${e.height}px`, whiteSpace: 'pre'}}>
        {text}
      </div>
    );
  }
  return null;
};

// 字幕按真实音频时长、按字数比例重新分配
function subtitleTimes(sh: any, audioFrames: number) {
  const n = (s: string) => s.replace(/[\s，。：？！,.:?!—]/g, '').length || 1;
  const total = sh.subtitles.reduce((a: number, s: any) => a + n(s.text), 0);
  let t = 0;
  return sh.subtitles.map((s: any, i: number) => {
    const from = Math.round((t / total) * audioFrames);
    t += n(s.text);
    const to = i === sh.subtitles.length - 1 ? audioFrames + 6 : Math.round((t / total) * audioFrames) - 1;
    return {text: s.text, from, to};
  });
}

const Shot: React.FC<{p: any}> = ({p}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {sh, dur, audioFrames} = p;
  const tr = sh.transition ?? {type: 'none', durationInFrames: 0};
  const td = tr.durationInFrames || 0;
  const out = td ? interpolate(frame, [dur - td, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  const inFade = interpolate(frame, [0, 6], [0, 1], {extrapolateRight: 'clamp'});
  let style: React.CSSProperties = {};
  if (tr.type === 'fade') style = {opacity: 1 - out};
  if (tr.type === 'slide') style = {transform: `translateX(${-out * 1920}px)`};
  if (tr.type === 'wipe') style = {clipPath: `inset(0 0 0 ${out * 100}%)`};
  const subs = subtitleTimes(sh, audioFrames);
  const cur = subs.find((s: any) => frame >= s.from && frame <= s.to);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{...style, opacity: (style.opacity ?? 1) * (p.from === 0 ? 1 : inFade)}}>
        {sh.elements.filter((e: any) => e.role !== 'subtitle').map((e: any) => <Element key={e.id} e={e} anims={sh.animations} frame={frame} fps={fps} />)}
      </AbsoluteFill>
      {cur && (
        <div style={{position: 'absolute', left: 160, width: 1600, top: 930, textAlign: 'center'}}>
          <span style={{fontFamily: FONT, fontSize: 46, fontWeight: 600, color: P.text, background: 'rgba(0,0,0,0.55)', padding: '10px 28px', borderRadius: 10}}>{cur.text}</span>
        </div>
      )}
      <Audio src={staticFile(`audio/${sh.id}.wav`)} />
      {(SFX[sh.id] ?? []).map((s, i) => (
        <Sequence key={i} from={s.f} layout="none"><Audio src={staticFile(`sfx/${s.src}`)} volume={s.v} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};

const Grid = () => (
  <AbsoluteFill style={{backgroundImage: 'radial-gradient(#1E293B 1.5px, transparent 1.5px)', backgroundSize: '48px 48px', opacity: 0.6}} />
);

export const Main: React.FC = () => (
  <AbsoluteFill style={{background: P.bg}}>
    {plan.map((p) => (
      <Sequence key={p.sh.id} from={p.from} durationInFrames={p.dur} name={p.sh.id}>
        <Grid />
        <Shot p={p} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
