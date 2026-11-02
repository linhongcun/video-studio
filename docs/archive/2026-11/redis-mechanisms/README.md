# Redis Sentinel / Cluster / 近似 LRU 三期

2026-11-02（北京时间）按用户授权制作 Redis 相关待安排选题。三期已完成制作、独立来源/叙事/声音/动态/正式媒体、图文及本地与线上原生播放器检查，并由 **v0.99.0 交付 GitHub 站点**。实际发布身份与回执见 [publication.json](publication.json)。已交付跳表 EP40 和既有缓存两期保持。

| issue | EP / slug | 正式媒体 | 当前冻结输入 | 源码 |
| --- | --- | --- | ---: | --- |
| #296 | EP50 / redis-sentinel | 4589帧 / 152.967秒 | 257 | [制作输入](../../../../episodes/redis/redis-sentinel/production/) |
| #297 | EP51 / redis-cluster-failover | 4616帧 / 153.867秒 | 326 | [制作输入](../../../../episodes/redis/redis-cluster-failover/production/revisions/pre-release-state-text/) |
| #302 | EP52 / redis-lru | 4463帧 / 148.767秒 | 193 | [制作输入](../../../../episodes/redis/redis-lru/production/) |

三个最终 MP4 的完整 SHA、正文/资料帧数和当前 `sourcePath` 见 [media.json](media.json)。每片正文后均有一页5秒原题/机构资料列表，配套文章分别有2/3/2张来自同份成片的精确帧 JPEG。

## 来源与真实运行

开工前工作区干净，已 fetch 最新主干 `01cd181caf24d4a8ce846c0eb8faeeab8f0054e2`；使用现行 `episodes/redis/<slug>/{production,publication}`、新装的各期锁文件依赖和现有共享配音/起音/混音/资料工具。旧57期、原冻结共享工具及迁移账本保持。旧忽略缓存仅移出仓库保存；可重建预演 bundle 保留本机并排除 Git 传输，唯一源、图片、原始失败与检查回执继续保留。

产品固定 Redis 8.4.0 / `60ba86f3c8b4e1ec96451171753a0a38e5c45a0c`，官方 tag/API、源码与文档原始 GET、版本/许可及精确短引均保存。实际本地编译、二进制身份见 [runtime](runtime/runtime-manifest.json)。教学模型与真实运行分开：Sentinel 验证已知5台而只剩2台时 ODOWN/无多数授权，以及3台授权后排除 priority0、副本晋升和重新复制；Cluster 验证六进程正常晋升/槽归属和已有 FAIL 后仅一票不足；LRU 实测最旧 A 存活、较新键淘汰且 expired=0。均为本地进程/配置范围，不是断电、全部署安全或性能基准。

## 独立检查与修订

三期使用同系列银灰/Redis红、实际 EP，三比例封面来自新增不可变 v3 模板。源/音轨/资料及默认入口在编码前冻结，正式媒体做真实 limited BT.709 转换，资料页同色；JPEG 显式转换709→601。原文引用和 Figure 回看保留站点共享交互。

独立动态审查拦截并修正了文字抢先、消息路线遮字和候选删除后的旧提示；原图/源码/报告均保留。Cluster 正式成片复核又发现晋升前先写“已接管”、选票飞行时先写“抵达”，因此保留原309输入与旧成片，建立 `pre-release-state-text` 独立修订，只改三处状态文字及必要路径适配，冻结326项后重新默认编码。旧/新全部6980个 AAC 包及时间戳完全一致，原 WAV、模型、旁白与镜头时序相同。资料附录和当前成片回执由真实新流程产生，不改写旧清单追认。

当前正式媒体独立验收：Sentinel118帧、Cluster修订63帧（原候选154帧另审）、LRU76帧及各资料页/正文字幕边界/全部图位实际看图；三条完整视频与 AAC 解码通过，最终响度均−16.0LUFS，峰值分别−3.8/−3.6/−3.0dBTP。决定见 [Sentinel](qa/sentinel-encoded-final-decision.json)、[Cluster](qa/editorial/cluster-revision-encoded-final/independent-final-decision.json)、[LRU](qa/lru-encoded-initial/independent-final-decision.json)。LRU449帧预演封装少一帧的失败及无重渲封装修正保留，见L061。

本地原生浏览器检查覆盖桌面/390视口、实际播放暂停、56个严格 presentation PTS、章节/七图回看与原图、所有引用、两主题横溢和 Fullscreen API；三期共176项动作，Cluster修订再单独68项/20PTS。初始海报原生加载弧、可见原生控件遮暗部分底部烧录字幕、窄屏字号及模拟视口范围如实保留，不能称真机或所有暂停状态无遮挡。机器回执与实际图审分别存放，不改原 `visualReviewed=false` 机器记录。

## 发布范围

本批仅 GitHub 与本站。首发字段按实际站点发布流程启动时刻写入，创建时间只归一至站点支持的毫秒精度，原值保留在日期格式回执；不重设创建日期。[制作PR #455](https://github.com/linhongcun/video-studio/pull/455) squash 合并 `7971d833e37b145eac5ccf66901773beba5cd0a6`，附注 tag 与 [Release v0.99.0](https://github.com/linhongcun/video-studio/releases/tag/v0.99.0) 后再次手动 [Pages41417179935](https://github.com/linhongcun/video-studio/actions/runs/41417179935) 于17:09:32（北京时间）成功。完整核验后已回填并关闭 #296/#297/#302 为 completed；#294 保持 open，总览更新为6已交付、1待安排、2取消，其中Redis4含已交付跳表，其他2已交付、1待安排。未执行全片人工语义听辨、逐字 ASR、物理手机或学习效果实验，不预记用户已观看认可。

## 线上核验与收尾

[26次普通 canonical 完整 GET](qa/online-full-get-after-release.json)在 Release 后手动部署成功后执行，三支 MP4、海报、VTT 与七图的完整 SHA 全匹配；系列6课、首页/内容库/兼容学习入口、章节/原文、RSS首发时间、实际 Release 和更新日志链接通过。无 Range、cache-busting、TLS忽略或请求回填。

线上原生浏览器在初次成功部署后执行，三期分别50/68/58动作、18/20/18严格PTS；手动部署与初次同主干、同媒体，后续完整GET闭合最终发布字节。56张实际 canonical 解码PNG与具名当前本地PNG全部逐字节相同，见[像素身份](qa/site-online-pixel-identity.json)。实际页面图审另存 [Sentinel](qa/site-online/redis-sentinel/visual-review.json)、[Cluster](qa/site-online-review/redis-cluster-failover.json)、[LRU](qa/site-online-review/redis-lru.json)及[未参与制作的LRU同伴图审](qa/site-online-review/redis-lru-peer.json)。

目录的三张桌面封面已实际等待解码并看图；390目录按既有响应式CSS隐藏缩略图，文字卡正常。第一次补验误等待隐藏lazy IMG的decode而由root中止，原失败回执保留，改按真实可见性补验；无产品代码变动，见[补验与实图结论](qa/site-online-thumbnail-visual-review.json)。各期首屏loading弧、原生暂停控件压暗/遮底字幕及竖屏细字小仍如实记录。

此前57期与196份旧冻结清单保持原字节。密钥扫描原始失败中的48个旧公开源码/协议常量均与基线同字节，新增/变化/未解决命中均0；生成预演bundle中的Remotion公开常量由source-map定位，缓存本机保留并排除Git传输，原日志未改，见[扫描复核](qa/secret-scan-final-review.json)。issue更新前后快照及研究段落保护验证见[issues-closeout](qa/issues-closeout/)。
