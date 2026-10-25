# 三片发布记录

2026-10-25（北京时间）完成，实际版本[v0.57.0](https://github.com/linhongcun/video-studio/releases/tag/v0.57.0)。本次只上GitHub站点。

[制作与集成PR #231](https://github.com/linhongcun/video-studio/pull/231)已合并为`1834450d6dd6e36762aa1862a72282c4e89822ac`；附注标签v0.57.0指向同一提交，没有覆盖保留的v0.56.4。实际Release于2026-10-24T23:52:06Z发出，正文显式关联三片完整URL。

- [LC.1 两数之和](https://linhongcun.github.io/video-studio/episodes/two-sum/)
- [LC.206 反转链表](https://linhongcun.github.io/video-studio/episodes/reverse-linked-list/)
- [LC.70 爬楼梯](https://linhongcun.github.io/video-studio/episodes/climbing-stairs/)

Release后手动[Pages运行40144462891](https://github.com/linhongcun/video-studio/actions/runs/40144462891)实际success，部署头为同一1834450d。2026-10-24T23:57:50Z完成17次实际HTTPS GET：三份完整MP4和海报的制作/canonical/线上完整SHA相同，76句VTT与已检验dist逐字节且逐句/帧时序一致，每页四章、代码卡内无字幕、源码/原生控件、首页/节目库/系列/RSS正常；线上新Release自己的更新日志条目关联全部三片。

[线上完整核验](online-verification.json)、[部署API证据](deployment.json)、[实际Release](release-api.json)、[附注标签身份](tag.json)保留完整字段。三个制作issue #75/#77/#81已在实际成功核验后以completed关闭，真实状态/时间见[收尾记录](issue-completion.json)，未把平台上传勾成完成。

经验已写入开工同步规范、L032（旧ignored依赖与最新主干）、L033（查询值/返回下标）及S018（共享批量流程、保留逐片验收）。局部避让拦截补到L003，保留其他机器新增的L031。新三片尚无用户观看反馈；不将软件与声学检查写成人工全片听辨、逐字ASR或学习效果。
