# EP05 CDN：地图与术语返工

2026-10-24，用户观看v0.48.0后要求增加真实地理地图与CDN等技术名词；本轮保留同一图片主线，地图参与调度、未命中回源与命中短返。旧版输入/结果/检查在revisions/v0.48.0，旧发布事实不作为本轮完成证明。

当前状态：本轮本地成片已编码，3989帧/132.966667秒，完整SHA `3715e0514c8ec1cef02a8b32027910de16fd18b04ef5b1b0191f9596f277d9e6`；102项冻结输入、全解码/响度与制作实际54帧抽样已通过，新最终片独立35帧/6联系图复核已完成，所看无未解决阻断（qa-independent-encoded.md）。root负责站点/Git/发布，本执行者只制作本目录；本记录不宣称已发布。

复现：仓内episodes/_shared/voice/prep.py、gen.py（voice/jobs_map.json）、build.py；新选定takes保留，避免重请求不确定TTS。assemble.py生成真实句级边界/字幕/术语起音；共享selfcheck/place_v2/label_onset_strict与preflight.py检查；地图转换python assets/map/convert.py。remotion目录npm ci、tsc --noEmit、npm run covers、npm run render。

TMPDIR和QA大文件均使用本期remotion/out工作盘；flock /tmp/video-studio-render.lock串行较大预演与正式编码。freeze.py冻结地图原始GeoJSON/公开许可依据/元数据/转换脚本与src静态路径、选定音轨、脚本、共享实现等实际输入；freeze.py --verify只读核对。check-render.py对真实MP4测量解码/帧数/响度/完整SHA。

Natural Earth 110m land公有领域；源/许可/固定上游commit/SHA与投影在assets/map/source/metadata.json和assets/map/convert.py。配乐Kevin MacLeod《Wallpaper》CC BY4.0沿用共享。无运行时远端URL。

没有逐字ASR或完整独立人工听辨的结论；字幕来自原稿和实际句级边界，术语位于句首并使用共享声学起音规则。qa-motion、qa-final及qa-independent-*记录本轮实际完成范围；本地制作与检查已完成，站点发布和线上核验由root继续记录。
