# P06 · 12球称重

本期从main `d2548e674a8cbc3b5994388894a941a1294e6c97`开工，选择[#210](https://github.com/linhongcun/video-studio/issues/210)，EP56／`twelve-balls`。12球恰1异常、未知轻重、无外部正常参照，最多3称须找编号及方向。先以24候选与剩余称数推导分组，再构造混合候选；主例6轻走左重→左重→平衡，其他分支从明确前提恢复，完整树与24表留配套文章。

独立Python精确有理质量及Node BigInt分别执行完整24状态，有限质量夹具与任意合法质量的等数量消去证明分开；原始结果见model-verification及qa/model-independent-results。参考清单和实际来源研究均为本期新建，未继承旧片媒体、声音、时序、冻结或QA身份。

## 实际制作入口

新remotion依本期锁fresh npm ci；只复用当前共享实现和薄包装。选定takes保留，普通复核不重新请求非确定性TTS。

```bash
node site/scripts/check-references.mjs --sources episodes/puzzles/twelve-balls/production
python3 episodes/puzzles/twelve-balls/production/verify_protocol.py
python3 episodes/puzzles/twelve-balls/production/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes/puzzles/twelve-balls/production
python3 episodes/_shared/voice/build.py --dir episodes/puzzles/twelve-balls/production
python3 episodes/puzzles/twelve-balls/production/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes/puzzles/twelve-balls/production --mode whole
python3 episodes/puzzles/twelve-balls/production/verify.py
```

配音来源与选段、真实句级时序和能力边界以本期voice/与QA实际记录为准；不把声学句界当逐字ASR或全片语义听辨。公开音轨为逐字节一致的实体文件。术语cue没有声明时，严格label检查0项不代表完成内部词对齐。

真实voice就位、动画及文章准确图位定稿、独立动态与封面复核完成后，所有源写入负责人停写；新增文件先纳入diff样式检查，避免未跟踪文件被遗漏，再冻结与编码：

```bash
python3 episodes/puzzles/twelve-balls/production/make-props.py
python3 episodes/puzzles/twelve-balls/production/freeze.py
python3 episodes/puzzles/twelve-balls/production/freeze.py --verify
npm --prefix episodes/puzzles/twelve-balls/production/remotion run check:types
bash episodes/puzzles/twelve-balls/production/render-final.sh
python3 episodes/puzzles/twelve-balls/production/verify.py --final
python3 episodes/puzzles/twelve-balls/production/export-article.py
```

Composition为TwelveBalls，1920×1080、30fps。唯一完整渲染锁`/tmp/video-studio-render.lock`；默认入口先来源与冻结检查，再渲染正文，实际full601→limited709像素转换，共享混音后接默认5秒原题／作者资料列表。最终交付是video.mp4，不能用out/body.mp4代替。Figure图位编码前按真实稳定态写入并冻结；最终JPEG从同一准确整数帧做limited709→full601像素转换后实际查看。

完整媒体、原生桌面／手机模拟视口、引用／回看和最终完整HTTPS SHA检查按真实执行范围留QA。发布元数据读取render-result实际区间、帧数与媒体SHA，burnedInCaptions须由实际编码图确认。GitHub站点按持续授权交付，外部平台本轮未获批次新发授权；未完成的检查不由本说明预记通过。
