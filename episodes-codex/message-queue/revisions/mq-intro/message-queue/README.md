# EP.10 · MQ系列入门改造

独立修订工程，开工基线为`16689e572c594224bd779a9b4403964e049cc99c`。沿用`message-queue`站点slug、EP.10及原创建/首发身份；原根工程、冻结清单、历史媒体与QA保持原位。本目录只继承基础设施和明确选中的声源，不继承旧成片或验收结论。

已随v0.79.0上线并完成线上核验，正式3700帧/123.333秒，含5秒资料卡。实际范围见[本轮QA](qa-final.md)、[独立动态审查](qa-motion-independent.md)和[独立成片审查](qa-video-independent.md)；GitHub发布与线上结果见[发布记录](release.md)。

## 入口

本期使用共享句级装配，`prepare.py`与`assemble.py`仅转发共享实现；`plan.json`已按定稿12镜核对镜号、slug、四章与2个句首术语。`episode-config.json`提供标题、范围、封面文案。

仓根执行，Python使用已有视频venv，且安装仓内附录依赖锁：

```sh
/workspace/.venvs/video-studio/bin/python -m pip install -r episodes-codex/_shared/requirements-reference-appendix.txt
/workspace/.venvs/video-studio/bin/python episodes-codex/message-queue/revisions/mq-intro/message-queue/prepare.py
```

仅在稿件通过审查后调用共享`voice/gen.py`生成确需修改的句子；可复用take应先验证原句、送模文本和音频SHA，并保留`voice/input-provenance.json`。选择结束后：

```sh
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/build.py --dir episodes-codex/message-queue/revisions/mq-intro/message-queue
/workspace/.venvs/video-studio/bin/python episodes-codex/message-queue/revisions/mq-intro/message-queue/assemble.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir episodes-codex/message-queue/revisions/mq-intro/message-queue --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/label_onset_strict.py --dir episodes-codex/message-queue/revisions/mq-intro/message-queue
/workspace/.venvs/video-studio/bin/python episodes-codex/message-queue/revisions/mq-intro/message-queue/verify.py
```

Remotion在本nested目录按自身锁文件`npm ci`安装实体依赖，不能沿用指向已删除工程的旧软链。`npm run covers`生成三份PNG/JPG并生成3:4 poster副本；`npm run stills -- OUTPUT`只做首帧与镜中采样，不代表动态审查。

本机默认npm缓存目录不可写，实际冷安装使用下列命令；保留原代理及锁文件。已安装257个包，当前TypeScript检查通过；这些是基础设施检查，不是成片验收。

```sh
cd episodes-codex/message-queue/revisions/mq-intro/message-queue/remotion
npm ci --cache /workspace/work/mq-intro-npm-cache --no-audit --no-fund
npm run check:types
```

稿件、来源与视觉停写、动态检查闭合后执行`freeze.py`。冻结器调用未修改的共享句级冻结器，再补本期实际参考资料、入口、共享组件、证据与声源provenance；不纳入MP4或生成回执。

```sh
/workspace/.venvs/video-studio/bin/python episodes-codex/message-queue/revisions/mq-intro/message-queue/freeze.py
bash episodes-codex/message-queue/revisions/mq-intro/message-queue/render-final.sh
```

默认渲染完整执行正文混音与`title-author`参考资料附录，每页最多4项、默认5秒。`video.mp4`为最终成片，正文在`remotion/out/body.mp4`；两者的帧数不可混用。资料回执和`render-result.json.publicationMetadata`给出实际发布区间；本期`verify.py --final`核对正文与附录范围，不覆盖共享入口生成的发布回执。

句级声学窗口不是逐字ASR；未完成人工听辨、真实Broker实验或用户观看时如实记录。媒体完成后按冻结文章的预定Figure图位抽图并实际查看；需要改稿则保留冻结制作稿，另做有SHA记录的站点派生稿。

站点接入仍使用`episodes/message-queue/`，按真实结果更新sourcePath、修改日期、总帧数、附录、文章、字幕、章节和海报。运行站点的`check:references`、`check:articles`与构建，再实际检查桌面/手机播放器、图文回看及来源浮层。按持续授权发布GitHub站点并线上核验，不据此重发外部平台。
