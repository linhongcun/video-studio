# 校验

规范以 [RULES.md](RULES.md) 为准，逐项顺序见 [qa.md](qa.md)。当前工程在 `episodes-codex/<slug>/`，先读该期 README；旧期的校验器和制作入口已随被替代工程清理。通用共享工具仍在 `episodes/_shared/`，不要复制起音、铺轨或配音算法。

## 当前工程入口

每期实际入口以 README 为准。当前 EP.14 的只读冻结核对为：

```sh
python3 episodes-codex/degradation/verify-freeze.py
```

它逐文件核对 `source-sha256.json` 的完整 SHA-256，缺文件或字节不一致会失败。不能通过重写清单把已编码媒体未采用的源码追认为通过。

制作阶段，当前 EP.14 的 `check-inputs.py` 核对脚本与音轨哈希、实体公开音轨、音频样本数、镜头和字幕帧、术语停留、配音位置、封面元数据；它会写入本期 `precheck-report.json`。`freeze.py` 会写冻结快照与清单，只能在输入定稿后执行。检查已发布工程时不重跑这类写入步骤。

独立句级装配工程的通用入口与字段见 [episodes-codex/_shared/README.md](../episodes-codex/_shared/README.md)。其装配、检查、冻结、编码检查分别承担不同阶段，不将某一期的入口假定为全系列统一入口。

## 参考资料：渲染前与发布前

新片从调研起准备 `presentation: title-author` 的 `references.json`，随脚本和配套文章同步定稿。`title` 与实际文档原题一致，`titleEvidence: {locator, evidence}` 齐全。明确公开个人署名才填写非空字符串 `author`，否则省略该字段并显示 `organization`，关联核验记录能定位署名依据。视频不使用 `displayTitle`、`displaySupport`、`supports`、译文或研究摘录代替原题/署名。正式编码前从仓根只读检查来源字段、核验记录与文章链接：

```sh
node site/scripts/check-references.mjs --sources EPDIR
```

`EPDIR` 指 `episodes-codex/<slug>`。缺来源、原题/署名依据，未核验或题文不符时先修正，不启动昂贵的正文编码；字段通过并不表示工具已经阅读原文或确认论点真实，技术审稿仍须逐项核对实际题名、作者/机构及论点上下文。有保留研究摘录时仍核对原句与证据，不自行改词、拼接或添加省略；摘录与位置只用于文章或研究，不进入视频。

采用新期默认入口时，`python3 episodes-codex/_shared/render_with_references.py EPDIR --verify` 复核本期来源、冻结输入与最终媒体，并只写QA报告。不要对已编码工程重跑会改写输入的准备步骤来追认通过。

成片和资料文件接入 `episodes/<slug>/` 后，从仓根检查最终交付：

```sh
npm --prefix site run check:references
```

