import source from '../../storyboard.json';
import type {FrameMode, FrameSpec} from './frameMode';

export type ShotElement = {
  id: string; x: number; y: number; w: number; h: number;
  appearFrame?: number; disappearFrame?: number; opacity?: number; z?: number;
  frame?: FrameMode | {from: number; frame: FrameMode}[];
  canvas?: boolean;
  [key: string]: any;
};
export type Animation = {
  elementId: string; property: string; easing?: string;
  keyframes: {frame: number; value: number | string}[];
};
export type Shot = {
  id: string; from: number; durationInFrames: number; direction: string;
  frame?: FrameSpec;
  elements: ShotElement[]; animations: Animation[];
  subtitles: {text: string; from: number; to: number}[];
  voice: {id: string; wavStart: number; wavEnd: number; localStart: number; localEnd: number}[];
};

export const storyboard = source;
export const shots: Shot[] = (source.scenes as unknown as {shots: Shot[]}[]).flatMap((scene) => scene.shots);
export const totalFrames = source.meta.durationInFrames;
