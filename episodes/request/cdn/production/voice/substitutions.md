# 地图返工送模替换与选片

2026-10-24，沿用共享prep/gen/build，音色冰糖（mimo-v2.5-tts）。CDN字幕/脚本原文保留CDN，params.subst仅将送模文本改为C D N，要求按三个英文字母读；不把这份送模请求记录冒称完整人工听辨。选中03-network-1/03-network-2/04-edge-1/05-miss-2的b候选；其余20句沿用v0.48.0的a候选。所有旧a候选保留，未覆盖。生成作业jobs_map.json与gen-map.log保留。

历史v0.48.0的params中曾沿用无实际匹配的Cookie替换，本期没有Cookie口播，当前只保留有用的CDN替换。共享prep添加的“好。”是裁切尾标，字幕和成片旁白均不包含。
