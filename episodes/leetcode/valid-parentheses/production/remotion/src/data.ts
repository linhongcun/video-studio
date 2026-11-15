import storyboard from '@storyboard';
import trace from '../../trace/main-example.json';

export type EventKind = 'push' | 'pop' | 'mismatch' | 'empty' | 'leftover' | 'finish';
export type TraceEvent = {kind: EventKind; index: number; char?: string; top?: string; stack: string[]};
export type Run = {s: string; chars: string[]; valid: boolean; events: TraceEvent[]};
export type ActionCue = {id: string; cue: string; sentence: number; endCue?: string; endOffsetFrames?: number; events?: number[]};
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
  elements?: BoardElement[];
  actionCues?: ActionCue[];
};
export type Storyboard = {
  meta: {width: number; height: number; fps: number; durationInFrames: number; pendingAudio?: boolean; layoutPreviewOnly?: boolean};
  scenes: {shots: Shot[]}[];
};
export const STORYBOARD = storyboard as unknown as Storyboard;
export const TRACE = trace as unknown as {label: string; main: Run; cases: Record<string, Run>};
export const MAIN = TRACE.main;
export const shots: Shot[] = STORYBOARD.scenes.flatMap((scene) => scene.shots);
export const VIDEO = {
  width: STORYBOARD.meta.width,
  height: STORYBOARD.meta.height,
  fps: STORYBOARD.meta.fps,
  durationInFrames: STORYBOARD.meta.durationInFrames,
};

export type BoardState = {
  stack: number[];
  matched: Set<number>;
  failed: Set<number>;
  verdict?: 'valid' | 'invalid';
  stackEmptyFailure?: boolean;
};

export function replay(run: Run, count: number): BoardState {
  const state: BoardState = {stack: [], matched: new Set(), failed: new Set()};
  run.events.slice(0, Math.max(0, count)).forEach((event) => {
    if (event.kind === 'push') state.stack.push(event.index);
    else if (event.kind === 'pop') {
      const left = state.stack.pop();
      if (left !== undefined) state.matched.add(left);
      state.matched.add(event.index);
    } else if (event.kind === 'mismatch') {
      state.failed.add(event.index);
      state.failed.add(state.stack[state.stack.length - 1]);
      state.verdict = 'invalid';
    } else if (event.kind === 'empty') {
      state.failed.add(event.index);
      state.stackEmptyFailure = true;
      state.verdict = 'invalid';
    } else if (event.kind === 'leftover') {
      state.stack.forEach((index) => state.failed.add(index));
      state.verdict = 'invalid';
    } else if (event.kind === 'finish') state.verdict = 'valid';
  });
  return state;
}
