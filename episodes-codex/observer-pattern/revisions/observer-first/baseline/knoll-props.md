# 观察者模式实战修订制作说明

当前制作基线9834e2cd，10镜20句，body4182帧，Java尾卡150帧，总4332帧（144.4秒），1920×1080/30fps。保留首镜2句flow take，其余18句重配冰糖，07定义修正选mq2。MQ送模文本为M Q；原文字幕不改。原媒体通过基线追溯，原源和QA保存revisions/mq-practice/baseline，旧证据不覆盖认可本轮。

当前生产入口在remotion，实体依赖由当前锁文件npm ci。共享prep/gen/build负责句级配音，assemble_sentence_episode负责分镜字幕，place_v2整轨复制，label_onset_strict负责3句首术语。append_java_endcard用独立revisions/mq-practice/voiced-body保存真实正文，再追加5秒零PCM；不要用旧flow-ui-java/body验证新稿。

从仓根运行 /workspace/.venvs/video-studio/bin/python episodes-codex/observer-pattern/freeze.py，核对时加--verify。冻结器调用共享Java验证与标准句级冻结器，再追加当前正文、Java源与编译证据、官方阅读记录和实际中间件图标依赖。冻结前停写，成功读回清单后才允许正式render。

预演在remotion执行 npm run qa -- out/mq-practice-preflight --no-captions。关键事件首中末、入队/消费/业务/确认、故障重置/断连检测/重投/去重与纯Java卡需要实际查看；另采连续运动区间，避免仅看静态端点。正式编码使用短TMPDIR与/tmp/video-studio-render.lock，以及本期npm run render。先编码voice.mp4，再共享混音到video.mp4；正式检查按check_encoded_episode读取真实响度、格式、全解码和冻结输入。

站点直接复制article.mdx，无旧article-site派生稿；保留原slug/ep/创建/首次发布身份，只更新内容修改时间、时长、描述和章节。GitHub主干与站点发布已有持续授权，外平台未新发。实际听辨/ASR与页面交互能力限制必须如实记录，不能把信号计算、渲染成功当完整人工听辨或观众学习收益。
