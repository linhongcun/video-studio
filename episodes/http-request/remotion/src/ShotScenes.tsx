import React from 'react';
import {Easing, interpolate} from 'remotion';
import {animatedValue, progress} from './animation';
import {Shot, ShotElement, shots} from './storyboard';
import {MONO, P} from './theme';
import {BrowserChrome} from './components/BrowserChrome';
import {StyledPage} from './components/StyledPage';
import {Laptop} from './components/Laptop';
import {FileCard} from './components/FileCard';
import {FileManager} from './components/FileManager';
import {FlyingLabel, arcPoint} from './components/FlyingLabel';
import {KeyCap} from './components/KeyCap';
import {WireframePage} from './components/WireframePage';
import {StepBar} from './components/StepBar';
import {PhoneContacts} from './components/PhoneContacts';
import {CafeScene} from './components/CafeScene';
import {DevToolsNetwork, NetworkRow} from './components/DevToolsNetwork';
import {Arrow, Check, Folder, Gear, ServerRack} from './components/Legacy';

export type SceneProps = {shot: Shot; frame: number};

const element = (shot: Shot, id: string): ShotElement => {
  const found = shot.elements.find((e) => e.id === id);
  if (!found) throw new Error(`Missing storyboard element ${shot.id}/${id}`);
  return found;
};
const value = (shot: Shot, frame: number, id: string, property: string, fallback: number) => Number(animatedValue(shot, id, property, frame, fallback));
const at = (shot: Shot, id: string) => element(shot, id).appearFrame ?? 0;

/** Used both on positioned layers and on named parts inside composite drawings. */
const motion = (shot: Shot, frame: number, id: string): React.CSSProperties => {
  const e = element(shot, id);
  const visible = frame >= (e.appearFrame ?? 0) && (e.disappearFrame === undefined || frame < e.disappearFrame);
  // Item cues replace the group's entrance, avoiding a second fade on item one.
  const perItem = Array.isArray(e.itemAppearFrames);
  return {
    opacity: visible ? perItem ? e.opacity ?? 1 : value(shot, frame, id, 'opacity', e.opacity ?? 1) : 0,
    transform: `scale(${perItem ? 1 : value(shot, frame, id, 'scale', 1)}) rotate(${value(shot, frame, id, 'rotate', 0)}deg) rotateY(${value(shot, frame, id, 'rotateY', 0)}deg)`,
  };
};

const Layer: React.FC<SceneProps & {id: string; style?: React.CSSProperties; children?: React.ReactNode}> = ({shot, frame, id, style, children}) => {
  const e = element(shot, id), m = motion(shot, frame, id);
  return <div data-element={id} data-component={e.component ?? e.type} style={{position: 'absolute', left: value(shot, frame, id, 'x', e.x), top: value(shot, frame, id, 'y', e.y), width: value(shot, frame, id, 'w', e.w), height: value(shot, frame, id, 'h', e.h), zIndex: e.z ?? 2, ...style, opacity: Number(m.opacity) * Number(style?.opacity ?? 1), transform: `${style?.transform ?? ''} ${m.transform}`}}>{children}</div>;
};

/** Named parts embedded in a composite use the same timing as positioned layers. */
const Part: React.FC<SceneProps & {id: string; style?: React.CSSProperties; children?: React.ReactNode}> = ({shot, frame, id, style, children}) => <div data-element={id} data-component={element(shot, id).component} style={{...style, ...motion(shot, frame, id)}}>{children}</div>;

const TextLayer: React.FC<SceneProps & {id: string; style?: React.CSSProperties}> = ({shot, frame, id, style}) => {
  const e = element(shot, id);
  return <Layer shot={shot} frame={frame} id={id} style={{fontSize: e.fontSize, fontWeight: e.fontWeight, color: e.color, whiteSpace: 'pre-line', textAlign: e.align, display: 'flex', alignItems: 'center', justifyContent: e.align === 'center' ? 'center' : 'flex-start', ...style}}>{e.text}</Layer>;
};

