# 两集新视觉源独立审查

EP.08 Scene仅将收尾品牌y460→650的限定视觉改动逆转后，与原Scene全字节相同；EP.09 Scene本来全字节相同。两集sequence与字幕HTML/时序条件保持，UI逻辑仅移除装饰glow。

EP.09分支拓扑、标签、场景配置及navigationContext经import层级与颜色别名逆转后逐字节相同；data/motion直接复用旧定义。共享导航渲染器只有配色和HUD位置/字号变化，camera/phase/activepath计算直接使用原actualNavState/navigationEvents。没有因视觉统一改写读写顺序、重置、回填、错误交错或删除失败。

共享palette9字段与字体栈沿用跳表；原Redis标记字节保持。Header/说明/标题、品牌与价格、全局/局部/HUD和字幕仍需实际预演检查。逐项SHA和精确限定变化见JSON。
