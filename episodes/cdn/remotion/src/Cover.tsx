import React from 'react';
import {AbsoluteFill} from 'remotion';
// cdn-v1: '@covers' resolves to ../covers.json once it exists, else src/placeholders/covers.json.
import coversJson from '@covers';
const covers: any = coversJson;
import {ShotElement} from './storyboard';
import type {FrameMode} from './frameMode';
import {FONT, P} from './theme';
import {StoryboardComponent} from './components/StoryboardComponent';
import {Copy, colorToken} from './components/ui';
export const COVER_SIZES = covers.sizes;
// Covers are stills: maps render their settled state (dots popped in, labels faded in, lines drawn).
const COVER_SETTLED_FRAME = 600;
type CoverSize = '16x9' | '4x3' | '3x4';
type CoverElement = ShotElement & {frame?: FrameMode};
const Cover: React.FC<{size: CoverSize}> = ({size}) => {
  const cover = COVER_SIZES[size], wm = covers.watermark;
  return <AbsoluteFill style={{background: P.bg, color: P.text, fontFamily: FONT}}>
    {cover.elements.map(raw => {
      const e = raw as CoverElement;
      const pill = e.type === 'pill', paddingInline = pill ? (e.radius ?? e.h / 2) / 2 : 0;
      const style: React.CSSProperties = {position: 'absolute', left: e.x, top: e.y, width: e.w, height: e.h, zIndex: e.z, boxSizing: 'border-box'};
      if (e.component) return <div key={e.id} data-element={e.id} data-component={e.component} style={style}><StoryboardComponent e={e} frame={/^WorldMap/.test(e.component) ? COVER_SETTLED_FRAME : 0} canvas={e.frame === 'canvas'} siblings={cover.elements as ShotElement[]} /></div>;
      return <div key={e.id} data-element={e.id} style={{...style, display: 'flex', alignItems: 'center', justifyContent: 'center', paddingInline, overflow: 'hidden', background: colorToken(e.background ?? e.fill), borderRadius: e.radius, fontWeight: typeof e.fontWeight === 'number' ? e.fontWeight : 700, color: e.color}}><Copy text={e.text} size={e.fontSize} width={e.w - paddingInline * 2} height={e.h} style={{textAlign: pill ? 'center' : e.align, ...(pill ? {whiteSpace: 'nowrap' as const} : {}), lineHeight: 1.15}}>{e.text.split('\n').map((line: string, i: number) => <React.Fragment key={i}>{i > 0 && '\n'}<span style={{color: i === 1 ? e.secondLineColor ?? e.color : e.color}}>{line}</span></React.Fragment>)}</Copy></div>;
    })}
    <div data-watermark style={{position: 'absolute', right: wm.offset[0], top: wm.offset[1], fontSize: wm.fontSize, color: wm.color, fontWeight: 700}}>{wm.text}</div>
  </AbsoluteFill>;
};
export const Cover16x9: React.FC = () => <Cover size="16x9" />;
export const Cover4x3: React.FC = () => <Cover size="4x3" />;
export const Cover3x4: React.FC = () => <Cover size="3x4" />;
