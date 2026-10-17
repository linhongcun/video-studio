import {Easing, interpolate, interpolateColors, spring} from 'remotion';
import {Shot, storyboard} from './storyboard';

export const clamp = (n: number) => Math.max(0, Math.min(1, n));
export const progress = (frame: number, start: number, duration: number) => clamp((frame - start) / Math.max(1, duration));

/** Evaluate the storyboard's local keyframes, including held endpoints. */
export function animatedValue(shot: Shot, id: string, property: string, frame: number, fallback: number | string): number | string {
  const keys = shot.animations.filter((a) => a.elementId === id && a.property === property)
    .flatMap((a) => a.keyframes.map((key) => ({...key, easing: a.easing})))
    .sort((a, b) => a.frame - b.frame);
  if (!keys.length) return fallback;
  if (frame <= keys[0].frame) return keys[0].value;
  for (let i = 1; i < keys.length; i++) {
    const a = keys[i - 1], b = keys[i];
    if (frame > b.frame) continue;
    if (typeof a.value === 'string' && typeof b.value === 'string') {
      return interpolateColors(frame, [a.frame, b.frame], [a.value, b.value]);
    }
    const easing = (b.easing === 'easeInOut' || b.easing === 'inOutCubic') ? Easing.inOut(Easing.cubic) : b.easing === 'easeIn' ? Easing.in(Easing.cubic) : b.easing === 'easeOut' ? Easing.out(Easing.cubic) : Easing.linear;
    const p = b.easing === 'spring' ? spring({frame: frame - a.frame, fps: storyboardFps, durationInFrames: b.frame - a.frame, config: {damping: 14}}) : interpolate(frame, [a.frame, b.frame], [0, 1], {easing});
    return Number(a.value) + (Number(b.value) - Number(a.value)) * p;
  }
  return keys[keys.length - 1].value;
}

// All shot keyframes in this episode use the storyboard's 30 fps timebase.
const storyboardFps = storyboard.meta.fps;
