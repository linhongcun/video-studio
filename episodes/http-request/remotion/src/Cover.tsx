import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Laptop} from './components/Laptop';
import {Spinner} from './ShotScenes';
import addendum from './covers-addendum.json';
import {FONT, P} from './theme';
import type {ShotElement} from './storyboard';
import type {FrameMode} from './frameMode';
import {COMPONENTS, StoryboardComponent} from './components/StoryboardComponent';

/* Covers follow Miyazaki's covers-addendum.md (storyboard stays 25cd1d63): title, series pill, laptops, labels.
 * Laptops keep the BrowserPair aspect and are fitted uniformly (centred) inside each box, so pages are never squashed. */
export type CoverElement = Omit<ShotElement, 'frame'> & {frame?: FrameMode};
export const COVER_SIZES = addendum as Record<'16x9' | '4x3' | '3x4', {width: number; height: number; elements: CoverElement[]}>;
type CoverRatio = keyof typeof COVER_SIZES;
const LAPTOP_ASPECT = (580 + 84) / 908; // height / full base width (908 units incl. overhang)

export const Cover: React.FC<{ratio: CoverRatio}> = ({ratio}) => {
  const frame = useCurrentFrame();
  const spec = COVER_SIZES[ratio];
  return <AbsoluteFill style={{background: P.bg, color: P.text, fontFamily: FONT, overflow: 'hidden'}}>
    {spec.elements.map((e) => {
      const canvas = e.frame === 'canvas';
      const box: React.CSSProperties = {position: 'absolute', left: e.x, top: e.y, width: e.w, height: e.h};
      if (COMPONENTS[e.component]) return <div key={e.id} data-element={e.id} data-component={e.component} style={box}><StoryboardComponent e={e} frame={frame} canvas={canvas} /></div>;
      if (e.id === 'title') return <div key={e.id} data-element="title" style={{...box, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: e.align === 'center' ? 'center' : 'flex-start', textAlign: e.align, fontSize: e.fontSize, fontWeight: 900, lineHeight: 1.2, color: '#FFFFFF', whiteSpace: 'nowrap'}}>
        {String(e.text).split('\n').map((line: string, i: number) => <span key={i} style={{color: i === 1 ? '#F59E0B' : undefined}}>{line}</span>)}
      </div>;
      if (e.type === 'pill') return <div key={e.id} data-element={e.id} style={{...box, borderRadius: e.radius, background: e.fill, color: e.color, fontSize: e.fontSize, fontWeight: 800, display: 'flex', alignItems: 'center', justifyContent: 'center', whiteSpace: 'nowrap'}}>{e.text}</div>;
      if (e.type === 'text') return <div key={e.id} data-element={e.id} style={{...box, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: e.fontSize, fontWeight: 800, color: e.color, whiteSpace: 'nowrap'}}>{e.text}</div>;
      const fullW = Math.min(e.w, e.h / LAPTOP_ASPECT), unit = fullW / 908;
      const width = 860 * unit, height = fullW * LAPTOP_ASPECT;
      const ox = (e.w - fullW) / 2, oy = (e.h - height) / 2;
      const browserHeight = height - 84 * unit, chromeHeight = 136 * unit;
      const spinnerSize = Math.min(width * 0.22, (browserHeight - chromeHeight) * 0.65);
      return <div key={e.id} data-element={e.id} style={box}>
        <div style={{position: 'absolute', left: ox + 24 * unit, top: oy}}><Laptop canvas={canvas} width={width} height={height} loaded={e.state === 'loaded'} loading={e.state === 'spinning'} /></div>
        {e.state === 'spinning' && <div style={{position: 'absolute', left: ox + 24 * unit + (width - spinnerSize) / 2, top: oy + chromeHeight + (browserHeight - chromeHeight - spinnerSize) / 2, width: spinnerSize, height: spinnerSize}}><Spinner frame={frame} /></div>}
      </div>;
    })}
    <div style={{position: 'absolute', right: spec.width * 0.05, top: spec.height * 0.05, fontSize: 24, lineHeight: 1, fontWeight: 700, color: P.text2}}>IT小村</div>
  </AbsoluteFill>;
};

export const Cover16x9: React.FC = () => <Cover ratio="16x9" />;
export const Cover4x3: React.FC = () => <Cover ratio="4x3" />;
export const Cover3x4: React.FC = () => <Cover ratio="3x4" />;
