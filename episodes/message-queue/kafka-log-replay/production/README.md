# Kafka MQ03 · 日志重放（EP43）

[选题#311](https://github.com/linhongcun/video-studio/issues/311)，[系列#308](https://github.com/linhongcun/video-studio/issues/308)。本期回答：消息读过后为什么还在，消费组怎样回退恢复位置重读，旧日志已清理时又有什么边界。

清洁工作区fetch最新main，以`9e44109511cac1b0fb54d8aa9383b9d7dfe9074b`建立`codex/mq03-20261030`。只复用MQ02制作基础设施源码与锁文件，本期fresh npm ci；未继承上一期输出、QA回执或冻结。共享style-v1保持，mutable封面输入逐字快照在cover-inputs，不使未来题库增长破坏本期冻结。

## 内容与真实时序

11镜22句、4章。两分区四事件，P1两组均已完成提交2作背景；聚焦P0的E01/offset0与E03/offset1。逐条poll、应用处理与提交下一条恢复位置分别发生；积分组独立前进；停通知整组后只改notify/P0提交位置2→0，重启后再读取同ID/offset。封闭旧段清理后不能回读旧记录，11明确切回仍保留条件作机制总结。

正文3943帧/131.4333秒，最终另加150帧/5秒原题机构资料，预计4093帧/136.4333秒（以实际render-result为准）。最终人声SHA-256 `0f75a80c027bc2ce786434489cd5a9a422f6cfa1ca436a5c0376ec1f3dbd7d10`。06-retained-2的a候选短尾风险已保留，只换同文b，其余21个源take不变；不是错字听辨宣称。

模型与官方4.4.0固定来源见research.md、references.json、sources/。137项有限模型检查、独立模型审读与22句声学/拼接检查按实际报告记录；未启动真实Broker或执行CLI/外部通知积分副作用，未进行逐字ASR、全片人工语义听辨或物理手机实验。

## 制作入口

仓根执行。已有选定takes不要为普通复核重新请求非确定性TTS；密钥只用环境变量MIMO_API_KEY，不写入仓库。

```bash
python3 episodes-codex/kafka-log-replay/model.py
node site/scripts/check-references.mjs --sources episodes-codex/kafka-log-replay
python3 episodes-codex/kafka-log-replay/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes-codex/kafka-log-replay
python3 episodes/_shared/voice/gen.py --dir episodes-codex/kafka-log-replay --jobs jobs-b.json
python3 episodes/_shared/voice/build.py --dir episodes-codex/kafka-log-replay
python3 episodes-codex/kafka-log-replay/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/kafka-log-replay --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/kafka-log-replay
python3 episodes-codex/kafka-log-replay/verify.py
```

实际封面：

```bash
python3 episodes-codex/_shared/kafka-covers/render.py --slug kafka-log-replay --out-dir episodes-codex/kafka-log-replay/qa/covers
python3 episodes-codex/_shared/kafka-covers/render.py --slug kafka-log-replay --out-dir episodes-codex/kafka-log-replay/qa/covers --install
```

完成本期真实音轨下的连续预演、COPYFIT/状态/边界、三比例及4:3安全区检查，所有源负责人停写后：

```bash
python3 episodes-codex/kafka-log-replay/freeze.py
python3 episodes-codex/kafka-log-replay/freeze.py --verify
npm --prefix episodes-codex/kafka-log-replay/remotion run check:types
bash episodes-codex/kafka-log-replay/render-final.sh
python3 episodes-codex/kafka-log-replay/verify.py --final
```

默认render完成真实pc601→limited BT.709像素转换、混音与同色原题/机构资料附录，每页最多4项、5秒。最终为video.mp4，不发布out/body.mp4。编码前后只读核验同一份清单，不重写清单追认旧媒体。

文章在编码前固定Figure的1445/2900/3251/3572整数帧，成片后只按这些帧生成并核验截图；JPEG从实际limited BT.709明确转换为full BT.601。需要改文稿时保留原冻结稿，用前后SHA明确的站点派生稿，不重写原输入。

## GitHub站点

按publication-guide.md将检查通过的同一媒体、图文、封面、来源及附录回执本地接入；build及真实网页检查通过后，沿持续授权提交PR、合并、发Release、部署Pages，普通canonical完整GET/SHA和线上原生浏览器复核后再completed关闭#311、同步#308。本轮只上GitHub站点，无外部平台新发；最终实际状态见release.md/publication.json。

制作中再次fetch并整合主干72b841c1（v0.94.0）；保留“其他”分类与新站点指导，MQ03明确仍归message-queue。13项上游改动与本期模型、声音、动画、封面及共享渲染输入零交集，候选Release顺延v0.95.0；实际交集记录见qa/upstream-integration.json。
