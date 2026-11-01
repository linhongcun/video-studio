# 线上播放器核验

Release v0.79.0；Release后Pages40473036363成功后执行。未修改既有check-site.py，原脚本93项实际播放器/图文检查通过。报告见verification.json；实际网络传输、原生Chromium CA失败与校验范围见transport.json。远端响应通过已配置CA验证的urllib获取，保持canonical origin并真实执行浏览器播放、跳转、字幕与全屏交互；未关闭TLS验证。

根代理实际查看reference-paused-1440.png、reference-paused-390.png和reference-fullscreen-landscape-844.png。窄屏小窗按视频比例显示，横屏全屏资料原题/机构可读。未进行真机或全片人工听审。
