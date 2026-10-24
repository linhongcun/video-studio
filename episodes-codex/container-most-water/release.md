# LC.11 · v0.49.0 发布记录

用户在本聊天明确要求制作《盛最多水的容器：为什么每次都移动短边？》，完成后合并项目并发布网站；无需再索取逐期发布确认。仅GitHub与站点，不包含三个外部视频平台。

## 本地交付

- 站点slug：`container-most-water`，展示LC.11，内部ep22。
- 版本：v0.49.0；开工后先同步其他机器已发布的v0.48.0与主干34d7789，保留EP.01–14重制、事务四片和历史路径。
- 正式视频：6544帧、218.133秒，完整SHA256为`624c2fa8dec7c8f96caad8b25d5890ae83c1854f4c16443617b32685002f18e0`。
- 186冻结输入、完整解码、音量、字幕/起音、实际MP4采样与干净构建结果见`qa-final.md`及各独立报告。
- 制作与站点媒体逐字节一致；两次本地网站构建、44句VTT/四章/历史路径回归、32页面与8播放器状态检查通过。平台空提示修正后局部复验和短时播放通过。检查后已合并、发布Release并部署，线上实际结果见下节。

## GitHub与线上状态

- [PR #154](https://github.com/linhongcun/video-studio/pull/154)已squash合并，主干提交为`d9377782d2c29844669cb7aa118d47bb5c06566f`，保留本次Codex联合署名。
- 附注tag `v0.49.0`指向同一合并提交，[GitHub Release](https://github.com/linhongcun/video-studio/releases/tag/v0.49.0)已发布，正文明确只上站点。
- Release之后手动触发的[部署40093925916](https://github.com/linhongcun/video-studio/actions/runs/40093925916)于2026-10-24 20:28:52（北京时间）成功，head SHA与合并提交一致；API状态证据见`deployment.json`。合并自动触发的部署也已完成，未发生实际取消。
- 2026-10-24 20:30:09（北京时间）执行`verify_online.py`实际HTTPS GET核验通过：线上视频10,061,885 bytes、完整SHA与上述正式媒体相同；海报108,815 bytes，SHA为`60edf894e938ee067c453b5725f272b32c6198767917675083e4c37c0971f4e1`。
- 线上44句VTT与本地已检查构建逐字节相同（SHA `51a28b58f7ae2d0220fb05cc42737a5c1c32f8af07244b034c3e0a3008bac192`），四章payload按实际帧/fps保持精确起点，正文锚点和源码入口正确。首页、独立算法系列、RSS与包含v0.49.0和本片链接的更新日志均通过。
- 线上核验后，已将[#78](https://github.com/linhongcun/video-studio/issues/78)关闭，state=`closed`、state_reason=`completed`。未将原选题模板里的平台发布事项视作已完成；本期没有外部平台投稿。

正式页面：<https://linhongcun.github.io/video-studio/episodes/container-most-water/>。全部实际GET结果见`online-verification.json`。没有用户观看认可、逐字ASR或全片人工听辨结论。
