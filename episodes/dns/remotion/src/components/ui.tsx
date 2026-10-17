import React from 'react';
import {ShotElement} from '../storyboard';
import {FONT, MONO, P} from '../theme';
export type UIProps = {e: ShotElement; frame: number; source?: ShotElement; siblings?: ShotElement[]};
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
export const textWidth = (text: string, fontSize: number, mono = false) => Array.from(text).reduce((sum, ch) => sum + (/[^\u0000-\u00ff]/.test(ch) ? fontSize : fontSize * (mono ? .61 : .58)), 0);
/** Fit explicit line breaks in both dimensions, with a small font-metric allowance. */
export function fitSize(text: string, width: number, desired = 40, mono = false, height = Infinity, lineHeight = 1.2) {
  const lines = String(text).split('\n');
  const widest = Math.max(1, ...lines.map(line => textWidth(line, 1, mono)));
  return Math.max(1, Math.min(desired, Math.max(1, width) / (widest * 1.03), height / (lines.length * lineHeight)));
}
export const Copy: React.FC<{children?: React.ReactNode; size?: number; width?: number; height?: number; mono?: boolean; style?: React.CSSProperties}> = ({children, size = 40, width, height, mono, style}) => <div style={{...box, fontFamily: mono ? MONO : FONT, fontSize: fitSize(String(children ?? ''), width ?? Infinity, size, mono, height), lineHeight: 1.2, whiteSpace: 'pre-wrap', overflow: 'hidden', ...style}}>{children}</div>;
