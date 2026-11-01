# Kafka MQ06 · 消息保序

《消息保序：订单已退款，为什么又变回已支付？》EP46，issue314。制作基线f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3，root统一发布。独占本目录，旧制作源、冻结、共享和站点输入不写。

先读research.md、implementation-map.json、outline.md。script/plan/model/article经独立编辑审定；editorial-candidate.json保存精确旁白SHA。真实类运行只验证key序列化/hash，完整Broker/应用屏障实验另有回执。源码/模型/实验/编辑与视觉能力范围分别记录。

## 当前可执行检查

从仓根执行：

```bash
python3 episodes-codex/kafka-message-ordering/model.py
node episodes-codex/kafka-message-ordering/check-references.mjs --sources episodes-codex/kafka-message-ordering
npm --prefix episodes-codex/kafka-message-ordering/remotion run check:types
```

本期fresh npm ci已按新锁安装，来源字段/原文/链接及Python语法/框架类型检查通过。root已提供最终真实voice/board：4966帧/165.533秒，声音独立信号通过；当前正做真实动态自预检，不以类型检查当动态验收。

## 后续生产闸门

新声轨已由root在独立稿审通过后使用shared TTS生成。本地prepare/assemble仅薄调用当前shared；voice/build/place/onset不复制。真实voice/board后补精确图位/字幕与动态预检；source停写后交独立QA。root统一放行freeze与串行正式编码，默认render接实际limitedBT709及title-author附录。

```bash
python3 episodes-codex/kafka-message-ordering/prepare.py
python3 episodes-codex/kafka-message-ordering/assemble.py
python3 episodes-codex/kafka-message-ordering/verify.py
```

以上生产命令须按当前阶段执行，不重复非确定性TTS、不以重新装配代替已冻结输入只读核查。正式freeze/render尚未执行。
