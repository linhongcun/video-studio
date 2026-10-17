import React from 'react';
import {MONO, P} from '../theme';

const GLYPHS = '7X#9@Q%2&K*5Z+8?';
const clamp = (value: number) => Math.max(0, Math.min(1, Number.isFinite(value) ? value : 0));

/** Stable character selection: progress only adds substitutions, never random flicker. */
export const scrambleText = (text: string, progress: number): string => {
  const chars = Array.from(text);
  const order = chars.map((char, index) => ({char, index, rank: ((index + 1) * 2654435761) >>> 0}))
    .filter(({char}) => !/\s/u.test(char))
    .sort((a, b) => a.rank - b.rank);
  const changed = new Set(order.slice(0, Math.floor(clamp(progress) * order.length)).map(({index}) => index));
  return chars.map((char, index) => {
    if (!changed.has(index)) return char;
    const code = char.codePointAt(0) ?? 0;
    const replacement = GLYPHS[(index * 7 + code) % GLYPHS.length];
    return replacement === char ? GLYPHS[(index * 7 + code + 1) % GLYPHS.length] : replacement;
  }).join('');
};

export type ScrambleTextProps = {
  text?: string;
  progress: number;
  to?: string;
  style?: React.CSSProperties;
};

export const ScrambleText: React.FC<ScrambleTextProps> = ({text = 'GET example.com', progress, to, style}) => (
  <span style={{fontFamily: MONO, fontSize: 40, color: P.primary, whiteSpace: 'pre', ...style}}>{to && progress >= 1 ? to : scrambleText(text, progress)}</span>
);
