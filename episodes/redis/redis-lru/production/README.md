# Redis EP52 · 近似LRU 制作输入

本期为issue302《Redis近似LRU：为什么未必淘汰真正最久没用的键？》，slug `redis-lru`，Redis系列。制作基线 `01cd181caf24d4a8ce846c0eb8faeeab8f0054e2`；新实体production/publication目录，不依赖已经移出的episodes-codex缓存。

本文件是编码前输入快照；后续最终编码、发布和独立检查状态写新回执，不改写已冻结输入。本轮用户授权制作Redis相关待办，GitHub本站交付沿持续授权；不包含外部平台投稿。

## 研究、叙事与教学边界

Redis8.4.0 / 官方commit `60ba86f3c8b4e1ec96451171753a0a38e5c45a0c`；官方Key eviction固定docs提交 `8e40c52452233daad74a303d3714586f53640a36`。实际GET、解码原文、标题/连续短引与产品/文档许可原文保存在sources，具体读到的执行范围见research。Redis8产品源码为RSALv2/SSPLv1/AGPLv3三选许可，文档按保存的官方CC许可原文保留；不误用识别图标的MIT许可概括源码或文档。

完整主线：同一八键访问史 → 精确LRU参照 → 近似抽样C/D/E →16项候选池 → 先删C而A留存 → 旧D/E保留 → 新FGH加入后D胜出 → 失效候选只做存在检查并跳过。两轮示例无额外读取且位于同一粗时钟；旧分数是采样时快照，不每轮全量更新。ghost独立条件先DEL E、写K填空，再有L写入压力，不能把DEL本身当作额外淘汰触发。

model.py为确定样本的有限教学模型，26项检查、7个关键快照，不模拟Redis字典随机数，主例不含等分候选，不声称精确复刻C的等分插入顺序。runtime_verify.py为真实loopback进程，独占16700，samples1/allkeys-lru/noTTL。成功记录保存1个fresh进程试验、7项断言，A空闲8秒仍存活、D空闲5秒被淘汰、evicted增1/expired0。产品实测只观察实际键/内存/统计，不证明动画预设CDE/FGH样本。之前一次命令JSON序列化失败的实际尝试独立保留，不冒充成功receipt；脚本与产品实验均不是性能基准。

## 音轨与动画

script.md为独立叙事批准的12镜24句；完整SHA `70f6e253282c7122938d7a2fd856abe737b4878af7699fc4de28123e12c49e03`。实际选中a声源经共享prep/gen/build生成4313帧、143.7666667秒，voiceSHA `552d44714b59bbb94f372fe26fede262d1f30492b158ad31e59b1d8d3f2c8ee2`。LRU/CPU仅送模分字母，不改字幕。words为真实句级声学包络，没有逐字ASR或内层字词对齐；无独立首字标签cue，所以label入口报告0cue，不把它当作已校验任意内部术语时点。

独立voice信号检查由根协调；源音轨约-16LUFS/-1.3dBTP不是最终AAC的TP目标，正式默认mix执行两遍响度/峰值控制后另量最终音轨。未执行ASR、全片人工听辨、真机或用户观看认可不写通过。

Main.tsx引用不可变Redis Frame/theme/style，EP52与短题近似LRU；按每个动作真实因果画键、样本复制、保留候选、存在检查与删除。数据与池项分层，顺序参照使用第二行渐次建立，避免多键对向运动交叉。SVG几何helper入口显式转Number，初版坐标字符串加法造成文字越界的真实预演与修复后50帧/DOM留证保存qa-self。

三比例封面由根扩展现行Redis模板v3，来源/许可、字体、输入与图片SHA记录在covers/cover-style.json，并复制为本期covers.json写入board.meta.covers；旧系列模板和已发布媒体保持。由此产生的covers字段更新不改音轨、时序或视觉模型，有限保留证明见qa-self。

## 从当前输入复现

依赖以本期remotion/package-lock.json执行fresh `npm ci`（4.0.534/React18.3.1）。Python使用已配置的 `/workspace/.venvs/video-studio/bin/python`，含numpy/scipy/soundfile/Pillow。字体入口 `font-check.py`解析6个实际字体并绑定文件完整SHA；verify不改旧身份。

以下为本期实际入口，不复制共享配音、起音、混音和时序实现：

```bash
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/build.py --dir episodes/redis/redis-lru/production
/workspace/.venvs/video-studio/bin/python episodes/redis/redis-lru/production/assemble.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir episodes/redis/redis-lru/production --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/check_sentence_episode.py episodes/redis/redis-lru/production
node episodes/redis/redis-lru/production/remotion/self-preview.mjs
node episodes/redis/redis-lru/production/remotion/self-preview.mjs --clips
```

上述build/assembly是制作步骤，会写输入；冻结后不以重跑代替只读验证。独立动态与文章/资料通过、根关闭实际额外输入清单后，才运行以下正式步骤（从本目录）：

```bash
python3 freeze.py
python3 freeze.py --verify
bash render-final.sh
python3 verify.py --final
```

render-final.sh持全局 `/tmp/video-studio-render.lock`；默认render先检查真实资料/输入，再输出正文，实际fullBT601→limitedBT709像素转换，共享mix，最后追加同色原始题名/Redis机构资料页。2项来源同页5秒，预计完整4463帧，以真实render-result/receipt为准；不能拿out/body.mp4当最终交付。

文章已按真实board计划两张Figure：2025f/67.5s为池中C70与全局A90对照，2872f/95.7333333s为旧D60胜过新FGH、尚未删除D。正文JPEG需从正式编码后逐帧抽取并真实709→601/full范围转换核对，不能拿预演图冒充最终媒体图。

最终还须审实际正文/字幕、全部参考资料页首中末、完整解码、AAC响度/TP、MDX来源与配图、原生播放器及线上完整SHA，实际状态保存本轮新回执；上述命令和源输入不预记这些最终结果。
