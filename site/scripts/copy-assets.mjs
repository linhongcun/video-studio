// 从各系列单期的 publication/ 复制媒体，公开 URL 仍为 /episodes/<slug>/。
// 本地构建对同盘媒体优先使用硬链接，避免在 publication/、site/public/、site/dist/ 占多份磁盘；
// 启用外部视频托管（site/src/content/video-host.json 或 VIDEO_HOST_BASE_URL）时跳过复制 MP4，避免触及 Pages 1 GB 上限。
import fs from 'node:fs';
import path from 'node:path';
import {episodeDirectory, listEpisodes} from './episode-paths.mjs';
import {shouldCopyVideoToPublic, resolveVideoHostConfig} from './video-host.mjs';

const out = path.resolve(import.meta.dirname, '../public/episodes');
const imageTypes = /\.(?:avif|gif|jpe?g|png|svg|webp)$/i;
const isDev = process.env.ASTRO_DEV === '1' || process.argv.includes('--dev');

function linkOrCopyFile(source, destination) {
  fs.rmSync(destination, {force: true});
  try {
    fs.linkSync(source, destination);
    return 'link';
  } catch (err) {
    if (!['EXDEV', 'EPERM', 'EACCES', 'EMLINK', 'ENOSYS'].includes(err?.code)) throw err;
    fs.copyFileSync(source, destination);
    return 'copy';
  }
}

function copyArticleImages(directory, destination) {
  if (fs.lstatSync(directory).isSymbolicLink()) throw new Error(`[copy-assets] article images cannot be symlinks: ${directory}`);
  for (const entry of fs.readdirSync(directory, {withFileTypes: true})) {
    const source = path.join(directory, entry.name);
    const target = path.join(destination, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`[copy-assets] article images cannot be symlinks: ${source}`);
    if (entry.isDirectory()) copyArticleImages(source, target);
    else if (entry.isFile() && imageTypes.test(entry.name)) {
      fs.mkdirSync(destination, {recursive: true});
      linkOrCopyFile(source, target);
    }
  }
}

const hostConfig = resolveVideoHostConfig();
let skippedExternalVideos = 0;
let linkedFiles = 0;
let copiedFiles = 0;

fs.rmSync(out, {recursive: true, force: true});
for (const {slug, directory, meta} of listEpisodes()) {
  if (meta.draft && process.env.SHOW_DRAFTS !== '1') { console.log(`[copy-assets] ${slug}: draft，跳过`); continue; }
  fs.mkdirSync(path.join(out, slug), {recursive: true});
  const copyVideo = shouldCopyVideoToPublic({config: hostConfig, isDev, isDraft: !!meta.draft});
  const mediaList = [copyVideo ? meta.video : null, meta.poster].filter(Boolean);
  if (!copyVideo && meta.video) skippedExternalVideos += 1;
  for (const f of mediaList) {
    const src = path.join(directory, f);
    if (!fs.existsSync(src)) { if (meta.draft) { console.warn(`[copy-assets] ${slug}: draft 缺少 ${f}`); continue; } throw new Error(`[copy-assets] 缺少文件: ${src}`); }
    const mode = linkOrCopyFile(src, path.join(out, slug, f));
    if (mode === 'link') linkedFiles += 1; else copiedFiles += 1;
    console.log(`[copy-assets] ${slug}/${f} (${mode})`);
  }
  const articleImages = path.join(directory, 'article');
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
if (shouldCopyVideoToPublic({config: hostConfig, isDev, isDraft: false})) {
  linkOrCopyFile(path.join(episodeDirectory(FULL), 'video.mp4'), path.join(legacy, 'video.mp4'));
}
fs.writeFileSync(path.join(legacy, 'index.html'), redirectHtml);
const quick = path.join(out, 'http-request-quick');
fs.mkdirSync(quick, {recursive: true});
fs.writeFileSync(path.join(quick, 'index.html'), redirectHtml);
console.log(
  `[copy-assets] summary: linked=${linkedFiles}, copied=${copiedFiles}, skippedExternalVideos=${skippedExternalVideos} (videoHost=${hostConfig.mode})`,
);
