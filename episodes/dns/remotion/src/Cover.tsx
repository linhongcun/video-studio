import React from 'react';
import {AbsoluteFill} from 'remotion';
import {storyboard, CoverElement} from './storyboard';
import {FONT, P} from './theme';
import {StoryboardComponent} from './components/StoryboardComponent';
import {Copy} from './components/ui';
import coverBadges from './cover-badges.json';
export const COVER_SIZES = storyboard.meta.covers.sizes;
type CoverSize = keyof typeof COVER_SIZES;
const Cover: React.FC<{size: CoverSize}> = ({size}) => {
  const cover = COVER_SIZES[size], wm = storyboard.meta.covers.watermark;
  return <AbsoluteFill style={{background: P.bg, color: P.text, fontFamily: FONT}}>
    {[...cover.elements, ...((coverBadges as Record<string, unknown>)[size] as CoverElement[] ?? [])].map(raw => {
      // A frameless cover card always gets a visible panel (cover only; video shots unchanged).
      const e = (raw.component === 'NotepadWindow' && raw.frame === 'canvas' ? {...raw, coverCard: true} : raw) as CoverElement;
      const style: React.CSSProperties = {position: 'absolute', left: e.x, top: e.y, width: e.w, height: e.h, zIndex: e.z, boxSizing: 'border-box'};
      if (e.component) return <div key={e.id} data-element={e.id} data-component={e.component} style={style}><StoryboardComponent e={e} frame={0} canvas={e.frame === 'canvas'} /></div>;
      return <div key={e.id} data-element={e.id} style={{...style, display: 'flex', flexDirection: 'column', alignItems: e.type === 'pill' || e.align === 'center' ? 'center' : 'flex-start', justifyContent: 'center', background: e.fill, borderRadius: e.radius, fontWeight: typeof e.fontWeight === 'number' ? e.fontWeight : 700, color: e.color}}>{e.text.split('\n').map((line: string, i: number) => <Copy key={i} size={e.fontSize} width={e.w} style={{textAlign: e.align, whiteSpace: 'nowrap', fontWeight: typeof e.fontWeight === 'number' ? e.fontWeight : 700, color: i === 1 ? e.secondLineColor ?? e.color : e.color, lineHeight: 1.15}}>{line}</Copy>)}</div>;
    })}
    <div data-watermark style={{position: 'absolute', right: wm.offset[0], top: wm.offset[1], fontSize: wm.fontSize, color: wm.color, fontWeight: 700}}>{wm.text}</div>
  </AbsoluteFill>;
};
export const Cover16x9: React.FC = () => <Cover size="16x9" />;
export const Cover4x3: React.FC = () => <Cover size="4x3" />;
export const Cover3x4: React.FC = () => <Cover size="3x4" />;
