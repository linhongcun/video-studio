# LC.11 · 盛最多水的容器

标题：《盛最多水的容器：为什么每次都移动短边？》。对应[#78](https://github.com/linhongcun/video-studio/issues/78)，用户授权制作、合并项目并发布GitHub网站。站点展示LC.11，内部排序ep22；独立LeetCode系列，不要求先学分布式事务。制作检查不等于用户已经观看认可。

## 本期内容

同一组高度`[2,3,10,5,7,8,9]`先解释“距离×较矮高度”，再固定短边、逐个缩小另一端的距离，看见整组配对为什么都不可能更优。正式查找和排除演示明确分开，扫描面积12→15→36→24→14→5，保留最大值36。等高与完整Python实现见配套文章。

22镜44句、4章，1920×1080、30fps，真实音轨6544帧，约3分38秒；冰糖自然语速。章节实际起点由冻结分镜计算：面积0秒、排除依据44.267秒、完整扫描103.067秒、代码176.2秒。没有额外全局片尾。

## 文件入口

- `research.md`、`research/verify_algorithm.py`：已读公开题意、独立推导与可复现实现验证；来源获取限制如实记录。
- `script.md`、`article.mdx`、`pronunciation.md`：旁白、配套文章和读音表。
- `plan.json`、`episode-config.json`：共享句级装配所需镜头映射与配置；不另写配音或起音算法。
- `storyboard.json`、`words.json`、`voice.wav`：真实句级时间、声学起音和最终人声。
- `visual-direction.md`、`knoll-props.md`：动画因果、分支重置、检查与发布范围。
- `qa-independent.md`与`voice/*audit*.json`：独立复核与实际能力边界。
- `source-sha256.json`、`qa-timing.json`、`render-result.json`、`qa-final.md`、`release.md`：冻结、媒体与发布收尾记录，按实际完成情况生成。

## 构建

```sh
cd episodes-codex/container-most-water/remotion
npm ci
npx tsc --noEmit
npm run covers
npm run stills -- out/qa-local
npm run render
```

所有渲染和封面使用本期package脚本。输出视频在制作目录`video.mp4`，站点实际读取`episodes/container-most-water/`中的逐字节副本。大批采样/编码前同时检查工作盘与临时盘；可将TMPDIR设在当期已忽略的`remotion/out/`内。

共享装配、时序和冻结流程：`episodes-codex/_shared/README.md`；配音只用`episodes/_shared/voice/`，起音只用`episodes/_shared/onset_rule.py`。真实音轨/图形稳定后再冻结，正式编码后核对全部输入SHA；不可用更新清单的方式认可旧视频。

## 检查范围

句级字幕逐字与脚本一致、连续覆盖全片，48kHz音轨样本数与6544帧匹配，whole放置偏移为0；唯一首次术语“双指针”通过真实声学起音窗口，无豁免。所有44句选中raw→48k PCM逐样本闭合，6句风险候选换过take。具体动态预演与实际编码查看范围由QA文件记录。

本地无可用官方ASR模型，未执行逐字ASR、句内词级对齐或全片人工听辨。字符兼容字段只表示句包络，不能当成词级时间。平台投稿不在本次授权内。
