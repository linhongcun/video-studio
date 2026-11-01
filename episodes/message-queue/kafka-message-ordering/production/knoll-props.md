# MQ06 制作说明

EP46 / Kafka MQ06 / kafka-message-ordering / issue314；新输入只在本目录，旧制作源/媒体/冻结不改。基线f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3，root统一声音、freeze/正式串行编码与发布。视频title-author资料附录默认4源/5秒。

14镜28句经root与独立编辑审定后，由root完成全新配音；最终正文4966帧/165.533秒，voiceSHA a4f16ecbbaccc4851dfe794f57c5eaeafc07f00614ce9fc5586fb9c9c03588b8。完整源链research/implementation-map；真实路由类计算和有限29快照分开，Broker与latch报告由运行代理负责，不能提前宣称实测通过。

依赖从本期package-lock fresh npm ci，未复制旧node_modules。动画采用源码新Main，公共调色/原Kafka标记为只读共享依赖，public背景为本期实体副本。声音输入由shared gen/build/place/onset和薄prepare/assemble处理，无本地重实现算法。

prepare报告旁白SHA定义是精确旁白行按镜号直接无分隔拼接（UTF8），不额外加LF，与editorial-candidate一致。正式words/storyboard的声音SHA仍以shared实际算法与实体voice.wav为准。

render默认链：Remotion新fullBT601像素→normalize-color真实limitedBT709转换并setparams→shared背景音乐混音→本期Kafka配色title-author附录→完整媒体/声音保真检查。当前只安装/类型检查，不运行freeze或正式编码。

4文章图位已按真实声轨在article-figure-plan.json确定整数1642/2430/3825/4214，MDX seekTo同步。当前尚无正式编码JPEG验收；随后只按既定图位导实际成片JPEG（limited709→full601），不能冻结后改稿追认。

封面由root负责独立kafka-covers-mq05-07分支和本地输入快照，本目录不修改旧catalog/style-v1。
