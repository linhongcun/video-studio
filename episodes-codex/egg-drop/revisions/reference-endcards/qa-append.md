# P05实际参考资料追加

本工序实际完成共享append，未重渲正文、未TTS／build／混音、未修改voice.wav或24句字幕／words／SB。默认render入口已接入真实源码正文→混音body→共享append。root随后实际完成185项严格当前清单和共享默认完整验证，结果及执行归属见本报告末段。

- 实际完成：2026-10-25T15:03:20.153406+00:00，发布毫秒值2026-10-25T15:03:20.153Z。
- 最终MP4：10,085,034B，5719帧／190.6333秒，SHA `94672a7375b77d0fa16234031056bc34df2c48ae61536b6ef4708acbfd04fa69`。
- 原主体：5569帧，SHA `b43510f3196f92964d21a3b854941a65f4af33fffd2484c171ca518f9f747c66`，实体保存于body/video.mp4。原169manifest SHA `fe45b05e132f1458e332da9b58b61d6568513b4bc08e95ba5c66f1388bc995ff`，在wiring变动前逐项PASS并保存body/source-sha256.json；旧freeze.py／package的原字节快照也保留。
- 实际append前固定13项输入到append-source-sha256.json，涵盖body、资料、证据、追加器／依赖锁、主题、字体和预检器；不是生成后为原主体改SHA。原169历史、实际append13和后续当前交付冻结各自保留适用范围。
- 资料：1项本期已完整读取的LeetCode官方1884题面，核验依据与范围在research.md；本轮没有假称重新访问官网或读取付费Editorial。支持题设规则与n=100答案14，不为本片14/27/39路线借用官方背书。
- 一页150帧，区间半开[5569,5719)。原生卡PNG为references-01.png；其SHA `5627ffd15d293564e74e122a821a36dc6ad26a5711ab371c131e99fea9fb3efc`。来源预检通过，原文支持及卡片／播放器可读性另由root及独立审稿复核。

共享追加器实际全文件验证：全部5569个主体解码帧及对应时间戳精确相等，最终5719帧时间线连续；8703个原AAC包的payload／顺序／PTS／DTS／duration精确相等，完整解码PCM相等。音频原端点185.642秒保持，无新增音频包；不把这一实现写成向voice.wav补了150帧零样本。H264主体没有再次编码；重封装不等于MP4字节前缀或每个H264包字节完全不变。

实际媒体指纹见reference-appendix-media-check.json：主体framemd5行序列SHA为64006837e796667f6a22a20a6b3b811479def7c7515b57b19ca20c6313c790df，AAC包及时序SHA为3adef8c361289417100650f02cff76bd5c6ab4681f34ea984450ad8ac1cb4d28，PCM为SHA256=d22a1ee97a598c9d4b06778e9820fa26da00888d61d37a86362597d5f2bce365。静态有损卡的150帧出现31个不同解码哈希，脚本只保证帧数／可解码，不将此当作视觉可读性证明。

两份receipt已复制期根；render-result保留原1920×1080／30/1及原音频事实，明确该音量数据沿用已验收主体、非新增测量。根音源QA、二分修订的24句／20句复用证明保持原身份。ASRPerformed=false，semanticListeningPerformed=false，fullHumanListeningPerformed=false。未执行发布、commit或push。

root默认完整验证已实测PASS：2026-10-25T15:11:08.084554+00:00执行`python3 episodes-codex/_shared/render_with_references.py episodes-codex/egg-drop --verify`，exit0。当前185输入清单SHA为21bbae8767832ed133b7a805c4bc2caa01232d007b27142faf1ef32bee5b3822；root保存qa-default-verify.json与default-verify.log.gz。该次验证覆盖严格当前冻结、资料／root发布metadata以及实际全文件帧／音频保留，不改变body169与编码前append13的历史范围。current-pipeline-freeze.json明确原169中仅freeze.py／package两项wiring变化、其余167同；不使用历史特判绕过当前失配，也不声称主体按185项重渲。此后仅改未冻结的README及本报告，没有再执行重型检查。
