// npm run covers -- <slug> [--out <dir>] [--only Cover169,Cover43,Cover34] [--set-poster]
// --set-poster：把 meta.json 的 poster 指向 cover-16x9.jpg（站点首页 / 卡片 / 播放器封面 / og:image 都改用专用封面）
// 读 episodes/<slug>/storyboard.json 的 cover 节点（没有则 covers/cover-spec.json[slug]），出 cover-16x9.jpg / cover-4x3.jpg / cover-3x4.jpg（JPG ≤2MB，超了降质量）。
import fs from 'node:fs'; import path from 'node:path'; import {execFileSync} from 'node:child_process'; import {fileURLToPath} from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url)); const repo = path.resolve(here, '..', '..', '..');
const args = process.argv.slice(2); const VAL = new Set(['--out', '--only']);
const slug = args.find((a, i) => !a.startsWith('--') && !VAL.has(args[i - 1]));
if (!slug) { console.error('用法：npm run covers -- <slug> [--out dir]'); process.exit(1); }
const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
const readJson = (p) => (fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : undefined);
const ep = path.join(repo, 'episodes', slug);
const spec = readJson(path.join(ep, 'storyboard.json'))?.cover ?? readJson(path.join(repo, 'covers', 'cover-spec.json'))?.[slug];
if (!spec?.sizes) { console.error(`没有 ${slug} 的 cover 节点`); process.exit(1); }
const files = [...new Set([...(spec.subject ?? []), ...(spec.subject16 ?? [])].map((s) => s.asset).filter(Boolean))];
const bb = JSON.parse(execFileSync('python3', [path.join(here, 'bbox.py'), ...files.map((f) => path.join(ep, f))], {encoding: 'utf8'}));
const assets = Object.fromEntries(files.map((f) => [f, {svg: fs.readFileSync(path.join(ep, f), 'utf8'), bbox: bb[path.join(ep, f)]}]));
const out = opt('--out') ? path.resolve(opt('--out')) : ep; fs.mkdirSync(out, {recursive: true});
const JOBS = {Cover169: ['cover-16x9', {size: '16x9'}], Cover43: ['cover-4x3', {size: '16x9', offsetX: 240}], Cover34: ['cover-3x4', {size: '3x4'}]};
const only = (opt('--only') ?? Object.keys(JOBS).join(',')).split(',');
fs.mkdirSync(path.join(here, 'out'), {recursive: true});
for (const id of only) {
  const [name, extra] = JOBS[id]; const pf = path.join(here, 'out', `${slug}-${id}.props.json`);
  fs.writeFileSync(pf, JSON.stringify({spec, assets, ...extra}));
  const file = path.join(out, `${name}.jpg`);
  for (const q of [92, 85, 78, 70, 60]) {
    execFileSync('npx', ['remotion', 'still', 'src/index.ts', id, file, `--props=${pf}`, '--image-format=jpeg', `--jpeg-quality=${q}`, '--log=error'], {cwd: here, stdio: 'inherit'});
    if (fs.statSync(file).size <= 2 * 1024 * 1024) break;
  }
  console.log(file, Math.round(fs.statSync(file).size / 1024) + 'KB');
}

if (args.includes('--set-poster')) {
  if (opt('--out')) { console.error('--set-poster 只能配合默认输出目录'); process.exit(1); }
  const mp = path.join(ep, 'meta.json'); const meta = JSON.parse(fs.readFileSync(mp, 'utf8'));
  meta.poster = 'cover-16x9.jpg'; fs.writeFileSync(mp, JSON.stringify(meta, null, 2) + '\n'); console.log(`${slug}/meta.json poster → cover-16x9.jpg`);
}
