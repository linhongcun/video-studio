import React from 'react';
import {ShotElement} from '../storyboard';
import {FONT, MONO, P} from '../theme';
export type UIProps = {e: ShotElement; frame: number; canvas?: boolean};
export const box: React.CSSProperties = {boxSizing: 'border-box', minWidth: 0, minHeight: 0};

/** Keep cumulative state properties until an authored keyframe replaces them. */
export function stateAt(e: ShotElement, frame: number): ShotElement {
  let resolved = {...e};
  for (const key of e.stateKeyframes ?? []) {
    if (frame >= key.frame) resolved = {...resolved, ...key, stateFrame: key.frame};
  }
  return resolved;
}
export const colorToken = (color?: string) => P[color as keyof typeof P] ?? color;
export const textWidth = (text: string, fontSize: number, mono = false) => Array.from(text).reduce((sum, ch) => sum + (/[^\u0000-\u00ff]/.test(ch) ? fontSize : fontSize * (mono ? .61 : .57)), 0);
export function fitSize(text: string, width: number, desired = 40, mono = false) {
  return Math.max(24, Math.min(desired, width / Math.max(1, textWidth(text, 1, mono))));
}
export const Copy: React.FC<{children?: React.ReactNode; size?: number; width?: number; mono?: boolean; style?: React.CSSProperties}> = ({children, size = 40, width, mono, style}) => <div style={{...box, fontFamily: mono ? MONO : FONT, fontSize: width ? fitSize(String(children ?? ''), width, size, mono) : Math.max(24, size), lineHeight: 1.2, overflowWrap: 'anywhere', whiteSpace: 'pre-wrap', ...style}}>{children}</div>;
