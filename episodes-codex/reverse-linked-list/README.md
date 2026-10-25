# 反转链表：为什么要先保存下一个节点？

本批制作与开工同步见[三片批量记录](../../docs/leetcode-batch-20261025/README.md)。本目录为当前制作工程，站点副本为 `episodes/reverse-linked-list/`。真实MiMo句级配音、共享整轨/起音/混音；不声称逐字ASR或全片人工听辨。

Python工具环境需numpy、scipy、soundfile与Pillow；Node依赖按本期锁文件安装。

## 实际入口

30fps，4961帧，165.367秒。末150帧为完整静态Python代码，提示暂停，旁白PCM为零且无字幕；原生播放器支持暂停和字幕。完整程序、文章代码块、显示JSON同源，执行核验见 `research/algorithm-verification.json`。

```sh
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/check_sentence_episode.py episodes-codex/reverse-linked-list
/workspace/.venvs/video-studio/bin/python episodes-codex/reverse-linked-list/freeze.py --verify
```

制作输入实际定稿后才运行 `freeze.py` 写入清单；已编码或发布的检查必须用 `--verify`，不能重写清单追认旧媒体。真实有字幕预览及无字幕连续动作记录在 `qa-motion-samples.json`，预检和成片审分别看 `qa-preflight.md`、`qa-final-independent.md`（产物生成前不得推断通过）。

到本期 `remotion/`：`./node_modules/.bin/tsc --noEmit`；`npm run stills -- out/preflight`；`npm run covers`。完整渲染用短TMPDIR、共享 `/tmp/video-studio-render.lock` 串行执行 `npm run render`，并发2。依赖由本批two-sum当前锁文件新安装，另两期仅共享该有效目录，不引用已删除旧工程。

编码后复制 `remotion/out/mix-report.json` 至期根；运行共享 `check_encoded_episode.py` 和 `extract_encoded_samples.py` 核对实际MP4及预览一致性。发布只复制MP4/JPG和必要站点文本数据，不复制WAV、PNG与Remotion工程。网站统一验证与线上完整SHA记录在批量目录。
