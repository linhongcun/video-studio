# LC70 楼梯场景返工基线

本目录保存旧版身份及本轮保留审计。基线为 `bb9b4e9782ed4b7b2d12a8fac9fd478193febfb8`（v0.60.4）。`before/` 的字节直接读取固定Git blob，未从正在编辑的工作区复制。大媒体不重复存储，由 `baseline-inputs.json` 绑定固定路径、blob、SHA及现场身份。production视频为ignored输出，以固定Git中的canonical视频为基准并另核对现场身份。

原片为12镜24句、4779帧/30fps；完整Python卡从4629帧起持续150帧。`baseline-sentences.json` 记录每句原文/TTS、选中take、句窗与四类音频文件身份。`media-identity.json` 记录原视频、AAC、解码混音PCM、人声PCM及代码卡无声样本区间。没有生成新配音、重跑算法或渲染正式视频。

固定Git的124输入匹配原冻结清单；独立开工核对时现场124项也全部匹配。现行 `freeze.py --verify` 只读；普通冻结会更新输入清单。共享冻结器递归收录 `remotion/src`，新增 `Staircase.tsx` 自动进入新清单，无须改共享freezer。现依赖软链指向保留的two-sum实际安装目录，两片锁包图匹配；未恢复已删除的Agent工程或缓存。

旧算法执行报告绑定的程序、显示源和文章SHA全部匹配，因此字节不变时复用旧执行证据。新场景的动作、预检、正式媒体与站点验收由后续报告记录，不能由本基线冒称通过。`qa-scene-preservation.json` 当前只记录基线及受保护输入，正式新视频产生后再更新。

原成片AAC已无重编码提取到 `inputs/original-audio.m4a`，作为新画面最终mux的明确冻结输入。7469个包的内容、顺序、PTS/DTS/duration与固定Git原片逐包相同，解码PCM也相同，见 `audio-extraction.json`。本片wrapper须显式纳入该M4A；它不属于共享freezer默认输入。

视觉返工需要修改script画面说明与SB视觉元数据，因此不要求这三份文件整字节不变。`qa-scene-preservation.json` 独立逐字比较12镜24句旁白，words只允许scriptSha256封套变化，SB只允许明确列出的视觉说明及来源封套变化；所有实际时序、字幕、cue与句窗保持原值。旧source清单不改写，后续正式渲染前另行冻结新视觉输入。
