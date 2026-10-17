import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {existsSync, readFileSync, readdirSync} from 'node:fs';
import path from 'node:path';
import {parse} from '@babel/parser';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {SHOT_SCENES, cameraStyle, motion, resolvedElement, visibleAt} from '../src/ShotScenes';
import {shots, totalFrames, ShotElement} from '../src/storyboard';
import {SHOT_LOCAL_STILL_FRAMES, SHOT_STILL_FRAMES} from '../src/shotFrames';
import {COVER_SIZES, Cover16x9, Cover4x3, Cover3x4} from '../src/Cover';
import {COMPONENTS, StoryboardComponent} from '../src/components/StoryboardComponent';
import {stateAt, fitSize, textWidth} from '../src/components/ui';
import {animatedValue} from '../src/animation';

assert.equal(createHash('sha256').update(readFileSync('../storyboard.json')).digest('hex'), '4af2331bba205c7e1cfe856195ae137d2caecd4b8361db30d618000c823ec369');
assert.equal(totalFrames, 3757);
assert.equal(shots.length, 16);
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
const find = (id: string, elementId: string) => shotById(id).elements.find(e => e.id === elementId)!;
const change = (id: string, elementId: string, state: string) => find(id, elementId).stateKeyframes.find(k => k.state === state).frame;
const render = (id: string, frame: number) => {
  const Component = SHOT_SCENES[id];
  return renderToStaticMarkup(<Component shot={shotById(id)} frame={frame} />);
};
const componentMarkup = (e: ShotElement, frame: number) => renderToStaticMarkup(<StoryboardComponent e={e} frame={frame} />);
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
    const keys = [e.appearFrame, e.disappearFrame, ...(e.stateKeyframes ?? []).flatMap(k => [k.frame, k.frame + (k.fadeFrames ?? 0)]), ...shot.animations.filter(a => a.elementId === e.id).flatMap(a => a.keyframes.map(k => k.frame))];
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
for (const id of ['05-local-cache', '08-root-refers']) {
  const e = shotById(id).elements.find(e => e.stateKeyframes?.some(k => k.appendLine))!;
  const key = e.stateKeyframes.find(k => k.appendLine);
  assert(!componentMarkup(e, key.frame - 1).includes(key.appendLine.text));
  assert(componentMarkup(e, key.frame).includes(key.appendLine.text));
  assert(componentMarkup(e, shotById(id).durationInFrames - 1).includes(key.appendLine.text));
}
const resolver = find('06-recursive-resolver', 'resolver');
assert(componentMarkup(resolver, 0).includes('display:none'));
assert(!componentMarkup(resolver, change('06-recursive-resolver', 'resolver', 'line2')).includes('display:none'));
assert(componentMarkup(resolver, change('06-recursive-resolver', 'resolver', 'line1')).includes('opacity:0.35'));
const hook = shotById('01-hook');
const fading = find(hook.id, 'cover-title').stateKeyframes.find(k => k.opacityTo === 0);
assert.equal(motion(hook, fading.frame, 'cover-title').opacity, 1);
assert.equal(motion(hook, fading.frame + fading.fadeFrames / 2, 'cover-title').opacity, .5);
assert.equal(motion(hook, fading.frame + fading.fadeFrames, 'cover-title').opacity, 0);
assert(render(hook.id, fading.frame).includes('页面还空着'));
const slow = find('03-slow-motion', 'browser'), slowFrame = change('03-slow-motion', 'browser', 'slowMotion');
assert(componentMarkup(slow, slowFrame).includes('data-spinner-speed="0.1"'));
assert(componentMarkup(slow, slowFrame + 1).includes(`rotate(${(slowFrame + .1) * 10}deg)`));
const ttl = shotById('11-ttl'), old = find(ttl.id, 'term-ttl'), swap = old.disappearFrame;
assert.equal(motion(ttl, swap - 3, old.id).opacity, .5);
for (const e of ttl.elements.filter(e => e.disappearFrame !== undefined)) {
  assert(visibleAt(e, swap - 1)); assert(!visibleAt(e, swap));
}
assert(!visibleAt(find(ttl.id, 'about-net'), swap - 1));
assert(visibleAt(find(ttl.id, 'about-net'), swap));
assert(componentMarkup(find(ttl.id, 'about-net'), swap).includes('data-dns-record'));
const load = '13-page-starts-loading', browser = find(load, 'browser'), row = find(load, 'row-doc');
for (const key of row.stateKeyframes.slice(1)) for (const cell of key.cells) assert(componentMarkup(row, key.frame).includes(cell));
const titleFrame = change(load, 'browser', 'titleShown'), cardsFrame = change(load, 'browser', 'cardsShown');
assert(!componentMarkup(browser, titleFrame - 1).includes(browser.pageTitle));
assert(componentMarkup(browser, titleFrame).includes(browser.pageTitle));
assert(!componentMarkup(browser, titleFrame).includes('data-shop-cards'));
assert(componentMarkup(browser, cardsFrame).includes('data-shop-cards'));
assert(!componentMarkup(browser, cardsFrame).includes('data-tab-loading'));
const comment = find('14b-question', 'comment-box');
assert(componentMarkup(comment, 0).includes('opacity:1'));
assert(componentMarkup(comment, 15).includes('opacity:0'));
const followShot = '15-next-cookie', follow = find(followShot, 'follow');
for (const [state, lit] of [['initial', 1], ['likeLit', 2], ['allLit', 3]] as const) {
  const markup = render(followShot, change(followShot, follow.id, state));
  assert.equal([...markup.matchAll(/data-lit="true"/g)].length, lit);
  assert(markup.includes('background:#22D3EE'));
}
const storage = componentMarkup(find(followShot, 'devtools'), 0);
assert(storage.includes('data-panel="storage"'));
assert(storage.includes('（还没有 Cookie）'));
// The same browser uses short cards only while its sibling docked panel is present.
const shopCardMarkup = (markup: string) => markup.match(/data-shop-cards([\s\S]*?)<\/svg>/)![1];
const endingBrowser = find(followShot, 'browser'), endingPanel = find(followShot, 'devtools');
const browserWithPanel = (panel: ShotElement, frame: number) => renderToStaticMarkup(<StoryboardComponent e={endingBrowser} frame={frame} siblings={[endingBrowser, panel]} />);
assert(shopCardMarkup(render(followShot, 150)).includes('height:70px'));
assert(shopCardMarkup(render('14b-question', 150)).includes('height:146px'));
assert(shopCardMarkup(componentMarkup(endingBrowser, 150)).includes('height:146px'));
assert(shopCardMarkup(browserWithPanel({...endingPanel, appearFrame: 10}, 9)).includes('height:146px'));
assert(shopCardMarkup(browserWithPanel({...endingPanel, appearFrame: 10}, 10)).includes('height:70px'));
assert(shopCardMarkup(browserWithPanel({...endingPanel, layout: 'standalone'}, 10)).includes('height:146px'));
assert(shopCardMarkup(browserWithPanel({...endingPanel, x: endingBrowser.x + endingBrowser.w}, 10)).includes('height:146px'));
for (const [size, Component] of Object.entries({'16x9': Cover16x9, '4x3': Cover4x3, '3x4': Cover3x4})) {
  const cover = COVER_SIZES[size], markup = renderToStaticMarkup(<Component />);
  validateMarkup(markup, size);
  for (const e of cover.elements) {
    assert(markup.includes(`data-element="${e.id}"`));
    assert(e.x >= 0 && e.y >= 0 && e.x + e.w <= cover.width && e.y + e.h <= cover.bottom15Y);
    if ('centerRegion' in cover) assert(e.x >= cover.centerRegion[0] && e.x + e.w <= cover.centerRegion[1]);
  }
  for (const text of ['服务器在哪？', 'shop.example', '203.0.113.10', '查询结果', 'IT小村']) assert(markup.includes(text));
  assert(markup.includes('data-tab-loading'));
  assert(markup.includes('data-terminal-line="1" data-role="answer" data-highlighted="true"'));
  assert(!markup.includes('data-address-icon="lock"'));
  for (const e of cover.elements.filter(e => 'component' in e)) assert.equal(e.w / e.h, 3 / 2);
}
const main = readFileSync('src/Main.tsx', 'utf8');
assert.equal([...main.matchAll(/<Audio\b/g)].length, 1);
assert(main.includes("staticFile('audio/voice.wav')"));
assert(main.includes('from={shot.from} durationInFrames={shot.durationInFrames}'));
assert(main.includes('shot.subtitles.find'));
console.log(`Verified frozen 4af2331b: ${shots.length} shots, ${samples} boundary samples, terminal/browser states, animations/camera, ${Object.keys(COVER_SIZES).length} covers, continuous audio, and no physical components.`);
