# P05两枚鸡蛋：成片检查

文稿、正式成片、声音及两视口本地站点检查通过，133项冻结输入编码及合并后保持。内部EP33／趣味推理P05已按v0.67.0发布，Release后Pages成功；线上9次普通站点GET与1份独立Release证据核验通过，#209已completed关闭、#204完成5题。实际身份与能力范围见release.md。

## 内容与冻结身份

《两枚鸡蛋、100层楼，怎样保证14次内找到答案？》，12镜24句、四章，旁白654字含标点／577字不含标点，正常语速。真实时序5257帧／30fps，175.2333秒，约2分55秒；制作画幅1920×1080。正式视频1920×1080／H.264／AAC48kHz，容器175.253秒，与5257帧的175.2333秒分别记录；实测−16.0LUFS／−3.6dBTP。9,546,440字节，SHA256：`f5876353b2d2f4b8f6709e59a6091edfd2ab1ae5303e239751e1b9eca42b9179`。

目标是确定最高安全F，F可0到100；未碎可复用、碎则消耗。由最后一枚不能跳过未知层，推到固定10层晚碎的10＋9＝19次，再从14次预算构造14、27、39……且100封顶。实际F31走8次，最终0蛋且答案唯一仍成功。03另有明确的跳15失败思考分支，0蛋／F仍10…14，不计入成功策略。严格最少性与完整边界只在文章，视频没有证明尾段、文章口头入口或代码卡。

- 133项冻结清单SHA256：`01a072baad2799520e9b5041789422bf9de2677b508cf557c43623ed72f3801f`。
- storyboard及placeholder SHA256：`504f4706df184c178e37b1027f73f320b232fb65beeaccf48b927dad3ca7eeec`。
- 原声SHA256：`2ea3e8b68eee14f11b6c5699bb865fe17d2c92f25a82d6e2cdcc249086b6ef2c`。

root独立完成freeze、verify，visual另verify成功后才渲染；编码与合并后已再次核对同一清单，见qa-preflight.json。

## 资料、文稿与数学

实际读取LeetCode1884官方完整题面、例子、限制与提示，日期未标，不将版权年份当发布日期。官方首测9与本片首测14路线分开注明；其他候选PDF的作者／提取边界保留，未凑作专家背书。独立路线各遍历101个F，递减最坏14、固定10最坏19、F31实际8，F0实际2、F100实际12。区间最坏搜索与独立容量递推对107个规模一致，13次91层、14次105层与101阈值状态未混用；root另执行临时输出核对。

五稿经root与独立编辑完整双审，TTS前补齐03逐层查的因果，修正序数“第一枚”和数量“一枚”等读音。分别复述题目目标与为何选择递减方法通过。见research.md、research-math.md、qa-math.json、qa-editorial-root.json和qa-editorial.json。

## 原声与句级来源

24份a＋5份同文b共29候选保留，最终19a／5b，文字标点未改、无变速。最终最大句内低声间隔0.46秒、无inner_dropouts；这些信号测量不证明某个错字出现或消失。原声48kHz单声道16-bit，共8,411,200样本，末句后97,367零样本约2.02848秒；原WAV−16.0LUFS／−2.1dBTP，正式混音另验。

实际送模文本、raw→48k转换、24句WAV／整轨区间逐项核对，public/audio实体副本一致；7,617,833句样本与793,367零间隙覆盖全部样本。共享铺轨0偏移，字幕逐字／句窗一致。plan实际0命名cue，检查为0cue／0fail；字符包络不冒充逐字识别。

原始cut波形与共享处理后的WAV曾用单一增益拟合，在临时0.995线下01第一句、05第一句未通过，最低0.99055063。该线性模型不能完整描述非线性限幅；原诊断保留，未降低阈值或修改声音。随后用相同sents／picks／params、原takes及同一未修改shared build复现，完整WAV、build元数据和全部24句WAV逐字节相等，由完整处理链byte-exact闭合来源一致性。见qa-voice.md及voice/qa-source-pcm*.json；这不等于语义或音质听辨。

