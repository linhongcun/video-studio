#!/usr/bin/env node
/**
 * Real headless Chromium/Chrome DOM + screenshot verifier for FrameV2.tsx.
 * Bundles the actual FrameV2.tsx React component via esbuild, renders representative
 * short/long/mixed/4-digit/compact/duplicate-detail cases at 1920x1080, and checks
 * real bounding boxes, single-line rendering, collision gaps, and safe regions.
 *
 * Usage:
 *   node episodes/_shared/leetcode-video/verify-header-v2.mjs [--out-dir DIR] [--remotion-dir DIR] [--browser PATH]
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../../..');

const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) {
  if (!['--out-dir', '--remotion-dir', '--browser'].includes(args[i]) || args[i + 1] === undefined) {
    throw new Error('Usage: verify-header-v2.mjs [--out-dir DIR] [--remotion-dir DIR] [--browser PATH]');
  }
  options[args[i]] = args[i + 1];
}

function findRemotionDir() {
  if (options['--remotion-dir']) return path.resolve(options['--remotion-dir']);
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
  throw new Error('No installed Remotion directory with esbuild/react/react-dom/@remotion/renderer found; pass --remotion-dir');
}

function findBrowser() {
  if (options['--browser']) return options['--browser'];
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

const CASES = [
  {
    id: '01-short-two-sum',
    slug: 'two-sum',
    identity: undefined, // tests identities-v1 fallback
    detail: '先查补数，再存入哈希表',
    compact: false,
    expectedLabel: '两数之和',
    expectDetail: true,
    bodyTitle: '为什么边遍历边查表，比先建整张表更自然？',
  },
  {
    id: '02-rotting-oranges',
    slug: 'rotting-oranges',
    identity: {number: 994, title: '腐烂的橘子', method: '广度优先搜索'},
    detail: '为何初始烂橘子要一起入队',
    compact: false,
    expectedLabel: '腐烂的橘子',
    expectDetail: true,
    bodyTitle: '队列按层推进：一层刚好等于一分钟',
  },
  {
    id: '03-long-cjk-lc3',
    slug: 'longest-substring',
    identity: undefined,
    detail: '重复出现时，左边界要移到哪里？',
    compact: false,
    expectedLabel: '无重复字符的最长子串',
    expectDetail: true,
    bodyTitle: '左指针只向右移动，绝不回头',
  },
  {
    id: '04-mixed-english-trie',
    slug: 'implement-trie',
    identity: {number: 208, title: '实现 Trie（前缀树）', method: '字典树'},
    detail: '查一个前缀，为什么不用比完所有词？',
    compact: false,
    expectedLabel: '实现 Trie（前缀树）',
    expectDetail: true,
    bodyTitle: '按字符路径逐层展开公共前缀',
  },
  {
    id: '05-mixed-spaced-topk',
    slug: 'top-k-frequent-elements',
    identity: {number: 347, title: '前 K 个高频元素', method: '小顶堆'},
    detail: '为什么把次数最少的留在堆顶',
    compact: false,
    expectedLabel: '前 K 个高频元素',
    expectDetail: true,
    bodyTitle: '超过 K 个时只淘汰当前最小频率',
  },
  {
    id: '06-long-10char-stock',
    slug: 'best-time-to-buy-and-sell-stock',
    identity: {number: 121, title: '买卖股票的最佳时机', method: '一次遍历'},
    detail: '只扫一遍，怎样锁定历史最低买点',
    compact: false,
    expectedLabel: '买卖股票的最佳时机',
    expectDetail: true,
    bodyTitle: '维护截至今天的最低买入价',
  },
  {
    id: '07-stress-14char-tree',
    slug: 'construct-binary-tree',
    identity: {number: 105, title: '从前序与中序遍历序列构造二叉树', method: '分治递归'},
    detail: '前序定根，中序切出左右子树',
    compact: false,
    expectedLabel: '从前序与中序遍历序列构造二叉树',
    expectDetail: true,
    bodyTitle: '每次用根节点下标锁定左子树长度',
  },
  {
    id: '08-four-digit-lc1143',
    slug: 'longest-common-subsequence',
    identity: {number: 1143, title: '最长公共子序列', method: '动态规划'},
    detail: '两个字符相等时为何只看左上角',
    compact: false,
    expectedLabel: '最长公共子序列',
    expectDetail: true,
    bodyTitle: '逐格填写公共子序列最大长度',
  },
  {
    id: '09-suppress-duplicate-detail',
    slug: 'climbing-stairs',
    identity: {number: 70, title: '爬楼梯', method: '动态规划'},
    detail: '爬楼梯',
    compact: false,
    expectedLabel: '爬楼梯',
    expectDetail: false,
    bodyTitle: '到第 n 阶只有最后一步跨 1 阶或 2 阶',
  },
  {
    id: '10-suppress-lc-prefixed-detail',
    slug: 'number-of-islands',
    identity: {number: 200, title: '岛屿数量', method: '深度优先搜索'},
    detail: 'LeetCode 200 · 岛屿数量',
    compact: false,
    expectedLabel: '岛屿数量',
    expectDetail: false,
    bodyTitle: '从输入网格到连通陆地的四邻展开',
  },
  {
    id: '11-compact-codecard',
    slug: 'rotting-oranges',
    identity: {number: 994, title: '腐烂的橘子', method: '广度优先搜索'},
    detail: '不会显示在紧凑代码页',
    compact: true,
    expectedLabel: '腐烂的橘子 · 广度优先搜索',
    expectDetail: false,
    bodyTitle: '',
  },
  {
    id: '12-compact-same-method-and-4digit',
    slug: 'longest-common-subsequence',
    identity: {number: 1143, title: '最长公共子序列', method: '动态规划'},
    detail: undefined,
    compact: true,
    expectedLabel: '最长公共子序列 · 动态规划',
    expectDetail: false,
    bodyTitle: '',
  },
  {
    id: '13-compact-dedupe-binary-search',
    slug: 'binary-search',
    identity: {number: 704, title: '二分查找', method: '二分查找'},
    detail: undefined,
    compact: true,
    expectedLabel: '二分查找',
    expectDetail: false,
    bodyTitle: '',
  },
];

const remotionDir = findRemotionDir();
const browserExecutable = findBrowser();
const require = createRequire(path.join(remotionDir, 'package.json'));
const esbuild = require('esbuild');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const {openBrowser} = require('@remotion/renderer');

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'leetcode-header-v2-'));
const compiledPath = path.join(tmpDir, 'FrameV2.mjs');
const outDir = options['--out-dir'] ? path.resolve(options['--out-dir']) : null;
if (outDir) fs.mkdirSync(outDir, {recursive: true});

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

  // Load with React resolvable from remotionDir
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

  const results = [];
  const allViolations = [];

  for (const item of CASES) {
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
          slug: item.slug,
          identity: item.identity,
          detail: item.detail,
          compact: item.compact,
        }),
        item.bodyTitle
          ? React.createElement(
              'div',
              {
                'data-body-title': 'true',
                style: {
                  position: 'absolute',
                  left: 125,
                  top: 174,
                  color: styleV2.palette.text,
                  fontFamily: styleV2.fonts.sans,
                  fontSize: 40,
                  fontWeight: 700,
                },
              },
              item.bodyTitle,
            )
          : null,
      ),
    );

    const html = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;width:1920px;height:1080px;background:${styleV2.palette.background};overflow:hidden;}</style></head><body>${markup}</body></html>`;
    const htmlFile = path.join(tmpDir, `${item.id}.html`);
    fs.writeFileSync(htmlFile, html);
    await page.goto({url: pathToFileURL(htmlFile).href, timeout: 15000});

    const audit = await page.evaluate(async (expected) => {
      await document.fonts.ready;
      const box = (el) => {
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return {x: r.x, y: r.y, w: r.width, h: r.height, right: r.right, bottom: r.bottom};
      };
      const textRangeRects = (el) => {
        if (!el || !el.firstChild) return [];
        const range = document.createRange();
        range.selectNodeContents(el);
        return [...range.getClientRects()].map((r) => ({
          x: r.x,
          y: r.y,
          w: r.width,
          h: r.height,
          right: r.right,
          bottom: r.bottom,
        }));
      };

      const header = document.querySelector('[data-leetcode-header]');
      const brand = document.querySelector('[data-leetcode-brand]');
      const pill = document.querySelector('[data-leetcode-number]');
      const title = document.querySelector('[data-leetcode-title]');
      const watermark = document.querySelector('[data-leetcode-watermark]');
      const detail = document.querySelector('[data-leetcode-detail]');
      const divider = document.querySelector('[data-leetcode-divider]');
      const bodyTitle = document.querySelector('[data-body-title]');

      const brandBox = box(brand);
      const pillBox = box(pill);
      const pillTextRects = textRangeRects(pill);
      const titleBox = box(title);
      const titleTextRects = textRangeRects(title);
      const watermarkBox = box(watermark);
      const detailBox = box(detail);
      const dividerBox = box(divider);
      const bodyTitleBox = box(bodyTitle);

      const violations = [];
      if (!header) violations.push({type: 'missing-header'});
      if (header?.getAttribute('data-header-version') !== 'v2') {
        violations.push({type: 'wrong-header-version', actual: header?.getAttribute('data-header-version')});
      }
      const actualTitle = title?.textContent ?? '';
      if (actualTitle !== expected.expectedLabel) {
        violations.push({type: 'unexpected-title-text', expected: expected.expectedLabel, actual: actualTitle});
      }
      if ((header?.textContent ?? '').includes('算法可视化')) {
        violations.push({type: 'forbidden-series-label-present'});
      }
      if (titleTextRects.length !== 1) {
        violations.push({type: 'title-wrapped-or-empty', lineCount: titleTextRects.length});
      }
      if (title && title.scrollWidth > title.clientWidth + 1) {
        violations.push({type: 'title-overflows-max-width', scrollWidth: title.scrollWidth, clientWidth: title.clientWidth});
      }
      if (pillTextRects.length !== 1) {
        violations.push({type: 'pill-wrapped-or-empty', lineCount: pillTextRects.length});
      } else if (pillBox) {
        const pt = pillTextRects[0];
        if (pt.x < pillBox.x + 8 || pt.right > pillBox.right - 8) {
          violations.push({type: 'pill-text-too-tight-or-overflow', pillBox, pillText: pt});
        }
      }
      if (brandBox && pillBox && pillBox.x - brandBox.right < 16) {
        violations.push({type: 'brand-pill-gap-too-small', gap: pillBox.x - brandBox.right});
      }
      if (pillBox && titleBox && titleBox.x - pillBox.right < 20) {
        violations.push({type: 'pill-title-gap-too-small', gap: titleBox.x - pillBox.right});
      }
      if (titleBox && watermarkBox && watermarkBox.x - titleBox.right < 24) {
        violations.push({type: 'title-watermark-gap-too-small', gap: watermarkBox.x - titleBox.right});
      }
      if (expected.expectDetail && !detailBox) {
        violations.push({type: 'expected-detail-missing'});
      }
      if (!expected.expectDetail && detailBox) {
        violations.push({type: 'unexpected-detail-rendered', text: detail?.textContent});
      }
      if (detailBox && pillBox && detailBox.y < pillBox.bottom) {
        violations.push({type: 'detail-overlaps-row1', detailBox, pillBox});
      }
      if (detailBox && dividerBox && detailBox.bottom > dividerBox.y + 1) {
        violations.push({type: 'detail-crosses-divider', detailBox, dividerBox});
      }
      if (dividerBox && bodyTitleBox && bodyTitleBox.y < dividerBox.bottom + 12) {
        violations.push({type: 'body-title-too-close-to-divider', bodyTitleBox, dividerBox});
      }
      for (const [name, b] of Object.entries({brand: brandBox, pill: pillBox, title: titleBox, watermark: watermarkBox, detail: detailBox})) {
        if (!b) continue;
        if (b.x < 35 || b.right > 1885 || b.y < 15 || (dividerBox && b.bottom > dividerBox.y + 2)) {
          violations.push({type: 'element-outside-header-safe-zone', name, box: b, dividerY: dividerBox?.y});
        }
      }

      return {
        actualTitle,
        brandBox,
        pillBox,
        titleBox,
        watermarkBox,
        detailBox,
        dividerY: dividerBox?.y ?? null,
        gaps: {
          brandToPill: brandBox && pillBox ? Number((pillBox.x - brandBox.right).toFixed(1)) : null,
          pillToTitle: pillBox && titleBox ? Number((titleBox.x - pillBox.right).toFixed(1)) : null,
          titleToWatermark: titleBox && watermarkBox ? Number((watermarkBox.x - titleBox.right).toFixed(1)) : null,
        },
        violations,
      };
    }, item);

    let screenshot = null;
    if (outDir) {
      screenshot = path.join(outDir, `${item.id}.png`);
      const shot = await page._client().send('Page.captureScreenshot', {
        format: 'png',
        clip: {x: 0, y: 0, width: 1920, height: 280, scale: 1},
      });
      const b64 = shot?.value?.data ?? shot?.data;
      fs.writeFileSync(screenshot, Buffer.from(b64, 'base64'));
    }

    results.push({id: item.id, slug: item.slug, compact: item.compact, screenshot, ...audit});
    for (const v of audit.violations) allViolations.push({id: item.id, ...v});
  }

  const report = {
    status: allViolations.length === 0 ? 'passed' : 'failed',
    checkedCases: results.length,
    violationCount: allViolations.length,
    browserExecutable,
    remotionDir: path.relative(repo, remotionDir),
    results,
    violations: allViolations,
  };
  if (outDir) {
    fs.writeFileSync(path.join(outDir, 'header-v2-dom-audit.json'), JSON.stringify(report, null, 2) + '\n');
  }
  console.log(
    `verify-header-v2: ${report.status} (${results.length} cases, ${allViolations.length} violations)`,
  );
  for (const r of results) {
    console.log(
      `  [${r.violations.length === 0 ? 'OK' : 'FAIL'}] ${r.id}: "${r.actualTitle}" | gaps=${JSON.stringify(r.gaps)} | detail=${Boolean(r.detailBox)}`,
    );
  }
  if (allViolations.length > 0) {
    console.error(JSON.stringify(allViolations, null, 2));
    process.exitCode = 1;
  }
} finally {
  if (browser) await browser.close({silent: true});
  fs.rmSync(tmpDir, {recursive: true, force: true});
}
