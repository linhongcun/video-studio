import source from '../../storyboard.json';

export type ShotElement = {
  id: string; x: number; y: number; w: number; h: number;
  appearFrame?: number; opacity?: number; z?: number;
  [key: string]: any;
};
export type Animation = {
  elementId: string; property: string; easing?: string;
  keyframes: {frame: number; value: number | string}[];
};
export type Shot = {
  id: string; from: number; durationInFrames: number; direction: string;
  elements: ShotElement[]; animations: Animation[];
  subtitles: {text: string; from: number; to: number}[];
  voice: {id: string; wavStart: number; wavEnd: number; localStart: number; localEnd: number}[];
};

export const storyboard = source;
export const shots: Shot[] = (source.scenes as unknown as {shots: Shot[]}[]).flatMap((scene) => scene.shots);
export const totalFrames = source.meta.durationInFrames;
