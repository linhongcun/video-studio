import React from 'react';
import {Easing, interpolate} from 'remotion';
import {animatedValue, clamp, progress} from './animation';
import {Shot, ShotElement, shots, storyboard} from './storyboard';
import {StoryboardComponent, COMPONENTS} from './components/StoryboardComponent';
import {stateAt, Copy, colorToken, emphasisStyle, pulseAt} from './components/ui';
import {MONO} from './theme';
import {browserContentLayout} from './components/browserLayout';
import {elementFrameMode, switchFramesOf, XFADE} from './frameMode';
const browserLayouts = new Map(shots.map(shot => [shot, new Map(shot.elements.filter(e => e.component === 'BrowserChrome').map(e => [e.id, browserContentLayout(shot, e)]))]));
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
export const motion = (shot: Shot, frame: number, id: string): React.CSSProperties => {
  const e = resolvedElement(shot, element(shot, id), frame);
  const switches = switchFramesOf(shot);
  const outgoing = switches.find(s => s.local === e.disappearFrame);
  const incoming = switches.filter(s => s.switchElement === id && s.local <= frame).pop();
  const crossFade = (outgoing ? 1 - clamp((frame - outgoing.local) / XFADE) : 1)
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
  const pulse = pulseAt(e, frame);
  return <Layer shot={shot} frame={frame} id={id} style={{fontWeight: e.fontWeight, color: colorToken(e.color), background: colorToken(e.background ?? e.fill), borderRadius: e.radius, overflow: 'hidden', display: 'flex', alignItems: 'center', ...emphasisStyle(e)}}><Copy text={e.text ?? ''} size={e.fontSize} width={e.w - (e.highlighted !== undefined ? 6 : 0)} height={e.h - (e.highlighted !== undefined ? 6 : 0)} mono={e.fontFamily === MONO} style={{fontFamily: e.fontFamily, textAlign: e.align, transform: `scale(${1 + pulse * .05})`, boxShadow: pulse ? `0 0 ${pulse * 24}px ${colorToken(e.color) ?? '#22D3EE'}` : undefined}}>{chunks ? <span>{chunks.map((chunk, i) => <React.Fragment key={i}>{i > 0 && ' · '}<span data-action={i} data-lit={i === 0 || e.state === 'allLit' || (i === 1 && e.state === 'likeLit')} style={{opacity: i === 0 || e.state === 'allLit' || (i === 1 && e.state === 'likeLit') ? 1 : .35}}>{chunk}</span></React.Fragment>)}</span> : e.text}</Copy></Layer>;
};
const StoryboardScene: React.FC<SceneProps> = ({shot, frame}) => <div data-camera-clip style={{position: 'absolute', inset: 0, clipPath: shot.camera ? `inset(0px 0px ${storyboard.meta.height - storyboard.meta.safeArea.contentMaxY}px 0px)` : undefined}}><div data-storyboard-scene data-camera={shot.camera?.target} style={{position: 'absolute', inset: 0, ...cameraStyle(shot, frame)}}>{shot.elements.filter(e => e.role !== 'subtitle' && e.binding !== 'subtitles').map(original => {
  const e = resolvedElement(shot, original, frame);
  // State cues carry a numeric frame; mode overrides come from the authored element.
  return e.component ? <Layer key={e.id} shot={shot} frame={frame} id={e.id}><StoryboardComponent e={original} frame={frame} canvas={elementFrameMode(shot, {...e, frame: original.frame}, frame) === 'canvas'} siblings={shot.elements} browserContentLayout={browserLayouts.get(shot)?.get(e.id)} /></Layer> : <TextLayer key={e.id} shot={shot} frame={frame} id={e.id} />;
})}</div></div>;
/** The shot registry, geometry, copy, and cue times all come from the storyboard. */
export const SHOT_SCENES: Record<string, React.FC<SceneProps>> = Object.fromEntries(shots.map(shot => {
  for (const e of shot.elements) if (e.component && !COMPONENTS[e.component]) throw new Error(`Unimplemented ${shot.id}/${e.component}`);
  const Scene: React.FC<SceneProps> = props => <StoryboardScene {...props} />;
  Scene.displayName = shot.id;
  return [shot.id, Scene];
}));
