# 趣味推理：正文延续封面

P01–P05当前视觉入口为各期`remotion/src/cover-continuity/index.ts`，读取原分镜、模型与字幕。字体、P标识和静态边缘图形在本目录；色值直接读取`../puzzles-covers/catalog.json`。浅紫表示系列/备选，珊瑚强调当前操作，青色表示已确认状态，粉色表示失败/排除；数值和标签继续明确身份。

原来的`src/index.ts`、制作源、音轨和冻结清单保留历史字节，不再用旧`npm run render`覆盖本轮成片。每期的当前制作说明位于`revisions/cover-continuity/README.md`，`meta.sourcePath`指向该修订。

## 复现

先按该期当前`remotion/package-lock.json`安装`npm ci`，备好Chromium、ffmpeg、Python Pillow及Noto CJK SC。五期当前锁的非根packages条目完全相同，可共用当前保留的horse-racing依赖；不能链接已删除旧工程。

基线发布MP4是唯一声音输入。按各期`baseline-publication.json`记录的`baselineCommit`和完整SHA，从Git恢复到`work/puzzles-video-style/baseline/<slug>.mp4`，例如Python调用`git show <commit>:episodes/<slug>/video.mp4`并将stdout以二进制写入目标；不得将新发布片误当旧基线。新制作也可显式传`--baseline`，须与已记录身份相同。

从仓根执行（`<slug>`换为具体一期）：

```bash
node episodes-codex/_shared/puzzles-video/qa.mjs <slug> --out-dir work/puzzles-qa/<slug>
python3 episodes-codex/_shared/puzzles-video/render.py <slug> --freeze
python3 episodes-codex/_shared/puzzles-video/render.py <slug> --render
python3 episodes-codex/_shared/puzzles-video/render.py <slug> --verify
```

默认仅显示plan；已冻结输入有变化时必须保留旧revision并选新的`--revision`，不重写清单追认。渲染先做资料预检、核对独立清单，再生成无声正文，完整复制基线AAC并核对所有包、PTS/DTS/持续时长和解码PCM。片尾复用已冻结的原题/署名排版与媒体验证器，只通过独立adapter读取紫色palette。最终附录继续每页最多4条、每页5秒，无旁白；输出、receipt、真实SHA及新清单均在本期revision，不列为编码前输入。

旧冻结只保留历史身份；新检查不冒称旧素材重渲复现、逐字ASR、全片人工听辨或用户已经认可新版。资料事实和实读日期沿原记录，视觉修订未增加事实或冒称重新技术调研。
