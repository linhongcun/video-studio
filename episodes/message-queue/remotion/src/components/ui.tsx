import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {flushSync} from 'react-dom';
import {cancelRender, continueRender, delayRender} from 'remotion';
import {Shot, ShotElement} from '../storyboard';
import {FONT, MONO, P} from '../theme';
import type {BrowserContentLayout} from './browserLayout';
export type UIProps = {e: ShotElement; frame: number; shot?: Shot; canvas?: boolean; source?: ShotElement; siblings?: ShotElement[]; browserContentLayout?: BrowserContentLayout};
export const box: React.CSSProperties = {boxSizing: 'border-box', minWidth: 0, minHeight: 0};

/** State fields accumulate; append events are retained independently of later states. */
export function stateAt(e: ShotElement, frame: number): ShotElement {
  let resolved = {...e};
  const appendedLines: any[] = [];
  for (const key of [...(e.stateKeyframes ?? [])].sort((a, b) => a.frame - b.frame)) {
    if (frame < key.frame) continue;
    resolved = {...resolved, ...key, stateFrame: key.frame};
    if (key.appendLine) appendedLines.push(key.appendLine);
  }
  return {...resolved, appendedLines};
}
export const colorToken = (color?: string) => P[color as keyof typeof P] ?? color;
/** Pulses are events, so later unrelated state keys cannot restart one. */
export function pulseAt(e: ShotElement, frame: number) {
  const start = [...(e.stateKeyframes ?? [])].filter(k => k.pulse && k.frame <= frame).sort((a, b) => b.frame - a.frame)[0]?.frame;
  return start === undefined || frame - start >= 10 ? 0 : Math.sin(Math.PI * (frame - start) / 10);
}
export const emphasisStyle = (e: ShotElement): React.CSSProperties => ({
  ...(e.dim ? {color: '#64748B'} : e.color ? {color: colorToken(e.color)} : {}),
  opacity: e.dim ? .65 : 1,
  ...(e.highlighted !== undefined ? {border: `3px solid ${e.highlighted && !e.dim ? colorToken(e.color) ?? P.accent : 'transparent'}`} : {}),
});
export const textWidth = (text: string, fontSize: number, mono = false) => Array.from(text).reduce((sum, ch) => sum + (/[^\u0000-\u00ff]/.test(ch) ? fontSize : fontSize * (mono ? .61 : .58)), 0);
/** Fit explicit line breaks in both dimensions, with a small font-metric allowance. */
export function fitSize(text: string, width: number, desired = 40, mono = false, height = Infinity, lineHeight = 1.2) {
  const lines = String(text).split('\n');
  const widest = Math.max(1, ...lines.map(line => textWidth(line, 1, mono)));
  return Math.max(1, Math.min(desired, Math.max(1, width) / (widest * 1.03), height / (lines.length * lineHeight)));
}
const useBrowserLayoutEffect = typeof document === 'undefined' ? useEffect : useLayoutEffect;
/** Static markup gets a conservative estimate; renders wait for actual font metrics. */
export const Copy: React.FC<{children?: React.ReactNode; text?: string; size?: number; width?: number; height?: number; mono?: boolean; style?: React.CSSProperties}> = ({children, text, size = 40, width = Infinity, height = Infinity, mono, style}) => {
  const content = text ?? String(children ?? ''), ref = useRef<HTMLDivElement>(null);
  const estimate = fitSize(content, width, size, mono, height, typeof style?.lineHeight === 'number' ? style.lineHeight : 1.2);
  const [measured, setMeasured] = useState<{key: string; size: number} | null>(null);
  const key = JSON.stringify([content, size, width, height, mono, style]);
  useBrowserLayoutEffect(() => {
    const handle = delayRender('Fit storyboard text');
    let cancelled = false, fontsReady = false;
    const measure = () => {
      if (cancelled || !fontsReady || !ref.current?.clientWidth) return;
      const node = ref.current, css = getComputedStyle(node);
      const context = document.createElement('canvas').getContext('2d');
      if (!context) return;
      context.font = `${css.fontStyle} ${css.fontWeight} ${size}px ${css.fontFamily}`;
      const lines = content.split('\n');
      const actualWidth = Math.max(1, ...lines.map(line => context.measureText(line).width));
      const available = Math.min(width, node.clientWidth);
      const lineHeight = parseFloat(css.lineHeight) / parseFloat(css.fontSize) || 1.2;
      const fitted = Math.max(1, Math.min(size, size * available / (actualWidth * 1.03), height / (lines.length * lineHeight)));
      flushSync(() => setMeasured(previous => previous?.key === key && previous.size === fitted ? previous : {key, size: fitted}));
    };
    // Display:none rows must be measured when revealed, rather than cached at 1px.
    const observer = new ResizeObserver(measure);
    if (ref.current) observer.observe(ref.current);
    void document.fonts.ready.then(() => {fontsReady = true; measure();}).catch(cancelRender).finally(() => continueRender(handle));
    return () => {cancelled = true; observer.disconnect(); continueRender(handle);};
  }, [key]);
  return <div ref={ref} data-fitted-text style={{...box, width: Number.isFinite(width) ? width : undefined, maxWidth: '100%', maxHeight: '100%', flexShrink: 1, fontFamily: mono ? MONO : FONT, lineHeight: 1.2, whiteSpace: 'pre-wrap', overflow: 'hidden', ...style, fontSize: measured?.key === key ? measured.size : estimate}}>{children}</div>;
};
