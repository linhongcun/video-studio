# MQ02 · 消费组（EP42）

问题：通知与积分都需要完整订单事件，为什么放在同一个消费组后各少一半？本期用Kafka传统消费组的两分区/四事件，对照误放同组、两个业务独立组、通知组内增加实例。05与08都明确重置同数据、同一保留开头；模型不是实际Broker实验。

选题[#310](https://github.com/linhongcun/video-studio/issues/310)，系列总览[#308](https://github.com/linhongcun/video-studio/issues/308)。开工清洁工作树，fetch最新主干后从`68d2d2dbea525f08fce8a10441b77bec243d9ca7`建立制作分支。依赖从本期当前锁文件fresh `npm ci`安装，站点另按`site/package-lock.json`安装，没有引用已删除工程的node_modules。

## 实际制作入口

从仓根执行。配音需要环境变量MIMO_API_KEY，不打印或写入密钥。TTS非确定性；已有选定takes勿为复核重新生成。

```bash
python3 episodes-codex/kafka-consumer-groups/model.py
python3 episodes-codex/kafka-consumer-groups/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes-codex/kafka-consumer-groups
python3 episodes/_shared/voice/build.py --dir episodes-codex/kafka-consumer-groups
python3 episodes-codex/kafka-consumer-groups/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/kafka-consumer-groups --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/kafka-consumer-groups
python3 episodes-codex/kafka-consumer-groups/verify.py
node site/scripts/check-references.mjs --sources episodes-codex/kafka-consumer-groups
```

正文10镜20句，实际3445帧/114.8333秒；配音PCM SHA-256为`21f2fcd410384282dc172f8623e4cd864acfbc011e7bf8c934d4c83747302339`。`words.json`保留句级声学边界，非逐字ASR。现有候选、裁尾及整轨检查见`qa/voice-independent.json`；没有逐字ASR、全片人工语义听辨或物理手机宣称。

封面本轮命令（实际三比例已独立检查）：

```bash
python3 episodes-codex/_shared/kafka-covers/render.py --slug kafka-consumer-groups --out-dir episodes-codex/kafka-consumer-groups/qa/covers
python3 episodes-codex/_shared/kafka-covers/render.py --slug kafka-consumer-groups --out-dir episodes-codex/kafka-consumer-groups/qa/covers --install
```

本轮封面输入逐字快照在`cover-inputs/`，完整原路径和SHA映射在其中`input-provenance.json`；本期冻结引用本地快照，后续扩展共享题库不会使本期制作冻结失效。两个既有MQ01历史目录未改写。

正文与封面读取不可变Kafka style-v1。先完成真实音轨下的动态预演和封面/图文审查，所有写源负责人停写后冻结：

```bash
python3 episodes-codex/kafka-consumer-groups/freeze.py
python3 episodes-codex/kafka-consumer-groups/freeze.py --verify
npm --prefix episodes-codex/kafka-consumer-groups/remotion run check:types
flock /tmp/video-studio-render.lock npm --prefix episodes-codex/kafka-consumer-groups/remotion run render
python3 episodes-codex/kafka-consumer-groups/verify.py --final
```

默认render接本期私有adapter，正文真实转换为limited BT.709后混音，资料列表保持同色编码。参考资料使用Introduction、Design的原题与Apache Kafka机构署名，5秒、无旁白；最终视频是`video.mp4`，不是`remotion/out/body.mp4`。实际帧数、完整媒体SHA与资料区间以`render-result.json`和附录回执为准。编码前后只读核验原冻结清单，不重写追认已编码文件。

文章制作稿在冻结前定好三处Figure；成片后按指定精确帧1304、2232、2956生成图片，明确由实际limited BT.709转full BT.601 JPEG，不修改冻结文章。需要修改时另存带前后SHA的站点派生稿。

## GitHub站点交付

发布步骤和真实文件安装入口见[publication-guide.md](publication-guide.md)。本期只上GitHub站点，沿持续授权完成PR合并、Release、Pages及线上完整资产/章节/播放器核验后，再以completed关闭#310并更新#308。最终证据另记`release.md`，技术检查不代表用户观看认可。
