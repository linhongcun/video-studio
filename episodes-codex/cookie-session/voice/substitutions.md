# 配音选段与能力边界

本期使用共享 gen.py 产生的 a take；02-separate-1、05-cookie-2、07-lookup-2 选择 b，选段明确记入 picks.json；共享 build.py 负责裁掉附加的“好。”尾巴与整轨，不复制裁切/起音算法。送模文字与原旁白的差异以 params.json 的 subst 为准。Cookie 送模为“库奇”，字幕保留原文。

检查了 build.json 的句内静音、拼接跃变、句间响度与 tailCut；本轮未安装 faster-whisper/ctranslate2，官方模型端点被环境 proxy CONNECT 403 拒绝（root 集中检查）。未执行 ASR、逐字对齐或独立人工听辨，不将声学包络当作错字识别。保留全部选中 takes 与原送模文本，便于复核、换候选。

words.json 仅包含真实句级边界与实测句首声学起音；内部字符的 sentence envelope 明确不代表逐字时间。只将句首术语用于严格起音检查，不估算句中词。

尾段复查：上述三句 a 候选的 tailCut 为0.065、0.123、0.153秒，不能据此断言错字，但存在把末端噪声当作附加尾声的风险。生成 b 后，对应值为0.334、0.466、0.511秒，选择替代并重新铺轨/冻结；共享裁切算法未改。
