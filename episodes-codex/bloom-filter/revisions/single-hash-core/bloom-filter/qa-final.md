# EP39 单位置主线：发布前检查

最终成片4720帧、157.333333秒（正文4570帧，原题参考资料150帧），1080p30 H264/AAC。完整SHA-256：`e47e4cb2707d108f739232fc4f763aea6a459e45e30a6d8f8bb75b3444cfe2dd`。冻结130项输入，清单SHA：`06632c370fe18c66636221cd04f31413d6c5042352ddb8cfdc19888f6f673dcb`。

单哈希8位模型经独立60,349项断言与逐句技术/叙事审读；197真实PNG/DOM、4段无字幕连续片段和14,219项实际DOM检查通过。独立实看45张预检图与56张最终MP4图，完整解码/4720帧PTS/资料首中末/7142AAC包保持均通过。root另实看9张预检PNG、10张真实短片解码图及8张最终MP4图。3比例6份封面通过；不将静图当成全片实时观看。

18段来源PCM与共享整轨重放一致。最终实测−16.02LUFS、−3.65dBTP，混音延迟95样本、句间漂移0；3个原始源低电平旗标及2个整轨旗标保留，来源区间和编码前后量值对应，未宣称词语语义或全片人工听辨通过。没有逐字ASR。

站点构建与参考资料/日期检查通过。实际Chromium桌面1440与窄屏390各42项，共84项；18条原生VTT、四章、第一资料帧4570精确paint/无active cue、原生fullscreen API、文章SVG/代码复制反馈、六方向入口/工程算法两课与RSS首发时间均通过。窄屏及横屏为headless桌面Chromium视口，不是真机。实际截图审读另见站点QA记录。

原URL/EP39/创建及首发身份保留，仅updatedAt更新；902份其他发布文件全文SHA不变。旧版150冻结输入与旧MP4仍保持原字节。只上GitHub站点；Release后Pages与线上完整SHA/字幕/章节/海报/更新日志验证完成后，再补发布收尾和关闭#342。此报告不代表用户已观看认可新版。

代码可达性补充检查通过：实际容器横向及整页纵向滚动、完整复制内容与示例执行另见qa-site-code-access.json。新增QA首轮未等待smooth滚动导致的断言失败已归档；改用即时滚动后通过，没有修改产品或放宽边界。

## 上线收尾

已由[PR #343](https://github.com/linhongcun/video-studio/pull/343)合并`47e27a7b`，随[v0.71.1](https://github.com/linhongcun/video-studio/releases/tag/v0.71.1)发布。[课程页面](https://linhongcun.github.io/video-studio/episodes/bloom-filter/)保持原URL、EP39与首发身份，修改时间为2026-10-26T10:15:31+08:00。

最终4720帧、157.333333秒，完整SHA-256：`e47e4cb2707d108f739232fc4f763aea6a459e45e30a6d8f8bb75b3444cfe2dd`。130项冻结输入的清单SHA：`06632c370fe18c66636221cd04f31413d6c5042352ddb8cfdc19888f6f673dcb`。

独立模型/审稿、真实动态/DOM、56张实际MP4图及完整解码/音轨数值检查通过；桌面/窄屏84项本地检查及代码滚动、完整复制/执行可达性通过。最新[Pages40262765700](https://github.com/linhongcun/video-studio/actions/runs/40262765700)成功，2026-10-26T11:16:49.910345+08:00的10个普通canonical GET核对完整媒体SHA、海报、VTT、四章及实际Release/更新日志通过；线上两视口实际播放、章跳转、4570首资料帧paint与无active cue通过。

实际阶段结果见[最终QA](qa-final.md)、[动态预检](qa-motion-independent.md)、[实际成片](qa-video-independent.md)、[网页审查](qa-site-visual-independent.md)、[发布证据](publication-evidence.json)。Release首轮识别检查发现说明缺课程URL，补齐后重新部署同步日志，原失败记录保留；没有重配或替换成片。旧150项冻结和原媒体、其他902份发布文件保持。没有全片人工听辨、逐字ASR或新版用户观看认可；窄屏为headless视口，非真机。仅GitHub站点，无外部平台新发。
