# EA01 一致性哈希发布记录

本地成片及网站验收通过，计划首发v0.70.0，制作PR#304，内部EP38。制作初始基线d515f0d4，已整合46395cfb的三条新LeetCode内容、v0.69.0和字幕边界修复。

- 目标页面：https://linhongcun.github.io/video-studio/episodes/consistent-hashing/
- 媒体SHA-256：`5a54624a31f293fb2b68161ed9875a184a992fc322996a5a010d3fca61d3242e`，10,263,723字节，5881帧。
- 本地检查：见qa-final.md、qa-video-independent.md、qa-site-browser.json；146冻结输入保持。
- 当前发版阶段：等待实际合并、tag/Release和Release后Pages部署，线上结果随后按真实证据补齐，不以本记录预记成功。
- 本次范围：只上GitHub站点，无外部平台投稿；尚无用户观看结论。

Pages只发布video.mp4与meta.poster（16:9）；4:3/3:4封面留在Git和本地检查。原冻结verify_online.py误包含未公开封面URL，未执行它；QA-only的verify_published.py只修正了线上GET范围，并记录原验证器SHA与本地封面摘要，未改146输入或成片。
