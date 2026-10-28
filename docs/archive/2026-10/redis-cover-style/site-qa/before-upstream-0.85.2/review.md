# Redis封面站点QA · 原v0.85.2

14项双视口检查、14张实际截图和11个静态原资产比较通过。实际查看两张合辑中的全部截图，以及library-1440、poster-390、series-1440三张原图；新封面、真实EP40/标题、单课筛选和入口正确。

手机series缩略图按既有CSS隐藏；library新封面完整显示。手机原生播放器暂停控件覆盖封面下部问题文字，不宣称所有原生控件状态无遮挡。正文仍是原历史工程算法标识，媒体未重制。Fullscreen API实际进入/退出，但未点原生全屏按钮或测物理手机。

两次前置静态脚本路径假设在浏览器启动前失败并保留日志；最终依据真实发布树检查meta/video/article/storyboard/script。HTTP keepalive连接被导航中止产生4次ConnectionResetError，浏览器pageerror为零、全部实际断言通过。

之后主干新增分布式独立系列/runtime与version，此报告保留0.85.2实际身份；待新build后重跑同一有界14项，不挪用旧通过结果。
