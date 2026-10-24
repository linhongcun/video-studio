# LC.11 发布记录

用户在本聊天明确要求制作《盛最多水的容器：为什么每次都移动短边？》，完成后合并项目并发布网站；无需再索取逐期发布确认。仅GitHub与站点，不包含三个外部视频平台。

## v0.49.0 初版交付

- 站点slug：`container-most-water`，展示LC.11，内部ep22。
- 版本：v0.49.0；开工后先同步其他机器已发布的v0.48.0与主干34d7789，保留EP.01–14重制、事务四片和历史路径。
- 正式视频：6544帧、218.133秒，完整SHA256为`624c2fa8dec7c8f96caad8b25d5890ae83c1854f4c16443617b32685002f18e0`。
- 186冻结输入、完整解码、音量、字幕/起音、实际MP4采样与干净构建结果见`qa-final.md`及各独立报告。
- 制作与站点媒体逐字节一致；两次本地网站构建、44句VTT/四章/历史路径回归、32页面与8播放器状态检查通过。平台空提示修正后局部复验和短时播放通过。检查后已合并、发布Release并部署，线上实际结果见下节。

## v0.49.0 初版上线

- [PR #154](https://github.com/linhongcun/video-studio/pull/154)已squash合并，主干提交为`d9377782d2c29844669cb7aa118d47bb5c06566f`，保留本次Codex联合署名。
- 附注tag `v0.49.0`指向同一合并提交，[GitHub Release](https://github.com/linhongcun/video-studio/releases/tag/v0.49.0)已发布，正文明确只上站点。
- Release之后手动触发的[部署40093925916](https://github.com/linhongcun/video-studio/actions/runs/40093925916)于2026-10-24 20:28:52（北京时间）成功，head SHA与合并提交一致；API状态证据见`revisions/progress-removal/v1-deployment.json`。合并自动触发的部署也已完成，未发生实际取消。
- 2026-10-24 20:30:09（北京时间）执行`verify_online.py`实际HTTPS GET核验通过：线上视频10,061,885 bytes、完整SHA与上述正式媒体相同；海报108,815 bytes，SHA为`60edf894e938ee067c453b5725f272b32c6198767917675083e4c37c0971f4e1`。
- 线上44句VTT与本地已检查构建逐字节相同（SHA `51a28b58f7ae2d0220fb05cc42737a5c1c32f8af07244b034c3e0a3008bac192`），四章payload按实际帧/fps保持精确起点，正文锚点和源码入口正确。首页、独立算法系列、RSS与包含v0.49.0和本片链接的更新日志均通过。
- 线上核验后，已将[#78](https://github.com/linhongcun/video-studio/issues/78)关闭，state=`closed`、state_reason=`completed`。未将原选题模板里的平台发布事项视作已完成；本期没有外部平台投稿。

正式页面：<https://linhongcun.github.io/video-studio/episodes/container-most-water/>。初版实际GET结果归档于`revisions/progress-removal/v1-online-verification.json`。初版发布时尚无用户观看结论；后续实际反馈见下节。没有逐字ASR或全片人工听辨结论。

## v0.50.1：按观看反馈去除装饰进度条

- 用户实际观看并表示“这个视频做得真不错”，认可v0.49.0主体，唯一修改意见是去除画面下方持续增长的进度条，避免分散注意力，并要求更新教训。
- 仅删除两条SVG矩形；22镜/44句/6544帧、配音、字幕、章节、文章、封面与讲解动画时序保持。预演主体逐像素相同，解码PCM完整hash与v1相同；全6544帧底带无青色线及旧轨道色命中，独立实际编码检查通过。
- 修订2视频完整SHA256：`6d1e3b4ca5c0094b3d351dad8aa2a1f53348224b3cd4a28d6e6b2afa674c8adb`，10,017,737 bytes，218.133333秒、1080p/30fps，−16.0LUFS/−3.7dBTP。
- 已同步其他机器新增Agent系列的v0.50.0，保留其内容；本次按全局补丁版本v0.50.1发布，LC.11的firstRelease仍为v0.49.0。发布文案使用题号LC.11避免与另一独立系列的内部期号混淆。
- 教训L018、画面规范、制作检查清单与项目记忆已更新；S012补充真实用户认可范围，不将v1认可预写成已观看新版。原生播放器控件保留。
- 新版上线前通过修订专用独立检查与网站复验；合并、Release、部署与实际GET结果将在完成后追加。平台没有新增投稿。

### 修订2上线核验完成

- [PR #157](https://github.com/linhongcun/video-studio/pull/157)已合并，提交`ab825f324aa8ea255f61c23d5ad702438ac9b7d2`；附注tag和[Release v0.50.1](https://github.com/linhongcun/video-studio/releases/tag/v0.50.1)已发布。
- Release后[部署40097496603](https://github.com/linhongcun/video-studio/actions/runs/40097496603)成功，source head一致，实际API证据见revisions/python-endcard/v2-deployment.json。
- 2026-10-24 21:21:43（北京时间）实际GET核验通过：线上完整视频SHA为上述修订2的6d1e3b4c…8adb，10,017,737 bytes；海报完整SHA与v1相同，44句VTT逐字节保持、四章精确起点/锚点、源码入口、独立系列/RSS、首页和更新日志通过。见revisions/python-endcard/v2-online-verification.json。
- 教训L018的修后验证已补齐。用户对v1主体的认可与本次独立检查分开记录，不声称用户已观看新版。

## v0.50.2：片尾完整 Python 解法

- 按用户明确要求，在原讲解之后追加15秒静态完整Python解法，含可提交接口、缩进、两个指针分支和返回值，提示暂停查看。正文的关键行讲解与原四章保持；代码卡不显示旧字幕，不恢复装饰进度条。
- 程序、显示源和文章16行实现一致，独立代表用例、真实预演和正式编码保真检查通过。总6994帧，画面233.133333秒，容器233.152秒；视频10,636,628 bytes，完整SHA256为`072ae1db566209c671dfb3819cfbbac1f927098e2b65bfe7df9bd89cf903535b`。
- 原44句时间及人声PCM前缀严格保持，新增尾部人声全零；BGM沿用共享混音流程。190冻结输入、完整解码、−16.0LUFS和−3.7dBTP通过，详见当前`qa-final.md`及独立报告。
- S013、画面规范、制作检查清单和项目记忆记录“讲解后附完整代码”的方法及验证范围；本期15秒不固定为全系列参数，不将用户新要求误写成已观看认可新卡片。
- 站点发布按既有持续授权完成，实际合并、Release、部署及线上完整GET证据见下节。修订2证据已归档，不新增平台投稿。

### 修订3合并与发布

- [PR #159](https://github.com/linhongcun/video-studio/pull/159)已squash合并，提交`431c0ab8bc16863eea8be919d38082a1df69babb`保留Codex联合署名。
- 同提交的附注tag与[Release v0.50.2](https://github.com/linhongcun/video-studio/releases/tag/v0.50.2)已发布，LC.11的firstRelease继续为v0.49.0。Release文案使用题号，避免混淆Agent独立系列的内部期号。
- Release后[部署40100807342](https://github.com/linhongcun/video-studio/actions/runs/40100807342)于2026-10-24 22:06:39（北京时间）成功，head SHA与合并提交一致，API结果见`revisions/codecard-five-seconds/v3-deployment.json`。
- 2026-10-24 22:07:07（北京时间）实际HTTPS GET核验通过：线上视频10,636,628 bytes、完整SHA与修订3媒体一致；海报完整SHA保持，44句VTT与已检查构建逐字节一致。四章精确起点及正文锚点、源码入口、独立算法系列/RSS、首页版本与v0.50.2更新日志通过，见`revisions/codecard-five-seconds/v3-online-verification.json`。
- 用户未被要求再次审批，未将其对旧主体的认可写成已看过新代码卡。制作issue #78此前已按completed关闭，本次为同一视频修订，无平台新发。

## v0.50.4：代码卡改为5秒

- 用户指出15秒过长，要求5秒和暂停提示。本版卡片6544..6693共150帧，总6694帧、223.133333秒，约3:43，较上一版缩短10秒。完整程序与暂停提示保持。
- 复用已验收编码画面快速准确截短，重新按新时长共享混音；不整条重渲动画、不重复不变程序测试和全课程检查。人声PCM前缀及44句时间保持，必要的准确末PTS、末帧、字幕及网站时长检查仍执行。
- 正式媒体SHA256为`f95993b77f0412218af38f9c159596f928009336af1e730f18a4b1d7af401c04`，10,061,812 bytes；190冻结输入、完整解码及−16.0LUFS/−3.7dBTP通过。L020、S013、制作记忆和局部修订清单已更新。具体合并和线上结果完成后追加。
