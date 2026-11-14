import type {Shot} from './data';

export const FPS = 30;
export const PLACEHOLDER_FRAMES_PER_SHOT = 90;
export const END_CARD_SECONDS = 5;
export const END_CARD_FRAMES = END_CARD_SECONDS * FPS;
export const REFERENCES_SECONDS = 5;
export const clamp = (value: number) => Math.max(0, Math.min(1, value));
export const ease = (value: number) => {
  const x = clamp(value);
  return x * x * (3 - 2 * x);
};
export function actionProgress(
  shot: Shot,
  frame: number,
  actionId: string,
  startFraction = 0,
  endFraction = 0.92,
) {
  const action = shot.actionCues?.find((cue) => cue.id === actionId);
  if (!action) return 0;
  const cueFrame = shot.cueFrames?.labels?.[action.cue]
    ?? shot.elements?.find((element) => element.cueText === action.cue)?.appearFrame;
  if (cueFrame === undefined) return 0;
  const endCueFrame = action.endCue ? shot.cueFrames?.labels?.[action.endCue] : undefined;
  if (action.endCue && endCueFrame === undefined) return 0;
  const subtitles = shot.subtitles ?? [];
  const lastSubtitle = subtitles.length > 0 ? subtitles[subtitles.length - 1] : undefined;
  const subtitleEnd = lastSubtitle?.to ?? shot.durationInFrames - 1;
  const safeEnd = Math.min(shot.durationInFrames - 6, subtitleEnd - 4);
  const endLimit = endCueFrame === undefined
    ? safeEnd
    : Math.min(safeEnd, endCueFrame - (action.endOffsetFrames ?? 6));
  const available = endLimit - cueFrame;
  if (available <= 1) return 0;
  const start = cueFrame + available * clamp(startFraction);
  const end = cueFrame + available * Math.max(startFraction, endFraction);
  if (end <= start) return 0;
  return ease((frame - start) / (end - start));
}
