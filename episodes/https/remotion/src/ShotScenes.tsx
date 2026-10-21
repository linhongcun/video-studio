import React from 'react';
import {Easing, interpolate} from 'remotion';
import {animatedValue, clamp, progress} from './animation';
import {Shot, ShotElement, shots, storyboard} from './storyboard';
import {StoryboardComponent, COMPONENTS} from './components/StoryboardComponent';
import {stateAt, fitSize, colorToken} from './components/ui';
import {elementFrameMode, switchFramesOf, XFADE} from './frameMode';
export {Spinner} from './components/Spinner';
export type SceneProps = {shot: Shot; frame: number};
export const element = (shot: Shot, id: string): ShotElement => {
  const found = shot.elements.find(e => e.id === id);
  if (!found) throw new Error(`Missing storyboard element ${shot.id}/${id}`);
  return found;
};
const value = (shot: Shot, frame: number, id: string, property: string, fallback: number) => Number(animatedValue(shot, id, property, frame, fallback));
export const visibleAt = (e: ShotElement, frame: number, shot?: Shot) => {
  const tail = shot && switchFramesOf(shot).some(s => s.local === e.disappearFrame) ? XFADE : 0;
  // #89 dim placeholder: an element with dimFrom is already on screen (at dimOpacity) from dimFrom until it lights up at appearFrame.
  const start = typeof e.dimFrom === 'number' ? Math.min(e.appearFrame ?? 0, e.dimFrom) : e.appearFrame ?? 0;
  return frame >= start && (e.disappearFrame === undefined || frame < e.disappearFrame + tail) && stateAt(e, frame).state !== 'hidden';
};
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
/** Only authored keyframes interpolate; states switch on their exact frame. */
export const motion = (shot: Shot, frame: number, id: string): React.CSSProperties => {
  const e = stateAt(element(shot, id), frame);
  const switches = switchFramesOf(shot);
  const outgoing = switches.find(s => s.local === e.disappearFrame);
  const incoming = switches.filter(s => s.switchElement === id && s.local <= frame).pop();
  const crossFade = (outgoing ? 1 - clamp((frame - outgoing.local) / XFADE) : 1)
    * (incoming ? clamp((frame - incoming.local) / XFADE) : 1);
  const motionShot = switchMotionShot(shot, e);
  const fade = e.state === 'fadingOut' ? 1 - progress(frame, e.stateFrame, e.fadeFrames ?? e.durationFrames) : 1;
  const dimmed = typeof e.dimFrom === 'number' && frame < (e.appearFrame ?? 0);
  return {opacity: visibleAt(e, frame, shot) ? (dimmed ? e.dimOpacity ?? 0.25 : value(motionShot, frame, id, 'opacity', e.opacity ?? 1)) * fade * crossFade : 0, transform: `scale(${value(motionShot, frame, id, 'scale', 1)}) rotate(${value(shot, frame, id, 'rotate', 0)}deg) rotateY(${value(shot, frame, id, 'rotateY', 0)}deg)`};
};
export const Layer: React.FC<SceneProps & {id: string; style?: React.CSSProperties; children?: React.ReactNode}> = ({shot, frame, id, style, children}) => {
  const e = stateAt(element(shot, id), frame), m = motion(shot, frame, id);
  return <div data-element={id} data-component={e.component ?? e.type} data-state={e.state} style={{position: 'absolute', left: value(shot, frame, id, 'x', e.x), top: value(shot, frame, id, 'y', e.y), width: value(shot, frame, id, 'w', e.w), height: value(shot, frame, id, 'h', e.h), zIndex: e.z ?? 0, boxSizing: 'border-box', ...style, opacity: Number(m.opacity) * Number(style?.opacity ?? 1), transform: `${style?.transform ?? ''} ${m.transform}`}}>{children}</div>;
};
export const Part: React.FC<SceneProps & {id: string; style?: React.CSSProperties; children?: React.ReactNode}> = ({shot, frame, id, style, children}) => <div data-element={id} data-component={element(shot, id).component} style={{...style, ...motion(shot, frame, id)}}>{children}</div>;
export function cameraStyle(shot: Shot, frame: number): React.CSSProperties {
  if (!shot.camera) return {};
  const camera = shot.camera, target = stateAt(element(shot, camera.target), frame), keys = camera.keyframes;
  const scale = keys.length === 1 ? keys[0].scale : interpolate(frame, keys.map(k => k.frame), keys.map(k => k.scale), {easing: camera.easing === 'inOutCubic' ? Easing.inOut(Easing.cubic) : Easing.linear, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const origin = camera.transformOrigin;
  const coordinate = (p: string | number | undefined, size: number) => typeof p === 'string' && p.endsWith('%') ? parseFloat(p) / 100 * size : p === undefined ? size / 2 : Number(p);
  return {transform: `scale(${scale})`, transformOrigin: `${target.x + coordinate(origin?.x, target.w)}px ${target.y + coordinate(origin?.y, target.h)}px`};
}
/** Reflow peripheral text/icons into the visible part of their own rectangle.
 * Browser edges may leave the canvas during a push; readable copy does not. */
function horizontalInsets(shot: Shot, frame: number, e: ShotElement) {
  if (!shot.camera || screenCaption(e)) return {left: 0, right: 0};
  const camera = cameraStyle(shot, frame);
  const scale = Number(String(camera.transform).match(/scale\(([^)]+)\)/)?.[1] ?? 1);
  const origin = parseFloat(String(camera.transformOrigin));
  const leftEdge = origin + (0 - origin) / scale;
  const rightEdge = origin + (storyboard.meta.width - origin) / scale;
  return {left: Math.max(0, leftEdge - e.x), right: Math.max(0, e.x + e.w - rightEdge)};
}
const containedBy = (child: ShotElement, parent: ShotElement) => child.x >= parent.x && child.y >= parent.y && child.x + child.w <= parent.x + parent.w && child.y + child.h <= parent.y + parent.h;
const browserPart = (child: ShotElement, parent: ShotElement) => containedBy(child, parent) && (
  ['LockIcon', 'AddressBarTyping'].includes(child.component) ||
  (child.component === 'CornerBadge' && child.y - parent.y < child.h)
);
/** Bind annotation state to native UI parts without changing authored rectangles. */
export function resolvedElement(shot: Shot, original: ShotElement, frame: number): ShotElement {
  let e = stateAt(original, frame);
  const others = shot.elements.filter(o => o.id !== e.id).map(o => stateAt(o, frame));
  if (e.component === 'NotepadWindow') {
    const outline = others.find(o => o.component === 'RedPulseOutline' && containedBy(o, e));
    if (outline) e = {...e, contentBounds: outline};
  }
  if (e.component === 'BrowserChrome') {
    const address = others.find(o => o.component === 'BlockHighlight' && containedBy(o, e));
    const bind = (component: string) => {
      const part = others.find(o => o.component === component && browserPart(o, e));
      return part && {element: part, style: motion(shot, frame, part.id)};
    };
    e = {...e, browserLock: bind('LockIcon'), browserBadge: bind('CornerBadge'), browserTyping: bind('AddressBarTyping'), addressHighlighted: address?.state === 'domainHighlighted', lockHighlighted: address?.state === 'lockHighlighted', highlightText: address?.highlightText};
    if (address?.state === 'tabClosed') e = {...e, url: address.url, showPadlock: address.showPadlock, title: shots.flatMap(s => s.elements).find(o => o.component === 'BrowserChrome' && o.url === '')?.title, state: 'tabClosed'};
    if (e.state === 'fakeLoginShown') e.loginLines = shots.map(s => s.elements.filter(o => !o.component && o.type === 'text' && /^(账号|密码)：/.test(o.text))).find(lines => lines.some(o => o.text.startsWith('账号：')) && lines.some(o => o.text.startsWith('密码：')))?.map(o => o.text);
  }
  // An address annotation closes its containing page and its page-bound text.
  const parent = others.find(o => o.component === 'BrowserChrome' && containedBy(e, o));
  if (parent && browserPart(e, parent)) e = {...e, nativeBrowserPart: true};
  const closed = parent && others.find(o => o.component === 'BlockHighlight' && containedBy(o, parent) && o.state === 'tabClosed');
  if (closed && !['BlockHighlight', 'BrowserChrome'].includes(e.component)) e = {...e, state: 'hidden'};
  if (e.component === 'BlockHighlight' && e.state === 'urgencyHighlighted' && e.target) {
    const target = element(shot, e.target);
    e = {...e, x: target.x, y: target.y, w: target.w, h: target.h};
  }
  if (e.component === 'ScrambleText' || e.component === 'FlyingLabel') {
    const start = e.appearFrame ?? 0;
    const later = others.flatMap(o => [o.appearFrame, ...(o.stateKeyframes ?? []).map(k => k.frame)]).filter(f => f !== undefined && f > start);
    const end = e.component === 'ScrambleText' ? others.flatMap(o => o.stateKeyframes ?? []).find(k => k.state === 'fullyGarbled')?.frame ?? Math.min(shot.durationInFrames - 1, ...later) : others.flatMap(o => o.stateKeyframes ?? []).find(k => k.state === 'keyCapturedRed')?.frame ?? Math.min(shot.durationInFrames - 1, ...later);
    e = {...e, scrambleProgress: e.from_ === e.to ? 1 : progress(frame, start, end - start), flightProgress: progress(frame, start, end - start)};
  }
  return e;
}
export const TextLayer: React.FC<SceneProps & {id: string; style?: React.CSSProperties}> = ({shot, frame, id, style}) => {
  const e = resolvedElement(shot, element(shot, id), frame);
  const insets = horizontalInsets(shot, frame, e);
  const chunks = e.stateKeyframes?.some(k => ['likeLit', 'allLit'].includes(k.state)) ? String(e.text).split(' · ') : null;
  return <Layer shot={shot} frame={frame} id={id} style={{fontSize: fitSize(e.text ?? '', e.w - insets.left - insets.right, e.fontSize), fontWeight: e.fontWeight, color: colorToken(e.color), background: colorToken(e.background), borderRadius: e.radius, paddingLeft: insets.left, paddingRight: insets.right, overflowWrap: 'anywhere', whiteSpace: 'pre-line', lineHeight: 1.2, textAlign: e.align, display: 'flex', alignItems: 'center', justifyContent: e.align === 'center' ? 'center' : 'flex-start', ...style, ...(e.state === 'hidden' ? {opacity: 0} : {})}}>{chunks ? <span>{chunks.map((chunk, i) => <React.Fragment key={i}>{i > 0 && ' · '}<span data-action={i} style={{opacity: i === 0 || e.state === 'allLit' || (i === 1 && e.state === 'likeLit') ? 1 : .35}}>{chunk}</span></React.Fragment>)}</span> : e.text}</Layer>;
};
const SceneElement: React.FC<SceneProps & {original: ShotElement}> = ({shot, frame, original}) => {
  const e = resolvedElement(shot, original, frame);
  if (e.nativeBrowserPart) return null;
  const insets = horizontalInsets(shot, frame, e);
  const content = <StoryboardComponent e={e} frame={frame} canvas={elementFrameMode(shot, {...e, frame: original.frame}, frame) === 'canvas'} />;
  const icon = ['WifiIcon', 'KeyIcon', 'LockIcon'].includes(e.component);
  return e.component ? <Layer shot={shot} frame={frame} id={e.id} style={{...(e.state === 'hidden' ? {opacity: 0} : {}), ...(e.component === 'BlockHighlight' && e.target && e.state === 'urgencyHighlighted' ? {left: e.x, top: e.y, width: e.w, height: e.h} : {})}}>{icon && insets.left + insets.right > 0 ? <div style={{position: 'relative', left: insets.left, width: Math.max(0, e.w - insets.left - insets.right), height: '100%'}}>{content}</div> : content}</Layer> : <TextLayer shot={shot} frame={frame} id={e.id} />;
};
// Screen captions stay in their authored viewport band while the page zooms.
const screenCaption = (e: ShotElement) => !e.component && e.background && e.overlayOk;
const StoryboardScene: React.FC<SceneProps> = ({shot, frame}) => <>
  <div data-camera={shot.camera?.target} style={{position: 'absolute', inset: 0, ...cameraStyle(shot, frame)}}>{shot.elements.filter(e => e.id !== 'subtitle' && !screenCaption(e)).map(original => <SceneElement key={original.id} shot={shot} frame={frame} original={original} />)}</div>
  {shot.elements.filter(screenCaption).map(original => <SceneElement key={original.id} shot={shot} frame={frame} original={original} />)}
</>;
/** One scene per frozen shot id; no duplicated layout, copy, or cue timings. */
export const SHOT_SCENES: Record<string, React.FC<SceneProps>> = Object.fromEntries(shots.map(shot => {
  for (const e of shot.elements) if (e.component && !COMPONENTS[e.component]) throw new Error(`Unimplemented ${shot.id}/${e.component}`);
  const Scene: React.FC<SceneProps> = props => <StoryboardScene {...props} />;
  Scene.displayName = shot.id;
  return [shot.id, Scene];
}));
