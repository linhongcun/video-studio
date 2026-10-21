import {progress} from '../animation';

type Key = {frame: number; [field: string]: any};
export const latestKey = (keys: Key[] = [], frame: number): Key | undefined => [...keys]
  .filter(key => key.frame <= frame).sort((a, b) => b.frame - a.frame)[0];

/** Only a change to this field starts its counter; unrelated cues do not restart it. */
export function rollingNumber(initial: number | null, keys: Key[], field: string, frame: number, duration: number) {
  let previous = initial, value = initial, start: number | undefined;
  for (const key of [...keys].sort((a, b) => a.frame - b.frame)) {
    if (key.frame > frame) break;
    if (key[field] === undefined || key[field] === value) continue;
    previous = value;
    value = key[field];
    start = key.frame;
  }
  if (value === null || previous === null || start === undefined || duration <= 0) return value;
  return Math.round(previous + (value - previous) * progress(frame, start, duration));
}