站点 `build` 在复制媒体前自动执行同一项。检查资料JSON、文章链接、原题/署名及实际附录记录、发布元数据的区间和最终帧数，以及实际MP4与记录的完整SHA；新片只有文章出处、概括题名、空资料标题或过期媒体记录时不能发布。完整解码、原题与作者/机构的实际显示、原生字幕首卡边界、资料可读性及播放器控件遮挡仍按[成片审](qa.md#成片审)实际检查。

`site/scripts/reference-legacy.json` 固定登记本次流程接入前45片的slug和原视频SHA，仅未接入附录且实际MP4仍与基线字节相同的旧片可分批暂缓。已开始接入附录的旧片、旧slug重制或更换MP4后均须完整检查，不能通过扩大名单或重写基线SHA绕过。检查命令不改写资料、媒体或冻结清单，失败后不能靠重写哈希追认未使用的输入。

## 冻结与媒体身份

`audioSha256` 是实际 `voice.wav` 的全文 SHA-256；`scriptSha256` 的输入可能是整份脚本或旁白提取文本，必须按该期装配实现核对。当前 EP.14 的 `check-inputs.py` 比较整份 `script.md`，历史 fixture 的旁白哈希定义不同。

`meta.timingSource` 和镜头 `timing.source` 应对应实际音轨和时序输入。若本期保存 `storyboard.<sha8>.json`，副本应与对应分镜字节一致；以本期冻结清单和验证器判断，不把存在一个同名快照当成成功。

完整 SHA 使用 `hashlib.sha256` 或 `sha256sum`。8 位前缀只方便展示，发布前与线上媒体必须比较完整值。

## 起音

唯一算法是 `episodes/_shared/onset_rule.py` 的 `Rule`。静音后首个真正开口点、−45 dB 阈值及参数见 [voice.md](voice.md)。窗口为 −6..+2 帧，入场公式是 `max(1, floor(onsetLocal) − 2) + d`。

```sh
python3 episodes/_shared/label_onset_strict.py --dir EPDIR --out /tmp/label-onset-strict.txt
```

`EPDIR` 是本期 `episodes-codex/<slug>`。分镜模式不加 `--words`，因为它只列规则起音而不检查标签。退出码 0 表示无 FAIL、NOT FOUND、MISMATCH。已批准的 `--exc 06,18` 只把相应镜号前缀的窗口越界改记 EXCEPTION，不抵消缺失或不一致。wav 默认读取期根 `voice.wav`，没有则读 `remotion/public/audio/voice.wav`。

期目录从仓根定位共享模块，或使用已有薄包装；不复制算法函数体。旧冻结分镜中的 module/checker 字符串可能记录旧路径，实际实现以仓内这两份共享文件为准。

## COPYFIT 与版式

文字不得靠自动缩小掩盖溢出。使用本期 README 或 package.json 提供的静帧、版式、封面和动态检查入口，实际检查范围写入 QA。并非每个工程都有名为 `prep-stills.mjs`、`diagfit.mjs` 或 `ui.tsx` 的文件，不能套用已删除旧工程的组件及命令。

预检字宽估算不能代替渲染检查。检查关键帧与变换中间态中的文字裁切、边界、水印、字幕带、节点重叠和箭头方向；有 COPYFIT 日志时必须为空。没有记录日志的静帧脚本不能被表述为已检查 COPYFIT。

题目场景有人物或对象连续移动时，说明文字、组别标签和结果区须避开完整运动包络，包括抬脚、腾空和落脚。起点与终点互不重叠不能代替过程中互不遮挡；跨两阶等最大动作需要实际连续片段复核。

浏览器壳只给真网页、地址栏和 DevTools，讲解表和图用 canvas。标签、状态和窗口在相邻镜头间按真实过程连续；切换情景前先回到正确前提。页面注释、按钮、地址栏、标签行的尺寸和间距以该期实际组件为准。历史样例的 BrowserChrome 公式只用于对应 fixture。

## 镜头、字幕与动作

- `scenes` 和镜头首尾相接，镜内字幕合法且与旁白逐字对应；元素 id 唯一，状态帧严格递增，入场和退场落在镜头范围内。
- 原位整轨铺放时，`|from + localStart − wavStart|` 不超过 0.5 帧；没有故意停留的镜头不添加隐藏 hold。只读检查可运行下方铺轨命令。
- 总帧数、音轨样本数和镜头之和按本期生成规范一致。实际成片可包含显式尾帧或无旁白代码附录，最终帧数按本期元数据和编码检查确定。
- 术语完整显示至少 63 帧，DevTools 和正文代码画面范围按 RULES；具体术语、点击反馈和动作停留按脚本设计。不把历史单镜 180–300 帧作为全系列限制。
- 算法片的完整代码附录与正文、文章和执行源一致，字幕不跨入无旁白代码卡；附录时间、音轨静音和最终帧数按共享编码检查核对。

```sh
python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole --no-copy \
  --src EPDIR/remotion/public/audio/voice.wav --report /tmp/place_v2.json
```

脚本退出码 1 时先修正，不渲染。`--no-copy` 只读音轨并写报告，不改公开音轨。

## 封面

封面以当期 `covers.json` 和 `Cover.tsx` 为准。若分镜嵌入 `meta.covers`，解析后应与 `covers.json` 相等。4:3 内容落在 x 315..1125、底边 y < 918，水印使用该尺寸 watermarkZone，不能挪入内容安全区；三种尺寸均不得裁切文字。

部分工程用 elements，部分工程用 textBoxes，不能拿旧期固定字段检查新封面。按实际渲染逻辑及元数据核对；地址栏、标题行和组件留白取当期源码约定。封面 JPG、PNG 和 `meta.poster` 指定海报都要查看。

## 页身色

演示页身采用 `episodes/_shared/theme/pageTheme.ts` 的 `pageBg` `#0F172A`、`pageInk` `#E5E7EB`。浏览器框和 DevTools 按各期主题，讲解 canvas 外底按本期画面约定，不机械要求所有像素都是 pageBg。

渲染前核对源码和分镜，禁止大面积纯白页身；页身组件用共享主题，不抄一套色值。原 EP.14 的人工筛查阈值仍可用于同类页身：亮度大于 0.8 的 background/fill 总面积不超过画布 5%，纯白底不得超过画布 1%。这些不是共享校验器已自动覆盖的项目，实际执行范围须记录。

渲染后在 `/tmp` 保存全尺寸 PNG，只采样网页内容区，不采样浏览器壳、DevTools、字幕和水印。页身边界按本期窗口及页头实现确定。原 EP.14 的人工像素检查以近白像素（RGB 均 ≥240）不超过页身 2%、内角接近 pageBg 为参考，JPEG 只能看大块发白，不能卡通道差。按钮、高亮和正文笔画不单独判失败，仍需肉眼复核。

## 成片响度与编码

读当期 `remotion/out/mix-report.json`，核对 `final_LUFS` 及 `true_peak_dBTP`，目标为 −16 LUFS、−2.0 dBTP。配置目标不能代替实际测量。

视频完整解码、帧数、分辨率、音轨、动态表达和配音复核见 [qa.md](qa.md)。句级声学计算、静帧或软件检测都不能冒充全片人工听辨或逐字 ASR。

## 共享工具回归

共享工具保留通用分镜生成/校验器及 [固定 EP.14 v0.45.0 输入](../episodes/_shared/tests/fixtures/degradation-v0.45.0/README.md)。这是 20 镜、5152 帧的历史回归，不使用 live 站点分镜，不将它的镜号、组件、专属术语限制套给当前视频。

```sh
sh episodes/_shared/tests/run_all.sh
sh episodes/_shared/storyboard/examples/degradation/rerun.sh
```

第一条运行共享音轨、起音、铺轨、制作说明、合成分镜测试和密钥扫描；第二条在临时目录重建历史样例，核对冻结稿逐字节一致。样例预期为 6623 项检查、91/91 起音，分镜前缀 `6265993b`、封面前缀 `8cb7aafb`。固定输入和 golden 保持原字节，不为迎合新片改写。

只读校验历史 fixture 的完整入口：

```sh
python3 -B episodes/_shared/storyboard/validate.py \
  --spec episodes/_shared/storyboard/examples/degradation/validate_spec.py \
  --episode-dir episodes/_shared/tests/fixtures/degradation-v0.45.0 \
  --inputs episodes/_shared/storyboard/examples/degradation/repo-inputs.json \
  --storyboard episodes/_shared/tests/fixtures/degradation-v0.45.0/storyboard.json \
  --covers episodes/_shared/tests/fixtures/degradation-v0.45.0/covers.json \
  --report /tmp/validate.txt
```

引擎支持的字段及 spec 写法见 [storyboard-schema.md](storyboard-schema.md) 和 [共享分镜工具说明](../episodes/_shared/storyboard/README.md)。现行句级工程按自己的 README 校验，不默认使用历史 EP.14 spec。
