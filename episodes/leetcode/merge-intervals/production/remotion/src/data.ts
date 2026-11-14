import storyboard from '@storyboard';
import trace from '../../trace/linear-example.json';
import plan from '../../plan.json';

export type Interval = readonly [number, number];
export type TraceEvent = {
  kind: string;
  id?: number;
  order?: number[];
  before?: Interval;
  incoming?: Interval;
  current?: Interval | null;
  completed?: Interval[];
  relation?: string;
  processedIds?: number[];
};
export type ActionCue = {id: string; cue: string; sentence: number};
export type Subtitle = {text: string; from: number; to?: number; duration?: number};
export type BoardElement = {text: string; cueText?: string; appearFrame: number};
export type Shot = {
  id: string;
  scriptShot?: number;
  from: number;
  durationInFrames: number;
  visualType: string;
  chapterId?: string;
  chapterTitle?: string;
  cueFrames?: {sentences?: number[]; labels?: Record<string, number>};
  subtitles?: Subtitle[];
  codeCardFrom?: number;
  traceEvents?: {kind: string; id?: number}[];
  elements?: BoardElement[];
  actionCues?: ActionCue[];
};
export type Storyboard = {
  meta: {width: number; height: number; fps: number; durationInFrames: number; pendingAudio?: boolean; layoutPreviewOnly?: boolean};
  scenes: {shots: Shot[]}[];
};
export type PlanItem = {
  id: string;
  actions: ActionCue[];
  traceEvents: {kind: string; id?: number}[];
};
export const STORYBOARD = storyboard as unknown as Storyboard;
export const TRACE = trace as unknown as {input: Interval[]; result: Interval[]; events: TraceEvent[]};
export const PLAN = plan as unknown as PlanItem[];
export const EVENTS = TRACE.events;
export const shots: Shot[] = STORYBOARD.scenes.flatMap((scene) => scene.shots);
export const VIDEO = {
  width: STORYBOARD.meta.width,
  height: STORYBOARD.meta.height,
  fps: STORYBOARD.meta.fps,
  durationInFrames: STORYBOARD.meta.durationInFrames,
};
export const traceEventsFor = (shot: Shot) => {
  const id = shot.scriptShot ?? Number(shot.id);
  const selectors = PLAN.find((item) => Number(item.id) === id)?.traceEvents ?? [];
  return selectors.map((selector) => EVENTS.find((event) =>
    event.kind === selector.kind && (selector.id === undefined || event.id === selector.id),
  )).filter((event): event is TraceEvent => Boolean(event));
};