最终只补storyboard.meta.covers，声音、words、句窗、字幕、动作及其他元数据不变。旧空封面分镜和原始TTS生成来源保留，未将旧预演重写成新来源，见voice/final-cover-sync.json及voice/assembly-history。

## 源码、DOM与实际动态

独立执行全部5257帧的生产Scene纯React树，核对5257世界props、10514蛋actor、38337楼层文字、约151万次节点求值及14个动作commit。实际09–12严格匹配F31八次历史；03仅具名失败示意可0蛋未定。另有两路线各101F、2349模型状态、130967阶段／261934姿态检查。纯树、源坐标代理与实际DOM明确分开；句内分段按实际整句窗和文本比例安排，非词级ASR。见qa-source-review.json/md，首轮原样留qa-source-review-v1.json。

实际初批4图曾有9项底部边界问题，同点修后0；随后487帧DOM检出39项文字相交，涉及03变焦0／10标签和08跨层说明。原失败、源zip及根所看失败图保留，23是来源输入数。修正退场、注记／括号后，最终同源487帧font-loaded DOM为0违规，974个actor实测bounds与文字31163对检查0碰撞。根实看失败与同点修复；见qa-root-dense-failure.json、qa-root-layout-fixed.json、qa-visual-preflight.json及qa-revisions。

根另实看六张最终联系表72个源阶段。独立质检看64个含字幕阶段，并从三支实际无字幕MP4自行解码、实看137个阶段：规则／代价46、预算26、完整实例65；实际hideSubtitles为true，代表解码帧字幕带无前景。所看范围内，楼层到同一地面的动作、蛋复用／消耗、假设切换、实际8次与最终31无阻塞。这些片段不是正式全片MP4，也不是完整实时观看。见qa-root-final-preview.json、qa-motion-independent.md/json。

## 封面与上游

三尺寸实际封面DOM0违规，制作及root均实看PNG／JPG六文件，固定三行标题、楼体／双蛋及14／27／39计划间隔可读，4:3保留居中竖构图。初版间距问题和修正单独归档。后续主体Building虽改，Cover只import纯Egg；该导出函数字节相同，其余七份声明依赖SHA相同，故保留原六图及其原渲染来源身份。**复用证明没有把旧图改称新源重渲染，也未替换原封面QA的旧Building摘要。** 见qa-covers.json、qa-covers-root-view.json、cover-source-reuse.json。

干净基线7e0172a2开工，EP33由PR270隐藏草稿预留。片段读取期间只fetch，生产读取停止后才整合37e096c2；507条变化与133冻结输入交集为空，23项renderer依赖保持。既有P04反馈、课程／站点v0.64.1和旧平台一次性发布记录均保留；P05仍只在GitHub授权内。v0.65.0当时未占，后续发布前复核见下段；开工与编码前事实见startup.json、upstream-before-encoding.json。


发布前再次fetch发现LC200已先按v0.66.0上线。旧v0.65.0本地候选、全部QA/截图/原日志和关键HTML已按原身份归档qa-site-candidates/v0.65.0-4aa95321，未发布该候选；完整整合2da29e20，396条变化与133输入交集0，合入后133逐项复验通过，视频仍同一完整SHA。包/锁与同一导航helper的并行变更分别保留上游逻辑及两项LC标签不变量，本期只顺延发布元数据为v0.67.0，再以当前完整树重新构建/双视口检验；没有重配音或重新编码，见upstream-before-release.json。

## 正式视频与编码音轨

