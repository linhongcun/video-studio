# MQ01 · 存储与执行的源码机制修订

<!-- mq-source-depth-current-status -->
当前：本修订已随v0.96.1更新原页面，通过非作者成片、本地及原生线上复核，重制#443已completed关闭。完整媒体SHA与实际检查范围见[批次记录](../../../../docs/archive/2026-10/mq-source-depth-remake/README.md)。下文保留制作阶段记录。
<!-- /mq-source-depth-current-status -->

保留EP10 / `message-queue` / 《订单已提交，为什么还没处理完？》、创建/首发身份与旧封面。制作基线`923305b49cea1b18d7fc7e4dd8ac70ad830bc673`，批次[#443](https://github.com/linhongcun/video-studio/issues/443)。本目录是全新输入与配音/时序/模型/动画，旧冻结、takes、QA、媒体没有被覆盖。没有复制旧输出或旧验证结果作为新验收。

核心沿同一E01/订单7042解释任务数据先编码、Broker按分区末尾追加、消费者携位置拉取，再由应用调用通知与保存结果。13镜26句、4章，正文当前4661帧/155.366667秒；默认资料附录150帧，最终帧数以root实际渲染回执为准。详细执行链与语义边界在research.md，源码原字节在sources/。

## 当前检查状态

26句为新TTS，24句选a；07-accepted-1与09-decode-2因独立声学裁尾风险追加同文b并选用，旧a/旧报告仍保留。新整轨/起音/样本与字幕装配检查通过；34项有限模型断言通过。没有逐字ASR、全片人工语义听辨、真实通知服务或学习效果测试。真实Kafka最小实验只按独立runtime记录的实际范围引用，不把模型当实测。

Remotion依当前锁文件在本D独立npm ci；类型检查已通过。自身首轮真实4695帧候选69图/4无字幕片发现反向SVG箭头字符串缺分隔，报告与旧Main保留qa/self-preview.json及qa/before-arrow-fix/Main.tsx。修正箭头和09执行顺序后，按两句新b的4661帧重新运行qa/self-preview-v2；最终状态以该报告与独立QA为准，尚未冻结/正式编码。

## 可复用入口（从仓根）

```bash
node episodes-codex/message-queue/revisions/source-depth-v2/check-references.mjs --sources episodes-codex/message-queue/revisions/source-depth-v2
python3 episodes-codex/message-queue/revisions/source-depth-v2/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes-codex/message-queue/revisions/source-depth-v2
python3 episodes/_shared/voice/build.py --dir episodes-codex/message-queue/revisions/source-depth-v2
python3 episodes-codex/message-queue/revisions/source-depth-v2/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/message-queue/revisions/source-depth-v2 --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/message-queue/revisions/source-depth-v2
python3 episodes-codex/message-queue/revisions/source-depth-v2/verify.py
npm --prefix episodes-codex/message-queue/revisions/source-depth-v2/remotion run check:types
```

后续复核不要重请求已有takes。原共享CLI以目录basename推测slug，本目录basename为source-depth-v2，因此薄check-references.mjs调用同一共享checkSources并显式传真实slug=message-queue；没有修改或放宽共享检查规则。render/freeze/pipeline-tools均使用此薄入口，ROOT动态寻找AGENTS。

独立QA后root才执行freeze.py、render-final.sh和verify.py --final；本制作阶段未执行这些写冻结/正式媒体的命令。默认render包含真实BT709像素转换与title-author附录，不交付只有正文的out/body.mp4。站点复制、旧封面保留、版本/合并/Release/Pages与线上核验由root统一进行，无本轮外部平台新发。
