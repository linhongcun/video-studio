import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BrowserChrome} from './components/BrowserChrome';
import {StyledPage} from './components/StyledPage';
import {DevToolsNetwork, NETWORK_ROWS} from './components/DevToolsNetwork';
import {PhoneContacts} from './components/PhoneContacts';
import {CafeScene} from './components/CafeScene';
import {FONT, P} from './theme';
import {WireframePage} from './components/WireframePage';
import {FileCard} from './components/FileCard';
import {FileManager} from './components/FileManager';
import {FlyingLabel} from './components/FlyingLabel';
import {StepBar} from './components/StepBar';
import {KeyCap} from './components/KeyCap';
import {ImagePlaceholder} from './components/ImagePlaceholder';

const Canvas: React.FC<{children: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{background: P.bg, color: P.text, fontFamily: FONT, alignItems: 'center', justifyContent: 'center'}}>{children}</AbsoluteFill>
);

export const BrowserChromeGallery: React.FC = () => (
  <Canvas><BrowserChrome width={1460} height={850} showPadlock><StyledPage /></BrowserChrome></Canvas>
);

export const BrowserTypingGallery: React.FC = () => (
  <Canvas><BrowserChrome width={1460} height={850} title="新标签页" text="example.com" typedChars={7} showCursor /></Canvas>
);

export const BrowserCertificateGallery: React.FC = () => (
  <Canvas><BrowserChrome width={1460} height={850} showPadlock certificateOpen><StyledPage /></BrowserChrome></Canvas>
);

export const StyledPageGallery: React.FC = () => (
  <Canvas><div style={{width: 1460, height: 850}}><StyledPage /></div></Canvas>
);

export const StyledPageRevealGallery: React.FC = () => (
  <Canvas><div style={{width: 1460, height: 850}}><StyledPage imagesRevealed={[1, 0.5, 0]} /></div></Canvas>
);

export const NetworkPendingGallery: React.FC = () => (
  <Canvas><DevToolsNetwork rows={[NETWORK_ROWS[0]]} pending /></Canvas>
);

export const NetworkDoneGallery: React.FC = () => (
  <Canvas><DevToolsNetwork rows={[NETWORK_ROWS[0]]} /></Canvas>
);

export const Network404Gallery: React.FC = () => (
  <Canvas><DevToolsNetwork rows={[{...NETWORK_ROWS[0], status: 404, size: '0.4 kB', time: '42 ms', duration: 42}]} notFound notFoundStart={0} /></Canvas>
);

export const NetworkWaterfallGallery: React.FC = () => (
  <Canvas><DevToolsNetwork rows={NETWORK_ROWS} scrollOffset={132} /></Canvas>
);

export const PhoneContactsGallery: React.FC = () => (
  <Canvas><PhoneContacts /></Canvas>
);

export const CafeSceneGallery: React.FC = () => (
  <Canvas><CafeScene progress={0.5} /></Canvas>
);

export const CafeSceneScrambledGallery: React.FC = () => (
  <Canvas><CafeScene progress={1} /></Canvas>
);

export const WireframePageGallery: React.FC = () => (
  <Canvas><div style={{width: 1000, height: 730}}><WireframePage highlight="title" /></div></Canvas>
);
export const FileManagerGallery: React.FC = () => (
  <Canvas><div style={{width: 1460, height: 680}}><FileManager /></div></Canvas>
);
export const FileCardGallery: React.FC = () => (
  <Canvas><div style={{display: 'flex', gap: 60}}>{(['fresh', 'check', 'stale'] as const).map((state, i) => <div key={state} style={{width: 400, height: 450}}><FileCard state={state} filename={i === 0 ? 'logo.png' : 'style.css'} date={i === 2 ? '9月18日' : '10月12日'} /></div>)}</div></Canvas>
);
export const FlyingLabelGallery: React.FC = () => (
  <Canvas><svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}><path d="M360 600 C640 360 1040 360 1320 600" fill="none" stroke={P.muted} strokeWidth={3} strokeDasharray="12 16" /></svg><FlyingLabel text="example.com" x0={360} y0={600} x1={1320} y1={600} progress={0.5} arcHeight={180} /></Canvas>
);
export const StepBarGallery: React.FC = () => (
  <Canvas><div style={{width: 1600, height: 280}}><StepBar activeCount={3} /></div></Canvas>
);
export const KeyCapGallery: React.FC = () => (
  <Canvas><div style={{display: 'flex', gap: 140}}>{[false, true].map((pressed) => <div key={String(pressed)} style={{width: 360, height: 300}}><KeyCap pressed={pressed} /></div>)}</div></Canvas>
);
export const ImagePlaceholderGallery: React.FC = () => (
  <Canvas><div style={{display: 'flex', gap: 50}}>{[0, 0.4, 1].map((progress) => <div key={progress} style={{width: 500, height: 360}}><ImagePlaceholder progress={progress} /></div>)}</div></Canvas>
);

const Laptop: React.FC<{loading?: boolean}> = ({loading = false}) => (
  <div style={{position: 'relative', width: 860}}>
    <BrowserChrome width={860} height={580} loading={loading} showPadlock={!loading}>
      {!loading && <StyledPage />}
    </BrowserChrome>
    <div style={{height: 32, borderRadius: '0 0 14px 14px', background: P.panel2, borderBottom: `3px solid ${P.muted}`}} />
    <svg width={908} height={54} viewBox="0 0 908 54" style={{display: 'block', marginLeft: -24}} aria-hidden="true">
      <path d="M24 2h860l22 31q-10 17-40 17H42Q12 50 2 33Z" fill={P.panel2} stroke={P.muted} strokeWidth={3} strokeLinejoin="round" />
      <path d="M348 3h212l-12 15H360Z" fill={P.muted} />
      <path d="M8 34h892" stroke={P.muted} strokeWidth={3} />
    </svg>
  </div>
);

/** Shot 1 layout: title occupies the top 20%; each screen is about 45% wide. */
export const BrowserPair: React.FC = () => (
  <Canvas>
    <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 216, background: P.panel, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 28, borderTop: `12px solid ${P.primary}`, boxSizing: 'border-box'}}>
      <span style={{fontSize: 76, fontWeight: 700, whiteSpace: 'nowrap'}}>浏览器输入网址后</span>
      <span style={{fontSize: 76, fontWeight: 700, color: P.bg, background: P.primary, borderRadius: 16, padding: '8px 24px', whiteSpace: 'nowrap'}}>发生了什么？</span>
    </div>
    <div style={{position: 'absolute', left: 60, right: 60, top: 246, display: 'flex', justifyContent: 'space-between'}}>
      {(['秒开', '一直转圈'] as const).map((label, i) => (
        <div key={label} style={{width: 860}}>
          <div style={{height: 64, marginBottom: 20, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 14, fontSize: 42, fontWeight: 700, color: i === 0 ? P.success : P.accent}}>
            <div style={{width: 12, height: 36, borderRadius: 6, background: i === 0 ? P.success : P.accent}} />{label}
          </div>
          <Laptop loading={i === 1} />
        </div>
      ))}
    </div>
  </Canvas>
);
