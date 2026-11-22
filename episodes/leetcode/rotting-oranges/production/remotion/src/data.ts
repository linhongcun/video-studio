import storyboard from '@storyboard';
import trace from '../../trace/main-example.json';

export type ActionCue = {
  id: string;
  cue: string;
  sentence: number;
  endCue?: string;
  endOffsetFrames?: number;
  events?: number[];
};

export type Subtitle = {
  text: string;
  from: number;
  to?: number;
  duration?: number;
};

export type Shot = {
  id: string;
  slug?: string;
  from: number;
  durationInFrames: number;
  visualType: string;
  chapterId?: string;
  chapterTitle?: string;
  codeCardFrom?: number;
  cueFrames?: {sentences?: number[]; labels?: Record<string, number>};
  subtitles?: Subtitle[];
  elements?: {cueText?: string; appearFrame: number}[];
  actionCues?: ActionCue[];
};

export type NeighborCheck = {
  dir: 'up' | 'down' | 'left' | 'right';
  to: [number, number];
  outcome: 'oob' | 'empty' | 'already_rotten' | 'rot';
  existingMinute?: number | null;
};

export type TraceEvent = {
  id: number;
  kind: 'init' | 'layer_start' | 'expand' | 'layer_end' | 'result';
  grid: number[][];
  rotTime: (number | null)[][];
  queue: [number, number][];
  fresh: number;
  minutes: number;
  initialRotten?: [number, number][];
  initialFresh?: number;
  layerMinute?: number;
  layerSize?: number;
  layerBatch?: [number, number][];
  source?: [number, number];
  checks?: NeighborCheck[];
  infected?: [number, number][];
  remainingInLayer?: number;
  nextLayerCount?: number;
  completedMinute?: number;
  newlyRotted?: [number, number][];
  value?: number;
  stopReason?: string;
  remainingFresh?: [number, number][];
};

export type Run = {
  rows: number;
  cols: number;
  initialGrid: number[][];
  initialRotten: [number, number][];
  result: number;
  stopReason: string;
  events: TraceEvent[];
};

export type ContrastData = {
  grid: number[][];
  fromTopLeft: (number | null)[][];
  fromBottomRight: (number | null)[][];
  combinedMin: (number | null)[][];
};

export const TRACE = trace as unknown as {
  main: Run;
  contrastSingleSource: ContrastData;
  impossible: Run;
  officialEx1: Run;
  noFresh: Run;
  noRotten: Run;
};

export const STORYBOARD = storyboard as unknown as {
  meta: {
    width: number;
    height: number;
    fps: number;
    durationInFrames: number;
    pendingAudio?: boolean;
  };
  scenes: {shots: Shot[]}[];
};

export const shots = STORYBOARD.scenes.flatMap((s) => s.shots);
export const VIDEO = {
  width: STORYBOARD.meta.width,
  height: STORYBOARD.meta.height,
  fps: STORYBOARD.meta.fps,
  durationInFrames: STORYBOARD.meta.durationInFrames,
};
