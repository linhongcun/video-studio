// 成片帧数检查（本地运行，需要 ffprobe）：node site/scripts/check-frames.mjs [slug...]
// 规则：video.mp4 帧数 == storyboard meta.finalVideoFrames（有写时）；
//   EP.22 起（Main.tsx 有 TAIL_HOLD、Root 不再追加全局片尾卡）：成片 = 分镜 durationInFrames + 片尾停留（ending-2 30 帧）；
//   之前各期：成片 = 分镜 durationInFrames + 全局片尾卡 60 帧（episodes/_shared/branding/spec.json endCard.frames）。
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../episodes');
const endCard = JSON.parse(fs.readFileSync(path.join(root, '_shared/branding/spec.json'), 'utf8')).endCard?.frames ?? 0;
const slugs = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(root).filter((s) => fs.existsSync(path.join(root, s, 'video.mp4')));
let bad = 0;
for (const slug of slugs) {
  const dir = path.join(root, slug);
  const sb = JSON.parse(fs.readFileSync(path.join(dir, 'storyboard.json'), 'utf8')).meta ?? {};
  const mainTsx = path.join(dir, 'remotion/src/Main.tsx');
  const src = fs.existsSync(mainTsx) ? fs.readFileSync(mainTsx, 'utf8') : '';
  const m = src.match(/TAIL_HOLD[^=]*=\s*\{([^}]*)\}/);
  const tail = m ? [...m[1].matchAll(/:\s*(\d+)/g)].reduce((a, x) => a + Number(x[1]), 0) : null;
  const expected = tail !== null ? sb.durationInFrames + tail : sb.durationInFrames + endCard;
  const rule = tail !== null ? `分镜 ${sb.durationInFrames} + 片尾停留 ${tail}` : `分镜 ${sb.durationInFrames} + 片尾卡 ${endCard}`;
  const n = Number(execFileSync('ffprobe', ['-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', path.join(dir, 'video.mp4')]).toString().trim());
  const errs = [];
  if (sb.finalVideoFrames != null && sb.finalVideoFrames !== n) errs.push(`finalVideoFrames=${sb.finalVideoFrames}`);
  if (tail !== null && expected !== n) errs.push(`期望 ${expected}（${rule}）`);
  if (errs.length) bad++;
  console.log(`${errs.length ? '✗' : '✓'} ${slug}: video ${n} 帧${tail !== null ? `；${rule} = ${expected}` : ''}${errs.length ? '；不符：' + errs.join('，') : ''}`);
}
process.exit(bad ? 1 : 0);
