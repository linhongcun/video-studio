# D02 观察者模式：MQ实战修订

用户要求直接修改现有视频，将手写观察者代码压缩为原理说明，主要讲跨服务项目使用MQ发布订阅。保留订单17、摘要和变化记录、原URL和首次发布身份。当前正文10镜20句、4182帧，加5秒Java卡共4332帧/144.4秒；原片5328帧/177.6秒。

原理段后明确切换跨服务教学部署，用RabbitMQ交换机向两个独立队列路由。重点演出消费后确认、离线积压、恢复、确认丢失及断连检测后的重投、原子去重与一致性边界。消息是状态变化事实，不是要求再付款。不是任何商家后台的实测架构，也不是生产消息系统集成测试。

当前源码：remotion/src/Main.tsx、motion.ts；完整Java原理示例：demo-java/。原12镜源与旧媒体身份：revisions/mq-practice/baseline/manifest.json；历史制作证据仍保留，当前结论以本轮qa-mq-*和qa-voice-mq为准，不沿旧报告承诺新版通过。

## 生产与检查

Python使用/workspace/.venvs/video-studio/bin/python，Remotion按当前锁文件npm ci。共享voice/prep.py→gen.py→build.py，随后共享assemble_sentence_episode.py→place_v2.py→label_onset_strict.py。2句首镜复用flow，18句新配，07第二句选mq2；字幕保持MQ，送模替换M Q。配音来源与信号限制见qa-voice-mq。

Java尾卡使用共享append_java_endcard.py append/verify并指定--body-dir revisions/mq-practice/voiced-body，真实正文冻结后不能再覆盖装配。正文语音与字幕不伸进卡区，PCM前缀精确保持且尾区全零。完整程序运行与21行节选源码映射重新验证通过。

冻结执行本期freeze.py，核对加--verify；包裹共享标准冻结器，不改已被其他片固定引用的实现。新增正文、公开阅读证据、Java源、共享中间件图标与QA入口一起纳入。正式编码须在负责人停写和独立预检通过后，从remotion执行npm run render，使用短TMPDIR与共享渲染锁。check_encoded_episode.py验证实际完整媒体，mix-report.json来自本次混音。

三比例封面副文案改为MQ实战并重出。site-integrate.py保留旧元数据身份、直接复制当前article和已检查的媒体。verify-online.py核对线上完整视频/海报/VTT字节、5章、源码/课程目录与实际Release。真实交付状态见docs/observer-mq-practice/README.md和本期release.md；未完成的能力不预记通过。
