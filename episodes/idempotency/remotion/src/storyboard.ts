// cdn-v1: '@storyboard' resolves to ../storyboard.json once frozen, else src/placeholders/storyboard.json (see remotion.config.ts / tsconfig paths).
import sourceJson from '@storyboard';
import type {FrameMode, FrameSpec} from './frameMode';
const source: any = sourceJson;

export type ShotElement = {
  id: string; x: number; y: number; w: number; h: number;
  appearFrame?: number; opacity?: number; z?: number;
  frame?: FrameMode;
  [key: string]: any;
};
export type Animation = {
  elementId: string; property: string; easing?: string;
  keyframes: {frame: number; value: number | string}[];
};
export type Shot = {
  id: string; from: number; durationInFrames: number; direction: string;
  frame?: FrameSpec;
  scriptVisual?: string;
  camera?: {type: string; target: string; transformOrigin?: {x: string | number; y: string | number}; easing: string; keyframes: {frame: number; scale: number}[]} | null;
  elements: ShotElement[]; animations: Animation[];
  subtitles: {text: string; from: number; to: number}[];
  voice: {id: string; wavStart: number; wavEnd: number; localStart: number; localEnd: number}[];
};

export const storyboard = source;
export const shots: Shot[] = (source.scenes as unknown as {shots: Shot[]}[]).flatMap((scene) => scene.shots);
export const totalFrames = source.meta.durationInFrames;
