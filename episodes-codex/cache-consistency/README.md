# cache-consistency Codex重制工程

2026-10-24，用户授权EP01–14按今天Codex制作规格和经验整体重制。本目录为独立新工程；公开依据见research.md，视觉设计见visual-direction.md，最终检查状态见qa-final.md。

共享配音命令均从仓根执行：prep.py → gen.py → build.py（各带--dir episodes-codex/cache-consistency），再运行本期assemble.py、共享selfcheck.py/place_v2.py/label_onset_strict.py。ASR能力限制单独记录；不重新请求已有选定takes。

运行依赖：FFmpeg、/usr/bin/chromium、Noto Sans CJK SC；Python依赖沿用仓内共享配音环境。

Remotion：在remotion目录npm ci、npx tsc --noEmit、npm run covers、npm run render。正式编码用flock /tmp/video-studio-render.lock串行协调有限资源，单次渲染并发2。开发node_modules软链不提交；锁文件可独立安装。配乐Kevin MacLeod《Wallpaper》，CC BY 4.0，目标−16 LUFS。

站点由root统一接入发布；本目录制作代理不修改episodes/。
