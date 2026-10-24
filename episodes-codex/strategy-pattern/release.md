# 策略模式D01：发布记录

## 已完成的本地交付

- 制作issue：[#163](https://github.com/linhongcun/video-studio/issues/163)，系列总览：[#161](https://github.com/linhongcun/video-studio/issues/161)。
- EP.23 · 设计模式D01，slug：`strategy-pattern`。
- 成片：5198帧，约2分53秒，1920×1080/30fps，−16.0LUFS、−3.7dBTP。
- 视频完整SHA-256：`c80f9e44ee8eb668fb702266170d4fd8773d14f120e315b568d6ed5d07c27431`。
- 海报完整SHA-256：`cf343bd67aecd80e26f5bb31c905a6fc9811eb1d8e23b43b02daa75dfa8c048e`。
- 完整本地媒体、实际画面与站点检查见 `qa-final.md`、`qa-independent.md` 和站点副本的检查JSON。

## GitHub发布状态

计划版本v0.52.0，新增独立设计模式系列首期。当前等待合并、发布Release、Release后Pages部署及线上普通HTTP GET核验；后续在本节补实际PR、提交与部署记录。

线上目标：[策略模式视频与配套文章](https://linhongcun.github.io/video-studio/episodes/strategy-pattern/)。线上验证脚本为本期 `verify-online.py`，读取canonical页面、视频、海报、VTT、系列、首页、RSS与更新日志；视频流式完整哈希，不下载另存远程媒体。

用户尚未观看本期，不将本地或线上检查称为用户认可。平台新发未执行。
