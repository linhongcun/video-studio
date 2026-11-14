import storyboard from '@storyboard';
import trace from '../../trace/linear-example.json';
import plan from '../../plan.json';

export type Interval = number[];
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
export type Shot = {
  id: string;
  scriptShot?: number;
  from: number;
  durationInFrames: number;
  visualType: string;
  chapterId?: string;
  chapterTitle?: string;
  cueFrames?: {sentences?: number[]};
  subtitles?: {text: string; from: number; to?: number; duration?: number}[];
  codeCardFrom?: number;
  traceEvents?: {kind: string; id?: number}[];
  elements?: {text: string; cueText?: string; appearFrame: number}[];
};
export const STORYBOARD = storyboard as any;
export const TRACE = trace as {input: Interval[]; result: Interval[]; events: TraceEvent[]};
export const PLAN = plan as {id: string; traceEvents: {kind: string; id?: number}[]}[];
export const EVENTS = TRACE.events;
export const shots: Shot[] = STORYBOARD.scenes.flatMap((scene: any) => scene.shots);
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
