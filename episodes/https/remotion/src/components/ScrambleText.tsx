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
  red?: boolean; editedIndex?: number; label?: string;
};

export const ScrambleText: React.FC<ScrambleTextProps> = ({text = '', progress, to, style, red, editedIndex, label}) => {
  const output = to && progress >= 1 ? to : scrambleText(text, progress);
  return <div style={{fontFamily: MONO, fontSize: 40, color: red && editedIndex === undefined ? P.danger : P.primary, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', ...style}}>
    <span>{Array.from(output).map((char, i) => i === editedIndex ? <span key={i} data-edited-byte={i} style={{color: P.danger, background: `${P.danger}22`, boxShadow: `0 0 0 3px ${P.danger}`, borderRadius: 4}}>{scrambleText(String(char), 1)}</span> : <React.Fragment key={i}>{char}</React.Fragment>)}</span>
    {label && <div style={{fontSize: 24, marginTop: 8, color: P.danger}}>{label}</div>}
  </div>;
};
