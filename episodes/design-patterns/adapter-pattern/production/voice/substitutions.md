# D03业务边界版配音与时序

2026-10-25（北京时间）。用户否定v0.63.0内容复杂、像被迫包装后，本轮按根与独立概念/叙事门通过的10镜20句重新制作。主线是业务自己定义使用约定和把外部格式升级影响留在接入边界。20句全部新录，没有为了保留媒体强行套旧句或复用旧take。

四份启动源在root放行时核对：script `8d3010eef4866c4f795e227691e72b7ad2a35f944d667f65542dd127d654e33a`；plan `caf569e2a85cd5cf04ba728892e068cfee6e191accc2f4ec89dcd8c752b829a7`；config `6b9e0700c8b51cde85f05a9c716ab955fe25a6ddd12f7ebd44a13f9ab3bcb0b4`；covers `ede634f4a8e4329bca153d1771e2d1058b75c86e5fe53af1f67b682a3ad3f656`。逐句UTF-8加换行（含末换行）摘要 `f1101ccc7f628759da41f63423e40da32f00d76afdcc6fb567a32f29d2328f73`。生成与选段仍以这些完整身份为准，不修改口播稿。

## 新候选与旧记录

使用现有共享prep/gen、MiMo mimo-v2.5-tts/冰糖，自然适中科普语气，未变速、未作词语替换。共享gen的jobs第二字段直接使用独立后缀v2a，避免旧a同名文件导致skip；不另写生成算法。20句各生成一个v2a，全部采用，无实际裁尾/格式硬失败，无补配。文本侧录与冻结输入20/20匹配，原始转48kHz单声道PCM16逐样本20/20一致。

候选保留4项低信号标记：02第一句0.53秒、03第二句0.58秒、05第一句0.59秒、06第一句0.64秒；归一后仍达0.50秒的项目为 `[{"id": "02-business-first-1", "maxInnerSilenceSeconds": 0.51}, {"id": "03-adapter-structure-2", "maxInnerSilenceSeconds": 0.57}, {"id": "05-convert-and-delegate-1", "maxInnerSilenceSeconds": 0.57}]`。这些只是包络阈值标记，不能当作已识别的漏字、错字或发音异常；不为清零正常停顿反复TTS。完整候选指标见candidate-audit.json。

149份旧source/voice归档与原baseline-manifest逐项一致，75份live历史take相关文件原位SHA不变。旧完整5271帧声轨另存previous-track/voice.wav及manifest，live/public在归档时完整字节一致，只存一份完整WAV。没有覆盖旧baseline或旧默认voiced-body快照。

## 真实正文与Java静卡

共享build/assemble建立正文3861帧/128.7秒，原sentence checker通过10镜20句、4章和逐字字幕；whole偏移0。03第一句“适配器模式”全局786帧出现、声学起音787.02，差−1.02帧，无例外且完整保留至少63帧。

调用既有append_java_endcard时显式给出 `--body-dir revisions/business-boundary-v2/voiced-body`，先保存真正正文，再追加150帧/240000样本全零PCM；最终4011帧/133.7秒。meta.javaEndCard是java-design-pattern，从全局3861开始；末镜javaCardFrom是local。正文PCM前缀6177600样本逐样本一致，字幕/句界完全保留，静卡无字幕或人声。旧默认revisions/flow-ui-java/voiced-body的18文件与manifest原样不变。

最终voice SHA-256 `0d85d55499a8ca4902c39391d857f517d867b0c2169776ad5802629af476d2ad`；words `f5220a27260170b90dd1653f03234fe694579b33c030a096948f9f26b936ed43`；storyboard `d38d64b596bbaa4c250ad54922803997aa30e20f6bbbcdb8da601e0a87fe0fb9`。最终人声-16.0LUFS、4倍采样真峰值-2.20dBTP；20份归一后逐句PCM与最终轨切片相同。build.json及qa-timing.json描述正文；最终时长以words/storyboard和qa-java-endcard.json为准。对final使用新helper verify并指定新body-dir，不直接用仅识别Python卡的旧checker。

## 范围与能力限制

01仍只有一次发货提醒，04–06明确回看同次提交；07–08是后来升级的开发变更对照，不是第二次发送或运行中替换。09两句说明防腐作用与能力/维护边界，不再口播拒绝/未知支线。声学句界仅服务这些叙事阶段，不能代替动画和业务语义审查。

未发现可用ASR包或转写工具，未执行逐字ASR、发音/变调听辨或全片人工听辨。文字侧录、声学起音、PCM/AAC相关不能证明实际说出的字词、读音或观众理解。正式编码及Wallpaper/AAC一致性在实际render完成后另行检查，不预写通过。
