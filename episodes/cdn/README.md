# EP.05 CDN 分镜（Miyazaki）
- storyboard.json：13 镜头，3802 帧 @30fps（不含全局片尾 60 帧），provisionalTiming=false（Knoll 实测 /workspace/share/ep5-timing-v091.json → timing.mimo.json，scale 1，miss-2 的 +30 hold 已含；v0.9.1 已删开头/结尾「我是 IT小村」）
- 工具链：gen_assets.py → gen.py → validate.py；frame.py 出检查帧（check/）；make_timing.py 暂定时长；map_timing.py 接 Knoll 实测
- 配音到后：Knoll 的 cdn timing（键 why-1 origin-1 edge-1 dns-1 miss-1 recap-1，每章一条）存为 timing.mimo.json → `PYTHONDONTWRITEBYTECODE=1 python3 map_timing.py && python3 gen.py && python3 validate.py`
- 拆分（common_split.py）：why 1+2、origin 2+2、edge 2+3、dns 2+2、miss 2+1+2、recap 2+2（句数）
- 新图标（自绘、无文字、可商用）：warehouse / store / store-empty / map / truck；复用第三期 phonebook.svg（查号台），globe.svg 备用未用
- branding v1.3.0：中央淡水印已取消（旧选位文件移到 _v090/）；只有右上水印 + 60 帧片尾卡（全局组件）
