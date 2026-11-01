# LC.3 思路前置：独立动态预检与画面复用审批

执行者：Codex `derive_audit_three`，2026-10-25（北京时间）。本次范围内通过，可以按已审计划渲染新片段、拼接与重新混音；最终MP4尚须另验。机器详情见[qa-preflight-approach.json](qa-preflight-approach.json)。

实际重新计算177项Core输入，均与 `revisions/approach-first/preflight-source-sha256.json`（完整SHA `66ab6343fd68141c71544b4276e4c25527b9d9007cd23017cdd455d596589ed4`）相符。当前预览清单完整SHA `2693434ecf0b8218d3890c7bd824b5ea699c666860b2aca23793164cb7f95871`，其逐文件源绑定全符。

## 真实预览与连续过程

实际查看58张有字幕PNG的四份联系表，并单独打开1137、1252、1735与5830/5905/5979原960×540图片。另从真实隐藏字幕连续片 `derive-and-reset.mp4`（全局567–2037，SHA `d8715a4478d0a765b0c0032c17eaec913abbb814d51c1a8db47291ca5dce5974`）自行解码并查看34个阶段，包含跨03/04/05/06首尾。证据在ignored `remotion/out/approach-independent/`，逐帧索引和完整SHA记录于机器报告。

03依次检查a→ab→abc后碰新b，再从起点1重读b/c后碰同一新b；检查记录明确属于同一输入。04固定右端3，起点0/1均有两份b，不能挖掉中间旧b保留不连续a·cb；随后边界移到最早合法起点2，连续cb保留。05才出现“滑动窗口”，明确重回空区间，实际看到空集合、当前0/最佳0，没有把分析的cb带进正式遍历；06从a重新读入到abc。连续片中未见正文字幕，范围内标题、箭头、身份/下标、说明和字幕无裁切/重叠或装饰进度条。

## 每个复用项目的实际证据

已实际查看21组当前源PNG/原MP4同局部帧配对，并独立重算全部MAE，最大 `2.108717207/255`；覆盖17个实际reuse项目，含完整代码卡。配对不是只凭旁白相同：实际Git e38基线的Scene前helper、题意两分支及grow之后所有分支与当前源保持；Root/data/CodeCard/theme/alias/lock等也核对。除Main新增/过渡分支外，package仅移除render:opener、render:reuse-body、render:revised三个过时入口，保留命令、运行依赖与锁文件不变；不误称package全文字节相同。

明确批准 `code-best:-1`：原282→新281帧，句cue均为[0,133]，仅末字幕结束281→280。新人声结束于局部260.95帧，距新片段结束仍约20帧。我独立解码并实际查看原全局4387（保留末帧、局部280）与4388（删去末帧、局部281），状态均为dea/当前3/最佳5及return best总结，二者MAE `0.000154963992/255`，没有独有动作或词被截断。现19 edge因内部句cue漂移1帧已列fresh，未纳入复用，也未放宽复用时序要求。

审批文件[visual-reuse-review.json](revisions/approach-first/visual-reuse-review.json)按真实template逐项绑定基线视频、当前视觉源、17个slug与上述唯一tail映射。该审批允许有证据的局部画面复用，不声称所有编码像素完全相同。

代码卡首/中/末5830/5905/5979三张PNG字节相同，已单独打开，14行完整Python的接口、循环缩进和return best清楚，暂停提示可见，三样本无正文字幕；原150帧时长和代码源保持。六份封面PNG/JPG实际hash与基线相同，沿用原验收，本次未重开封面。

本记录不是正式成片通过、全片实时观看、逐字ASR、全片人工听辨、新手理解实验或用户认可；不改源、不跑Remotion。正式MP4、响度/解码/PTS与全部150卡帧另验。
