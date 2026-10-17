import React from 'react';
import {FONT, P} from '../theme';
import {ImagePlaceholder} from './ImagePlaceholder';

export type StyledPageProps = {
  /** Load progress for the hero image, left image, and right image; 1 is ready. */
  imagesRevealed?: readonly [number, number, number];
  title?: string;
  imageStyle?: React.CSSProperties;
  /** Separate the page blocks from their independently timed image layer. */
  hideImages?: boolean;
  imagesOnly?: boolean;
  imageGreyColor?: string;
};

/** Large blocks stay legible inside an 860px browser. No small body copy or photos. */
export const StyledPage: React.FC<StyledPageProps> = ({imagesRevealed = [1, 1, 1], title = 'Hello, example.', imageStyle, hideImages = false, imagesOnly = false, imageGreyColor}) => (
  <div style={{width: '100%', height: '100%', boxSizing: 'border-box', padding: '3%', display: 'flex', flexDirection: 'column', gap: '5%', background: imagesOnly ? 'transparent' : P.bg, color: P.text, fontFamily: FONT, containerType: 'inline-size'}}>
    <div style={{height: '12%', minHeight: 0, visibility: imagesOnly ? 'hidden' : undefined, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 3%', background: P.panel2, borderRadius: 10}}>
      <div style={{width: '21%', height: '36%', background: P.primary, borderRadius: 5}} />
      <div style={{display: 'flex', gap: 12, width: '27%', height: '24%'}}>
        {[0, 1, 2].map((i) => <div key={i} style={{flex: 1, borderRadius: 4, background: P.muted}} />)}
      </div>
    </div>
    <div style={{height: '43%', minHeight: 0, display: 'flex', alignItems: 'stretch', gap: '4%', padding: '3%', boxSizing: 'border-box', background: imagesOnly ? 'transparent' : P.panel2, borderRadius: 14}}>
      <div style={{flex: 1.2, minWidth: 0, visibility: imagesOnly ? 'hidden' : undefined, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', gap: '16%'}}>
        <div style={{fontSize: '5.6cqw', fontWeight: 700, lineHeight: 1.15, letterSpacing: '-0.04em', whiteSpace: 'nowrap'}}>{title}</div>
        <div style={{width: '54%', height: '29%', background: P.secondary, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center'}} aria-label="页面按钮">
          <svg width="32%" height="65%" viewBox="0 0 64 32" fill="none" stroke={P.text} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M8 16h46M42 5l12 11-12 11" /></svg>
        </div>
      </div>
      <div style={{flex: 1, minWidth: 0, visibility: hideImages ? 'hidden' : undefined, ...imageStyle}}><ImagePlaceholder progress={imagesRevealed[0]} greyColor={imageGreyColor} variant="hero" /></div>
    </div>
    <div style={{flex: 1, minHeight: 0, display: 'flex', gap: '4%'}}>
      <div style={{flex: 1, padding: '2.5%', boxSizing: 'border-box', visibility: hideImages ? 'hidden' : undefined, background: imagesRevealed[1] >= 1 ? P.secondary : imageGreyColor ?? '#6B7280', borderRadius: 14, ...imageStyle}}><ImagePlaceholder progress={imagesRevealed[1]} greyColor={imageGreyColor} variant="left" /></div>
      <div style={{flex: 1, padding: '2.5%', boxSizing: 'border-box', visibility: hideImages ? 'hidden' : undefined, background: imagesRevealed[2] >= 1 ? P.primary : imageGreyColor ?? '#6B7280', borderRadius: 14, ...imageStyle}}><ImagePlaceholder progress={imagesRevealed[2]} greyColor={imageGreyColor} variant="right" /></div>
    </div>
  </div>
);
