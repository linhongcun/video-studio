# LC.739 栈入门修订 · 制作说明

本轮因用户实际观看后指出默认懂单调栈而返工。旧版v0.69.0完整基线在revisions/stack-primer-before，baseline.json记录46395cfb基线及旧video/voice/storyboard/source摘要。内部EP35、片内LC.739、标题与slug保持。

创作范围是16镜32句：03后新增04 stack-basics、05 monotone，旧04/05成为06 order、07 name，原06–14顺延08–16。原28句逐字不变，只有04/05四句需要新TTS。四章ID保持。script/plan/config已锁稿交独立审读，真实起音由root共享装配处理。

新增StackPrimer.tsx只服务两镜概念示意；真实append/pop五步数据来自research/make_stack_primer_operations.py生成的stack-primer-operations.json。它不解每日温度、不计算天数。原算法solution.py/solution.json/trace.json不变，完整Python卡和三比例封面保持。

06 OrderPrimer使用实际算法trace完整演出30出、31出、35留、32进，07承接35≥32，不暗中回滚。旧Weather/PLAYBACK尽量逐字保留，其他12镜的源码和局部时序保留，供root以共享remix_approach及旧基线做复用证明与局部编码，不重录原28句。

本执行者只创作稿件、源组件与必要文档，不生成TTS，不写真实storyboard/words/voice，不调用freeze，不跑build_draft，不渲染正式媒体。当前真实SB仍是旧14镜基线；root后续负责配音、句级装配、真实时序、冻结及局部正式编码。新镜需要独立动态和成片检查，旧检查不预先追认新源。

全部新图形程序化SVG，不使用第三方实物图或天气服务。代码卡固定36字号，最后150帧静态并提示暂停。新术语栈、单调、单调栈分别在04、05、07第二句句首起音后才显示；ASR、人耳或用户观看效果均按实际执行记录。
