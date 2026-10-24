# LC.11 · v0.49.0 发布记录

用户在本聊天明确要求制作《盛最多水的容器：为什么每次都移动短边？》，完成后合并项目并发布网站；无需再索取逐期发布确认。仅GitHub与站点，不包含三个外部视频平台。

## 本地交付

- 站点slug：`container-most-water`，展示LC.11，内部ep22。
- 版本：v0.49.0；开工后先同步其他机器已发布的v0.48.0与主干34d7789，保留EP.01–14重制、事务四片和历史路径。
- 正式视频：6544帧、218.133秒，完整SHA256为`624c2fa8dec7c8f96caad8b25d5890ae83c1854f4c16443617b32685002f18e0`。
- 186冻结输入、完整解码、音量、字幕/起音、实际MP4采样与干净构建结果见`qa-final.md`及各独立报告。
- 制作与站点媒体逐字节一致；两次本地网站构建、44句VTT/四章/历史路径回归、32页面与8播放器状态检查通过。平台空提示修正后局部复验和短时播放通过。接下来合并并发布Release，Release之后部署、核验线上实际文件。

## GitHub与线上状态

本文件初始记录发布准备；PR、合并SHA、Release、部署运行及实际GET核验结果在发布完成后追加，不预写已上线或已关闭issue。线上核验脚本为`verify_online.py`，实际结果写`online-verification.json`。

目标页面：<https://linhongcun.github.io/video-studio/episodes/container-most-water/>。对应[#78](https://github.com/linhongcun/video-studio/issues/78)只在网站核验完成后以completed关闭。未将原选题模板里的平台发布事项视作已完成。
