# P01 · 25匹马赛跑

对应[制作issue #205](https://github.com/linhongcun/video-studio/issues/205)与[趣味推理系列总览 #204](https://github.com/linhongcun/video-studio/issues/204)。制作目录为本目录，站点读取 `episodes/horse-racing/`，系列键为`puzzles`，内部EP.24／趣味推理P01。

主线是先讲清25匹、每场最多5匹、只知名次且恒速无并列，再用同一组教学赛果演示7场方案。每次排除先展示至少三匹确定更快的马，最后五候选的前二补齐总亚季军。组内名次、本场名次和总名次分别标注。完整的任意六场自适应赛程下界放配套文章。

## 内容与数学

- `script.md`、`plan.json`：18镜、36句、6章，先题意后解法，章节有口头承接。
- `article.mdx`：视频主线、全部排除见证和严格最优性证明。
- `research.md`／`research-math.md`：实际读取的公开出处、日期、支持范围与独立证明。
- `verify_math.py`：独立oracle的13,800种前三放置与1,000个完整随机全序；偏序与单场交换引理核验。有限核验不替代证明。
- `qa-editorial.md`／`qa-article-math.md`：独立文字审读与数学审校，未将其记成动态或成片检查。

## 配音与真实时序

共享`episodes/_shared/voice/`生成冰糖配音，经共享句级装配及声学起音核验。正式音轨6327帧、210.9秒（3分30.9秒），6章起点为0、647、1631、2593、4208、5204帧。没有加速，没有程序代码卡或额外时长。

`voice.wav`完整SHA为`2af8c739a08c2cf9c1972b22a0c31e1dd30cb6260fc92af749dd987a693def66`。public/audio副本为实体文件，逐字节相同。39份候选保留，最终34份a、1份b、1份c；调整送模标点与裁尾记录见`qa-voice.md`和`voice/substitutions.md`。

未执行逐字ASR、内部词对齐或全片人工听辨。兼容chars/words字段是整句包络，只有句首有声学起音依据；0个首现术语cue不扩大成全部发音与动画同步验收。

## 检查与制作命令

在仓库根执行数学和句级检查：

```sh
python3 episodes-codex/horse-racing/verify_math.py
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/horse-racing
python3 episodes/_shared/place_v2.py --dir episodes-codex/horse-racing --mode whole --no-copy
```

本期Remotion工程从package-lock安装。基础画面、封面及关键无字幕小样由本期`remotion/scripts/`生成，真实动态审读闭合、所有生产输入停写后才冻结：

```sh
python3 episodes-codex/horse-racing/freeze.py
python3 episodes-codex/horse-racing/freeze.py --verify
```

本期freeze只薄包装共享冻结器，额外纳入数学输入及本期渲染/QA脚本，不修改已发布片固定引用的共享实现。之后在本期remotion目录执行`npx tsc --noEmit`、`npm run covers`、`npm run render`。大渲染TMPDIR用空间充足的短工作盘路径`/workspace/horse-tmp`，共用渲染锁`/tmp/video-studio-render.lock`。混音报告复制到本期根目录，再执行：

```sh
python3 episodes-codex/_shared/check_encoded_episode.py episodes-codex/horse-racing
python3 episodes-codex/horse-racing/freeze.py --verify
```

正式检查范围、实际媒体完整SHA和发布状态写入`qa-final.md`、`render-result.json`及`release.md`；未完成前不以命令清单或截图存在宣称通过。

## 站点与发布

网站页面为[赛马题](https://linhongcun.github.io/video-studio/episodes/horse-racing/)。完成独立动态、实际编码与站点核验后，按用户已有GitHub持续授权合并、发布Release、部署并核对线上完整视频/海报SHA、36句VTT与6章。线上核验完成后关闭#205为completed，再同步#204。其他平台新发未包含在本次任务中。

本文件为制作入口；最新实际状态以QA和release记录为准，发布与技术检查不代表用户已经观看认可或已测量初学者学习效果。

