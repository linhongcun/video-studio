# Kafka MQ15 / EP49 制作输入

《Kafka 多副本确认：写入成功，到底哪些副本已经跟上？》；issue #323。本文件是正式冻结前的制作快照，后续编码、发布与站点进度只追加到[批次记录](../../../../docs/archive/2026-11/mq08-15-implementation/README.md)，不为更新进度改写已冻结的本文件。开工基线8769a592856fe2618e5daf3d84849bf4b052e22b，新实体production目录；未依赖已移出的episodes-codex缓存。

同一E01/order7042/P0、三份数据副本。正文沿Leader追加→Follower Fetch0与同offset追加→下一次Fetch1使Leader获知进度→共同进度HW→完成判断→网站收到响应展开。物理末尾、Leader已知末尾和网站结果分开；原日志记录不移动。acks1可在跟随尚未复制时成功，选定单Broker故障后clean新主可能没有E01，原主离线字节仍保留。all对照从相同空日志重置，完整复制再故障，clean新主保留记录。

固定Kafka/Java4.4.0 commit1156b2752aaa28eafc0b4c4d387e63356793268d，RF3/min.insync.replicas2、ELR feature0/unclean关闭，单producer单条发送、幂等关闭/retries0/inflight1、P0显式指定。HW简化限于稳定ISR、无待加入或额外近期追齐候选；ISR3时minISR2不等于只等两份，ISR2等当前两份；稳定ISR1在本次前置判断拒绝且无追加，不推广成所有失败没写入。确认复制不代表每块盘已fsync，也不代表消费业务完成。

sources/保留本轮官方固定commitGET、Contents API原题证据及精确执行段。references.json五项title-author，机构Apache Kafka；article-sources.json另三项，文章八个具体SourceQuote和四章。model.py/model.json是39态/505有限教学检查，不是Broker实测。examples/actual-runtime与runtime-cross-evidence.json原字节映射独立三节点运行：7分支/34断言、33份日志快照官方解码、21批CRC有效。复制Fetch门控保持CLIENT/CONTROLLER可达；故障是单进程终止，不是断电、全副本字节消失或时延benchmark。原失败尝试/原false回执与同字节数字名后复核分开保留。

根已接受最终同文b声轨：5460帧/182秒，voiceSHA256 **388aa7072e3329d76360aca4063c20b901d642bdad256307869a40200286b9d9**。scriptSHA256619e9a37ac6560c56c36e5d331b4ee45d45851bbed19c5c27aa48d14ad20b147；canonical无分隔旁白03057d2617ca879886f16b4452dd579137465d39fce3a6bea9819e82672d49b3，13镜26句。旧标题解析失败、原声及2b来源链均保留，作者未重配声音。Main字面@storyboard使用真实D/storyboard.json，prevoice估计板及旧自查保留历史身份，不当正式时序。

作者自查：107真实无字幕PNG/39态/13镜、34字幕PNG覆盖26句、三段1696帧原声无字幕短窗完整video+AAC解码，71个连续时点实际图审；范围/局限见qa-self/actual-handoff.json。独立复核已抓标题修前候选图和连续片，并发现第8镜报告后标题仍称等待报告的歧义；根批准只按模型id守卫标题。旧Main/图/报告保留在qa-self/header-state-fix，新2964/2965/3281各无字幕/字幕共6帧类型与实际图复验通过。受影响08独立fresh复核仍待收束，不把作者或实测通过当最终媒体通过。四图位1621/3281/3732/4964，seconds=frame/30与MDX seekTo一致；实际JPEG须正式编码后抽取验收。文章raw1<2的MDX格式失败已保存，唯一行内代码修复后站点真实parseArticle八引用四图与来源检查通过。

根统一冻结、编码、封面与publication；作者当前停写，未正式冻结/整片编码。fresh npm ci按本期锁安装。默认渲染是实际limitedBT709转换、混音，再追加同色原题/机构资料；五来源默认两页各5秒，预期完整5760帧，以正式输出回执为准。以下命令在本目录执行，仅由根完成独立闸门并确认freeze-inputs后运行：

```bash
python3 freeze.py
python3 freeze.py --verify
bash render-final.sh
python3 verify.py --final
```

render-final.sh使用全局flock串行默认render；不得以remotion/out/voice.mp4或正文替代含资料附录的video.mp4。编码后还须实际看资料首中末、字幕/正文退场、四JPEG与播放器，记录完整媒体SHA及能力范围；这些最终检查尚未发生。
