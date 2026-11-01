# 配音选段与能力边界

本期全部使用共享 gen.py 产生的 a take，选段明确记入 picks.json；共享 build.py 负责裁掉附加的“好。”尾巴与整轨，不复制裁切/起音算法。送模文字与原旁白的差异以 params.json 的 subst 为准。Cookie 送模为“库奇”，字幕保留原文。

检查了 build.json 的句内静音、拼接跃变、句间响度与 tailCut；本轮未安装 faster-whisper/ctranslate2，官方模型端点被环境 proxy CONNECT 403 拒绝（root 集中检查）。未执行 ASR、逐字对齐或独立人工听辨，不将声学包络当作错字识别。保留全部选中 takes 与原送模文本，便于复核、换候选。

words.json 仅包含真实句级边界与实测句首声学起音；内部字符的 sentence envelope 明确不代表逐字时间。只将句首术语用于严格起音检查，不估算句中词。
