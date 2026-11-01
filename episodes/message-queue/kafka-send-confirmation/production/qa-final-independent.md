# MQ04 独立质检

执行者：Codex 独立质检代理，2026-10-30。当前结论：**稿件、模型、声学、真实动态预检与正式成片独立验收通过；本地/线上浏览器由publication代理另报。**

11镜22句回答同一问题：网站发送调用返回之后能知道什么。先建立发送方、Kafka实际日志和下游通知业务，再比较正常成功、最终结果未知与确定本地未发送；两个情景切换明确回共同空日志起点。结果对象不充当成功凭证，成功metadata不充当消费业务证明；delivery终态超时不等于Future.get短等待超时，也不能仅凭错误推定日志是否有记录。关闭旧A后新B应用再次send同E01可生成新offset，与原批次内部幂等重试分别呈现。

独立直接核对17模型快照100项预期数据与源码证据完整性；未调用作者的model.verify，也不把其76项教学断言称为独立Broker测试。最终22个take的文本及送模记录、22段PCM和整轨逐样本、所有头尾/句间零信号一致，flags为空；最短抛弃尾0.3472秒、最大句内静音0.37秒、真峰值约−2.2002dBTP。信号通过不代表逐字ASR或全片人工语义听辨通过。

真实3417帧分镜预检先完成92份PNG/DOM，覆盖17态和4个预定文章图位；实际审图拦截04在日志仍空时提前宣称已写入、08在Future仍pending时标题与副行提前宣称已到最终期限。旧Main、完整SHA及实际失败962/2133帧保存。源作者只给04标题、08标题和副行加三处状态守卫；逆向撤除这三处即可逐字节还原旧Main，其余捕获输入SHA均不变。最终Main为 `becd78f7c8292d59944323c1c7f4152bf12b703ba358790354da6628fc43487c`。

最终定向19份PNG/DOM及04/08整镜无字幕片通过，未完成的10本地错误片也以最终源生成。实际查看18张连续联系图的99份解码画面，以及首0/2/5/15秒、17态代表、结尾与4图位：确认先追加、后收到成功响应，未知分支保留原记录、内部retry不新增，A失败历史与B成功分开，本地失败无Future/Produce；原ID可读，点走列间空隙，无压字或裁切。两段旧长片只复用有精确源差异支持的不变运动和衔接，旧04/08错误文字由最终短窗替代，不冒称旧长片是最终源。未执行全片实时人工播放或用户理解实验。

主要证据：[审稿](qa/editorial-independent.json)、[模型](qa/model-independent.json)、[声学](qa/voice-independent.json)、[文章与引文](qa/article-independent.json)、[最终动态结论](qa/motion-independent-final.json)、[实际失败](qa/preflight-failures/source-v1/findings.json)、[精确源差异](qa/preflight-evidence/source-difference.json)。原始大量PNG及无字幕视频留在ignored qa/out，保留必要失败、关键图和联系图供复查。

旧Kafka MQ01/02/03的实际freeze.py及依赖先源审再只读执行verify，160/159/170项声明通过；431个唯一保护输入含清单的字节及mtime不变。初始候选与base `2c54aa7c` 的episodes/1306个旧Git blob一致，只新增MQ04目录；见[保存检查](qa/preservation-independent.json)。安装正式媒体后已重跑同一有界检查通过：旧431受保护输入含清单字节及mtime不变，1306个旧Git blob零变化，新增24份文件全部位于新MQ04目录。

能力边界：官方固定版本源码与有限教学模型、真实渲染与有界实际图像复核；没有真实Kafka Broker/Java Producer/序列化器/网络故障/副本介质或消费副作用实验，没有逐字ASR、全片人工语义听辨、物理手机或学习效果测试。正式编码和实际资料附录已按下述证据闭合；原生播放器、本地/线上浏览器由publication代理执行与实图复核，不在本报告预记其未收到的结论。

正式媒体（已验）：175项冻结清单SHA `5886ba7ec04585ed01d70c459ac385d2ae8194522cb4626f58a8e2986ca5c671`；最终MP4 SHA `a3dd3f640b0032e363d7010410b496c6321a951b2e6c257ee2fde1efda3c2e13`。正文3417+资料150，共3567帧/118.9秒；实际1920×1080、30fps、H.264有限范围BT.709、AAC48kHz；mix-report为−16.0LUFS、−3.7dBTP。

独立从正式MP4一次整数解码n取55张，实际查看全部10张联系图；全视频解码同时启用xerror/err_detect，退出0，不再重复空解码。03结果对象、04追加/响应、06重置/追加、07内部retry、08最终超时与新标题副行、09关闭A/新B同E01追加1/成功、10重置与本地同步报错均在相邻编码帧核对。四个文章图位与同一状态匹配。3416末正文字幕保留，精确3417资料首卡无烧录字幕残留；3492/3566中/末卡只显示《Design》《Producer Configs》及Apache Kafka署名。见[正式编码报告](qa/encoded-independent.json)。完整音频/AAC/正文及附录同源核验由根任务verify.py --final另记，不冒充本代理重复执行。

网站实际动作、严格PTS和手机模拟横屏/原文弹层图由publication代理负责，使用其[本地浏览器报告](qa/site-independent/report.json)与后续线上报告；本代理没有覆盖其helper或把媒体通过写成浏览器/真机通过。


## 发布后实际补充（root / publication执行）

PR #440合并8d852e2c并发布v0.96.0，Release后Pages41035467904成功。14次普通canonical完整GET比对视频/海报/VTT/四图及四课/四章/22cue/真实Release通过；publication代理直接HTTPS原生Chromium线上48项动作/20严格PTS和A2亮暗触摸滚动两项通过并实看，root另看线上三张实际截图。没有TLS忽略或HTTP回填；这些网站动作不由本篇独立媒体QA冒称重复执行。#312已在核验后以completed关闭，#308当前4/9已交付，其余5未开工。详见online-verification.json、qa/site-online-native/report.json与publication.json。
