import {shots} from './storyboard';
/** Sample after the final authored cue, transition, and camera action has settled. */
export const SHOT_LOCAL_STILL_FRAMES: Record<string, number> = Object.fromEntries(shots.map(shot => {
  const actions = shot.elements.flatMap(e => [e.appearFrame ?? 0, e.disappearFrame ?? 0, ...(e.stateKeyframes ?? []).map(k => k.frame + (k.fadeFrames ?? k.durationFrames ?? 0))]);
  const endpoints = shot.animations.flatMap(a => a.keyframes.map(k => k.frame));
  const camera = shot.camera?.keyframes.map(k => k.frame) ?? [];
  const lastAction = Math.max(...actions, ...endpoints, ...camera);
  // Half of the remaining hold keeps the still away from either edit boundary.
  return [shot.id, Math.min(shot.durationInFrames - 1, Math.ceil((lastAction + shot.durationInFrames - 1) / 2))];
}));
export const SHOT_STILL_FRAMES: Record<string, number> = Object.fromEntries(shots.map(shot => [shot.id, shot.from + SHOT_LOCAL_STILL_FRAMES[shot.id]]));
