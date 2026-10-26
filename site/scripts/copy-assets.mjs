// 把每期的视频与封面从 episodes/<slug>/ 拷进 site/public/episodes/<slug>/（构建产物的一部分，不入库）
import fs from 'node:fs';
import path from 'node:path';
const root = path.resolve(import.meta.dirname, '../../episodes');
const out = path.resolve(import.meta.dirname, '../public/episodes');
const imageTypes = /\.(?:avif|gif|jpe?g|png|svg|webp)$/i;
function copyArticleImages(directory, destination) {
  if (fs.lstatSync(directory).isSymbolicLink()) throw new Error(`[copy-assets] article images cannot be symlinks: ${directory}`);
  for (const entry of fs.readdirSync(directory, {withFileTypes: true})) {
    const source = path.join(directory, entry.name);
    const target = path.join(destination, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`[copy-assets] article images cannot be symlinks: ${source}`);
    if (entry.isDirectory()) copyArticleImages(source, target);
    else if (entry.isFile() && imageTypes.test(entry.name)) {
      fs.mkdirSync(destination, {recursive: true});
      fs.copyFileSync(source, target);
    }
  }
}
fs.rmSync(out, {recursive: true, force: true});
for (const slug of fs.readdirSync(root)) {
  const metaPath = path.join(root, slug, 'meta.json');
  if (!fs.existsSync(metaPath)) continue;
  const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
  if (meta.draft && process.env.SHOW_DRAFTS !== '1') { console.log(`[copy-assets] ${slug}: draft，跳过`); continue; }
  fs.mkdirSync(path.join(out, slug), {recursive: true});
  for (const f of [meta.video, meta.poster].filter(Boolean)) {
    const src = path.join(root, slug, f);
    if (!fs.existsSync(src)) { if (meta.draft) { console.warn(`[copy-assets] ${slug}: draft 缺少 ${f}`); continue; } throw new Error(`[copy-assets] 缺少文件: ${src}`); }
    fs.copyFileSync(src, path.join(out, slug, f));
    console.log(`[copy-assets] ${slug}/${f}`);
  }
  const articleImages = path.join(root, slug, 'article');
  if (fs.existsSync(articleImages)) copyArticleImages(articleImages, path.join(out, slug, 'article'));
}

// 旧链接兼容（构建时生成，不在仓库里重复存二进制）：
// - v0.1.x 的 /videos/http-request/video.mp4 → 完整版视频；/videos/http-request/ → 完整版页面
// - v0.5.3 下线的旧短版 /episodes/http-request-quick/ → 完整版页面
const FULL = 'http-request';
const to = `/video-studio/episodes/${FULL}/`;
const redirectHtml = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>页面已迁移</title><meta http-equiv="refresh" content="0; url=${to}"><link rel="canonical" href="${to}"><meta name="robots" content="noindex"></head><body><p>此页已迁移到 <a href="${to}">${to}</a></p><script>location.replace(${JSON.stringify(to)})</script></body></html>\n`;
const legacy = path.resolve(import.meta.dirname, '../public/videos/http-request');
fs.rmSync(path.resolve(import.meta.dirname, '../public/videos'), {recursive: true, force: true});
fs.mkdirSync(legacy, {recursive: true});
fs.copyFileSync(path.join(root, FULL, 'video.mp4'), path.join(legacy, 'video.mp4'));
fs.writeFileSync(path.join(legacy, 'index.html'), redirectHtml);
const quick = path.join(out, 'http-request-quick');
fs.mkdirSync(quick, {recursive: true});
fs.writeFileSync(path.join(quick, 'index.html'), redirectHtml);
console.log('[copy-assets] legacy videos/http-request/{video.mp4,index.html}, episodes/http-request-quick/index.html');
