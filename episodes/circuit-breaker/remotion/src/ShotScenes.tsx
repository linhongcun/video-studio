import React from 'react';
import {Easing, interpolate} from 'remotion';
import {animatedValue, clamp, progress} from './animation';
import {Shot, ShotElement, shots, storyboard} from './storyboard';
import {StoryboardComponent, COMPONENTS} from './components/StoryboardComponent';
import {stateAt, Copy, colorToken, emphasisStyle, pulseAt, calloutFitWidth} from './components/ui';
import {MONO, P} from './theme';
// Knoll (EP.12/13): text elements with `strike` are drawn crossed out in `strikeColor` (default `color`), line width fontSize × 0.08 (knoll-props EP.13 §0).
const P_DANGER = P.danger;
import {browserContentLayout, browserHeaderHeight} from './components/browserLayout';
import {frameModeAt, switchFramesOf, XFADE} from './frameMode';
const browserLayouts = new Map(shots.map(shot => [shot, new Map(shot.elements.filter(e => e.component === 'BrowserChrome').map(e => [e.id, browserContentLayout(shot, e)]))]));
export type SceneProps = {shot: Shot; frame: number};
export const element = (shot: Shot, id: string): ShotElement => {
  const found = shot.elements.find(e => e.id === id);
  if (!found) throw new Error(`Missing storyboard element ${shot.id}/${id}`);
  return found;
};
const value = (shot: Shot, frame: number, id: string, property: string, fallback: number) => Number(animatedValue(shot, id, property, frame, fallback));
// Knoll (EP.13 vis1): an element that leaves on the same frame another element enters on top of it (same-frame swap, e.g.
// shot 19 tab switch: shot-18 callouts out, tab-C callouts in at the same place) is cut, not faded, so the two never double up.
const swappedOut = (e: ShotElement, shot?: Shot) => !!shot && e.disappearFrame !== undefined && shot.elements.some(o => o.id !== e.id
  && o.appearFrame === e.disappearFrame && o.x < e.x + e.w && o.x + o.w > e.x && o.y < e.y + e.h && o.y + o.h > e.y);
