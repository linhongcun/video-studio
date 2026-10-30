# MQ02 · 制作说明

本期独立source-depth-v2重制，13镜26句、四章，当前正文4926帧/164.2秒；对应voice SHA见words.json。根与独立QA已审定脚本/实现主线后才请求TTS，使用共享prep/gen/build/place/onset算法，不复制它们。本机无全片人工语义听辨/逐字ASR宣称。

真实实现依据：固定1156b275…源码，Range/AbstractPartitionAssignor计算表，经典coordinator/客户端交换和安装assignment，SubscriptionState/AbstractFetch枚举列表构造请求。实际编译执行的三份未修改源码与驱动、命令、原始输出在experiment/；这是内存类执行，不是Broker/协议网络实验。有限教学状态在model.json，用真实实验的归属结果交叉核验，图义检查另外完成。

Main读取真实storyboard和20个深拷贝教学快照。06/07商、余数、候选集合与表格同源；09请求只选已安装P0，10 N3无分区Fetch，11积分组独立表，12两组各自四条而原日志保留。画面数据不随字幕重新计算，不用代码名巡览替代解释。渲染读取实际Kafka style-v1与本地背景副本，右上末镜显示IT小村·原创。

目录嵌套适配：ROOT动态查AGENTS；check-references.mjs仅显式提供真实slug给共享checkSources，保持全部原有规则；pipeline-tools.py动态解析共享混音路径；render.py私有函数命名空间仅选择本地来源adapter和资料adapter，不改共享引擎。依赖按本修订锁文件fresh npm ci。

来源和字体、实际共享style/references、模型/图位、代码、选定配音/分镜及研究证据都在本修订冻结声明中；此阶段不执行freeze或正式渲染，root统一闸门与串行渲染锁。默认render会先来源/冻结预检，再正文pc601→tv709实际转换、共享混音和同色title-author片尾。旧封面由root发布时原字节复用。
