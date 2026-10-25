# EP.28 / A02：AI说要调用工具，到底是谁在执行？

制作issue [#132](https://github.com/linhongcun/video-studio/issues/132)，Agent系列第二课。制作与站点slug均为`agent-tool-execution`，承接A01。只回答：模型提出的工具调用请求，怎样变成应用程序真正执行的查询？

首屏直接呈现退款咨询功能：用户查询订单8124签收几天，助手准备查询，订单系统尚未收到。暂停点标明是调用请求刚生成，随后回到开始，完整演示请求、应用检查、实际查询、结果回传及对话答复。再明确重置到无权限的新用户新会话，展示应用拒绝、零次HTTP。片中没有退款政策和退款操作。

本期11镜22句、旁白514字符（含标点），真实音轨3305帧、110.166667秒。音轨完整SHA-256为`caabe6a5726f10cc8eef475165093ee5312db917115097300ce51fbc7d94a668`。最终媒体身份与实际复核范围在本期QA中记录；制作检查不能代替用户观看结论。

## 开工同步与依赖

已先检查干净工作区，`git fetch --no-tags origin main`后fast-forward整合16个上游提交，再建立本期文件。基线`1834450d6dd6e36762aa1862a72282c4e89822ac` / v0.57.0，分支`codex/agent-tool-execution`。同步后重读已更新规范、制作手册、L028–L033及新成功经验，核对旧工程删除与当前共享入口。完整启动记录见[startup.json](startup.json)。

使用保留的现行制作文件；本期Remotion按自己的锁文件`npm ci`，不链接被删除目录下的ignored依赖。共享配音、起音、装配及混音实现保持原字节。本期默认QA Python为`/workspace/.venvs/video-studio/bin/python`，包含NumPy/scipy/soundfile/Pillow；Remotion需Node/npm、ffmpeg及`/usr/bin/chromium`。渲染临时目录使用短的工作盘路径，并与其他任务共用`/tmp/video-studio-render.lock`。

编码前再次同步`e38fa9236fbc340f834581302320494d2a1c1ce7`，只新增LC三片上线收尾文档，无本期制作输入交集，站点版本仍为0.57.0。最终发版前仍须重新核对最新主干与版本标签。

## 资料、实测与能力边界

- [research.md](research.md)：2026-10-25（北京时间）重新联网读取官方Function calling、Agents SDK工具/授权说明及OWASP；Responses自定义function字段锁定官方SDK源码，SDK只作契约参考。
- [demo/README.md](demo/README.md)：标准库启动真实本地只读HTTP服务；有权限1次GET、无权限0次GET，同一case用同一调用标识关联结果。
- [demo/verified-results.json](demo/verified-results.json)：实际事件、HTTP计数、数据与输入SHA；`application_status:403`不是订单服务HTTP403。
- [qa-editorial.md](qa-editorial.md)：独立审读唯一问题、开头场景、回看/重置/回扣与新手所需关系；事实检查另见demo/editorial-fact-check.json。

模型调用与最终答复为固定fixture，没有真实模型推理、SDK执行、生产订单或退款。片中数字全部是教学示例。句级音频、声学起音及信号检测不冒充逐字ASR、全片人工听辨或真实观众学习效果。

## 重建入口

所有命令从仓根运行；音频需要上述Python依赖。首次请求TTS使用环境中的`MIMO_API_KEY`，不得打印或提交密钥；已有选定takes时从build开始，不重新请求非确定性候选。

```sh
python3 episodes/_shared/voice/prep.py --dir episodes-codex/agent-tool-execution
python3 episodes/_shared/voice/gen.py --dir episodes-codex/agent-tool-execution --jobs jobs-a.json
python3 episodes/_shared/voice/build.py --dir episodes-codex/agent-tool-execution
python3 episodes-codex/agent-tool-execution/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/agent-tool-execution --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/agent-tool-execution
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/agent-tool-execution
```

候选批次与取舍以voice/jobs-*.json、picks.json及substitutions.md为准。assemble.py是共享装配的薄包装，保留真实句边界和句首起音，没有另一份配音/起音算法。正式帧数由音轨决定。

在本期remotion目录，按实际package脚本安装、类型检查、出封面及小样：

```sh
npm ci
npx tsc --noEmit
npm run covers
node scripts/qa.mjs out/qa-captioned
```

无字幕连续过程使用同一QA入口的`--motion --no-captions`并选取本期镜头；先看实际输出是否确实没有字幕，再检查对象/动作。真实时序预演和独立动态复核通过、所有输入负责人停写后，从仓根冻结：

```sh
python3 episodes-codex/agent-tool-execution/freeze.py
```

随后在本期remotion目录正式编码：

```sh
flock /tmp/video-studio-render.lock npm run render
```

保存最终带字幕预演采样清单为qa-motion-samples.json；编码结束后从仓根检查：

```sh
cp episodes-codex/agent-tool-execution/remotion/out/mix-report.json episodes-codex/agent-tool-execution/mix-report.json
python3 episodes-codex/_shared/check_encoded_episode.py episodes-codex/agent-tool-execution
python3 episodes-codex/_shared/extract_encoded_samples.py episodes-codex/agent-tool-execution
```

检查冻结输入、完整解码、帧数/格式/响度与预演保真；独立查看正式MP4的入口、执行返回、权限拒绝和结尾。冻结后如需修源码，先停止本期排队或正在执行的编码，修订复验后重新冻结并编码，不用新清单追认旧媒体。

## 接入与发布

只将检查通过的同一MP4、JPG和发布所需数据接入`episodes/agent-tool-execution/`；WAV、PNG原稿、制作源码留本目录。精确章节使用冻结帧号除以fps，VTT与原旁白逐字一致。站点两视口实际播放/seek/字幕检查和线上完整SHA另记site-integration及release。

按GitHub站点持续授权完成PR、Release与Release后部署，核对真实标签内容、线上完整媒体/字幕/海报/章节和更新日志，再以completed关闭#132。并行任务可能推进版本，拟定版本不是最终发布身份；已有标签绝不移动。平台不新发。配乐Kevin MacLeod《Wallpaper》，CC BY 4.0，沿用项目署名。
