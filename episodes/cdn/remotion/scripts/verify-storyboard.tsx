import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {existsSync, readFileSync, readdirSync} from 'node:fs';
import path from 'node:path';
import {parse} from '@babel/parser';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {SHOT_SCENES, cameraStyle, motion, resolvedElement, visibleAt, TextLayer} from '../src/ShotScenes';
import {shots, totalFrames, storyboard, ShotElement} from '../src/storyboard';
import {SHOT_LOCAL_STILL_FRAMES, SHOT_STILL_FRAMES} from '../src/shotFrames';
import {COVER_SIZES, Cover16x9, Cover4x3, Cover3x4} from '../src/Cover';
import covers from '../../covers.json';
import {MAIN_VIDEO} from '../src/Main';
import {RemotionRoot} from '../src/Root';
import {COMPONENTS, StoryboardComponent} from '../src/components/StoryboardComponent';
import {stateAt, fitSize, textWidth, pulseAt} from '../src/components/ui';
import {animatedValue} from '../src/animation';
import {browserContentLayout, browserHeaderHeight} from '../src/components/browserLayout';

assert.equal(createHash('sha256').update(readFileSync('../storyboard.json')).digest('hex'), '1818c6d7da95c0b47ea0b0bc198b49e777c8ce4c0a4c98cf884fb12b68f12e45');
assert.equal(totalFrames, storyboard.meta.durationInFrames);
assert.equal(MAIN_VIDEO.durationInFrames, totalFrames);
assert.deepEqual(COVER_SIZES, covers.sizes);
assert.equal(shots.length, 14);
assert.deepEqual(Object.keys(SHOT_SCENES), shots.map(s => s.id));
const allowed = new Set(['BrowserChrome', 'NotepadWindow', 'DevToolsNetwork', 'NetworkRow', 'RowHighlight', 'BlockHighlight', 'StyledPage', 'CalloutTag', 'CornerBadge']);
assert.deepEqual(new Set(Object.keys(COMPONENTS)), allowed);
const forbidden = /laptop|desk|cup|phone|router|keyboard|hand/i;
const walk = (dir: string): string[] => readdirSync(dir, {withFileTypes: true}).flatMap(entry => entry.isDirectory() ? walk(path.join(dir, entry.name)) : [path.join(dir, entry.name)]);
for (const filename of walk('src').filter(f => /\.[jt]sx?$/.test(f))) {
  assert(!forbidden.test(path.basename(filename).replace(/\.[^.]+$/, '')), `Forbidden component file ${filename}`);
  const ast = parse(readFileSync(filename, 'utf8'), {sourceType: 'module', plugins: ['typescript', ...(filename.endsWith('tsx') ? ['jsx' as const] : [])]});
  const visit = (node: any) => {
    if (!node || typeof node !== 'object') return;
    if (node.type === 'JSXOpeningElement') assert(!forbidden.test(node.name.name ?? node.name.property?.name ?? ''), `${filename}: physical component`);
    for (const child of Object.values(node)) if (Array.isArray(child)) child.forEach(visit); else if (child && typeof child === 'object') visit(child);
  };
  visit(ast);
}
for (const name of ['CertPopup', 'ScrambleText', 'FlyingLabel', 'ImagePlaceholder']) assert(!existsSync(`src/components/${name}.tsx`));
const shotById = (id: string) => shots.find(s => s.id === id)!;
const render = (id: string, frame: number) => {
  const Component = SHOT_SCENES[id];
  return renderToStaticMarkup(<Component shot={shotById(id)} frame={frame} />);
};
const componentMarkup = (e: ShotElement, frame: number) => renderToStaticMarkup(<StoryboardComponent e={e} frame={frame} />);
// Late annotations reserve the same content area at every sampled frame.
for (const shot of shots) for (const browser of shot.elements.filter(e => e.component === 'BrowserChrome')) {
  const layout = browserContentLayout(shot, browser);
  if (!layout || browser.pageBlank || !['shopDemo', 'loginForm'].includes(browser.page)) continue;
  assert(layout.height > 0 && layout.height <= browser.h - browserHeaderHeight(browser) - 6);
  for (const frame of [0, shot.durationInFrames - 1]) assert(render(shot.id, frame).includes(`data-content-height="${layout.height}"`), `${shot.id}: reserved content height`);
}
const layoutShot = shots.find(s => s.elements.some(e => e.component === 'CalloutTag'))!;
const layoutBrowser = layoutShot.elements.find(e => e.component === 'BrowserChrome')!;
const annotation = layoutShot.elements.find(e => e.component === 'CalloutTag')!;
const withAnnotation = (e: ShotElement) => browserContentLayout({...layoutShot, elements: [layoutBrowser, e], animations: []}, layoutBrowser);
for (const e of [
  {...annotation, component: 'CornerBadge'}, {...annotation, component: 'NetworkRow'},
  {...annotation, component: 'RowHighlight'}, {...annotation, component: 'BlockHighlight'},
  {...annotation, component: 'DevToolsNetwork'}, {...annotation, role: 'subtitle'},
  {...annotation, binding: 'subtitles'}, {...annotation, x: layoutBrowser.x - 1},
  {...annotation, y: layoutBrowser.y + 90}, {...annotation, state: 'hidden'},
  {...annotation, opacity: 0}, {...annotation, appearFrame: layoutShot.durationInFrames},
  {...annotation, disappearFrame: 0},
]) assert.equal(withAnnotation(e), undefined);
assert(withAnnotation({...annotation, state: 'hidden', stateKeyframes: [{frame: 100, state: 'shown'}]}));
assert.equal(withAnnotation({...annotation, state: 'hidden', stateKeyframes: [{frame: layoutShot.durationInFrames, state: 'shown'}]}), undefined);
const validateMarkup = (markup: string, label: string) => assert(!/NaN|Infinity|undefinedpx/.test(markup), `${label}: invalid geometry`);
let samples = 0, expectedFrom = 0;
for (const shot of shots) {
  assert.equal(shot.from, expectedFrom);
  expectedFrom += shot.durationInFrames;
  const still = SHOT_LOCAL_STILL_FRAMES[shot.id];
  assert(still >= 0 && still < shot.durationInFrames);
  assert.equal(SHOT_STILL_FRAMES[shot.id], shot.from + still);
  const frames = new Set([0, still, shot.durationInFrames - 1]);
  for (const e of shot.elements) {
    if (e.component) assert(allowed.has(e.component));
    const keys = [e.appearFrame, e.disappearFrame, ...(e.stateKeyframes ?? []).flatMap(k => [k.frame, k.frame + (k.fadeFrames ?? (k.pulse ? 10 : 0))]), ...shot.animations.filter(a => a.elementId === e.id).flatMap(a => a.keyframes.map(k => k.frame))];
    for (const f of keys) if (f !== undefined) for (const offset of [-1, 0, 1]) if (f + offset >= 0 && f + offset < shot.durationInFrames) frames.add(f + offset);
    // Every authored property persists until its next replacement.
    for (const key of e.stateKeyframes ?? []) {
      const resolved = resolvedElement(shot, e, key.frame);
      for (const [prop, value] of Object.entries(key)) assert.deepEqual(resolved[prop], value);
    }
    if (!e.component && e.role !== 'subtitle') {
      for (const f of frames) {
        const text = stateAt(e, f);
        const size = fitSize(text.text, text.w, text.fontSize, false, text.h);
        assert(Math.max(...text.text.split('\n').map(line => textWidth(line, size))) <= text.w);
        assert(size * 1.2 * text.text.split('\n').length <= text.h + .001);
      }
    }
  }
  for (const frame of frames) {
    const markup = render(shot.id, frame);
    validateMarkup(markup, `${shot.id}/${frame}`);
    for (const e of shot.elements.filter(e => e.role !== 'subtitle')) {
      assert(markup.includes(`data-element="${e.id}"`), `${shot.id}: lost ${e.id}`);
      const opacity = Number(motion(shot, frame, e.id).opacity);
      assert(opacity >= 0 && opacity <= 1);
      if (!visibleAt(e, frame)) assert.equal(opacity, 0);
    }
    samples++;
  }
  for (const animation of shot.animations) for (const key of animation.keyframes) assert.equal(animatedValue(shot, animation.elementId, animation.property, key.frame, 0), key.value);
  if (shot.camera) for (const key of shot.camera.keyframes) assert.equal(cameraStyle(shot, key.frame).transform, `scale(${key.scale})`);
}
assert.equal(expectedFrom, totalFrames);
// Cumulative append events survive later, unrelated state changes.
const terminal: ShotElement = {id: 'terminal', component: 'NotepadWindow', variant: 'terminal', x: 100, y: 100, w: 800, h: 500, lines: [{text: 'first', x: 150, y: 200}], stateKeyframes: [{frame: 5, appendLine: {text: 'second', x: 150, y: 250}}, {frame: 10, highlightLines: [1]}, {frame: 15, appendLine: {text: 'third', x: 150, y: 300}}]};
assert(!componentMarkup(terminal, 4).includes('second'));
for (const f of [5, 10, 15, 100]) assert.equal([...componentMarkup(terminal, f).matchAll(/>second</g)].length, 1);
assert(componentMarkup(terminal, 15).includes('>third<'));
assert(componentMarkup(terminal, 0).includes('left:50px;top:100px'));
// Audit every authored visual field, including cover and state-only fields.
const common = 'id type component x y w h z aspect appearFrame disappearFrame opacity state stateKeyframes fontSize fontFamily fontWeight color background fill radius align timingRole timingReason cueText cueOnset disappearCueText overlayOk frame onsetLocal';
const supported: Record<string, string> = {
  text: 'text role binding opacityTo fadeFrames durationFrames pulse highlighted dim expiryMark secondLineColor',
  BrowserChrome: 'pressed title url showPadlock page pageTitle cards loginButton loginFields reloading conflict userBadge sampleData pageNote pageNoteColor',
  DevToolsNetwork: 'title panel layout columns rows emptyText request headerSection headers hideOthers singleLine dimOthers dimOpacity storageOrigin visibleRows consoleLines highlightRows sampleData sampleLabel',
  NetworkRow: 'cells',
  CornerBadge: 'text conflict sampleData pulse escalation pageNote pageNoteColor simulated expiryMark highlighted dim',
  CalloutTag: 'text sampleData expiryMark highlighted dim pulse',
  RowHighlight: 'highlightText', BlockHighlight: 'highlightText',
  StyledPage: 'variant placeholder cursorBlink text title lines sampleData sampleLabel',
};
for (const e of [...shots.flatMap(s => s.elements), ...Object.values(COVER_SIZES).flatMap(c => c.elements)] as ShotElement[]) {
  const allowedKeys = new Set((common + ' ' + supported[e.component ?? 'text']).split(' '));
  for (const source of [e, ...(e.stateKeyframes ?? [])]) for (const key of Object.keys(source)) assert(allowedKeys.has(key), `${e.id}: unhandled ${key}`);
}
const escaped = (text: string) => renderToStaticMarkup(<>{text}</>);
for (const shot of shots) for (const e of shot.elements) {
  const markup = e.component ? componentMarkup(e, 0) : '';
  if (e.component === 'BrowserChrome') {
    if (e.showPadlock) assert(markup.includes('data-address-icon="lock"'));
    if (e.pageNote) assert(markup.includes(escaped(e.pageNote)), `${shot.id}: initial pageNote`);
    for (const key of e.stateKeyframes ?? []) {
      if (key.state === 'reloaded') {
        assert(componentMarkup(e, key.frame - 1).includes('data-refresh-pressed="true"'));
        assert(componentMarkup(e, key.frame - 1).includes('data-reload-indicator'));
        assert(componentMarkup(e, key.frame).includes('data-reloading="false"'));
        assert(!componentMarkup(e, key.frame).includes('data-reload-indicator'));
      }
      if (key.pageNote) assert(componentMarkup(e, key.frame).includes(escaped(key.pageNote)));
      if (key.url) assert(componentMarkup(e, key.frame).includes(escaped(key.url)));
      if (key.loginFields) {
        const filled = componentMarkup(e, key.frame);
        assert(filled.includes(escaped(key.loginFields.account)));
        assert(filled.includes('•'.repeat(Array.from(key.loginFields.password).length)));
      }
      if (key.pressed === 'login') {
        assert(componentMarkup(e, key.frame - 1).includes('data-login-pressed="false"'));
        const pressed = componentMarkup(e, key.frame);
        assert(pressed.includes('data-login-pressed="true"'));
        assert(pressed.includes('translateY(3px) scale(.96)'));
        const next = e.stateKeyframes.find(k => k.frame > key.frame);
        if (next) {
          assert(componentMarkup(e, next.frame - 1).includes('data-login-pressed="true"'));
          assert(componentMarkup(e, next.frame).includes('data-login-pressed="false"'));
        }
      }
    }
    if (e.page === 'loginForm') {
      const secret = 'plain-secret';
      const masked = componentMarkup({...e, stateKeyframes: [], loginFields: {...e.loginFields, password: secret}}, 0);
      assert(masked.includes('•'.repeat(secret.length)));
      assert(!masked.includes(secret));
    }
  }
  if (e.sampleData) assert(markup.includes('data-sample-data="true"'));
  if (e.component === 'DevToolsNetwork') {
    assert(markup.includes(`data-panel="${e.panel}"`));
    for (const header of e.headers ?? []) {
      const top = e.singleLine ? 0 : header.y - e.y - 3;
      assert(markup.includes(`left:${header.x - e.x - 3}px;top:${top}`));
      assert(markup.includes(`data-role="${header.role}"`));
      assert(markup.includes(escaped(`${header.name}: ${header.value}`)));
      if (e.singleLine) {
        assert(markup.includes(`height:${e.h - 6}px;display:flex;align-items:center`));
        assert(markup.includes(`font-size:${header.fontSize}px`));
      }
    }
    if (e.hideOthers) {
      assert(!markup.includes('data-panel-title'));
      assert(!markup.includes(escaped(e.request)));
      assert(!markup.includes(escaped(e.headerSection)));
      assert(!markup.includes('role="row"'));
      assert.equal([...markup.matchAll(/data-header-line=/g)].length, e.headers.length);
      const footer = {...e, sampleLabel: storyboard.meta.sampleDataLabel};
      assert(!componentMarkup(footer, 0).includes(escaped(footer.sampleLabel)));
      // Both flags work independently; ordinary panels keep their scene coordinates.
      const normal = componentMarkup({...e, hideOthers: false, singleLine: false}, 0);
      assert(normal.includes('data-panel-title'));
      assert(normal.includes(escaped(e.request)));
      assert(normal.includes(escaped(e.headerSection)));
      assert(normal.includes(`left:${e.headers[0].x - e.x - 3}px;top:${e.headers[0].y - e.y - 3}px`));
      const lineOnly = componentMarkup({...e, hideOthers: false}, 0);
      assert(lineOnly.includes('data-panel-title'));
      assert(lineOnly.includes('align-items:center'));
      const hiddenOnly = componentMarkup({...e, singleLine: false}, 0);
      assert(!hiddenOnly.includes('data-panel-title'));
      assert(hiddenOnly.includes(`top:${e.headers[0].y - e.y - 3}px`));
    }
  }
  for (const key of e.stateKeyframes ?? []) {
    if (key.opacityTo === 0) {
      assert.equal(motion(shot, key.frame, e.id).opacity, 1);
      assert.equal(motion(shot, key.frame + key.fadeFrames / 2, e.id).opacity, .5);
      assert.equal(motion(shot, key.frame + key.fadeFrames, e.id).opacity, 0);
    }
    if (key.pulse) {
      assert.equal(pulseAt(e, key.frame - 1), 0);
      assert.equal(pulseAt(e, key.frame + 5), 1);
      assert.equal(pulseAt(e, key.frame + 10), 0);
      assert(componentMarkup(e, key.frame + 5).includes('data-pulse="true"'));
      assert(!componentMarkup(e, key.frame + 10).includes('box-shadow'));
      assert.equal(pulseAt({...e, stateKeyframes: [...e.stateKeyframes, {frame: key.frame + 3, text: e.text}]}, key.frame + 5), 1);
      if (key.pageNote) assert(render(shot.id, key.frame).includes(escaped(key.pageNote)));
    }
    if (!e.component && key.text !== undefined) {
      const textMarkup = (frame: number) => renderToStaticMarkup(<TextLayer shot={shot} frame={frame} id={e.id} />);
      const previous = stateAt(e, key.frame - 1);
      assert(textMarkup(key.frame - 1).includes(escaped(previous.text)));
      for (const frame of [key.frame, shot.durationInFrames - 1]) {
        const resolved = stateAt(e, frame), updated = textMarkup(frame);
        assert(updated.includes(escaped(resolved.text)));
        assert(!updated.includes(escaped(previous.text)));
        assert(updated.includes(`color:${resolved.color}`));
        assert(!updated.includes(`color:${previous.color}`));
      }
    }
  }
  if (e.component === 'StyledPage' && e.variant === 'commentBox') {
    assert(componentMarkup(e, e.appearFrame).includes(escaped(e.placeholder)));
    assert(componentMarkup(e, e.appearFrame).includes('data-comment-cursor'));
    assert(componentMarkup(e, 0).includes('opacity:1'));
    assert(componentMarkup(e, 15).includes('opacity:0'));
  }
  if (e.stateKeyframes?.some(k => k.state === 'likeLit')) {
    for (const [state, lit] of [['initial', 1], ['likeLit', 2], ['allLit', 3]] as const) {
      const frame = e.stateKeyframes.find(k => k.state === state).frame;
      const actions = render(shot.id, frame);
      assert.equal([...actions.matchAll(/data-lit="true"/g)].length, lit);
    }
  }
}
for (const [size, Component] of Object.entries({'16x9': Cover16x9, '4x3': Cover4x3, '3x4': Cover3x4})) {
  const cover = COVER_SIZES[size], markup = renderToStaticMarkup(<Component />);
  validateMarkup(markup, size);
  for (const e of cover.elements) {
    assert(markup.includes(`data-element="${e.id}"`));
    assert(e.x >= 0 && e.y >= 0 && e.x + e.w <= cover.width && e.y + e.h <= cover.bottom15Y);
    if ('centerRegion' in cover) assert(e.x >= cover.centerRegion[0] && e.x + e.w <= cover.centerRegion[1]);
    if ('component' in e) assert.equal(e.w / e.h, 3 / 2);
    if ('text' in e) for (const line of e.text.split('\n')) assert(markup.includes(escaped(line)));
  }
  const left = cover.elements.find(e => e.id === 'window-left') as ShotElement;
  const right = cover.elements.find(e => e.id === 'window-right') as ShotElement;
  for (const text of [left.userBadge, left.pageNote, right.title, right.sampleLabel, ...right.lines.map(line => line.text)]) assert(markup.includes(escaped(text)));
  assert(markup.includes('data-user-badge'));
  assert(markup.includes('data-address-icon="lock"'));
  assert(markup.includes('data-variant="sessionDemo"'));
  assert.equal([...markup.matchAll(/data-session-line=/g)].length, right.lines.length);
  const demo = componentMarkup(right, 0);
  for (const [i, line] of right.lines.entries()) assert(demo.includes(`data-session-line="${i}" data-highlighted="${line.highlight}"`));
  assert.equal([...demo.matchAll(/data-highlighted="true"/g)].length, right.lines.filter(line => line.highlight).length);
  assert(!markup.includes('data-panel='));
  assert(markup.includes('data-watermark'));
  assert(markup.includes(escaped(covers.watermark.text)));
}
// Inspect registered props without rendering video or requiring a player context.
const compositions = React.Children.toArray((RemotionRoot({}) as React.ReactElement).props.children) as React.ReactElement[];
const mainComposition = compositions.find(c => c.props.id === 'Main')!;
assert.deepEqual(Object.fromEntries(['width', 'height', 'fps', 'durationInFrames'].map(key => [key, mainComposition.props[key]])), MAIN_VIDEO);
for (const [size, cover] of Object.entries(COVER_SIZES)) {
  const composition = compositions.find(c => c.props.id === `Cover${size}`)!;
  assert.equal(composition.props.width, cover.width);
  assert.equal(composition.props.height, cover.height);
}
const main = readFileSync('src/Main.tsx', 'utf8');
assert.equal([...main.matchAll(/<Audio\b/g)].length, 1);
assert(main.includes("staticFile('audio/voice.wav')"));
assert(main.includes('from={shot.from} durationInFrames={shot.durationInFrames}'));
assert(main.includes('shot.subtitles.find'));
console.log(`Verified frozen 1818c6d7: ${shots.length} shots, ${samples} boundary samples, single-line headers, login press, initial notes, text replacement and session-demo states, text fitting, animations, ${Object.keys(COVER_SIZES).length} covers, continuous audio, and no physical components.`);
