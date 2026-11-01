# D02观察者模式：v0.58.0上线记录

[观看视频与配套图文](https://linhongcun.github.io/video-studio/episodes/observer-pattern/)。2026-10-25（北京时间），内部EP.28 / 设计模式D02。按用户已有GitHub持续发布授权完成，只上站点，外部平台未新发。

## 交付身份

- [PR #236](https://github.com/linhongcun/video-studio/pull/236)已合并，主干/附注tag实际目标为`530ddc75e14d9d0d5b1d2e01363969a9ab027266`；[Release v0.58.0](https://github.com/linhongcun/video-studio/releases/tag/v0.58.0)发布于北京时间08:32:24。
- [Release后Pages部署40147093346](https://github.com/linhongcun/video-studio/actions/runs/40147093346)为workflow_dispatch，head同上述提交，完整构建和部署成功。合并使用skip ci避免重复自动部署，Release后仍执行完整部署工作流。
- 标签中已核对0.58.0、firstRelease v0.58.0、EP.28、4979帧及实际检查视频，生产/发布目录与已验收feature分支树一致。见[tag身份](tag-identity.json)与[真实部署](deployment.json)。

12镜24句/5章，画面165.9667秒，容器165.973秒，约2分46秒。视频8,536,404字节，完整SHA-256：`76f38c9675e7ecf57520df1212cfac78093d6e24eaf534a38ed8c07a6e8c0c08`。1080p30fps/AAC48k，−16.0LUFS/−3.7dBTP；119项已编码输入保持。实际检查范围见[qa-final](qa-final.md)。

## 同步与发布范围

从干净主干先拉取1834450，重读上游清理/规范并在本期锁文件真实安装依赖；后续整合e38fa92、7d1d6f6/v0.57.1及28b347d上线记录，保留其他视频与最新手册。渲染输入与上游变更无交集，只解决网站版本为新的0.58.0；不改已有标签、不重渲无影响内容。

主片以订单17两次变化解释订阅、共同通知约定、各自响应与取消后的行为，没有语法教学。图文SVG属性按网页渲染器转换为发布派生稿，原冻结文章不变，正文事实/音视频/字幕均不改。修前与修后、派生SHA和定向范围分别保留，见site-article-derivation.json及site-svg-correction.json。开工/渲染启动错误记L034，SVG兼容问题记L035，S017更新本片应用及D01用户定性认可。

## 实际线上核验

北京时间`2026-10-25T08:35:41.637130+08:00`，首轮9个canonical普通GET全部200，无缓存查询参数，完整视频流计算SHA且未保存远端媒体。视频/海报/24句VTT与本地发布稿相同；5章起点0/769/1715/2962/3674，源码、目录、D01↔D02、首页、系列、RSS和真实v0.58.0 Release条目通过；线上SVG原生字体/居中属性亦已核对。完整记录见[site-online-verification.json](site-online-verification.json)。本地Release抓取降级的限制已由本次生产条目检查闭合。

核验通过后[#164](https://github.com/linhongcun/video-studio/issues/164)以completed关闭，系列[#161](https://github.com/linhongcun/video-studio/issues/161)保持open，D01/D02完成、其余21项待安排。本片尚无用户观看结论；没有逐字ASR、完整听辨或新手学习实验声明。