fresh完整编码退出0；完整解码、格式、响度与133输入前后核对通过。5257显示PTS从0到175.2秒严格单调，最大误差3.34e−7秒。147点同1920×1080网格，最大全图MAE1.614026/255、前景MAE8.778729/255，低于本次诊断阈3/20；14次land/commit n−1/n逐项覆盖。制作实看36个成片关键点；root另实际查看03local302、07local522、08local0、11local125与12最后帧五张原尺寸图。独立质检从实际MP4自行解码并view52帧（覆盖14commit前后），另看5张1920原图，指定修复、长字幕、八次结果与末帧无阻塞。见qa-visual-encoded.json、qa-video-independent.*、qa-video-root-view.json。

初次147条件合并的FFmpeg提取表达式碰到解析深度限制，保真步骤未完成；仅改临时QA提取器为50点×3批，保留原失败记录后完整重跑通过。媒体、冻结源和诊断阈未改，不将该工具错误写成媒体错误。

实际音轨全轨／24句与双声道检查通过。premix与原WAV全轨相关0.99997660、句最低0.99995866、偏移0；最终人声＋Wallpaper模型全轨相关0.99984716、句最低0.99975040，固定偏移95样本约1.98ms、句间变化0。句窗人声高BGM实测11.77973dB（生产报告12.0dB）。全部8,411,200源样本与24句完整覆盖，AAC尾比原声多960样本，对齐后还余865；原声单增益诊断与完整构建复现来源原字节保留，133项前后均一致，见qa-audio-content.md/json。

## 本地站点与线上交付

14项发布副本与制作文件一致，site及锁版本0.67.0；实际构建111HTML、Pagefind41页。1440×1000与390×844实际Chromium核对24句VTT文本／时间／activeCue、四章0/755/1676/3443帧、四处正文seek、首尾播放／最后帧／自然ended通过。why-fourteen/bounds为普通文章锚点，不跳视频；8次事件、12预算和5关键边界表逐格与数学报告相符，脚注长链接换行、页面无横向溢出，表格自身横滚。五课趣味推理目录独立；其他课程及新上线islands与上游当前meta/video保持一致。root实际看桌面／手机首屏、手机末帧／预算表／脚注五图，所看范围无阻塞。见qa-site.json及后续补充阅读／构建身份记录。

共享学习路径回归首次因旧六算法常数不允许新增islands隐藏草稿而失败，网页未把草稿公开。根保留历史六课身份／发布批次断言，将preview与live导航分别按全算法元数据检查，并断言draft不进入live；仅改site/scripts/check-learning-path.mjs，未改课程、媒体或133冻结输入。同一构建上node检查--built已实际通过，原失败与新通过日志分别保留。最终v0.67.0构建／八张浏览器图及共享回归日志另按原字节保留于qa-site-evidence/v0.67.0；本轮上游已发布七道算法课。

[制作PR #279](https://github.com/linhongcun/video-studio/pull/279)已合并549ac45b53e078547fe53ef2c7f8677f0a918db5，附注tag／Release v0.67.0精确指向同一提交；Release在09:32:49Z发布，之后Pages40181102180的build与deploy均成功，head同上。北京时间2026-10-25 17:36:27.059304，首轮9次普通站点canonical GET完成完整视频／海报SHA及字节、24句VTT逐字节、四章0/755/1676/3443帧、普通文章锚点／源码、五课目录／首页／系列／学习／RSS和真实v0.67.0新增日志核验。另1份真实Release通过GitHub connector独立取得，未冒充本地HTTP GET。无cache-bust、Range、强制缓存、站点重试或远端媒体保存。核验后#209已completed关闭，#204更新完成5题、剩余5题。见online-verification.json、release-connector.json、release-tag.json、deployment.json和issue-completion.json。

## 能力边界


ASRPerformed、semanticListeningPerformed、wordAlignmentPerformed、fullHumanListeningPerformed均为false；全片连续实时观看和新手理解实验也未执行。模型、源树、声源字节复现、DOM与抽样动态只支持各自范围，不证明所有发音／像素、完整人工审听或学习效果。发布时P05尚无用户观看结论；后续用户已反馈方法动机不清，见feedback.md。P04的认可不迁移为本片认可；本次未做P05外部平台投稿。
