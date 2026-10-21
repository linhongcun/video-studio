import React from 'react';
import {Easing, interpolate} from 'remotion';
import {animatedValue, clamp, progress} from './animation';
import {Shot, ShotElement, shots, storyboard} from './storyboard';
import {StoryboardComponent, COMPONENTS} from './components/StoryboardComponent';
import {stateAt, fitSize, colorToken} from './components/ui';
import {MONO} from './theme';
import {elementFrameMode, switchFramesOf, XFADE} from './frameMode';
export type SceneProps = {shot: Shot; frame: number};
export const element = (shot: Shot, id: string): ShotElement => {
  const found = shot.elements.find(e => e.id === id);
  if (!found) throw new Error(`Missing storyboard element ${shot.id}/${id}`);
  return found;
};
const value = (shot: Shot, frame: number, id: string, property: string, fallback: number) => Number(animatedValue(shot, id, property, frame, fallback));
export const visibleAt = (e: ShotElement, frame: number, shot?: Shot) => {
  const tail = shot && switchFramesOf(shot).some(s => s.local === e.disappearFrame) ? XFADE : 0;
  return frame >= (e.appearFrame ?? 0) && (e.disappearFrame === undefined || frame < e.disappearFrame + tail) && stateAt(e, frame).state !== 'hidden';
};
export const resolvedElement = (_shot: Shot, original: ShotElement, frame: number) => stateAt(original, frame);
/** Replace entrance keys with neutral holds, retaining animations outside each fade. */
const switchMotionShot = (shot: Shot, e: ShotElement): Shot => {
  const entrances = switchFramesOf(shot).filter(s => s.switchElement === e.id);
  if (!entrances.length) return shot;
  return {...shot, animations: [
    ...shot.animations.map(a => a.elementId === e.id && (a.property === 'opacity' || a.property === 'scale')
      ? {...a, keyframes: a.keyframes.filter(k => !entrances.some(s => k.frame >= s.local && k.frame <= s.local + XFADE))} : a),
    ...['opacity', 'scale'].map(property => ({elementId: e.id, property, keyframes: entrances.flatMap(s =>
      [s.local, s.local + XFADE].map(frame => ({frame, value: property === 'opacity' ? e.opacity ?? 1 : 1})))})),
  ]};
};
/** Authored fade-out window [start, L] of a switch's outgoing group: opacity keyframes that reach 0 exactly at the switch frame L. */
const groupFadeStart = (shot: Shot, local: number): number | undefined => {
  const outgoing = new Set(shot.elements.filter(e => e.disappearFrame === local).map(e => e.id));
  const starts = shot.animations.filter(a => a.property === 'opacity' && outgoing.has(a.elementId)).flatMap(a => {
    const i = a.keyframes.findIndex(k => k.frame === local && Number(k.value) === 0);
    return i > 0 ? [a.keyframes[i - 1].frame] : [];
  });
  return starts.length ? Math.min(...starts) : undefined;
};
const hasOwnFadeOut = (shot: Shot, id: string, local: number) => shot.animations.some(a => a.elementId === id && a.property === 'opacity' && a.keyframes.some(k => k.frame === local && Number(k.value) === 0));
export const motion = (shot: Shot, frame: number, id: string): React.CSSProperties => {
  const e = resolvedElement(shot, element(shot, id), frame);
  const switches = switchFramesOf(shot);
  const outgoing = switches.find(s => s.local === e.disappearFrame);
  const incoming = switches.filter(s => s.switchElement === id && s.local <= frame).pop();
  // dns-v1 workaround (#89, shot 11): outgoing elements without their own fade-out follow the group's authored fade, so they leave with the window instead of lingering into the switch.
  const lead = outgoing && !hasOwnFadeOut(shot, id, outgoing.local) ? groupFadeStart(shot, outgoing.local) : undefined;
  const groupFade = outgoing && lead !== undefined && lead < outgoing.local ? 1 - clamp((frame - lead) / (outgoing.local - lead)) : 1;
  const crossFade = groupFade * (outgoing ? 1 - clamp((frame - outgoing.local) / XFADE) : 1)
    * (incoming ? clamp((frame - incoming.local) / XFADE) : 1);
  const motionShot = switchMotionShot(shot, e);
  const fade = e.opacityTo !== undefined ? 1 + (e.opacityTo - 1) * progress(frame, e.stateFrame, e.fadeFrames ?? e.durationFrames ?? 0) : 1;
  return {opacity: visibleAt(e, frame, shot) ? value(motionShot, frame, id, 'opacity', e.opacity ?? 1) * fade * crossFade : 0, transform: `scale(${value(motionShot, frame, id, 'scale', 1)})`};
};
export function cameraStyle(shot: Shot, frame: number): React.CSSProperties {
  if (!shot.camera) return {};
  const camera = shot.camera, target = resolvedElement(shot, element(shot, camera.target), frame), keys = camera.keyframes;
  const scale = keys.length === 1 ? keys[0].scale : interpolate(frame, keys.map(k => k.frame), keys.map(k => k.scale), {easing: camera.easing === 'inOutCubic' ? Easing.inOut(Easing.cubic) : Easing.linear, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const coordinate = (p: string | number | undefined, size: number) => typeof p === 'string' && p.endsWith('%') ? parseFloat(p) / 100 * size : p === undefined ? size / 2 : Number(p);
  return {transform: `scale(${scale})`, transformOrigin: `${target.x + coordinate(camera.transformOrigin?.x, target.w)}px ${target.y + coordinate(camera.transformOrigin?.y, target.h)}px`};
}
export const Layer: React.FC<SceneProps & {id: string; children?: React.ReactNode; style?: React.CSSProperties}> = ({shot, frame, id, children, style}) => {
  const e = resolvedElement(shot, element(shot, id), frame);
  return <div data-element={id} data-component={e.component ?? e.type} data-state={e.state} style={{position: 'absolute', left: value(shot, frame, id, 'x', e.x), top: value(shot, frame, id, 'y', e.y), width: value(shot, frame, id, 'w', e.w), height: value(shot, frame, id, 'h', e.h), zIndex: e.z, boxSizing: 'border-box', visibility: visibleAt(e, frame, shot) ? 'visible' : 'hidden', ...style, ...motion(shot, frame, id)}}>{children}</div>;
};
export const TextLayer: React.FC<SceneProps & {id: string}> = ({shot, frame, id}) => {
  const e = resolvedElement(shot, element(shot, id), frame);
  const chunks = e.stateKeyframes?.some(k => ['likeLit', 'allLit'].includes(k.state)) ? String(e.text).split(' · ') : null;
  return <Layer shot={shot} frame={frame} id={id} style={{fontFamily: e.fontFamily, fontSize: fitSize(e.text ?? '', e.w, e.fontSize, e.fontFamily === MONO, e.h), fontWeight: e.fontWeight, color: colorToken(e.color), background: colorToken(e.background ?? e.fill), borderRadius: e.radius, whiteSpace: 'pre-wrap', overflow: 'hidden', lineHeight: 1.2, textAlign: e.align, display: 'flex', alignItems: 'center', justifyContent: e.align === 'center' ? 'center' : e.align === 'right' ? 'flex-end' : 'flex-start'}}>{chunks ? <span>{chunks.map((chunk, i) => <React.Fragment key={i}>{i > 0 && ' · '}<span data-action={i} data-lit={i === 0 || e.state === 'allLit' || (i === 1 && e.state === 'likeLit')} style={{opacity: i === 0 || e.state === 'allLit' || (i === 1 && e.state === 'likeLit') ? 1 : .35}}>{chunk}</span></React.Fragment>)}</span> : e.text}</Layer>;
};
const StoryboardScene: React.FC<SceneProps> = ({shot, frame}) => <div data-camera-clip style={{position: 'absolute', inset: 0, clipPath: shot.camera ? `inset(0px 0px ${storyboard.meta.height - storyboard.meta.safeArea.contentMaxY}px 0px)` : undefined}}><div data-storyboard-scene data-camera={shot.camera?.target} style={{position: 'absolute', inset: 0, ...cameraStyle(shot, frame)}}>{shot.elements.filter(e => e.role !== 'subtitle' && e.binding !== 'subtitles').map(original => {
  const e = resolvedElement(shot, original, frame);
  // State cue frames must not replace the authored element mode.
  return e.component ? <Layer key={e.id} shot={shot} frame={frame} id={e.id}><StoryboardComponent e={original} frame={frame} canvas={elementFrameMode(shot, {...e, frame: original.frame}, frame) === 'canvas'} siblings={shot.elements} /></Layer> : <TextLayer key={e.id} shot={shot} frame={frame} id={e.id} />;
})}</div></div>;
/** The shot registry, geometry, copy, and cue times all come from the storyboard. */
export const SHOT_SCENES: Record<string, React.FC<SceneProps>> = Object.fromEntries(shots.map(shot => {
  for (const e of shot.elements) if (e.component && !COMPONENTS[e.component]) throw new Error(`Unimplemented ${shot.id}/${e.component}`);
  const Scene: React.FC<SceneProps> = props => <StoryboardScene {...props} />;
  Scene.displayName = shot.id;
  return [shot.id, Scene];
}));
