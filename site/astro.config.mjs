import {defineConfig} from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import {fileURLToPath} from 'node:url';

// 编剧稿使用 `## 标题 {#id}` 写法；MDX 会把 {…} 当表达式解析，
// 这里在编译前把它转成转义文本，再由 remark 插件变成标题 id，不改动 article.mdx 原文。
const headingIdPre = () => ({
  name: 'heading-id-pre',
  enforce: 'pre',
  transform(code, id) {
    if (!id.split('?')[0].endsWith('.mdx')) return;
    return code.replace(/^(#{1,6} .*?)\s*\{#([\w-]+)\}[ \t]*$/gm, '$1 \\{#$2\\}');
  },
});
function remarkHeadingId() {
  return (tree) => {
    const walk = (n) => {
      if (n.type === 'heading') {
        const last = n.children[n.children.length - 1];
        const m = last && last.type === 'text' && last.value.match(/\s*\{#([\w-]+)\}\s*$/);
        if (m) {
          last.value = last.value.slice(0, m.index);
          n.data = {...(n.data || {}), hProperties: {...(n.data?.hProperties || {}), id: m[1]}};
        }
      }
      (n.children || []).forEach(walk);
    };
    walk(tree);
  };
}

// Raw MDX SVG is rendered as native markup. Normalize React-style property
// names on SVG JSX nodes so browsers apply the intended text and strokes.
// Walking JSX nodes leaves fenced code examples and article source untouched.
function remarkSvgAttributes() {
  const attributes = new Map([
    ['textAnchor', 'text-anchor'], ['dominantBaseline', 'dominant-baseline'],
    ['fontSize', 'font-size'], ['fontFamily', 'font-family'], ['fontWeight', 'font-weight'],
    ['strokeWidth', 'stroke-width'], ['strokeLinecap', 'stroke-linecap'],
    ['strokeLinejoin', 'stroke-linejoin'], ['strokeDasharray', 'stroke-dasharray'],
    ['strokeDashoffset', 'stroke-dashoffset'], ['markerEnd', 'marker-end'],
    ['markerStart', 'marker-start'], ['markerMid', 'marker-mid'],
    ['fillRule', 'fill-rule'], ['clipRule', 'clip-rule'],
  ]);
  return (tree) => {
    const walk = (node, insideSvg = false) => {
      const jsx = node.type === 'mdxJsxFlowElement' || node.type === 'mdxJsxTextElement';
      const svg = insideSvg || (jsx && node.name === 'svg');
      if (jsx && svg) for (const attribute of node.attributes ?? []) {
        if (attribute.type === 'mdxJsxAttribute' && attributes.has(attribute.name))
          attribute.name = attributes.get(attribute.name);
      }
      for (const child of node.children ?? []) walk(child, svg);
    };
    walk(tree);
  };
}

// 制作稿里的用途提示不作为读者标题；保留原始文章与既有锚点。
function rehypeReaderHeadings() {
  return (tree) => {
    const walk = (node) => {
      if (node.type === 'element' && /^h[1-6]$/.test(node.tagName)) {
        const first = node.children?.find((child) => child.type === 'text');
        if (first) first.value = first.value.replace(/^只放文章[：:]\s*/, '');
      }
      (node.children || []).forEach(walk);
    };
    walk(tree);
  };
}

// 把 “## 小结” 及其后到下一个 h2 前的内容包成 Summary 卡；最后一段“动手试试”包成 tip Callout
function rehypeSummary() {
  const text = (n) => (n.type === 'text' ? n.value : (n.children || []).map(text).join(''));
  return (tree, file) => {
    // 标记与 frontmatter chapters 对应的 h2，ChapterHeading 只给这些标题加“▶ 从这里看”
    const ids = new Set((file.data?.astro?.frontmatter?.chapters ?? []).map((c) => c.id));
    for (const n of tree.children) if (n.type === 'element' && /^h[23]$/.test(n.tagName) && ids.has(n.properties?.id)) n.properties.dataChapter = '';
    const kids = tree.children;
    const i = kids.findIndex((n) => n.type === 'element' && n.tagName === 'h2' && text(n).trim() === '小结');
    if (i < 0) return;
    let j = kids.findIndex((n, k) => k > i && n.type === 'element' && n.tagName === 'h2');
    if (j < 0) j = kids.length;
    const body = kids.slice(i, j);
    const lastP = [...body].reverse().find((n) => n.type === 'element' && n.tagName === 'p');
    if (lastP && /动手|试试|开发者工具/.test(text(lastP))) {
      const idx = body.indexOf(lastP);
      body[idx] = {type: 'element', tagName: 'aside', properties: {className: ['callout', 'callout-tip'], role: 'note'},
        children: [{type: 'element', tagName: 'span', properties: {className: ['ci'], ariaHidden: 'true'}, children: [{type: 'text', value: '✓'}]},
          {type: 'element', tagName: 'div', properties: {className: ['cbody']}, children: [{type: 'element', tagName: 'p', properties: {className: ['ctitle']}, children: [{type: 'text', value: '动手试试'}]}, lastP]}]};
    }
    body[0] = {...body[0], tagName: 'h2', properties: {...body[0].properties, dataSummary: ''}};
    kids.splice(i, j - i, {type: 'element', tagName: 'section', properties: {className: ['summary']}, children: body});
  };
}

export default defineConfig({
  site: 'https://linhongcun.github.io',
  base: '/video-studio/',
  trailingSlash: 'always',
  redirects: {
    '/tags/全局唯一ID/': '/video-studio/tags/分布式ID/',
    '/series/cache/': '/video-studio/series/redis/',
  },
  integrations: [sitemap({filter: (p) => !/\/videos\/|http-request-quick|\/(?:learn|series|all)\/$/.test(p)}), mdx({remarkPlugins: [remarkHeadingId, remarkSvgAttributes], rehypePlugins: [rehypeReaderHeadings, rehypeSummary], syntaxHighlight: false})],
  vite: {
    plugins: [headingIdPre()],
    server: {fs: {allow: [fileURLToPath(new URL('..', import.meta.url))]}},
  },
});
