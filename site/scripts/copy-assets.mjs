// 把每期的视频与封面从 episodes/<slug>/ 拷进 site/public/episodes/<slug>/（构建产物的一部分，不入库）
import fs from 'node:fs';
import path from 'node:path';
const root = path.resolve(import.meta.dirname, '../../episodes');
const out = path.resolve(import.meta.dirname, '../public/episodes');
fs.rmSync(out, {recursive: true, force: true});
for (const slug of fs.readdirSync(root)) {
  const metaPath = path.join(root, slug, 'meta.json');
  if (!fs.existsSync(metaPath)) continue;
  const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
  fs.mkdirSync(path.join(out, slug), {recursive: true});
  for (const f of [meta.video, meta.poster].filter(Boolean)) {
    const src = path.join(root, slug, f);
    if (!fs.existsSync(src)) throw new Error(`[copy-assets] 缺少文件: ${src}`);
    fs.copyFileSync(src, path.join(out, slug, f));
    console.log(`[copy-assets] ${slug}/${f}`);
  }
}
