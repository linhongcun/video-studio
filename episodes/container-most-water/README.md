# LC.11 · 盛最多水的容器

标题：《盛最多水的容器：为什么每次都移动短边？》。对应[#78](https://github.com/linhongcun/video-studio/issues/78)，用户授权制作、合并项目并发布GitHub网站。站点展示LC.11，内部排序ep22；独立LeetCode系列，不要求先学分布式事务。制作检查不等于用户已经观看认可。

用户随后实际观看v0.49.0并认可主体，要求去掉会分散注意力的底部装饰进度线。已上线的视觉修订2仅删除这两条SVG矩形，声音与讲解时序保持；新旧预演主体逐像素相同，正式成片全帧底带扫描和解码PCM精确对照通过。该轮检查见`qa-progress-removal-independent.md`，v1完整证据保存在`revisions/progress-removal/v1-*`。

当前为视觉修订3：按用户进一步要求，在原讲解后增加完整Python解法，供感兴趣观众暂停阅读，让思路与具体程序在视频内衔接。完整16行代码卡静态显示15秒，不新增口播，不显示旧旁白字幕或装饰进度条。用户对旧主体的认可与本次代码卡预检分开记录，不能据此声称已观看认可新片尾。修订2的原分镜、音轨数据、检查、冻结及上线证据已归档到`revisions/python-endcard/v2-*`。

## 本期内容

同一组高度`[2,3,10,5,7,8,9]`先解释“距离×较矮高度”，再固定短边、逐个缩小另一端的距离，看见整组配对为什么都不可能更优。正式查找和排除演示明确分开，扫描面积12→15→36→24→14→5，保留最大值36。配套文章保留证明与完整Python实现；视频末尾也完整呈现同一份可直接提交的`Solution.maxArea`程序。

22镜44句、4章，1920×1080、30fps，冰糖自然语速。原讲解为6544帧、约218.133秒；本期在其后追加450帧、15秒静态代码卡，总计6994帧、233.133秒（约3分53秒）。代码卡从6544帧开始，原44句字幕在6543帧结束，不延伸到无旁白附录。章节原起点保持：面积0秒、排除依据44.267秒、完整扫描103.067秒、代码176.2秒。15秒代码卡是本期明确设计，不是全系列统一片尾参数。

## 文件入口

- `research.md`、`research/verify_algorithm.py`：已读公开题意、独立推导与可复现实现验证；来源获取限制如实记录。
- `script.md`、`article.mdx`、`pronunciation.md`：旁白、配套文章和读音表。
- `solution.py`、`solution.json`：逐字复用文章的完整16行程序；前者用于执行，后者保存同一文字供画面读取。
- `plan.json`、`episode-config.json`：共享句级装配所需镜头映射与配置；不另写配音或起音算法。
- `storyboard.json`、`words.json`、`voice.wav`：真实句级时间、声学起音和最终人声。
- `visual-direction.md`、`knoll-props.md`：动画因果、分支重置、检查与发布范围。
- `qa-independent.md`与`voice/*audit*.json`：首发独立复核、配音来源与当时的实际能力边界。
- `qa-python-endcard-independent.md/json`：当前完整代码卡的程序、真实时序、前段保持与阅读检查；正式媒体结论按报告实际完成状态补齐。
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

当前预编码检查已通过：16行显示代码与文章、执行源同源，独立8个代表性用例运行正确且不改输入；真实预演的原段0/3964/6543同帧PNG与修订2逐字节相同，卡片首/中/末6544/6750/6993的PNG相同。独立实际查看完整代码、缩进、最长面积公式和末尾`return best`，34px字、38px行距清楚，暂停阅读提示可见。

原44句旁白、字幕和句级区间保持。字幕逐字与脚本一致、仅连续覆盖原讲解0..6543帧；6544..6993为独立无旁白代码附录，不延长旧字幕。48kHz人声轨共6994帧：前6544帧PCM与修订2完全相同，追加450帧的720,000个样本全部为0，whole放置偏移仍为0。首次术语“双指针”的真实起音、选定takes及原有读音来源检查保持；本轮没有重新生成语音。

190项实际生产输入冻结核对、6994帧正式编码、完整解码及−16.0LUFS/−3.7dBTP检查通过；实际成片7帧保真对照和独立450卡帧扫描通过，末尾return持续可见。正式编码与独立检查见`qa-final.md`、`qa-python-endcard-independent.md/json`；网站与上线收尾按实际结果写入`release.md`。

本地无可用官方ASR模型，未执行逐字ASR、句内词级对齐或全片人工听辨。字符兼容字段只表示句包络，不能当成词级时间。平台投稿不在本次授权内。
