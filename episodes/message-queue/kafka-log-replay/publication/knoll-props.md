# MQ03 source-depth-v2 制作说明

当前12镜24句、4章，正文4602帧/153.4秒。voice.wav完整SHA-256 486e6876c1139746f206cf854f5996a8d314d95f64d782b82e02c2dc6a6e27e4，整轨公开音频为实体副本；24句新配，11-retention-1原a短尾0.0806秒被拦截，仅同文选b约0.43秒，另12-recap-1原a的18满幅样本风险也仅同文选无满幅b，最终两个b、22个a保持。声学/句级时序与ASR/人工语义听辨分开。

共享voice/prep/gen/build、assemble_sentence_episode、place_v2和onset原实现未复制。nested ROOT由AGENTS定位；来源检查通过本地check-references.mjs显式传真实slug，默认render适配本地CHECKER与Kafka BT709附录，不改共享模块。fresh npmci使用当前MQ04锁图，新工程自己的node_modules，不指向旧ignored目录。

Main逐镜读取本期model.json的23份深拷贝快照，101有限断言；动作由本期真实voice localStart/localEnd驱动。DOM暴露模型态、文字/COPYFIT、移动体、position/committed/log-slice身份，独立QA按真实图义与时序复核。

默认render完整正文混音后追加title-author资料页，4个实际官方源码文件名与Apache Kafka机构，默认5秒，无原文/定位上屏；pc601→limitedBT709转换与正文/附录编码一致。最终帧数与实际MP4身份由根放行编码后的回执确定，不能把短clip或预期帧数当最终成片。

文章四图精确整数帧/秒数在article-figure-plan.json与MDX已定，正式编码前作为输入；截图之后由根select整数帧并从limited709明确转换到full601 JPEG。读取/恢复链有根的RF1 assign(P0)隔离真实实验交叉支持，影片业务、retention/动态组/文件格式演示仍是模型，不泛称已实测。

本代理只做到类型/PNG/短clip自查与独立动态预检交接；不冻结、不正式编码、不写发布目录或站点/git，由根统一放行。