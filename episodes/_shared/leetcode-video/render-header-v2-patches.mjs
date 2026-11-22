#!/usr/bin/env node
/**
 * Render frozen 734x56 header title patch PNGs directly from FrameV2.tsx in real
 * Headless Chrome at 1920x1080 for existing LeetCode episodes.
 *
 * Usage:
 *   node episodes/_shared/leetcode-video/render-header-v2-patches.mjs [--slugs a,b] [--revision header-title-v2]
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../../..');
const PATCH_RECT = {x: 486, y: 44, width: 734, height: 56};

const args = process.argv.slice(2);
const options = {revision: 'header-title-v2'};
for (let i = 0; i < args.length; i += 2) {
  if (!['--slugs', '--revision', '--remotion-dir', '--browser'].includes(args[i]) || args[i + 1] === undefined) {
    throw new Error('Usage: render-header-v2-patches.mjs [--slugs a,b] [--revision NAME] [--remotion-dir DIR] [--browser PATH]');
  }
  options[args[i].slice(2)] = args[i + 1];
}

function shaFile(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function findRemotionDir() {
  if (options['remotion-dir']) return path.resolve(options['remotion-dir']);
  const leetcodeRoot = path.join(repo, 'episodes/leetcode');
  for (const entry of fs.readdirSync(leetcodeRoot, {withFileTypes: true})) {
    if (!entry.isDirectory()) continue;
    const candidate = path.join(leetcodeRoot, entry.name, 'production/remotion');
    if (
      fs.existsSync(path.join(candidate, 'node_modules/esbuild')) &&
      fs.existsSync(path.join(candidate, 'node_modules/react')) &&
      fs.existsSync(path.join(candidate, 'node_modules/react-dom')) &&
      fs.existsSync(path.join(candidate, 'node_modules/@remotion/renderer'))
    ) {
      return candidate;
    }
  }
  throw new Error('No installed Remotion directory found; pass --remotion-dir');
}

function findBrowser() {
  if (options.browser) return options.browser;
  if (process.env.CHROMIUM_PATH && fs.existsSync(process.env.CHROMIUM_PATH)) {
    return process.env.CHROMIUM_PATH;
  }
  for (const candidate of [
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ]) {
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new Error('No Chromium/Chrome executable found; pass --browser or set CHROMIUM_PATH');
}

const catalog = JSON.parse(fs.readFileSync(path.join(repo, 'episodes/_shared/leetcode-covers/catalog.json'), 'utf8'));
const slugFilter = options.slugs ? new Set(options.slugs.split(',').map((s) => s.trim()).filter(Boolean)) : null;
const episodes = catalog.episodes
  .map((ep) => ({
    slug: ep.slug,
    number: ep.number,
    title: ep.title.join(''),
    method: ep.method,
  }))
  .filter((ep) => !slugFilter || slugFilter.has(ep.slug));

if (episodes.length === 0) {
  throw new Error('No matching LeetCode episodes selected');
}

const remotionDir = findRemotionDir();
const browserExecutable = findBrowser();
const require = createRequire(path.join(remotionDir, 'package.json'));
const esbuild = require('esbuild');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const {openBrowser} = require('@remotion/renderer');

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'lc-header-v2-patch-'));
const compiledPath = path.join(tmpDir, 'FrameV2.mjs');

let browser;
try {
  await esbuild.build({
    entryPoints: [path.join(here, 'FrameV2.tsx')],
    outfile: compiledPath,
    bundle: true,
    format: 'esm',
    platform: 'node',
    external: ['react', 'react/jsx-runtime'],
    jsx: 'automatic',
  });
  const moduleSrc = fs.readFileSync(compiledPath, 'utf8');
  const reactPath = pathToFileURL(require.resolve('react')).href;
  const jsxRuntimePath = pathToFileURL(require.resolve('react/jsx-runtime')).href;
  const patchedPath = path.join(tmpDir, 'FrameV2.resolved.mjs');
  fs.writeFileSync(
    patchedPath,
    moduleSrc
      .replaceAll('"react/jsx-runtime"', JSON.stringify(jsxRuntimePath))
      .replaceAll("'react/jsx-runtime'", JSON.stringify(jsxRuntimePath))
      .replaceAll('"react"', JSON.stringify(reactPath))
      .replaceAll("'react'", JSON.stringify(reactPath)),
  );
  const {LeetcodeBackdrop, LeetcodeHeaderV2} = await import(pathToFileURL(patchedPath).href);
  const styleV2 = JSON.parse(fs.readFileSync(path.join(here, 'style-v2.json'), 'utf8'));

  browser = await openBrowser('chrome', {browserExecutable, logLevel: 'error'});
  const page = await browser.newPage({
    context: null,
    logLevel: 'error',
    indent: false,
    pageIndex: 0,
    onBrowserLog: null,
    onLog: () => {},
  });
  await page.setViewport({width: 1920, height: 1080, deviceScaleFactor: 1});

  const summary = [];
  for (const ep of episodes) {
    const revDir = path.join(repo, 'episodes/leetcode', ep.slug, 'production/revisions', options.revision);
    fs.mkdirSync(revDir, {recursive: true});

    const markup = ReactDOMServer.renderToStaticMarkup(
      React.createElement(
        'div',
        {
          style: {
            position: 'relative',
            width: 1920,
            height: 1080,
            background: styleV2.palette.background,
            overflow: 'hidden',
          },
        },
        React.createElement(LeetcodeBackdrop),
        React.createElement(LeetcodeHeaderV2, {
          slug: ep.slug,
          identity: {number: ep.number, title: ep.title, method: ep.method},
        }),
      ),
    );
    const htmlFile = path.join(tmpDir, `${ep.slug}.html`);
    fs.writeFileSync(
      htmlFile,
      `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;width:1920px;height:1080px;background:${styleV2.palette.background};overflow:hidden;}</style></head><body>${markup}</body></html>`,
    );
    await page.goto({url: pathToFileURL(htmlFile).href, timeout: 15000});

    const audit = await page.evaluate(async ({expectedTitle, rect}) => {
      await document.fonts.ready;
      const box = (el) => {
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return {x: r.x, y: r.y, w: r.width, h: r.height, right: r.right, bottom: r.bottom};
      };
      const header = document.querySelector('[data-leetcode-header]');
      const pill = document.querySelector('[data-leetcode-number]');
      const title = document.querySelector('[data-leetcode-title]');
      const watermark = document.querySelector('[data-leetcode-watermark]');
      const range = document.createRange();
      range.selectNodeContents(title);
      const lineRects = [...range.getClientRects()].map((r) => ({
        x: r.x,
        y: r.y,
        w: r.width,
        h: r.height,
        right: r.right,
        bottom: r.bottom,
      }));
      const pillBox = box(pill);
      const titleBox = box(title);
      const watermarkBox = box(watermark);
      const violations = [];
      if (header?.getAttribute('data-header-version') !== 'v2') violations.push('wrong-header-version');
      if (title?.textContent !== expectedTitle) violations.push(`unexpected-title:${title?.textContent}`);
      if ((header?.textContent ?? '').includes('算法可视化')) violations.push('forbidden-label-present');
      if (lineRects.length !== 1) violations.push(`wrapped-lines:${lineRects.length}`);
      if (!titleBox || titleBox.x < rect.x + 4 || titleBox.right > rect.x + rect.width - 12) {
        violations.push(`title-outside-patch-x:${JSON.stringify(titleBox)}`);
      }
      if (!titleBox || titleBox.y < rect.y + 4 || titleBox.bottom > rect.y + rect.height - 2) {
        violations.push(`title-outside-patch-y:${JSON.stringify(titleBox)}`);
      }
      if (!pillBox || !titleBox || titleBox.x - pillBox.right < 20) violations.push('pill-gap-small');
      if (!watermarkBox || !titleBox || watermarkBox.x - titleBox.right < 24) violations.push('watermark-gap-small');
      return {
        expectedTitle,
        actualTitle: title?.textContent ?? '',
        pillBox,
        titleBox,
        watermarkBox,
        lineRects,
        violations,
      };
    }, {expectedTitle: ep.title, rect: PATCH_RECT});

    if (audit.violations.length > 0) {
      throw new Error(`DOM audit failed for ${ep.slug}: ${audit.violations.join(', ')}`);
    }

    const patchFile = path.join(revDir, 'patch.png');
    const shot = await page._client().send('Page.captureScreenshot', {
      format: 'png',
      clip: {...PATCH_RECT, scale: 1},
    });
    const b64 = shot?.value?.data ?? shot?.data;
    fs.writeFileSync(patchFile, Buffer.from(b64, 'base64'));
    const patchSHA256 = shaFile(patchFile);

    const record = {
      schemaVersion: 1,
      slug: ep.slug,
      identity: {number: ep.number, title: ep.title, method: ep.method},
      patchRect: PATCH_RECT,
      patchFile: 'patch.png',
      patchSHA256,
      sourceFiles: {
        'episodes/_shared/leetcode-video/FrameV2.tsx': shaFile(path.join(here, 'FrameV2.tsx')),
        'episodes/_shared/leetcode-video/header-v2.ts': shaFile(path.join(here, 'header-v2.ts')),
        'episodes/_shared/leetcode-video/style-v2.json': shaFile(path.join(here, 'style-v2.json')),
      },
      browserExecutable,
      domAudit: audit,
    };
    fs.writeFileSync(path.join(revDir, 'header-dom-audit.json'), JSON.stringify(record, null, 2) + '\n');
    summary.push({slug: ep.slug, number: ep.number, title: ep.title, titleRight: Number(audit.titleBox.right.toFixed(1)), patchSHA256});
    console.log(`[OK] LC.${String(ep.number).padEnd(3)} ${ep.slug.padEnd(24)} "${ep.title}" right=${audit.titleBox.right.toFixed(1)} sha=${patchSHA256.slice(0, 12)}`);
  }
  console.log(`Rendered and verified ${summary.length} FrameV2.tsx header patches.`);
} finally {
  if (browser) await browser.close({silent: true});
  fs.rmSync(tmpDir, {recursive: true, force: true});
}
