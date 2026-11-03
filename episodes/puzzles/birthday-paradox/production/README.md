# P07 · 生日悖论

本期从 [选题 #211](https://github.com/linhongcun/video-studio/issues/211) 制作新片，系列为趣味推理，slug `birthday-paradox`。开工从最新主干 `89fb1705a6f51c934a720d825a26e2593c4a1836` 建立 `codex/p07-birthday-paradox`；当时已发布最大 EP 为 52，本期编号由实际元数据确认。

输入、时序、媒体和验收结果分别以本期文件为准。本目录不继承旧片成片、音轨、冻结清单或 QA 身份；只复用现存句级配音、起音、铺轨、混音、参考资料与冻结基础设施。配色、字体和静态边缘样式沿当前趣味推理共享入口，动画使用本题自己的生日与条件概率模型。

## 制作入口

以下命令从仓根执行。先完成公开来源实读、脚本与数学复核，再请求新配音；保留选定 takes，不为普通复核重请求 TTS。

```bash
node site/scripts/check-references.mjs --sources episodes/puzzles/birthday-paradox/production
python3 episodes/puzzles/birthday-paradox/production/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes/puzzles/birthday-paradox/production
python3 episodes/_shared/voice/build.py --dir episodes/puzzles/birthday-paradox/production
python3 episodes/puzzles/birthday-paradox/production/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes/puzzles/birthday-paradox/production --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes/puzzles/birthday-paradox/production
python3 episodes/puzzles/birthday-paradox/production/verify.py
```

`assemble.py` 只委托共享句级装配并声明紫色画布，不复制整轨、起音或字幕算法。兼容字符字段只是整句包络；未执行逐字 ASR、全片人工语义听辨时，不将信号检查写成上述能力通过。

独立动态、真实时序、COPYFIT、三比例封面及 4:3 安全区检查完成并停写后：

```bash
python3 episodes/puzzles/birthday-paradox/production/freeze.py
python3 episodes/puzzles/birthday-paradox/production/freeze.py --verify
npm --prefix episodes/puzzles/birthday-paradox/production/remotion run check:types
bash episodes/puzzles/birthday-paradox/production/render-final.sh
python3 episodes/puzzles/birthday-paradox/production/verify.py --final
```

新期动画依当前锁文件 `npm ci` 安装到本目录。共享完整渲染锁为 `/tmp/video-studio-render.lock`，composition 为 `BirthdayParadox`，入口 `remotion/src/index.ts`。

默认 `npm run render` 先检查来源与同一份冻结清单，生成含新声轨的正文，将 full-range BT.601 **像素转换**为 limited BT.709，调用共享混音，再自动追加同色的原题／作者资料列表，每页最多四项、五秒。最终交付 `video.mp4`，不交付 `remotion/out/body.mp4`。本地 `references-adapter.py` 只适配紫色、实际色彩转换和新片正文来源，既有附录版式与完整媒体保真引擎保持原字节。

图文在编码前冻结有效 Figure 图位和 SourceQuote；成片后按既定时间生成与实看图片。修改稿件须保留冻结制作稿，另记站点派生。发布时复制最终媒体、文章、来源及附录两份回执，按 `render-result.json.publicationMetadata` 填元数据，并实际核验播放器、引用、配图与线上完整 SHA。GitHub 交付按持续授权，外部平台本轮未获新发授权。实际检查和交付结果另记本期 QA 与发布记录，不由这份入口说明预记通过。

## 本期实际成片与验收

本期为EP53，最终3831帧／127.7秒（含5秒参考资料），最终媒体与图文配图已生成。独立动态、正式编码、声学/来源与本地网站检查通过，真实范围及首轮失败见[成片审](qa-final.md)和[交付记录](release.md)。GitHub发布与线上核验以交付记录后续实际结果为准，不由本说明预记完成或用户认可。
