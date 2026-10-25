// Run from the repository or site/: node site/scripts/check-episode-dates.mjs [--built]
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {transformSync} from 'esbuild';

const site = path.resolve(import.meta.dirname, '..');
const root = path.resolve(site, '../episodes');
const source = fs.readFileSync(path.join(site, 'src/lib/episodes.ts'), 'utf8');
const dateSource = source.slice(source.indexOf('/** 历史日期'), source.indexOf('/** NEW 根据'));
const {code} = transformSync(dateSource.replace(/^export /gm, ''), {loader: 'ts'});
const {dateIso, episodeDates, fmtDate, fmtVersion} = vm.compileFunction(
  `${code}\nreturn {dateIso, episodeDates, fmtDate, fmtVersion};`, [])();

assert.equal(dateIso('2026-10-25'), '2026-10-25T00:00:00+08:00');
assert.equal(fmtVersion('2026-10-25'), '2026-10-25 版');
assert.equal(fmtDate('2026-10-25'), '2026年10月25日');
assert.equal(fmtVersion('2026-10-24T16:30:12Z'), '2026-10-25 00:30:12 版');
assert.equal(fmtDate('2026-10-25T00:30:12+08:00'), '2026年10月25日 00:30:12');
assert.equal(fmtVersion('2026-10-25T15:30:12+08:00'), fmtVersion('2026-10-25T07:30:12Z'));
assert.notEqual(fmtVersion('2026-10-25T15:30:12+08:00'), fmtVersion('2026-10-25T15:30:13+08:00'));
for (const bad of ['', '2026-02-30', '2026-02-30T12:00:00Z', '2026-10-25T15:30:00', '2026-13-01'])
  assert.throws(() => dateIso(bad), /无效/);
assert.throws(() => episodeDates({createdAt: '2026-10-25', updatedAt: '2026-10-24', publishedAt: '2026-10-25'}), /早于/);
const original = {publishedAt: '2026-10-12'};
assert.equal(episodeDates(original).updatedAt, '2026-10-12');
assert.equal(Object.keys(original).length, 1, 'Reading legacy dates must not mutate metadata');
const draft = {draft: true, createdAt: '2026-10-25T15:30:00+08:00', updatedAt: '2026-10-25T15:30:00+08:00'};
assert.equal(episodeDates(draft).publishedAt, undefined, 'A draft may exist before first publication');
assert.throws(() => episodeDates({...draft, draft: false}), /缺少首次公开时间/);

let total = 0;
const built = process.argv.includes('--built');
const library = built ? fs.readFileSync(path.join(site, 'dist/library/index.html'), 'utf8') : '';
const rss = built ? fs.readFileSync(path.join(site, 'dist/rss.xml'), 'utf8') : '';
for (const slug of fs.readdirSync(root)) {
  const file = path.join(root, slug, 'meta.json');
  if (!fs.existsSync(file)) continue;
  const meta = JSON.parse(fs.readFileSync(file, 'utf8'));
  assert.ok(meta.createdAt && meta.updatedAt, `${slug}: explicitly record both content dates`);
  const dates = episodeDates(meta);
  total++;
  if (!built || meta.draft) continue;
  const html = fs.readFileSync(path.join(site, `dist/episodes/${slug}/index.html`), 'utf8');
  assert.ok(html.includes(fmtVersion(dates.updatedAt)), `${slug}: missing current version`);
  assert.ok(html.includes('创建于') && html.includes('修改于'), `${slug}: both dates must be visible, including on the same day`);
  for (const date of [dates.createdAt, dates.updatedAt]) assert.ok(html.includes(fmtDate(date)), `${slug}: incorrect displayed date`);
  const jsonLd = JSON.parse(html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
  assert.equal(jsonLd.dateCreated, dateIso(dates.createdAt), `${slug}: dateCreated`);
  assert.equal(jsonLd.dateModified, dateIso(dates.updatedAt), `${slug}: dateModified`);
  assert.equal(jsonLd.uploadDate, dateIso(dates.publishedAt), `${slug}: uploadDate must remain first publication`);
  if (!meta.archived) {
    assert.ok(library.includes(fmtVersion(dates.updatedAt)), `${slug}: missing card version`);
    const item = rss.split('<item>').find((item) => item.includes(`/episodes/${slug}/`));
    assert.ok(item, `${slug}: missing RSS item`);
    assert.equal(Date.parse(item.match(/<pubDate>([^<]+)<\/pubDate>/)[1]), Date.parse(dateIso(dates.publishedAt)), `${slug}: RSS must keep first publication`);
  }
}
console.log(`Episode dates passed: ${total} records; historical precision, timezone boundaries, same-day versions, invalid inputs${built ? ', built pages and RSS' : ''}.`);
