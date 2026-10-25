# D01保留原例的流程调整 · 制作说明

2026-10-25。原100元会员90/活动80、单选不叠加保留。11镜22句中5句新配、17句沿用，另150帧静默Java节选；总帧按storyboard/words与javaEndCard。旧源、时序及媒体身份在revisions/flow-ui-java/baseline。

01以结算UI教学示意进入，读取原价、选择优惠、查看应付；改选活动先计算中、后80元。02进入背后程序，03–04分离具体定价并保留共同约定。05稀疏结构逐一对应Client/main、Checkout上下文、PricingStrategy约定与两个具体策略；接口不当作一次计算。06选择会员后沿共同步骤委托、收90元才继续；07清旧结果、重用100元改活动得80元。08–11保留协作、维护边界、成本与回扣。

首现策略模式cue仍为04第一句，唯一算法是共享onset_rule。Java卡静默，标节选/暂停；Main在javaCardFrom关闭旧字幕与页眉，motion.at用此作为正文末端。卡JSON来自真实Java源并逐行验证，正文不口播语法。金额单位为元，精度/舍入政策见demo-java说明。

依赖来自当前保留的strategy-pattern/remotion/node_modules，需按lock确认。预演用npm run qa，核无字幕有效props与实际输出、COPYFIT、事件相邻帧和跨镜接续。01/02/05/06需新画面，旧正文只有证明local时序与像素一致才复用，否则重渲。负责人全部停写后由根任务冻结，短TMPDIR与共享锁正式编码；本代理不发版。

图文主章why/delegate/change/boundary保留，Java锚点java，SVG用原生属性。媒体解码、源SHA、音轨/字幕、实际状态与线上字节检查由对应报告记录，不冒称逐字ASR、听辨或用户学习效果。