export const Spinner: React.FC<{frame: number; color?: string}> = ({frame, color = P.primary}) => <svg width="100%" height="100%" viewBox="0 0 100 100" style={{transform: `rotate(${frame * 10}deg)`}} aria-label="加载中"><circle cx={50} cy={50} r={38} stroke={P.muted} strokeWidth={8} fill="none" /><path d="M50 12a38 38 0 0 1 38 38" fill="none" stroke={color} strokeWidth={8} strokeLinecap="round" /></svg>;
const Logo: React.FC = () => <div style={{width: '100%', height: '100%', background: P.primary, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center'}}><svg width="70%" height="70%" viewBox="0 0 100 60"><circle cx={28} cy={22} r={16} fill={P.accent} /><path d="m15 56 35-44 35 44Z" fill={P.panel} /></svg></div>;
const LogoOnly: React.FC = () => <div style={{position: 'absolute', left: '4%', top: '7%', width: '20%', height: '17%'}}><Logo /></div>;
const Caption: React.FC<{children: React.ReactNode}> = ({children}) => <div style={{textAlign: 'center', fontSize: 32, color: P.text2, marginTop: 18}}>{children}</div>;

const HookScene: React.FC<SceneProps> = ({shot, frame}) => {
  const ctx = {shot, frame};
  return <>
    <Layer {...ctx} id="cover-title" style={{left: 0, top: 0, width: 1920, height: 216, background: P.panel, borderTop: `12px solid ${P.primary}`, boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 28}}>
      <span style={{fontSize: 76, fontWeight: 900}}>浏览器输入网址后</span><span style={{fontSize: 76, fontWeight: 900, color: P.bg, background: P.primary, padding: '8px 24px', borderRadius: 16}}>发生了什么？</span>
    </Layer>
    {['秒开', '一直转圈'].map((label, i) => <div key={label} style={{position: 'absolute', top: 246, left: i ? 1000 : 60, width: 860, color: i ? P.accent : P.success, fontSize: 42, fontWeight: 700, textAlign: 'center'}}>{label}</div>)}
    <Layer {...ctx} id="laptop-left" style={{left: 60, top: 320, height: 548}}><Laptop width={860} height={548} loaded><Part shot={shot} frame={frame} id="page-left" style={{width: '100%', height: '100%'}}><StyledPage /></Part></Laptop></Layer>
    <Layer {...ctx} id="laptop-right" style={{left: 1000, top: 320, height: 548}}><Laptop width={860} height={548} loading /></Layer>
    <Layer {...ctx} id="spinner-right" style={{left: 1370, top: 526}}><Spinner frame={frame} /></Layer>
    <Layer {...ctx} id="flash-left" style={{left: 64, top: 456, width: 852, height: 324, border: `5px solid ${P.success}`, borderRadius: 14, boxSizing: 'border-box', background: `${P.success}${Math.round(12 + 12 * Math.sin(frame / 6)).toString(16).padStart(2, '0')}`}} />
    <Layer {...ctx} id="stuck-right" style={{left: 1004, top: 456, width: 852, height: 324, border: `5px solid ${P.danger}`, borderRadius: 14, boxSizing: 'border-box', boxShadow: `0 0 ${12 + 12 * (1 + Math.sin(frame / 8))}px ${P.danger}55`}} />
  </>;
};

const TypingScene: React.FC<SceneProps> = ({shot, frame}) => {
  const browser = element(shot, 'browser');
  const typedChars = Math.floor(Math.max(0, frame - at(shot, 'typing')) * element(shot, 'typing').charsPerFrame);
  return <>
    <Layer shot={shot} frame={frame} id="browser" style={{transform: `scale(${1 + 0.015 * progress(frame, 0, 50)})`}}>
      <BrowserChrome width={browser.w} height={browser.h} title="新标签页" text={element(shot, 'typing').text} typedChars={typedChars} showCursor addressStyle={motion(shot, frame, 'typing')} addressElementId="typing" loading={frame >= (element(shot, 'keycap').cueOnset?.onsetLocal ?? at(shot, 'keycap'))} />
    </Layer>
    <Layer shot={shot} frame={frame} id="keycap"><KeyCap pressed={frame >= (element(shot, 'keycap').cueOnset?.onsetLocal ?? at(shot, 'keycap')) && frame < (element(shot, 'keycap').cueOnset?.onsetLocal ?? at(shot, 'keycap')) + 12} /></Layer>
    <Layer shot={shot} frame={frame} id="steps-hint" style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 48}}>{[0, 1, 2, 3, 4].map((i) => <div key={i} style={{width: 24, height: 24, borderRadius: 12, background: frame >= at(shot, 'steps-hint') + i * 7 ? P.primary : P.muted}} />)}</Layer>
  </>;
};

const CacheLookScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="browser-ghost"><BrowserChrome width={1600} height={element(shot, 'browser-ghost').h} chromeHeight={110} /></Layer>
  <Layer shot={shot} frame={frame} id="filemgr" style={{transform: `translateY(${(1 - progress(frame, at(shot, 'filemgr'), 20)) * 50}px)`}}><FileManager><></></FileManager></Layer>
  {['file-logo', 'file-css', 'file-old'].map((id) => <Layer key={id} shot={shot} frame={frame} id={id}><FileCard filename={element(shot, id).name} date={element(shot, id).date} /></Layer>)}
</>;

const CacheHitScene: React.FC<SceneProps> = ({shot, frame}) => {
  const file = element(shot, 'file-logo-check');
  const start = at(shot, 'file-logo-check') + 10;
  const p = progress(frame, start, at(shot, 'logo-lit') - start);
  const flight = arcPoint(file.x, file.y, file.flyTo[0], file.flyTo[1], p, 160);
  return <>
    <Layer shot={shot} frame={frame} id="filemgr"><FileManager><></></FileManager></Layer>
    <Layer shot={shot} frame={frame} id="browser"><BrowserChrome width={740} height={580} chromeHeight={80} /></Layer>
    <Layer shot={shot} frame={frame} id="file-old-grey"><FileCard filename={element(shot, 'file-old-grey').name} date="很久以前" state="stale" showExpiredBadge={false} /></Layer>
    <TextLayer shot={shot} frame={frame} id="expired-badge" style={{borderRadius: 10, background: P.panel, border: `3px solid ${P.danger}`, fontWeight: 800}} />
    <Layer shot={shot} frame={frame} id="file-logo-check" style={{left: flight.x, top: flight.y, transform: `scale(${1 - p * 0.55})`, transformOrigin: 'top left', opacity: 1 - Number(motion(shot, frame, 'logo-lit').opacity)}}><FileCard state="check" /></Layer>
    <Layer shot={shot} frame={frame} id="logo-lit" style={{boxShadow: `0 0 32px ${P.success}66`, borderRadius: 12}}><Logo /></Layer>
  </>;
};

const CacheMissScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="browser"><BrowserChrome width={1600} height={720}><LogoOnly /></BrowserChrome></Layer>
  <Layer shot={shot} frame={frame} id="qmark" style={{border: `4px dashed ${P.muted}`, borderRadius: 18, color: P.accent, background: P.panel, fontSize: 160, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>?</Layer>
</>;

const ContactsScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="phone" style={{overflow: 'hidden', borderRadius: 48}}>
    <PhoneContacts width={element(shot, 'phone').w} height={element(shot, 'phone').h} singleResult query={element(shot, 'search').text} contact={{name: element(shot, 'row').name, number: element(shot, 'row').number}} searchElementId="search" resultsElementId="row" searchStyle={motion(shot, frame, 'search')} resultsStyle={motion(shot, frame, 'row')} resultsOpacity={Number(motion(shot, frame, 'row').opacity)} />
  </Layer>
  <TextLayer shot={shot} frame={frame} id="zoom-row" style={{background: P.panel, border: `3px solid ${P.primary}`, borderRadius: 22, transformOrigin: 'left center'}} />
</>;

const DnsScene: React.FC<SceneProps> = ({shot, frame}) => {
  const fly = (id: string, returnTrip = false) => {
    const e = element(shot, id), start = returnTrip ? Math.max(at(shot, 'query') + 54, (e.appearFrame ?? 0) + 5) : (e.appearFrame ?? 0) + 5;
    const previous = shots.find((s) => s.id === '07a-dns-ask');
    const p = progress(frame + (shot.id === '07b-dns-ask' && !returnTrip ? previous.durationInFrames : 0), start, returnTrip ? 62 : 45);
    return <Layer key={id} shot={shot} frame={frame} id={id}><FlyingLabel text={e.text} x0={0} y0={0} x1={(returnTrip ? e.flyTo[0] : Math.min(1040, e.flyTo[0])) - e.x} y1={e.flyTo[1] - e.y} progress={p} arcHeight={returnTrip ? -55 : 70} color={returnTrip ? P.success : P.primary} /></Layer>;
  };
  return <>
    <Layer shot={shot} frame={frame} id="pc"><Laptop width={420} height={320} /><Caption>你的电脑</Caption></Layer>
    <Layer shot={shot} frame={frame} id="dns"><ServerRack color={P.primary} /><Caption>DNS 服务器</Caption></Layer>
    {fly('query')}{shot.id === '07b-dns-ask' && fly('answer', true)}
  </>;
};

const RememberScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="pc"><Laptop width={700} height={520} /></Layer>
  <Layer shot={shot} frame={frame} id="notepad" style={{boxSizing: 'border-box', border: `3px solid ${P.muted}`, borderRadius: 18, overflow: 'hidden', background: P.panel}}>
    <div style={{height: 86, padding: '0 26px', display: 'flex', alignItems: 'center', gap: 18, background: P.panel2, borderBottom: `2px solid ${P.muted}`}}>
      <svg width={34} height={42} viewBox="0 0 34 42" fill="none" stroke={P.primary} strokeWidth={3} aria-hidden="true"><rect x={3} y={2} width={28} height={38} rx={3} /><path d="M9 13h16M9 21h16M9 29h11" /></svg>
      <span style={{fontSize: 40, fontWeight: 700}}>{element(shot, 'notepad').title}</span>
      <span style={{marginLeft: 'auto', color: P.text2, fontSize: 36}} aria-hidden="true">− ×</span>
    </div>
    <div style={{padding: '42px 32px', color: P.text, fontFamily: MONO, fontSize: 40, lineHeight: 1.7, transform: `translateY(${(1 - progress(frame, at(shot, 'notepad') + 5, 30)) * -80}px)`}}>{element(shot, 'notepad').line.split(' → ').map((part: string, i: number) => <div key={part} style={{color: i ? P.success : P.text}}>{i ? '→ ' : ''}{part}</div>)}</div>
  </Layer>
  <Layer shot={shot} frame={frame} id="fade-line" style={{opacity: 1 - 0.85 * progress(frame, at(shot, 'fade-line') + 4, 30), borderTop: `4px dashed ${P.muted}`}} />
</>;

const HandshakeScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="pc"><Laptop width={420} height={320} /><Caption>浏览器</Caption></Layer>
  <Layer shot={shot} frame={frame} id="srv"><ServerRack color={P.secondary} /><Caption>服务器</Caption></Layer>
  {shot.elements.filter((e) => e.component === 'ArrowLabel').map((e, i) => {
    const id = e.id;
    const start = e.appearFrame ?? 0;
    return <Layer key={id} shot={shot} frame={frame} id={id}><Arrow e={{x: 0, y: 0, w: e.w, h: e.h, color: i === 1 ? P.success : P.primary, direction: e.dir === 'left' ? 'l' : 'r', label: e.text}} progress={progress(frame, start, 14)} /></Layer>;
  })}
</>;

const KeyIcon: React.FC = () => <svg viewBox="0 0 200 100" width="100%" height="100%" fill="none" stroke={P.accent} strokeWidth={12} strokeLinecap="round" strokeLinejoin="round"><circle cx={48} cy={44} r={26} /><path d="M76 44h100m-24 0v24m-24-24v18" /></svg>;

const LockScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="browser" style={{transform: `scale(${1 + 0.025 * progress(frame + (shot.id === '10b-lock' ? shots.find((s) => s.id === '10a-lock').durationInFrames : 0), 0, 40)})`, transformOrigin: '4% 12%'}}><BrowserChrome width={element(shot, 'browser').w} height={element(shot, 'browser').h} text={element(shot, 'browser').url} showPadlock padlockElementId="lock" padlockStyle={motion(shot, frame, 'lock')} /></Layer>
  <Layer shot={shot} frame={frame} id="server-end"><ServerRack color={P.secondary} size={element(shot, 'server-end').size} /></Layer>
  <Layer shot={shot} frame={frame} id="cert" style={{background: P.panel, border: `3px solid ${P.success}`, borderRadius: 18, boxSizing: 'border-box', padding: 32}}>
    {element(shot, 'cert').lines.map((line: string, i: number) => <div key={line} style={{fontSize: i ? 36 : 42, fontWeight: i ? 500 : 700, color: i ? P.text : P.success, marginBottom: 24, fontFamily: i === 2 ? MONO : undefined}}>{line}</div>)}
  </Layer>
  {shot.elements.filter((e) => e.component === 'KeyIcon').map(({id}) => <Layer key={id} shot={shot} frame={frame} id={id} style={{filter: `drop-shadow(0 0 ${12 + 6 * Math.sin((shot.from + frame) / 7)}px ${P.accent}88)`}}><KeyIcon /></Layer>)}
</>;

const WifiScene: React.FC<SceneProps> = ({shot, frame}) => <div style={{position: 'absolute', left: 230, top: 70, transform: 'scale(0.82)', transformOrigin: 'top left'}}><CafeScene fromText={element(shot, 'plain').from_} toText={element(shot, 'plain').to} progress={progress(frame, at(shot, 'plain') + 4, 70)} elementStyles={Object.fromEntries(['pc', 'srv', 'wire', 'plain', 'cup', 'peeker'].map((id) => [id, motion(shot, frame, id)]))} /></div>;

const WifiIcon: React.FC<{strength: number}> = ({strength}) => <svg width="100%" height="100%" viewBox="0 0 100 100" fill="none" strokeWidth={7} strokeLinecap="round"><path d="M12 32q38-36 76 0" stroke={strength >= 3 ? P.accent : P.muted} /><path d="M25 48q25-24 50 0" stroke={strength >= 2 ? P.accent : P.muted} /><path d="M39 64q11-11 22 0" stroke={strength >= 1 ? P.accent : P.muted} /><circle cx={50} cy={80} r={5} fill={P.accent} /></svg>;

/** Signal x follows the storyboard motion keyframes exactly (Knoll: no repetition; storyboard is authoritative). */
export const signalX = (e: ShotElement, frame: number): number => {
  const keys = e.motion as {frame: number; x: number}[];
  if (!keys?.length) return e.x;
  return interpolate(frame, keys.map((k) => k.frame), keys.map((k) => k.x), {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
};

const SlowScene: React.FC<SceneProps> = ({shot, frame}) => {
  const laptop = element(shot, 'laptop-right');
  const signal = element(shot, 'signal');
  const pulse = 0.5 + 0.5 * Math.sin((frame - (signal.appearFrame ?? 0)) / 4);
  return <>
    <Layer shot={shot} frame={frame} id="laptop-right"><Laptop width={laptop.w} height={laptop.h} loading /></Layer>
    <Layer shot={shot} frame={frame} id="spinner-big"><Spinner frame={frame} /></Layer>
    <Layer shot={shot} frame={frame} id="link-line" style={{background: P.muted, borderRadius: 2}} />
    <Layer shot={shot} frame={frame} id="srv"><ServerRack color={P.secondary} frame={frame} size={element(shot, 'srv').size} /></Layer>
    <Layer shot={shot} frame={frame} id="wifi-weak"><WifiIcon strength={element(shot, 'wifi-weak').strength} /></Layer>
    <Layer shot={shot} frame={frame} id="signal" style={{left: signalX(signal, frame), borderRadius: '50%', background: P.primary, boxShadow: `0 0 ${16 + 16 * pulse}px ${P.primary}, inset 0 0 12px white`}} />
  </>;
};

const RequestScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="devtools">
    <DevToolsNetwork width={element(shot, 'devtools').w} height={element(shot, 'devtools').h} rows={[requestRow(shot)]} pending focusRequest={element(shot, 'devtools').layout === 'focusRequest'} rowHeight={element(shot, 'row1').h} rowFontSize={element(shot, 'row1').fontSize} rowElementId="row1" rowStyle={motion(shot, frame, 'row1')} />
  </Layer>
  <Layer shot={shot} frame={frame} id="hl" style={{border: `4px solid ${P.primary}`, borderRadius: 10, boxSizing: 'border-box', background: `${P.primary}18`, pointerEvents: 'none'}} />
  <TextLayer shot={shot} frame={frame} id="row-label" style={{background: P.panel2, border: `3px solid ${P.accent}`, borderRadius: 16, fontWeight: 800}} />
</>;

const requestRow = (shot: Shot): NetworkRow => {
  const cells = element(shot, 'row1').cells;
  return {name: cells[0], method: cells[1], type: cells[3], status: Number(cells[2]) || undefined, size: cells[4], time: cells[5]};
};

const ServerWorkScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="srv"><ServerRack color={P.secondary} frame={frame} blinking /></Layer>
  <Layer shot={shot} frame={frame} id="folder" style={{transform: `translateX(${-30 * (1 - progress(frame, at(shot, 'folder'), 36))}px)`}}>
    <Folder color={P.accent} fileLift={progress(frame, at(shot, 'folder') + 5, 40) * 38} />
    <div style={{fontFamily: MONO, fontSize: 38, textAlign: 'center', color: P.primary, marginTop: 24}}>index.html</div>
  </Layer>
  <Layer shot={shot} frame={frame} id="gear">
    <div style={{width: '100%', height: '100%', transform: `rotate(${360 * progress(frame, at(shot, 'gear'), 70)}deg)`}}><Gear color={P.primary} /></div>
  </Layer>
  <Layer shot={shot} frame={frame} id="cart" style={{background: P.panel, border: `3px solid ${P.primary}`, borderRadius: 18, padding: 28, boxSizing: 'border-box'}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 20, fontSize: 44, fontWeight: 800, marginBottom: 30}}><svg width={54} height={50} viewBox="0 0 54 50" fill="none" stroke={P.primary} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round"><path d="M2 4h8l8 28h27l6-20H13" /><circle cx={22} cy={43} r={3} /><circle cx={42} cy={43} r={3} /></svg>购物车</div>
    {element(shot, 'cart').items.map((item: string, i: number) => <div key={item} style={{padding: '20px 0', fontSize: 40, borderTop: `2px solid ${P.muted}`, color: i === 2 ? P.primary : P.text, fontWeight: i === 2 ? 800 : 500}}>{item}</div>)}
  </Layer>
</>;

const ResponseScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="devtools">
    <DevToolsNetwork width={element(shot, 'devtools').w} height={element(shot, 'devtools').h} focusRequest={element(shot, 'devtools').layout === 'focusRequest'} rows={[{...requestRow(shot), status: Number(element(shot, 'status200').text), size: element(shot, 'status200').size, time: element(shot, 'status200').time}]} rowHeight={element(shot, 'row1').h} rowFontSize={element(shot, 'row1').fontSize} rowElementId="row1" rowStyle={motion(shot, frame, 'row1')} pending={frame < at(shot, 'status200')} statusElementId="status200" statusStyle={{...motion(shot, frame, 'status200'), fontSize: element(shot, 'status200').fontSize, color: element(shot, 'status200').color}} />
  </Layer>
  <TextLayer shot={shot} frame={frame} id="got-label" style={{background: P.panel2, border: `3px solid ${P.success}`, borderRadius: 16, fontWeight: 800}} />
  <Layer shot={shot} frame={frame} id="card404" style={{boxSizing: 'border-box', border: `4px solid ${P.danger}`, borderRadius: 24, background: P.panel, color: element(shot, 'card404').color, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12}}><strong style={{fontFamily: MONO, fontSize: 128, lineHeight: 1.1}}>{element(shot, 'card404').text.split(' ')[0]}</strong><span style={{fontSize: 56, fontWeight: 700}}>{element(shot, 'card404').text.split(' ').slice(1).join(' ')}</span></Layer>
</>;

export const waterfallRows = (shot: Shot): NetworkRow[] => element(shot, 'rows').names.map((name: string, i: number) => ({
  name, method: 'GET', status: 200,
  type: i === 0 ? 'document' : name.endsWith('.css') ? 'stylesheet' : name.endsWith('.js') ? 'script' : name.endsWith('.woff2') ? 'font' : 'image',
  size: `${[1.2, 4.8, 8.6, 126, 32, 48, 3.4, 98, 6, 72, 64, 36, 2][i]} kB`,
  time: `${64 + i * 19} ms`, start: 40 + i * 36, duration: 64 + i * 19,
}));

const WaterfallScene: React.FC<SceneProps> = ({shot, frame}) => {
  const first = shots.find((s) => s.id === '16a-waterfall');
  const continued = shot.id === '16b-waterfall';
  const elapsed = frame + (continued ? first.durationInFrames : 0);
  const start = at(first, 'rows');
  const panel = element(shot, 'devtools');
  // Keep the completed homepage visible while resources arrive at their existing cues.
  const spec = element(shot, 'rows');
  const rows = waterfallRows(shot);
  const rowProgress = rows.map((_, i) => i === 0 && spec.firstRowAlwaysVisible ? 1 : progress(elapsed, start + (i - 1) * spec.rowStaggerFrames, spec.rowGrowFrames));
  const {visibleRows, rowHeight} = spec;
  const zoom = interpolate(elapsed, [4, 24], [1, 1.9], {
    easing: Easing.inOut(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  // Anchor at the first filename's left edge and row center; use the shared clock
  // across both shots and pin scrolling so example.com and GET stay in frame.
  const firstRowCenter = 3 + (panel.h - 6 - visibleRows * rowHeight) + rowHeight / 2;
  return <Layer shot={shot} frame={frame} id="devtools" style={{overflow: 'hidden'}}>
    <div style={{transform: `translateY(${70 * (zoom - 1) / 0.9}px) scale(${zoom})` /* Knoll: shift down so column titles show in full */, transformOrigin: `28px ${firstRowCenter}px`}}>
      <DevToolsNetwork width={panel.w} height={panel.h} rows={rows} visibleRows={visibleRows} rowHeight={rowHeight} rowFontSize={spec.rowFontSize} rowProgress={rowProgress} rowGroupElementId="rows" rowGroupStyle={motion(shot, frame, 'rows')} firstRowAlwaysVisible={spec.firstRowAlwaysVisible} scrollOffset={spec.scrollOffset} />
    </div>
  </Layer>;
};

const HtmlScene: React.FC<SceneProps> = ({shot, frame}) => {
  const highlight = frame < at(shot, 'hl') ? null : frame < 178 ? 'title' : frame < 200 ? 'text' : 'button';
  return <>
    <Layer shot={shot} frame={frame} id="html-src" style={{background: P.panel, border: `3px solid ${P.muted}`, borderRadius: 18, boxSizing: 'border-box', padding: 40, display: 'flex', justifyContent: 'center', flexDirection: 'column', gap: 58}}>
      {element(shot, 'html-src').lines.map((line: string, i: number) => <div key={line} style={{fontFamily: MONO, fontSize: 44, whiteSpace: 'nowrap', color: ['title', 'text', 'button'][i] === highlight ? P.primary : P.text, borderLeft: `6px solid ${['title', 'text', 'button'][i] === highlight ? P.primary : 'transparent'}`, paddingLeft: 20}}>{line}</div>)}
    </Layer>
    <Layer shot={shot} frame={frame} id="wire"><WireframePage highlight={highlight} highlightElementId="hl" highlightStyle={motion(shot, frame, 'hl')} /></Layer>
  </>;
};

const CssScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <Layer shot={shot} frame={frame} id="wire"><WireframePage /></Layer>
  <Layer shot={shot} frame={frame} id="styled" style={{borderRadius: 18, overflow: 'hidden'}}><StyledPage /></Layer>
</>;

const PaintScene: React.FC<SceneProps> = ({shot, frame}) => {
  const first = shots.find((s) => s.id === '19a-paint');
  const continued = shot.id === '19b-paint';
  const fillSpec = element(shot, 'img-fill');
  const elapsed = frame + (continued ? first.durationInFrames : 0);
  const entranceEnd = Math.max(at(first, 'img-fill'), ...first.animations.filter((a) => a.elementId === 'img-fill').flatMap((a) => a.keyframes.map((k) => k.frame)));
  // Sharpen frames come from 19b img-fill.stateKeyframes ('sharp-N'), in 19b local frames (Knoll fix: storyboard-driven).
  const second = shots.find((s) => s.id === '19b-paint');
  const sharpKeys = (element(second, 'img-fill').stateKeyframes ?? []) as {frame: number; state: string}[];
  const images = [0, 1, 2].map((i) => {
    const k = sharpKeys.find((s) => s.state === `sharp-${i + 1}`);
    const startAt = k ? first.durationInFrames + k.frame : entranceEnd + i * fillSpec.staggerFrames;
    return progress(elapsed, startAt, fillSpec.sharpenFrames);
  }) as [number, number, number];
  return <Layer shot={shot} frame={frame} id="browser"><BrowserChrome width={1600} height={720} showPadlock>
    <Part shot={shot} frame={frame} id="page" style={{position: 'absolute', inset: 0}}><StyledPage hideImages /></Part>
    <Part shot={shot} frame={frame} id="img-fill" style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}><StyledPage imagesOnly imagesRevealed={images} imageGreyColor={fillSpec.greyColor} /></Part>
  </BrowserChrome></Layer>;
};

const RecapLaptops: React.FC<SceneProps & {compact?: boolean; allLoaded?: boolean}> = ({shot, frame, compact = false, allLoaded = false}) => {
  const loaded = allLoaded || (shot.id === '20b-recap' && frame >= at(shot, 'right-loaded'));
  const width = compact || shot.id === '20c-recap' ? 640 : 740;
  const height = element(shot, 'laptops').h;
  return <Layer shot={shot} frame={frame} id="laptops" style={{display: 'flex', justifyContent: 'space-between'}}>
    <Laptop width={width} height={height} loaded />
    <Laptop width={width} height={height} loading={!loaded} loaded={loaded}>
      {shot.id === '20b-recap' ? <Part shot={shot} frame={frame} id="right-loaded" style={{width: '100%', height: '100%'}}><StyledPage /></Part> : loaded ? <StyledPage /> : undefined}
    </Laptop>
  </Layer>;
};

const RecapStepsScene: React.FC<SceneProps> = ({shot, frame}) => {
  const activeCount = element(shot, 'steps').iconLightFrames.filter((cue: number) => frame >= cue).length;
  return <><RecapLaptops shot={shot} frame={frame} compact /><Layer shot={shot} frame={frame} id="steps"><StepBar activeCount={activeCount} labels={element(shot, 'steps').labels} /></Layer></>;
};

export const recapItemOpacity = (e: ShotElement, index: number, frame: number) =>
  e.itemAppearFrames?.[index] === undefined ? 1 : progress(frame, e.itemAppearFrames[index], 4);

const RecapCompareScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <RecapLaptops shot={shot} frame={frame} />
  <Layer shot={shot} frame={frame} id="spin-right"><Spinner frame={frame} /></Layer>
  <Layer shot={shot} frame={frame} id="checks-left" style={{display: 'flex', flexDirection: 'column', gap: 10}}>{element(shot, 'checks-left').items.map((text: string, i: number) => <div key={text} style={{display: 'flex', alignItems: 'center', gap: 18, color: P.success, fontSize: 32, opacity: recapItemOpacity(element(shot, 'checks-left'), i, frame)}}><div style={{width: 40, height: 40}}><Check color={P.success} /></div>{text}</div>)}</Layer>
  <Layer shot={shot} frame={frame} id="marks-right" style={{display: 'flex', flexDirection: 'column', gap: 20}}>{element(shot, 'marks-right').items.map((text: string, i: number) => <div key={text} style={{display: 'flex', alignItems: 'center', gap: 18, color: P.danger, fontSize: 34, opacity: recapItemOpacity(element(shot, 'marks-right'), i, frame)}}><svg width={40} height={40} viewBox="0 0 40 40" stroke={P.danger} strokeWidth={6} strokeLinecap="round"><path d="m9 9 22 22M31 9 9 31" /></svg>{text}</div>)}</Layer>
</>;

const RecapQuestionScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <RecapLaptops shot={shot} frame={frame} allLoaded />
  <TextLayer shot={shot} frame={frame} id="question" />
  <TextLayer shot={shot} frame={frame} id="follow" style={{background: P.primary, borderRadius: element(shot, 'follow').radius, fontSize: 52, whiteSpace: 'nowrap'}} />
</>;

/** Every storyboard shot has an explicit director implementation. Consecutive
 * parts share drawings, while retaining their own local element keyframes. */
export const SHOT_SCENES: Record<string, React.FC<SceneProps>> = {
  '01-hook': HookScene,
  '02-typing': TypingScene,
  '03-cache-look': CacheLookScene,
  '04-cache-hit': CacheHitScene,
  '05-cache-miss': CacheMissScene,
  '06-contacts': ContactsScene,
  '07a-dns-ask': DnsScene,
  '07b-dns-ask': DnsScene,
  '08-dns-remember': RememberScene,
  '09a-handshake': HandshakeScene,
  '09b-handshake': HandshakeScene,
  '10a-lock': LockScene,
  '10b-lock': LockScene,
  '11-wifi': WifiScene,
  '12-slow': SlowScene,
  '13a-devtools-request': RequestScene,
  '13b-devtools-request': RequestScene,
  '14-server-work': ServerWorkScene,
  '15-response': ResponseScene,
  '16a-waterfall': WaterfallScene,
  '16b-waterfall': WaterfallScene,
  '17-html': HtmlScene,
  '18a-css': CssScene,
  '18b-css': CssScene,
  '19a-paint': PaintScene,
  '19b-paint': PaintScene,
  '20a-recap': RecapStepsScene,
  '20b-recap': RecapCompareScene,
  '20c-recap': RecapQuestionScene,
};

// Fail at composition load if a frozen storyboard adds or removes a shot.
const mappedIds = Object.keys(SHOT_SCENES);
if (mappedIds.length !== shots.length || shots.some((shot) => !SHOT_SCENES[shot.id])) {
  throw new Error('Shot scene map must match the frozen storyboard exactly');
}
