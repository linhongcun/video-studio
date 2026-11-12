# EP58 · LeetCode 347 · 前K个高频元素

制作基线：`6868fd40b509a0811e5a89575639b16948144ca1`，分支`codex/lc347-top-k`。新期工程依当前package-lock fresh npm ci，不复用旧工程媒体、来源核验或冻结记录。初始工作区干净；本地legacy `episodes/degradation` 仅含未跟踪node_modules，移至`/tmp/video-studio-legacy-degradation-cache`保留以通过现行实体布局检查。

Python依赖见`requirements-runtime.txt`；本次使用`/workspace/.venv-lc347`（system-site-packages，仅额外安装soundfile 0.14.0）。执行下列TTS命令前激活该环境。Remotion依赖为本期fresh npm ci。

顺序：独立脚本逻辑/文章审读 → 真实冰糖配音 → 共享装配/铺轨/起音 → 实际静帧及无字幕连续小样/独立复核 → 停写冻结 → 正式正文及双片尾 → 独立成片检查 → 图文、站点接入及浏览器检查 → GitHub交付。

```sh
python3 episodes/_shared/voice/prep.py --dir episodes/leetcode/top-k-frequent-elements/production
python3 episodes/_shared/voice/gen.py --dir episodes/leetcode/top-k-frequent-elements/production
python3 episodes/_shared/voice/build.py --dir episodes/leetcode/top-k-frequent-elements/production
python3 episodes/leetcode/top-k-frequent-elements/production/prepare_code_endcard.py
python3 episodes/_shared/place_v2.py --dir episodes/leetcode/top-k-frequent-elements/production --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes/leetcode/top-k-frequent-elements/production
python3 episodes/_shared/check_sentence_episode.py episodes/leetcode/top-k-frequent-elements/production
node site/scripts/check-references.mjs --sources episodes/leetcode/top-k-frequent-elements/production
python3 episodes/leetcode/top-k-frequent-elements/production/scripts/check_audio.py
```

预检从本期remotion运行`node scripts/qa.mjs --out-dir ../qa/preflight --scale .5`；无字幕连续片段加`--clips` JSON参数，实际命令见独立预检报告；独立报告记录实际命令和输入SHA。source-sha256.json只在停写、预检通过后创建，不能重写追认已编码文件。

```sh
python3 episodes/leetcode/top-k-frequent-elements/production/freeze.py
cd episodes/leetcode/top-k-frequent-elements/production/remotion
npm run typecheck
npm run render
```

默认render调用本期私有limited BT.709薄包装（复用共享来源/冻结/原题作者/媒体引擎，不修改历史共享实现）；out/body.mp4只含讲解与5秒Python卡，production/video.mp4另含5秒原题/署名列表。正式输入验证：`python3 freeze.py --verify`；最终媒体验证：本期`python3 render.py --verify`。

本期起音仅声明句首“小顶堆”的声学同步。原始take、TTS文字元数据和整轨PCM可检查；本机无faster-whisper包或缓存模型，不声称已完成逐字识别、配音语义听辨或实体手机测试。正式质量与交付结论见本期qa记录。

当前真实装配：5654正文帧（188.466667秒），完整Python卡5504..5653；参考资料另外150帧，预期最终5804帧（193.466667秒）。32句，5章；最终旁白SHA `fcca505adaaea88986e9e4da317e0d0706789ccfa0283f87cd861bff56e0f11f`。Figure预定4784帧（159.466667秒）是14镜落稳的最终堆；正式编码后提取，源稿图位已启用。

实际Chromium小样发现默认pc/BT.601编码变暗，保留原预检和qa/precolor候选清单；正式正文改为Remotion的`--color-space=bt709`真实zscale limited转换，资料页通过本期私有adapter采用相同转换/标签。direct709短样实际背景(14,24,41)、surface(21,35,56)，与PNG(15,23,42)/(22,36,58)每通道差≤2；完整成片仍需逐帧颜色与网页复验。

本地最终质量检查见`qa-final.json`、`qa-final.md`和`qa-site.json`。最终video SHA256：`98d69b4704bb48ca3e259f92401b107cf748020d2901c87b0e8185a8778f8553`。冻结器默认会写入新清单，只有`--verify`为只读；它不提供`--help`入口。

实际首发：v0.106.0／PR #482／Pages43132468762，8项完整线上GET通过，#83已completed关闭。线上核验使用`qa/verify_online_postpublish.py --execute --version v0.106.0 --expected-commit ed088d557e59512c8b27946af4c3d39f91c48e16`：保留冻结旧检查器，修正其tree/main假设以符合站点完整构建SHA固定链接；本地Release-aware构建需NODE_USE_ENV_PROXY=1及仅环境传入GITHUB_TOKEN，实际HTTP证据见qa/online-verification.json。
