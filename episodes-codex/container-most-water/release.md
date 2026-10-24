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
- Release后[部署40097496603](https://github.com/linhongcun/video-studio/actions/runs/40097496603)成功，source head一致，实际API证据见deployment.json。
- 2026-10-24 21:21:43（北京时间）实际GET核验通过：线上完整视频SHA为上述修订2的6d1e3b4c…8adb，10,017,737 bytes；海报完整SHA与v1相同，44句VTT逐字节保持、四章精确起点/锚点、源码入口、独立系列/RSS、首页和更新日志通过。见online-verification.json。
- 教训L018的修后验证已补齐。用户对v1主体的认可与本次独立检查分开记录，不声称用户已观看新版。
