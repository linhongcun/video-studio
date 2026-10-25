# 设计模式 D02 · 观察者模式

制作issue [#164](https://github.com/linhongcun/video-studio/issues/164)，系列总览 [#161](https://github.com/linhongcun/video-studio/issues/161)。首发v0.58.0；用户随后要求改为“先产品操作、再结构逐节点、最后Java关键代码”的讲解流程，并明确保留原案例。本次不换订单故事，不引入购物车或支付渠道，不把思想课改成语法课。

## 本次修订

同一程序内的订单17仍由待付款变已付款，再变已发货；接收方仍是订单摘要和变化记录，摘要取消后保留历史已付款/停止接收，下一次仅记录收到已发货。

- 01商家订单详情教学页实际点击“标记为已付款”，看到来源状态、摘要和记录依次联动；不执行真实支付。
- 02从相同已付款结果展开Order来源、OrderObserver共同约定、SummaryObserver/ChangeLogObserver具体观察者，逐节点解释职责。契约是结构关系，不是中间转发服务。
- 03明确回看本次付款前，再从空名单演出登记；05–06解释01同一次付款的机制。08用可见关闭X说明摘要退出的生命周期理由，后续取消和发货沿原思想主线。
- 片尾单独5秒Java静默关键代码卡，注明节选/暂停，完整可运行程序和八项编译运行检查见`demo-java/`。角色名与结构相同，不逐行讲语法。

12镜24句仅5句重配，19句复用旧take。body5178帧，静默尾卡150帧，总5328帧/177.6秒，1920×1080/30fps。配音选用与声学边界见`voice/flow-reuse-provenance.json`、`voice/flow-candidate-audit.json`；完整能力限制如实记录，不声称逐字ASR、完整听辨或理解实验。

## 历史与复用

`revisions/flow-ui-java/baseline/source/`保存26份旧生产源，`baseline/voice-archive.json`及同目录保存旧音轨、时序与QA；旧takes原位保留。旧视频实体为`baseline/video.mp4`，SHA为`76f38c9675e7ecf57520df1212cfac78093d6e24eaf534a38ed8c07a6e8c0c08`，不靠新清单追认旧成片。旧版完整制作说明在`baseline/source/README.md`，历史发布在`release.md`的既有记录。

三比例封面及poster沿用原字节，七份完整SHA见`revisions/flow-ui-java/cover-reuse.json`，已与Git基线e2a0add逐字节比较。标题与案例未换，不重生成封面。

## 实际生产入口

Python工具环境`/workspace/.venvs/video-studio/bin/python`。正文继续用共享prep/build/assemble/place/onset工具，不复制裁尾/起音/铺轨算法。`revisions/flow-ui-java/voiced-body/`保存追加Java卡前的实际有声body；新增卡段由共享`episodes-codex/_shared/append_java_endcard.py`明确声明，旧句界和字幕不伸入代码卡。

只读核验Java尾卡及保存body（仓库根）：

```sh
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/append_java_endcard.py verify episodes-codex/observer-pattern
```

Remotion类型检查和关键无字幕预演（本期`remotion/`目录）：

```sh
npx tsc --noEmit
TMPDIR=/workspace/observer-tmp npm run qa -- out/flow-ui-java-preflight --shots=01,02,03,08,09,12 --no-captions --ranges=01:03,08:09
```

末镜`javaCardFrom`是镜内body终点，`meta.javaEndCard.from`是全局5178。Main在该处切到纯Java卡，禁旧字幕/旧header；`motion.at`末句使用body终点，150帧静默卡不延长原正文动作。卡片逐字读取`src/java-card.json.lines`，不自行重写源码节选。

关键产品/结构与关闭预演见`remotion/out/flow-ui-java-preflight/frames.json`；右侧Java职责映射补强只改卡函数，正文其余源完全相同，定向卡预演见`out/flow-ui-java-card-final/frames.json`。实际检查范围与源差异证明见`qa-flow-ui-java-editor.json`；独立报告按实际完成补齐，不把“渲染成功”当作已讲清。

## 冻结与正式编码

正式完整渲染由root在负责人停写、动态和卡片独立预检闭合后启动。本编辑只生产预演，不提前全片编码。编码前后核对同一份冻结输入，不能在输出后重写清单认可未被采用的新源码。使用当期`package.json`的`npm run render`、短路径TMPDIR及共享渲染锁，成片仍需完整解码/帧数/响度和实际状态/卡首中末检查。

站点接入直接复制本轮`article.mdx`，SVG采用原生`font-size`/`text-anchor`/`stroke-width`属性，不再派生`article-site.mdx`。五视频章id保持`why/subscribe/notify/unsubscribe/boundary`，Java图文入口为`#java`。站点历史firstRelease/publishedAt保留，实际版本与媒体/部署结果由root更新release及线上报告。平台未新发。

本轮实际冻结入口：从仓库根执行`python3 episodes-codex/observer-pattern/freeze.py`，编码前后只读复核加`--verify`。它委托新增pattern-flow共享包装，保留旧共享检查器，显式验证真实有声正文与Java静默尾卡派生，并纳入源码、Java、正文快照、旧媒体参照和复用依据。
