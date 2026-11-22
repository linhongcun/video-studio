import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {
  FORBIDDEN_HEADER_TITLE,
  computeHeaderV2Metrics,
  formatCompactHeaderLabel,
  isRedundantHeaderDetail,
  resolveLeetcodeHeaderV2,
} from '../leetcode-video/header-v2.ts';

const here = path.dirname(fileURLToPath(import.meta.url));
const sharedDir = path.resolve(here, '../leetcode-video');
const coversCatalogPath = path.resolve(here, '../leetcode-covers/catalog.json');

const styleV1 = JSON.parse(fs.readFileSync(path.join(sharedDir, 'style-v1.json'), 'utf8'));
const styleV2 = JSON.parse(fs.readFileSync(path.join(sharedDir, 'style-v2.json'), 'utf8'));
const identitiesV1 = JSON.parse(fs.readFileSync(path.join(sharedDir, 'identities-v1.json'), 'utf8'));
const coversCatalog = JSON.parse(fs.readFileSync(coversCatalogPath, 'utf8'));

const FROZEN_V1_SHA256 = {
  'Frame.tsx': '45fdd670ba1be105d086b225c110a0b47cfd6acf4135260dc74693f5d923358a',
  'identities-v1.json': '1d54f808d3beb0fb86436347c2c1e0e8cf50200f9066447aa6e3c97874635c12',
  'qa.mjs': 'bb7de0381e2db487e691e418068fc394f96940639f64c64b6035dbbf643fa9e9',
  'references.py': '9a420a424184cd405fb2a28fe6a81fd7aecb48b8fe425958eff115214eaf1d3c',
  'render.py': '745c9a618597b712c8b3a1a98245d4a3118cd1491904b0d5f7cb0baa3aa2fb7d',
  'style-v1.json': 'd01f36432049767fad0df3ac3bade96078c206829c015461f4992d6df48122c3',
  'theme.ts': 'cba666bbc3911d533de446d9a7aed89dd51c1eb51704a50d730308314041303b',
};

