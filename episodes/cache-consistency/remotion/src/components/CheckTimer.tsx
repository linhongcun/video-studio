import React from 'react';
import {progress} from '../animation';
import {colorToken, Copy, stateAt, UIProps} from './ui';

export const CheckTimer: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame), segments = [...(e.segments ?? [])].sort((a, b) => a.startFrame - b.startFrame);
  let seconds = segments[0]?.fromSec ?? 0;
  for (const segment of segments) {
    if (frame < segment.startFrame) break;
    seconds = segment.endFrame <= segment.startFrame ? segment.toSec : segment.fromSec + (segment.toSec - segment.fromSec) * progress(frame, segment.startFrame, segment.endFrame - segment.startFrame);
  }
  // Round formatted seconds so floating point interpolation cannot drop an integer.
  const sec = Math.round(seconds);
  const text = e.format === 'm:ss'
    ? `${e.label} ${Math.floor(sec / 60)}:${String(Math.floor(sec) % 60).padStart(2, '0')}${e.unit}`
    : `${e.label} ${Math.floor(seconds)} ${e.unit}`;
  return <div data-check-timer style={{width: '100%', height: '100%', boxSizing: 'border-box', borderRadius: 10, border: e.border === false ? 'none' : `3px solid ${colorToken(e.color)}`, color: colorToken(e.color), background: colorToken(e.background), display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 8px'}}><Copy size={e.fontSize} width={e.w - 22} height={e.h - 6} style={{fontWeight: 700, textAlign: 'center', whiteSpace: 'nowrap'}}>{text}</Copy></div>;
};
