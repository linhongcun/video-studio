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
export function actionProgress(shot: Shot, frame: number, start = 0.12, end = 0.82) {
  const cues = shot.cueFrames?.sentences ?? [];
  const a = cues[0] ?? 0;
  const b = cues[1] ?? shot.durationInFrames * 0.5;
  return ease((frame - (a + (b - a) * start)) / Math.max(1, (b - a) * (end - start)));
}
