export type FrameMode = 'browser' | 'canvas';
export type FrameSpec = FrameMode | {from: number; frame: FrameMode; switchElement?: string}[];
export const XFADE = 6;

export function switchFramesOf(shot: {from: number; frame?: unknown}): {local: number; switchElement?: string}[] {
  if (!Array.isArray(shot.frame)) return [];
  return shot.frame.slice(1)
    .filter(segment => segment && Number.isFinite(segment.from) && segment.from > shot.from)
    .map(segment => ({local: segment.from - shot.from, switchElement: segment.switchElement}));
}

/** Segment starts use absolute storyboard frames. */
export function frameModeAt(spec: unknown, absoluteFrame: number): FrameMode {
  if (!Array.isArray(spec)) return spec === 'canvas' ? 'canvas' : 'browser';
  let mode: FrameMode = 'browser';
  for (const segment of spec) {
    if (!segment || typeof segment.from !== 'number' || !Number.isFinite(segment.from)
      || !(segment.from <= absoluteFrame)) continue;
    mode = segment.frame === 'canvas' ? 'canvas' : 'browser';
  }
  return mode;
}

export function shotFrameMode(shot: {from: number; frame?: unknown}, localFrame: number): FrameMode {
  return frameModeAt(shot.frame, shot.from + localFrame);
}

/** Hold an element's mode at its lifetime endpoints, including outgoing fade tails. */
export function elementFrameMode(shot: {from: number; frame?: unknown}, element: {frame?: unknown; appearFrame?: number; disappearFrame?: number}, localFrame: number): FrameMode {
  const clampedLocal = Math.max(element.appearFrame ?? 0, Math.min(localFrame, (element.disappearFrame ?? Infinity) - 1));
  return frameModeAt(element.frame !== undefined ? element.frame : shot.frame, shot.from + clampedLocal);
}
