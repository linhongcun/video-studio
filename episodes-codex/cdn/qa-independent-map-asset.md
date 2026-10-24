# EP05 地图资产与投影只读复核

更新时间：2026-10-24T21:44:24.895897+08:00（北京时间）

本次范围内未见阻断性资产或投影源码问题。仅审地图子系统，并实际查看首批带字幕静帧03；不代替过程或最终MP4审查。

- 固定上游提交：`ca96624a56bd078437bca8184e78163e5039ad19`。已按原有proxy/TLS路径实际获取raw源，HTTP200，138160字节，与本地逐字节相同。完整SHA-256：`9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9`。
- 资产为Natural Earth `ne_110m_land`，比例尺1:110,000,000；127个Polygon、featurecla全为Land，128个闭合环（含1个内孔）。没有加载行政边界层。本地metadata、landPaths内嵌source SHA与实际源一致。
- convert与角色geo使用相同经纬换算。环逐点连续展开并平移±360，当前数据展开后没有大于180°的相邻跳跃，最大约9.032°。origin经度-125→235后与亚洲/北美同处太平洋视图，角色位置均在可见范围。代码没有把图上距离当真实网络测量。
- 实际查看 `remotion/out/map-first/03.png`：亚洲—太平洋—北美轮廓和user/selected edge/origin关系可辨。这是首批带字幕静帧，不是过程或最终成片通过结论。

可选点位建议：origin(-125,38)位于所用land轮廓外海；挪到(-121,38)会落北美陆地，画面右移30px，更直观。edge(132,35)在这份概化轮廓中也稍离岸。现有图已标节点/路线为示例，此项不作为事实阻断，也不要求为此返工。

实际访问官方正文（2026-10-24北京时间）：[Natural Earth使用条款](https://www.naturalearthdata.com/about/terms-of-use/)确认公有领域与可修改复用；[固定commit的上游README](https://github.com/nvkelso/natural-earth-vector/blob/ca96624a56bd078437bca8184e78163e5039ad19/README.md)核对数据集来源；[110m Land资产页](https://www.naturalearthdata.com/downloads/110m-physical-vectors/110m-land/)核对land polygons含主要岛屿（旧页面，仅参考静态资产类型）。

详细文件SHA、公式、点位和范围见同名JSON。没有改仓库文件/Git，没有运行项目测试、配音或渲染。
