# D02 观察者模式：模式主线修订

用户观看v0.68.4后指出MQ占据主要篇幅，偏离设计模式。当前从同一订单17、摘要和变化记录解释观察者的动机、角色与共同约定、订阅/通知/退出、收益成本；MQ仅第09镜13.53秒实践对应，结尾回到模式。不能把上一轮技术和部署检查当作用户认可主题。

新正文10镜20句、4292帧/143.07秒，其中模式129.53秒（90.54%），MQ13.53秒（9.46%）；静默Java原理卡150帧，总4442帧/148.07秒。代码不逐行讲语法，完整原例仍在demo-java。旧v0.68.4源码与身份在revisions/observer-first/baseline，原12镜源在revisions/mq-practice/baseline，旧检查范围按其版本保留。

01产品操作；02说明接收需求变化时分开来源与响应的动机；03逐节点角色；04明确回看付款前再登记；05先改来源、收到后各自响应；06关闭摘要并取消；07同一订单发货只到记录；08收益与成本；09框架事件/MQ短应用映射；10回原例的模式核心。原例最终订单已发货、记录两条、摘要已退出且最后值已付款；09独立映射不改变它，10回到同一最终结构。

## 实际生产入口

Python使用/workspace/.venvs/video-studio/bin/python。当前锁文件npm ci安装257包，node_modules为本期实体目录。共享voice/prep.py、gen.py、build.py→assemble_sentence_episode.py→place_v2.py→label_onset_strict.py负责配音、分镜与3句首标签；不复制裁音/起音算法。新配10句pattern take，旧10句按observer-first-reuse.json逐字/原字节映射到flow/reuse，选段见picks.json。

独立配音检查见qa-observer-first-voice.json，20句原始转换、模型文字、共享裁尾与正文PCM通过，内部低信号flags为空；没有逐字ASR或全片人工听辨。原理Java完整程序与真实节选另行校验，不把其运行当成MQ集成测试。

Java附录用共享append_java_endcard.py append/verify，必须指定--body-dir revisions/observer-first/voiced-body；正文真实快照不可覆盖，字幕不进入附录，音轨前缀一致且附录PCM全零。本期freeze.py先验证新正文派生，再调用标准冻结器并纳入真实当前take、程序、源码、共享图标、公开研究旧证据和拒绝版基线；核对加--verify。

预演使用remotion内npm run qa；关键采样入口由motion.events提供，需检查新动机、合并通知的完整收发、关闭与下一次通知、短应用映射到模式回收及Java卡边界。所有写入者停写、预检通过、冻结核对成功后才允许npm run render，使用短TMPDIR和共享渲染锁。正式成片用check_encoded_episode.py核对完整解码、帧数、音频、响度和冻结输入。

site-integrate.py直接复制当前文稿和通过验收的媒体，保留slug、创建与首发身份，仅更新内容修改时间、时长、描述和revisionIssue。verify-online.py检查线上完整视频/海报/VTT、20句、5章、模式主线和真正Release条目。实际交付见docs/observer-pattern-first/README.md及本期release.md；平台未新发，不预写用户观看认可。
