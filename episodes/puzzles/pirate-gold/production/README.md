# P09 · 海盗分金币

本期从最新主干`2159b75f8eb2fc246b7ff0174c31ac8542f97de6`开工，选择[#213](https://github.com/linhongcun/video-studio/issues/213)，EP54／趣味推理P09／pirate-gold。开工后执行环境短暂不可用，先在PR463保存静态草稿；环境恢复后接着生成本期配音与动画，恢复事实见startup.json。旧草稿QA保留其当时范围，不能当作后续媒体证据。

本期只复用现存共享TTS、句级装配、起音、整轨、混音、冻结与原题/机构资料列表工具；未继承P07或其他旧片的声轨、分镜、媒体、冻结或QA身份。两源实读与数学核验见research*、references.json、model-verification.json；实际V8核验和恢复后Node复跑分别保存在不同回执。主模型含提案者投票、至少半数通过、同钱反对，五人分配98／0／1／0／1。

## 制作入口

从仓根执行；首次依当前锁文件为本期remotion安装`npm ci`。选定takes已保存，普通复核不重复请求非确定性TTS。

```bash
node site/scripts/check-references.mjs --sources episodes/puzzles/pirate-gold/production
python3 episodes/puzzles/pirate-gold/production/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes/puzzles/pirate-gold/production
python3 episodes/_shared/voice/build.py --dir episodes/puzzles/pirate-gold/production
python3 episodes/puzzles/pirate-gold/production/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes/puzzles/pirate-gold/production --mode whole
python3 episodes/puzzles/pirate-gold/production/verify.py
```

正文实测4801帧／160.033秒、14镜28句、4章。28声学句首与真实board句cue分别检查；plan未声明术语label，label_onset_strict的0项不表示完成术语逐词对齐。未执行逐字ASR或全片语义听辨，producer与独立声音检查的实际能力以各自QA为准。

无字幕真实动态、COPYFIT、三比例封面与4:3安全区通过并停写后：

```bash
python3 episodes/puzzles/pirate-gold/production/freeze.py
python3 episodes/puzzles/pirate-gold/production/freeze.py --verify
npm --prefix episodes/puzzles/pirate-gold/production/remotion run check:types
bash episodes/puzzles/pirate-gold/production/render-final.sh
python3 episodes/puzzles/pirate-gold/production/verify.py --final
```

Composition为PirateGold，入口remotion/src/index.ts。唯一高清编码锁`/tmp/video-studio-render.lock`；默认入口先资料与冻结核验，再渲染本期正文，将full-range BT.601像素实际转换为limited BT.709，共享混音后自动追加同紫色原题/机构参考列表，每页最多4项、5秒。最终交付video.mp4，不能发布out/body.mp4。参考列表的原有版式及完整媒体引擎保持原字节，本期adapter只选择palette、色彩转换和真实正文来源。

图文两处SourceQuote与编码前Figure图位一并冻结：第09镜3000帧／100秒，第13镜4365帧／145.5秒。成片后从同一准确帧做limited709→full601 JPEG像素转换并实看；若正文制作稿后续需要改动，另保存派生与SHA，不能改旧冻结输入追认。

发布复制最终video、JPG、文章、字幕、分镜、来源与附录两份回执；metadata读取render-result.json真实字段，burnedInCaptions按实际成片设置。GitHub交付按持续授权执行；外平台本轮未获新发授权。实际独立预检、成片、站点及上线结果分别由qa与release/publication记录，不由本说明预记通过。
