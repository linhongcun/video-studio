# D03适配器：主动业务约定与升级隔离修订

2026-10-25，用户实际观看v0.63.0后认为内容复杂、像被迫兼容，要求讲日常主动统一业务用法、隔离外部接口升级两个收益。本轮保留订单17提醒，已完成新文稿/程序/声音/真实动态与184项冻结，正式成片、完整解码、独立编码帧和AAC一致性检查已通过；网站本地验收通过，修订尚未正式发布。修前实际证据见revisions/business-boundary-v2/baseline及固定v0.63.0 Git历史。

## 内容与资料

10镜20句，先给产品操作与两项收益，再逐个对应业务方、业务通知约定、适配器、外部服务；沿同一地址/正文/Q17完成一次去回。随后明确切到后来的开发变更对照：V2请求字段、嵌套回执发生变化，修改适配转换及创建接线，业务约定/发货流程保留。最后简短说明防腐作用、维护与能力前提，5秒Java节选供暂停。没有拒绝/未知独立剧情或语法口播。

实际一手出处采用已核验的固定Spring/OpenJDK/HTTPwg源，本轮新增Microsoft官方ACL完整106行及JDK包装关系证据；出处、commit、原句与采用范围见research.md、sources/business-boundary-evidence.json。适配器可承担防腐边界的转换，不等于完整ACL；包装本身不足以判定Adapter。没有GoF全文或无法获取网页的本次重读声明。

## 程序与声音

原AdapterDemo/VerifyAdapter完整字节保持，新AdapterUpgradeDemo复用原Notifier/Submission/ShipmentReminder，V2 destination/content及嵌套ENQUEUED/reference统一到原业务结果。制作与独立各实际Java21临时编译运行原12组＋升级8组共20组。卡15行/最长79字符，同源12行＋3空分组，明确非完整独立程序；完整源与依赖在文章。

20句全新v2a，无旧take复用或补配；正文3861帧/128.7秒，Java150帧，最终4011帧/133.7秒。真实whole偏移0，唯一03句首cue满足严格起音窗口。指定business-boundary-v2/voiced-body经原正文checker和Java helper检查，6177600正文PCM样本逐字节一致、240000尾样本全0；旧默认snapshot保持。源声轨实测−16.0LUFS/4x真峰值−2.20dBTP；最终混音实测−16.0LUFS/−3.8dBTP。三处归一后0.51–0.57秒句内低信号标记如实披露，不作漏字判断或为清零重录。没有逐字ASR、发音识别或全片人工听辨。

## 实际动态、封面与冻结

本轮真实时序预演122状态及01–03/04–06/07–08三段无字幕连续片，COPYFIT0、非provisional。新卡旧页脚“同一次”与两版本独立验证不符，在预检中仅修正文案；原components及V1 metadata保持真实，三新正文控制PNG与原字节同，三新卡帧同字节，复用范围详见本轮qa-visual-preflight.json。

独立实际解码查看三片36帧（10/15/11）、另7张边界/收束/卡PNG及6份封面；根另实际看12张预演PNG和3JPG。五阶段业务卡区域RGB哈希相同，证明本例外部升级/适配接线变化时左业务画面保持；不是所有业务升级零影响的结论。三尺寸封面安全区与文字通过。独立编辑终稿、20组Java及动态门均通过，准确范围见revisions/business-boundary-v2/qa-*-independent和qa-root-*。

所有owner停止读写后整合最新7e0172a2的P04反馈文档，与生产输入无交集。184项生产/参考输入冻结，源清单、真正文、声轨、Java、实际出处及页脚修前源档均纳入，所有输入已追踪并只读复核通过。旧共享脚本未改，独立新body目录未覆盖旧快照。正式编码用短TMPDIR/shared flock和显式remotion cwd；render-gate.json在启动前提交。

## 正式成片、站点与发布

正式完整编码session20342 exit0。实际H.264/1920×1080/30fps，4011帧，容器133.717秒，AAC48kHz，7,152,478字节，完整SHA f86d48b91d0bc0a00c3d5f51b69bc4ec57106d2dd422358a1c59d2f296528852。共享检查通过184源、参数/响度和全文件解码；独立实际查看32张1080p帧覆盖10镜及Java首中末，根另实际看13张1280×720帧，未发现阻塞。4011显示PTS/4011视频DTS/6269AAC包连续性通过。

未混AAC0偏移，全6417600参考样本相关0.9999814379、20句最低0.9999748274；最终含Wallpaper AAC偏移95样本约1.98ms，全部参考样本比较完成，相关0.9645796991、20句最低0.9630587788。解码各6418432样本，mixed排除前95/后737。Java参考与未混240000尾样本全0；最终卡段240000样本可完整比较，Wallpaper窗口相关0.9995282836。184冻结检查前后保持。精确范围见本轮qa-encoded-independent、qa-root-encoded及qa-encoded-voice-content。

网站已完成本轮初验build/历史回归和1440浅色/390深色用例：8次实际章节跳转、20句字幕、完整载入且showing的卡区三点0activeCue、解码暂停、两SVG、Java两个依赖源链接、三期目录及其他课程数据保持通过。共40发布页/5方向，P05草稿保留，已退两Agent未恢复。

实际浏览发现三处中文句号在粗体结束标记内、紧接后文导致CommonMark未闭合；保留初验与原截图，只在站点派生稿把句号移出粗体，原文字序与184冻结源保持。第二次build仅定验两个视口的三段strong/无裸标记/Java与无溢出；前后player、目录、JSONLD、VTT、meta、SB、视频、海报及源码路径同SHA，按明确不变范围复用原8seek/20cue，不声称重新播放。原文4f2e09fe…f35b，派生5c011029…ae65；完整三处diff在qa-site-format-correction.json。根实际看7张网站图，独立site执行者查看范围另记。

当前候选v0.64.1，firstRelease和publishedAt保留v0.63.0/2026-10-25，updatedAt与revisionRelease更新。Release后Pages和线上完整SHA仍待实际执行，不预填通过。本期本轮尚无用户观看结论；D01/D02认可不延伸为本修订已获认可。仅GitHub站点，外部平台未新发。
