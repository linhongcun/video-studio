import test from 'node:test';
import assert from 'node:assert/strict';
import {readerSummary, readerLinks, readerNotes} from '../src/lib/release-notes.mjs';

test('summaries keep reader changes and leave production evidence in the Release', () => {
  const body = '数据库四期封面统一，方便按系列辨认。后续同系列沿用这一风格。\n\n12图与44资产、456冻结输入检查通过，SHA abcdef0123456789。';
  assert.equal(readerSummary(body), '数据库四期封面统一，方便按系列辨认。后续同系列沿用这一风格。');
  assert.equal(readerSummary('## 更新\n\n冻结清单和 SHA 已检查通过。\n\n不把后面的质检记录当摘要。'), '');
});

test('Markdown lists become safe page and cover links instead of literal Markdown', () => {
  const body = [
    '- [EP.15 数据库索引](https://linhongcun.github.io/video-studio/episodes/db-index/)',
    '- [封面总览](https://github.com/linhongcun/video-studio/blob/main/design/database-covers/preview.png)',
    '- [下载PNG/JPG素材包](https://raw.githubusercontent.com/linhongcun/video-studio/main/design/database-covers/covers.zip)',
    '- [制作与验收记录](https://github.com/linhongcun/video-studio/tree/main/docs/archive/qa)',
    '- [重复课程](https://linhongcun.github.io/video-studio/episodes/db-index/)',
    '- [危险](javascript:alert(1))',
    '- [伪装](https://user:password@linhongcun.github.io/video-studio/library/)',
    '- [外部链接](https://example.com/design/covers.zip)',
  ].join('\n');
  const links = readerLinks(body);
  assert.equal(links.length, 3);
  assert.deepEqual(links[0], {label: 'EP.15 数据库索引', href: '/video-studio/episodes/db-index/', external: false});
  assert.equal(links[1].label, '封面总览');
  assert.equal(links[2].external, true);
});

test('a linked opening paragraph remains readable and headings omit version duplication', () => {
  const notes = readerNotes({name: 'v0.62.0：Agent Skills，只上站点', kind: '新增', body: '新增：[Agent Skills](https://linhongcun.github.io/video-studio/episodes/agent-skills/)。'});
  assert.equal(notes.heading, 'Agent Skills');
  assert.equal(notes.summary, '新增：Agent Skills。');
  assert.equal(notes.links.length, 1);
});

test('version/watch metadata does not hide the actual change, and bare URL clauses are omitted', () => {
  const body = '# P05：先说明为什么不能一直二分\n\n版本：v0.70.2。观看视频与配套文章：https://linhongcun.github.io/video-studio/episodes/egg-drop/\n\n根据观看反馈，重做开头两镜：先演示鸡蛋耗尽但答案仍不唯一，再说明逐层查的目的。完整示例保留。';
  assert.equal(readerSummary(body), '根据观看反馈，重做开头两镜：先演示鸡蛋耗尽但答案仍不唯一，再说明逐层查的目的。完整示例保留。');
  assert.equal(readerSummary('观看视频：https://linhongcun.github.io/video-studio/episodes/egg-drop/\n\n重做开头两镜。'), '重做开头两镜。');
  assert.equal(readerSummary('桌面导航栏新增 GitHub 图标入口，手机端菜单新增“GitHub 仓库”，点击后在新标签页打开 https://github.com/linhongcun/video-studio 。'), '桌面导航栏新增 GitHub 图标入口，手机端菜单新增“GitHub 仓库”。');
});
