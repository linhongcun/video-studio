# LC.704 二分查找

题目先于解法：先交代升序无重复数组、目标、从0开始的下标与未找到返回-1，再用同一数组的两次独立查找解释闭区间排除。目标13返回6，目标8在检查最后一格后返回-1。14镜28句，4748帧/30fps，约2分38秒；最后150帧为完整Python静态代码卡，提示暂停，无旁白和旧字幕。

制作issue为[#76](https://github.com/linhongcun/video-studio/issues/76)。公开资料、可执行核验、编辑检查分别见research.md、research/algorithm-verification.json、qa-editorial.md。动画/正式媒体/网站与上线结果以各自实际报告为准，不能由这些文稿检查推断通过。

## 重建

在仓库根目录执行共享配音流程：

```sh
python3 episodes/_shared/voice/prep.py --dir episodes-codex/binary-search
python3 episodes/_shared/voice/gen.py --dir episodes-codex/binary-search --jobs jobs.json
python3 episodes/_shared/voice/build.py --dir episodes-codex/binary-search
python3 episodes-codex/binary-search/prepare_code_endcard.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/binary-search --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/binary-search
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/binary-search
python3 episodes-codex/binary-search/freeze.py
```

`gen.py`会复用已有选中take；重新合成会改变音轨及句时，须重新装配、检查、冻结后再编码。没有复制整轨生成、起音或混音算法。片尾准备器仅调用共享装配并声明静态卡片边界。代码执行源、显示JSON及文章程序逐字相同。

在本期remotion目录安装依赖、类型检查和生成封面；正式编码使用短TMPDIR及共享编码锁：

```sh
npm ci
./node_modules/.bin/tsc --noEmit
npm run covers
mkdir -p out/tmp
ln -sfn /workspace/video-studio/episodes-codex/binary-search/remotion/out/tmp /workspace/bs-tmp
TMPDIR=/workspace/bs-tmp flock /tmp/video-studio-render.lock npm run render
cp out/mix-report.json ../mix-report.json
```

回到仓根核对同一份冻结输入与真实成片：

```sh
python3 episodes-codex/binary-search/freeze.py --verify
python3 episodes-codex/_shared/check_encoded_episode.py episodes-codex/binary-search
python3 episodes-codex/_shared/extract_encoded_samples.py episodes-codex/binary-search
```

真实预演的命令、PNG和无字幕连续片段清单见qa-motion-samples.json；开发临时时序不作为正式媒体证据。发布后执行verify_online.py，实际GET并核对完整媒体、海报、28句VTT、四章精确时间、系列/资料库/RSS及真实Release条目。

当前环境未安装faster-whisper，也未发现可用转写工具；已执行句级边界、共享声学起音、字幕/原文一致性和样本数检查，不声称逐字ASR、全片人工听辨或学习效果测量。生成初始两个请求停滞，终止本次对应子进程后用同一共享生成器重试两句，其余选中音频不重做；28句最终均具备实际take、送模文本与48k实体音轨。
