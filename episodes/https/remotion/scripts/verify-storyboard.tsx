import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync, readdirSync} from 'node:fs';
import path from 'node:path';
import {parse} from '@babel/parser';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {SHOT_SCENES, cameraStyle, motion, resolvedElement, visibleAt} from '../src/ShotScenes';
import {shots, totalFrames, storyboard, ShotElement} from '../src/storyboard';
import {SHOT_LOCAL_STILL_FRAMES, SHOT_STILL_FRAMES} from '../src/shotFrames';
import {COVER_SIZES, Cover16x9, Cover4x3, Cover3x4} from '../src/Cover';
import {COMPONENTS} from '../src/components/StoryboardComponent';
import {stateAt} from '../src/components/ui';
import {animatedValue} from '../src/animation';

assert.equal(createHash('sha256').update(readFileSync('../storyboard.json')).digest('hex'), '3c51e3d80b49759faa03af91894ca6bce7e5ce16b5b5a5caa10543436e2a0f38');
assert.equal(totalFrames, 4991);
assert.equal(shots.length, 23);
assert.deepEqual(Object.keys(SHOT_SCENES), shots.map(s => s.id));
assert.equal(new Set(Object.values(SHOT_SCENES)).size, shots.length);
const forbidden = /laptop|desk|table|cup|phone|router|keyboard|hand/i;
const allowed = new Set(['BrowserChrome', 'NotepadWindow', 'DevToolsNetwork', 'NetworkRow', 'RowHighlight', 'CertPopup', 'ScrambleText', 'KeyIcon', 'FlyingLabel', 'ArrowLabel', 'AddressBarTyping', 'WifiIcon', 'LockIcon', 'StyledPage', 'CalloutTag', 'CornerBadge', 'RedPulseOutline', 'BlockHighlight']);
assert.deepEqual(new Set(Object.keys(COMPONENTS)), allowed);
// Inspect actual JSX component names and component registries, never semantic ids
// such as the frozen "impersonator-laptop" or the TLS handshake shot names.
const walk = (dir: string): string[] => readdirSync(dir, {withFileTypes: true}).flatMap(entry => entry.isDirectory() ? walk(path.join(dir, entry.name)) : [path.join(dir, entry.name)]);
for (const filename of walk('src').filter(f => /\.[jt]sx?$/.test(f))) {
  assert(!forbidden.test(path.basename(filename).replace(/\.[^.]+$/, '')), `Forbidden component file ${filename}`);
  const ast = parse(readFileSync(filename, 'utf8'), {sourceType: 'module', plugins: ['typescript', ...(filename.endsWith('tsx') ? ['jsx' as const] : [])]});
  const visit = (node: any) => {
    if (!node || typeof node !== 'object') return;
    if (['JSXOpeningElement', 'JSXSelfClosingElement'].includes(node.type)) {
      const name = node.name;
      const component = name.type === 'JSXIdentifier' ? name.name : name.property?.name;
      assert(!forbidden.test(component ?? ''), `${filename}: forbidden rendered component ${component}`);
    }
    for (const child of Object.values(node)) if (Array.isArray(child)) child.forEach(visit); else if (child && typeof child === 'object') visit(child);
  };
  visit(ast);
}
const shotById = (id: string) => shots.find(s => s.id === id)!;
const find = (id: string, elementId: string) => shotById(id).elements.find(e => e.id === elementId)!;
const change = (id: string, elementId: string, state: string) => find(id, elementId).stateKeyframes.find(k => k.state === state).frame;
const render = (id: string, frame: number) => {
  const Component = SHOT_SCENES[id];
  return renderToStaticMarkup(<Component shot={shotById(id)} frame={frame} />);
};
const validateMarkup = (markup: string, label: string) => {
  assert(!/NaN|Infinity|undefinedpx/.test(markup), `${label}: invalid geometry`);
  for (const match of markup.matchAll(/font-size:([\d.]+)px/g)) assert(Number(match[1]) >= 24, `${label}: undersized text ${match[1]}`);
  for (const match of markup.matchAll(/data-component="([^"]*)"/g)) assert(!forbidden.test(match[1]), `${label}: forbidden rendered component ${match[1]}`);
};
let samples = 0;
let expectedFrom = 0;
for (const shot of shots) {
  assert.equal(shot.from, expectedFrom);
  expectedFrom += shot.durationInFrames;
  const still = SHOT_LOCAL_STILL_FRAMES[shot.id];
  assert(still >= 0 && still < shot.durationInFrames);
  assert.equal(SHOT_STILL_FRAMES[shot.id], shot.from + still);
  const frames = new Set([0, still, shot.durationInFrames - 1]);
  for (const e of shot.elements) {
    if (e.component) assert(allowed.has(e.component), `${shot.id}: unsupported ${e.component}`);
    assert(!('device' in e || 'hand' in e));
    for (const f of [e.appearFrame, e.disappearFrame, ...(e.stateKeyframes ?? []).map(k => k.frame), ...shot.animations.filter(a => a.elementId === e.id).flatMap(a => a.keyframes.map(k => k.frame))]) {
      if (f !== undefined) for (const offset of [-1, 0, 1]) if (f + offset >= 0 && f + offset < shot.durationInFrames) frames.add(f + offset);
    }
  }
  for (const frame of frames) {
    const markup = render(shot.id, frame);
    validateMarkup(markup, `${shot.id}/${frame}`);
    for (const e of shot.elements.filter(e => e.id !== 'subtitle')) assert(markup.includes(`data-element="${e.id}"`), `${shot.id}: lost ${e.id}`);
    samples++;
  }
  for (const line of shot.subtitles) assert(/[\p{L}\p{Script=Han}]/u.test(line.text), `${shot.id}: punctuation-only subtitle`);
  for (const animation of shot.animations) for (const key of animation.keyframes) assert.equal(animatedValue(shot, animation.elementId, animation.property, key.frame, 0), key.value);
  if (shot.camera) for (const key of shot.camera.keyframes) assert.equal(cameraStyle(shot, key.frame).transform, `scale(${key.scale})`);
}
assert.equal(expectedFrom, totalFrames);
// Exact-frame state regressions from the NEW storyboard.
const reveal = change('03-password-dots', 'f3-pass', 'revealed');
assert(!render('03-password-dots', reveal - 1).includes('qwer1234'));
assert(render('03-password-dots', reveal).includes('qwer1234'));
assert(!render('03-password-dots', change('03-password-dots', 'f3-pass', 'masked')).includes('qwer1234'));
const cert = find('14-signature-proof', 'cert');
const edited = change('14-signature-proof', 'cert', 'subjectEdited');
assert(render('14-signature-proof', edited).includes(stateAt(cert, edited).editedText));
assert(render('14-signature-proof', change('14-signature-proof', 'cert', 'signatureMismatch')).includes('data-signature-mark="✗"'));
assert(render('13-check-certificate', change('13-check-certificate', 'cert-chain', 'accepted')).includes('border:3px solid #22C55E'));
const failure = change('15a-copied-certificate-fails', 'proof-browser', 'secureConnectionFailed');
for (const frame of [failure, shotById('15a-copied-certificate-fails').durationInFrames - 1]) {
  const markup = render('15a-copied-certificate-fails', frame);
  assert(markup.includes('data-error="安全连接失败"'));
  assert(!markup.includes('data-address-icon="lock"'));
}
const recovery = shotById('15b-copied-certificate-fails');
const fading = recovery.elements.find(e => e.disappearFrame !== undefined)!;
assert.equal(motion(recovery, 0, fading.id).opacity, 1);
assert.equal(motion(recovery, fading.disappearFrame / 2, fading.id).opacity, .5);
assert.equal(motion(recovery, fading.disappearFrame, fading.id).opacity, 0);
assert(render(recovery.id, 0).includes('data-address-icon="lock"'));
assert(!render(recovery.id, 0).includes('⚠'));
assert(render(recovery.id, change(recovery.id, 'proof-browser', 'stopwatchShown')).includes('data-stopwatch='));
assert(render('16a-tls-handshake', change('16a-tls-handshake', 'row1', 'timingHighlighted')).includes('data-cell="2" data-highlighted="true"'));
assert.equal(motion(shotById('16b-tls-handshake'), change('16b-tls-handshake', 'row1', 'dimmed'), 'row1').opacity, .4);
const tamper = render('17b-tamper-rejected', change('17b-tamper-rejected', 'record', 'byteEdited'));
assert.equal([...tamper.matchAll(/data-edited-byte=/g)].length, 1);
const close = change('18b-question', 'phishing-address', 'tabClosed');
const page = resolvedElement(shotById('18b-question'), find('18b-question', 'phish'), close);
assert.equal(page.url, ''); assert.equal(page.showPadlock, false);
assert.equal(resolvedElement(shotById('18b-question'), find('18b-question', 'fp-urgent'), close).state, 'hidden');
assert(render('18a-phishing-also-has-lock', change('18a-phishing-also-has-lock', 'phishing-address', 'domainHighlighted')).includes('data-url-segment="-verify"'));
assert(render('19-next-dns', change('19-next-dns', 'typing', 'typedComplete')).includes('data-typed-address="true">shop.example'));
const firstKeys = shotById('10-key-exchange').elements.filter(e => e.component === 'KeyIcon');
assert.equal(firstKeys.length, 2); assert.equal(firstKeys[0].pairId, firstKeys[1].pairId);
for (const [size, Component] of Object.entries({ '16x9': Cover16x9, '4x3': Cover4x3, '3x4': Cover3x4 })) {
  const cover = COVER_SIZES[size];
  const markup = renderToStaticMarkup(<Component />);
  validateMarkup(markup, size);
  for (const text of ['qwer1234', '••••••', 'IT小村', '连接不安全', '热点控制者看到的内容']) assert(markup.includes(text));
  assert(markup.includes('data-password-highlight="qwer1234"'));
  assert(!markup.includes('data-address-icon="lock"'));
  const windows = cover.elements.filter(e => 'component' in e);
  assert.deepEqual(windows.map(e => e.component), ['BrowserChrome', 'NotepadWindow']);
  for (const e of cover.elements) {
    assert(e.x >= 0 && e.y >= 0 && e.x + e.w <= cover.width && e.y + e.h <= cover.bottom15Y);
    if ('centerRegion' in cover) assert(e.x >= cover.centerRegion[0] && e.x + e.w <= cover.centerRegion[1]);
  }
  for (const e of windows) assert.equal(e.w / e.h, 3 / 2);
}
// Timeline/audio contract remains the original continuous soundtrack + frozen sequences.
const main = readFileSync('src/Main.tsx', 'utf8');
assert.equal([...main.matchAll(/<Audio\b/g)].length, 1);
assert(main.includes("staticFile('audio/voice.wav')"));
assert(main.includes('from={shot.from} durationInFrames={shot.durationInFrames}'));
assert(main.includes('shot.subtitles.find'));
console.log(`Verified frozen 3c51e3d8: ${shots.length} shots, ${samples} boundary samples, states/animations/cameras, ${Object.keys(COVER_SIZES).length} covers, continuous audio, text >=24px, and no rendered physical components.`);
