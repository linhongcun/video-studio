import {defineConfig} from 'astro/config';
import mdx from '@astrojs/mdx';
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

export default defineConfig({
  site: 'https://linhongcun.github.io',
  base: '/video-studio/',
  trailingSlash: 'always',
  integrations: [mdx({remarkPlugins: [remarkHeadingId]})],
  vite: {
    plugins: [headingIdPre()],
    server: {fs: {allow: [fileURLToPath(new URL('..', import.meta.url))]}},
  },
});
