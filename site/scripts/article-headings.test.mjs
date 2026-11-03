import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluateSync} from '@mdx-js/mdx';
import remarkGfm from 'remark-gfm';
import {rehypeHeadingIds} from '@astrojs/markdown-remark';
import {remarkHeadingId, rehypeArticleHeadings} from '../src/lib/article-headings.mjs';

const jsx = (type, props) => typeof type === 'function' ? type(props) : {type, props};
const prepare = (source) => source.replace(/^(#{1,6} .*?)\s*\{#([\w-]+)\}[ \t]*$/gm, '$1 \\{#$2\\}');
function compile(source, frontmatter = {}) {
  // Astro runs its ordinary heading pass and export after custom plugins.
  return evaluateSync({value: prepare(source), path: 'article.mdx', data: {astro: {frontmatter}}}, {
    Fragment: 'fragment', jsx, jsxs: jsx,
    remarkPlugins: [remarkGfm, remarkHeadingId],
    rehypePlugins: [rehypeArticleHeadings, rehypeHeadingIds],
  });
}
function renderedHeadings(node, result = []) {
  if (Array.isArray(node)) { for (const child of node) renderedHeadings(child, result); return result; }
  if (!node || typeof node !== 'object') return result;
  if (/^h[1-6]$/.test(node.type)) result.push({id: node.props.id, depth: Number(node.type[1])});
  renderedHeadings(node.props?.children, result);
  return result;
}

test('explicit chapter IDs and generated Chinese/code titles link to the actual rendered headings', () => {
  const page = compile('## 关键机制 {#mechanism}\n\n### 从 `position` 读取\n\n## 小结');
  const headings = page.getArticleHeadings();
  assert.deepEqual(headings, [
    {id: 'mechanism', title: '关键机制', depth: 2},
    {id: '从-position-读取', title: '从 position 读取', depth: 3},
    {id: '小结', title: '小结', depth: 2},
  ]);
  assert.deepEqual(renderedHeadings(page.default({})), headings.map(({id, depth}) => ({id, depth})));
});

test('generated duplicate titles stay unique and cannot overwrite existing explicit anchors', () => {
  const page = compile('## Saved {#repeat}\n\n## repeat\n\n## repeat\n\n### 重复\n\n### 重复');
  const headings = page.getArticleHeadings();
  assert.equal(headings[0].id, 'repeat');
  assert.deepEqual(headings.slice(-2).map((heading) => heading.id), ['重复', '重复-1']);
  assert.equal(new Set(headings.map((heading) => heading.id)).size, headings.length);
  assert.deepEqual(renderedHeadings(page.default({})), headings.map(({id, depth}) => ({id, depth})));
});

test('a repeated explicit anchor fails instead of silently producing an ambiguous article link', () => {
  assert.throws(() => compile('## One {#fixed}\n\n## Two {#fixed}'), /Duplicate article heading id: fixed/);
});

test('an explicit TOC target cannot collide with a native span alias', () => {
  assert.throws(() => compile('<span id="fixed" />\n\n## 机制 {#fixed}'), /Duplicate article heading id: fixed/);
});

test('footnotes, hidden areas, figures and collapsed details do not become article sections', () => {
  const page = compile(`## 正文

文本[^note]

<div hidden>

## 隐藏一

</div>

<div style={{display: 'none'}}>

## 隐藏二

</div>

<figure>

### 图内标题

</figure>

<details>
<summary>展开说明</summary>

### 折叠内容

</details>

## 参考资料

[^note]: 注释
`);
  assert.deepEqual(page.getArticleHeadings().map((heading) => heading.title), ['正文', '参考资料']);
});

test('new article-only sections do not need or create a video chapter', () => {
  const chapters = Object.freeze([Object.freeze({id: 'mechanism', title: '视频机制章', start: 12.5, frame: 375})]);
  const before = structuredClone(chapters);
  const page = compile('## 机制 {#mechanism}\n\n## 深入阅读\n\n### 条件改变\n\n## 小结', {chapters});
  const headings = page.getArticleHeadings();
  assert.equal(headings.length, 4);
  assert.equal(headings.filter((heading) => chapters.some((chapter) => chapter.id === heading.id)).length, 1);
  assert.ok(headings.every((heading) => !('start' in heading) && !('frame' in heading)));
  assert.deepEqual(chapters, before);
});