export const visibleAt = (e: ShotElement, frame: number, shot?: Shot) => {
  const tail = e.fadeOut > 0 && !swappedOut(e, shot) ? e.fadeOut : shot && switchFramesOf(shot).some(s => s.local === e.disappearFrame) ? XFADE : 0;
  const start = typeof e.dimFrom === 'number' ? Math.min(e.appearFrame ?? 0, e.dimFrom) : e.appearFrame ?? 0;
  return frame >= start && (e.disappearFrame === undefined || frame < e.disappearFrame + tail) && stateAt(e, frame).state !== 'hidden';
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
  const outgoing = e.fadeOut > 0 ? undefined : switches.find(s => s.local === e.disappearFrame);
  const incoming = switches.filter(s => s.switchElement === id && s.local <= frame).pop();
  const crossFade = (outgoing ? 1 - clamp((frame - outgoing.local) / XFADE) : 1)
    * (incoming ? clamp((frame - incoming.local) / XFADE) : 1);
  const motionShot = switchMotionShot(shot, e);
  const fade = e.opacityTo !== undefined ? 1 + (e.opacityTo - 1) * progress(frame, e.stateFrame, e.fadeFrames ?? e.durationFrames ?? 0) : 1;
  const dimmed = typeof e.dimFrom === 'number' && frame < (e.appearFrame ?? 0);
  const fadeOut = e.disappearFrame !== undefined && e.fadeOut > 0 && !swappedOut(e, shot) ? 1 - progress(frame, e.disappearFrame, e.fadeOut) : 1;
  return {opacity: visibleAt(e, frame, shot) ? (dimmed ? e.dimOpacity ?? .25 : value(motionShot, frame, id, 'opacity', e.opacity ?? 1)) * fade * crossFade * fadeOut : 0, transform: `scale(${value(motionShot, frame, id, 'scale', 1)})`};
};
export function cameraStyle(shot: Shot, frame: number): React.CSSProperties {
  if (!shot.camera) return {};
  const camera = shot.camera, target = resolvedElement(shot, element(shot, camera.target), frame), keys = camera.keyframes;
  const scale = keys.length === 1 ? keys[0].scale : interpolate(frame, keys.map(k => k.frame), keys.map(k => k.scale), {easing: camera.easing === 'inOutCubic' ? Easing.inOut(Easing.cubic) : Easing.linear, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const coordinate = (p: string | number | undefined, size: number) => typeof p === 'string' && p.endsWith('%') ? parseFloat(p) / 100 * size : p === undefined ? size / 2 : Number(p);
  return {transform: `scale(${scale})`, transformOrigin: `${target.x + coordinate(camera.transformOrigin?.x, target.w)}px ${target.y + coordinate(camera.transformOrigin?.y, target.h)}px`};
}
export const Layer: React.FC<SceneProps & {id: string; children?: React.ReactNode; style?: React.CSSProperties}> = ({shot, frame, id, children, style}) => {
  const original = element(shot, id), e = resolvedElement(shot, original, frame);
  const browser = original.component === 'CornerBadge' ? shot.elements.find(chrome => chrome.component === 'BrowserChrome'
    && original.x < chrome.x + chrome.w && original.x + original.w > chrome.x
    && original.y < chrome.y + 3 + browserHeaderHeight(chrome) && original.y + original.h > chrome.y) : undefined;
  // Translate the authored box and its y animation together. Highlight clipping
  // measures this layer's bounds, so it sees the same relocated badge box.
  // EP.10: EP.09 rule (badge overlapping the tab/address bar moves into the page area, x/w/h unchanged), but it lands on
  // the page-content inset (page top + 20, the same inset as the authored page boxes, i.e. y >= 240 for a y=140 window)
  // and steps below any overlapping sibling badge/callout/text so it never covers other copy.
  const badgeY = (() => {
    if (!browser) return original.y;
    let y = browser.y + 3 + browserHeaderHeight(browser) + 20;
    const others = shot.elements.filter(o => o.id !== original.id && o.role !== 'subtitle' && o.binding !== 'subtitles'
      && !['BrowserChrome', 'DevToolsNetwork', 'BlockHighlight'].includes(o.component));
    for (let moved = true; moved;) {
      moved = false;
      for (const o of others) if (original.x < o.x + o.w && original.x + original.w > o.x && y < o.y + o.h && y + original.h > o.y) {y = o.y + o.h + 12; moved = true;}
    }
    return y;
  })();
  const yOffset = badgeY - original.y;
  const calloutWidth = calloutFitWidth(original, frame);
  return <div data-element={id} data-component={e.component ?? e.type} data-state={e.state} style={{position: 'absolute', left: value(shot, frame, id, 'x', e.x), top: value(shot, frame, id, 'y', e.y) + yOffset, width: calloutWidth ?? value(shot, frame, id, 'w', e.w), height: value(shot, frame, id, 'h', e.h), zIndex: e.z, boxSizing: 'border-box', visibility: visibleAt(e, frame, shot) ? 'visible' : 'hidden', ...style, ...motion(shot, frame, id)}}>{children}</div>;
};
export const TextLayer: React.FC<SceneProps & {id: string}> = ({shot, frame, id}) => {
  const e = resolvedElement(shot, element(shot, id), frame);
  if (e.type === 'rect') {
    if (value(shot, frame, id, 'w', e.w) <= .5 || value(shot, frame, id, 'h', e.h) <= .5) return null;
    return <Layer shot={shot} frame={frame} id={id} style={{background: colorToken(e.background ?? e.fill), borderRadius: e.radius, overflow: 'hidden'}} />;
  }
  // Keep every character in the final layout and fit Copy against the full text.
  const visibleCount = e.reveal?.mode === 'readAlong' ? e.reveal.frames.filter((f: number) => f <= frame).length : null;
  const revealedText = visibleCount === null ? null : Array.from(String(e.text ?? '')).map((character, i) => <span key={i} style={{color: i < visibleCount ? undefined : 'transparent'}}>{character}</span>);
  const chunks = e.stateKeyframes?.some(k => ['likeLit', 'allLit'].includes(k.state)) ? String(e.text).split(' · ') : null;
  const pulse = pulseAt(e, frame);
  // Knoll (EP.12 review): a left-aligned text bar with its own background that starts exactly on a browser window's left
  // border gets a 32 px left inset for its copy (the bar itself keeps its storyboard box).
  // EP.13: an authored `padLeft` wins; otherwise the EP.12 rule.
  const flushInset = typeof e.padLeft === 'number' ? e.padLeft : e.align === 'left' && (e.background ?? e.fill) && shot.elements.some(b => b.component === 'BrowserChrome' && b.x === e.x) ? 32 : 0;
  // Knoll (EP.13 vis1): a left-aligned text with a highlight border keeps its copy 10 px inside the border, and its pulse
  // scales from the aligned edge, so the first glyph is never cut by the layer's overflow clip.
  const hlInset = e.highlighted !== undefined && e.align === 'left' ? 10 : 0;
  return <Layer shot={shot} frame={frame} id={id} style={{paddingLeft: flushInset + hlInset || undefined, fontWeight: e.fontWeight, color: colorToken(e.color), background: colorToken(e.background ?? e.fill), borderRadius: e.radius, overflow: 'hidden', display: 'flex', alignItems: 'center', ...emphasisStyle(e), ...(e.strike ? {textDecorationLine: 'line-through', textDecorationColor: colorToken(e.strikeColor) ?? colorToken(e.color) ?? P_DANGER, textDecorationThickness: `${(e.fontSize ?? 40) * .08}px`} : {})}}><Copy text={e.text ?? ''} size={e.fontSize} width={e.w - flushInset - hlInset - (e.highlighted !== undefined ? 6 : 0)} height={e.h - (e.highlighted !== undefined ? 6 : 0)} mono={e.fontFamily === MONO} style={{fontFamily: e.fontFamily, textAlign: e.align, transform: `scale(${1 + pulse * .05})`, transformOrigin: e.align === 'left' ? 'left center' : e.align === 'right' ? 'right center' : 'center', boxShadow: pulse ? `0 0 ${pulse * 24}px ${colorToken(e.color) ?? '#22D3EE'}` : undefined}}>{revealedText ?? (chunks ? <span>{chunks.map((chunk, i) => <React.Fragment key={i}>{i > 0 && ' · '}<span data-action={i} data-lit={i === 0 || e.state === 'allLit' || (i === 1 && e.state === 'likeLit')} style={{opacity: i === 0 || e.state === 'allLit' || (i === 1 && e.state === 'likeLit') ? 1 : .35}}>{chunk}</span></React.Fragment>)}</span> : e.text)}</Copy></Layer>;
};
const StoryboardScene: React.FC<SceneProps> = ({shot, frame}) => <div data-camera-clip style={{position: 'absolute', inset: 0, clipPath: shot.camera ? `inset(0px 0px ${storyboard.meta.height - storyboard.meta.safeArea.contentMaxY}px 0px)` : undefined}}><div data-storyboard-scene data-camera={shot.camera?.target} style={{position: 'absolute', inset: 0, ...cameraStyle(shot, frame)}}>{shot.elements.filter(e => e.role !== 'subtitle' && e.binding !== 'subtitles').map(original => {
  const e = resolvedElement(shot, original, frame);
  const elementFrame = Math.max(e.appearFrame ?? 0, Math.min(frame, (e.disappearFrame ?? Infinity) - 1));
  return e.component ? <Layer key={e.id} shot={shot} frame={frame} id={e.id}><StoryboardComponent e={original} frame={frame} shot={shot} canvas={frameModeAt(shot.frame, shot.from + elementFrame) === 'canvas'} siblings={shot.elements} browserContentLayout={browserLayouts.get(shot)?.get(e.id)} /></Layer> : <TextLayer key={e.id} shot={shot} frame={frame} id={e.id} />;
})}</div></div>;
/** The shot registry, geometry, copy, and cue times all come from the storyboard. */
export const SHOT_SCENES: Record<string, React.FC<SceneProps>> = Object.fromEntries(shots.map(shot => {
  for (const e of shot.elements) if (e.component && !COMPONENTS[e.component]) throw new Error(`Unimplemented ${shot.id}/${e.component}`);
  const Scene: React.FC<SceneProps> = props => <StoryboardScene {...props} />;
  Scene.displayName = shot.id;
  return [shot.id, Scene];
}));