function sha256(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

test('frozen v1 shared files keep exact byte identity', () => {
  for (const [name, expected] of Object.entries(FROZEN_V1_SHA256)) {
    const actual = sha256(path.join(sharedDir, name));
    assert.equal(actual, expected, `Frozen v1 file changed unexpectedly: ${name}`);
  }
});

test('style-v2 preserves approved palette/fonts and omits seriesLabel "算法可视化"', () => {
  assert.equal(styleV2.version, 'leetcode-video-style-v2');
  assert.equal(styleV2.brand, styleV1.brand);
  assert.equal(styleV2.series, styleV1.series);
  assert.equal(styleV2.headerLabelMode, 'problem-title');
  assert.equal('seriesLabel' in styleV2, false);
  assert.deepEqual(styleV2.palette, styleV1.palette);
  assert.deepEqual(styleV2.fonts, styleV1.fonts);
  assert.equal(JSON.stringify(styleV2).includes('"seriesLabel"'), false);
});

test('fallback resolution covers all 11 v1 identities with problem titles instead of 算法可视化', () => {
  for (const ep of identitiesV1.episodes) {
    const expectedTitle = ep.title.join('');
    const resolved = resolveLeetcodeHeaderV2({
      slug: ep.slug,
      detail: '核心推导',
      fallbackEpisodes: identitiesV1.episodes,
    });
    assert.equal(resolved.number, ep.number);
    assert.equal(resolved.numberLabel, `LC.${ep.number}`);
    assert.equal(resolved.title, expectedTitle);
    assert.equal(resolved.primaryLabel, expectedTitle);
    assert.notEqual(resolved.primaryLabel, FORBIDDEN_HEADER_TITLE);
    assert.equal(resolved.showDetail, true);
    assert.equal(resolved.metrics.pillWidth, 142);
    assert.equal(resolved.metrics.titleLeft, 494);
  }
});

test('explicit identities cover all 17 published catalog titles and representative open Hot-100 titles', () => {
  const extraOpenIssues = [
    {slug: 'maximum-subarray', number: 53, title: '最大子数组和', method: '动态规划'},
    {slug: 'jump-game', number: 55, title: '跳跃游戏', method: '贪心'},
    {slug: 'edit-distance', number: 72, title: '编辑距离', method: '动态规划'},
    {slug: 'subsets', number: 78, title: '子集', method: '回溯'},
    {slug: 'validate-bst', number: 98, title: '验证二叉搜索树', method: '中序遍历'},
    {slug: 'level-order', number: 102, title: '二叉树的层序遍历', method: '广度优先搜索'},
    {slug: 'best-time-stock', number: 121, title: '买卖股票的最佳时机', method: '一次遍历'},
    {slug: 'longest-consecutive', number: 128, title: '最长连续序列', method: '哈希集合'},
    {slug: 'lru-cache', number: 146, title: 'LRU 缓存', method: '哈希表 + 双向链表'},
    {slug: 'implement-trie', number: 208, title: '实现 Trie（前缀树）', method: '字典树'},
    {slug: 'search-rotated', number: 33, title: '搜索旋转排序数组', method: '二分查找'},
    {slug: 'subarray-sum-k', number: 560, title: '和为 K 的子数组', method: '前缀和 + 哈希表'},
    {slug: 'longest-common-subsequence', number: 1143, title: '最长公共子序列', method: '动态规划'},
  ];

  const allCases = [
    ...coversCatalog.episodes.map((ep) => ({
      slug: ep.slug,
      number: ep.number,
      title: ep.title.join(''),
      method: ep.method,
    })),
    ...extraOpenIssues,
  ];

  for (const item of allCases) {
    const resolved = resolveLeetcodeHeaderV2({
      slug: item.slug,
      identity: {number: item.number, title: item.title, method: item.method},
      detail: '关键步骤演示',
    });
    assert.equal(resolved.primaryLabel, item.title);
    assert.notEqual(resolved.primaryLabel, FORBIDDEN_HEADER_TITLE);
    assert.equal(resolved.numberLabel, `LC.${item.number}`);
    assert.ok(resolved.metrics.titleMaxWidth >= 1100, `Insufficient title budget for ${item.slug}`);
  }
});

test('4-digit LC numbers widen the gold pill and shift titleLeft cleanly', () => {
  const m3 = computeHeaderV2Metrics(994, false);
  const m4 = computeHeaderV2Metrics(1143, false);
  const m4Compact = computeHeaderV2Metrics(1143, true);

  assert.equal(m3.pillWidth, 142);
  assert.equal(m3.titleLeft, 494);
  assert.equal(m4.pillWidth, 168);
  assert.equal(m4.titleLeft, 520);
  assert.equal(m4Compact.pillWidth, 154);
  assert.equal(m4Compact.titleLeft, 506);
});

test('compact CodeCard label combines title and method without duplication', () => {
  assert.equal(formatCompactHeaderLabel('腐烂的橘子', '广度优先搜索'), '腐烂的橘子 · 广度优先搜索');
  assert.equal(formatCompactHeaderLabel('二分查找', '二分查找'), '二分查找');
  assert.equal(formatCompactHeaderLabel('爬楼梯', '爬楼梯 · 两个滚动计数'), '爬楼梯 · 两个滚动计数');
  assert.equal(formatCompactHeaderLabel('两数之和', ''), '两数之和');

  const resolved = resolveLeetcodeHeaderV2({
    slug: 'rotting-oranges',
    identity: {number: 994, title: '腐烂的橘子', method: '广度优先搜索'},
    detail: '为何初始烂橘子要一起入队',
    compact: true,
  });
  assert.equal(resolved.primaryLabel, '腐烂的橘子 · 广度优先搜索');
  assert.equal(resolved.showDetail, false);
});

test('redundant detail matching title or LC number + title is suppressed automatically', () => {
  assert.equal(isRedundantHeaderDetail('爬楼梯', 70, '爬楼梯'), true);
  assert.equal(isRedundantHeaderDetail('  爬楼梯  ', 70, '爬楼梯'), true);
  assert.equal(isRedundantHeaderDetail('   ', 70, '爬楼梯'), true);
  assert.equal(isRedundantHeaderDetail('LeetCode 200 · 岛屿数量', 200, '岛屿数量'), true);
  assert.equal(isRedundantHeaderDetail('LC.994 · 腐烂的橘子', 994, '腐烂的橘子'), true);
  assert.equal(isRedundantHeaderDetail('腐烂的橘子 · LC.994', 994, '腐烂的橘子'), true);
  assert.equal(isRedundantHeaderDetail('为何初始烂橘子要一起入队', 994, '腐烂的橘子'), false);
  assert.equal(isRedundantHeaderDetail({type: 'span'}, 994, '腐烂的橘子'), false);

  const suppressed = resolveLeetcodeHeaderV2({
    slug: 'climbing-stairs',
    identity: {number: 70, title: '爬楼梯', method: '动态规划'},
    detail: '爬楼梯',
  });
  assert.equal(suppressed.showDetail, false);

  const kept = resolveLeetcodeHeaderV2({
    slug: 'rotting-oranges',
    identity: {number: 994, title: '腐烂的橘子', method: '广度优先搜索'},
    detail: '为何初始烂橘子要一起入队',
  });
  assert.equal(kept.showDetail, true);
});

test('invalid identities and forbidden label "算法可视化" fail fast', () => {
  assert.throws(
    () => resolveLeetcodeHeaderV2({slug: 'unknown-problem'}),
    /Missing LeetCode v2 identity/,
  );
  assert.throws(
    () =>
      resolveLeetcodeHeaderV2({
        slug: 'rotting-oranges',
        identity: {number: 994, title: '   '},
      }),
    /Missing problem title/,
  );
  assert.throws(
    () =>
      resolveLeetcodeHeaderV2({
        slug: 'rotting-oranges',
        identity: {number: 994, title: '算法可视化'},
      }),
    /must be the problem name/,
  );
  assert.throws(
    () =>
      resolveLeetcodeHeaderV2({
        slug: 'bad-number',
        identity: {number: 0, title: '两数之和'},
      }),
    /Invalid LeetCode problem number/,
  );
});
