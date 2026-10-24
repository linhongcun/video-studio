# LC.3 发布记录

用户在当前聊天要求再选一道有信心的题目制作精品。本期选择[#79](https://github.com/linhongcun/video-studio/issues/79)，持续授权覆盖制作检查完成后的GitHub合并、Release、Pages部署及实际线上核验；不包含外部平台投稿。

## 制作与本地检查

- slug：longest-substring，独立LeetCode系列，展示LC.3，内部ep23。首发v0.53.0（同步保留主干v0.51.0事务导航及v0.52.0策略模式），版本与主干其他系列分别记录。
- 18镜36句、4章，5078帧、30fps，约2分49秒，含5秒完整Python代码卡；字幕不延伸至附录。
- 先演示r3遇到重复b为何连续删a和旧b，再演示r7遇到a时当前窗口收为dea但历史最长cbade仍为5；集合成员与字符串位置、候选与合法窗口分别表达。全文程序与执行/显示源一致。
- 权威资料、独立程序和无字幕关键过程、真实配音时序及封面已检查，161输入冻结。正式媒体8,391,127 bytes，完整SHA256为`c8adbb517ccba5296a3b019cb48ea4a3695c47c861f27e325cef1ea76e342043`；完整解码及−16.0LUFS/−3.6dBTP通过。独立实际MP4的10个关键帧及1440/390新页复核通过，站点80页构建、29页索引与既有学习路径回归通过；可按持续授权合并发布。
- 只继承共享工具的已验证行为，不把前一期的用户认可写成本期已观看结论。没有ASR或全片人工听辨声明。

## 合并与上线

- [PR #194](https://github.com/linhongcun/video-studio/pull/194)已squash合并，主干提交`706f0b13cb1068d75eb99e61577e2ff0a006142c`保留Codex联合署名。
- 同提交的附注tag及[GitHub Release v0.53.0](https://github.com/linhongcun/video-studio/releases/tag/v0.53.0)已发布，firstRelease为v0.53.0，正式媒体保持检查后的同一份。


- [部署40105542981](https://github.com/linhongcun/video-studio/actions/runs/40105542981)于2026-10-24 23:09:55（北京时间）成功，head与合并提交一致，API证据见revisions/problem-first/before-deployment.json。合并触发的构建已收录实际v0.53.0 Release链接，线上脚本对此另有断言，不只比对页脚版本。
- 2026-10-24 23:10:27（北京时间）实际HTTPS GET核验通过：线上视频8,391,127 bytes、完整SHA与检查后媒体相同；海报123,430 bytes、完整SHA为85982c447c2494becba5d476367f9865b26c12d890fcf066cc8860b6334330b1；36句VTT逐字节一致，SHA为0bcfb90d0e8c7eb5a74c242e6a5b88cd41490cbd3491737890b8b3db03987785。
- 四章精确起点、正文锚点、源码入口、独立系列、首页/RSS及实际Release更新日志通过，见revisions/problem-first/before-online-verification.json。2026-10-24 23:10:55（北京时间）已将#79以completed关闭，API结果见issue-closure.json；不表示外部平台已经发布。
- Release后另按流程触发的[部署40105615410](https://github.com/linhongcun/video-studio/actions/runs/40105615410)也已成功，head与合并提交一致，见release-deployment.json；未取消其他工作流。

## v0.54.2：题意先于解法

- 按用户共同反馈重做前两镜：先讲输入、可选内容和限制、目标及返回值，再进入原方法。保留已发布正文和5秒完整Python卡；源文件后缀与后续takes不变，每镜仅静态尾停补剪最多1帧。
- 当前5129帧、170.966667秒，较上一版仅增加1.700秒；视频8,468,691 bytes，完整SHA256 `61e6d380eb260b2cac5a629aaef62f544fdcd3d7b928da8db242efe9f53088a1`。题意预检、独立实际MP4检查、166输入冻结、完整解码和音量通过。
- 本轮补丁接续学习站v0.54.0与策略模式v0.54.1，未回退其它机器的内容；题意规范、L026、经验与制作检查清单更新。网页1440两页/新VTT/章节检查通过，合并、Release、部署及实际线上证据完成后补齐，不声称用户已观看新版。
