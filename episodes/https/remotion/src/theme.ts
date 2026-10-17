// EP.01 v6 visual foundation. Episode dimensions remain storyboard-owned.
import {storyboard} from './storyboard';
export const P = {
  bg: '#0B1020',
  panel: '#111827',
  panel2: '#1F2937',
  primary: '#22D3EE',
  secondary: '#3B82F6',
  text: '#E5E7EB',
  text2: '#9CA3AF',
  muted: '#6B7280',
  success: '#22C55E',
  accent: '#F59E0B',
  danger: '#EF4444',
} as const;

export const FONT = '"Noto Sans CJK SC","Noto Sans SC",sans-serif';
export const MONO = '"DejaVu Sans Mono","Noto Sans Mono CJK SC",monospace';

export const VIDEO = {width: storyboard.meta.width, height: storyboard.meta.height, fps: storyboard.meta.fps};
