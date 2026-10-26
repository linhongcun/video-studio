# bridge-torch · 片尾参考资料

采用 `presentation: title-author`：完整原题与实际作者/公开项目发布名，每页最多4项、默认5秒，无quote/date/hint；不追加数学证明或口播。两个来源足够，不挂未读论文。

技术实读日期均保留 **2026-10-25**。26日只复用既有OEIS%N/%A证据及GET一次固定README核标题/署名，不冒称重新读技术正文；OEIS2018条目标历史仅参考，不把26年导出当新题。

证据见[sources-bridge-torch.json](../../docs/reference-endcards/batch-11/sources-bridge-torch.json)；[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/a1a9821845c83a61a57fbb3f0e10461ef4c55238/episodes-codex/bridge-torch/research.md)及[旧研究归档](../../docs/reference-endcards/batch-11/sources-bridge-torch-prior-research-a1a98218.md)是本仓历史记录，非外部原文镜像。

- 基线：`a1a9821845c83a61a57fbb3f0e10461ef4c55238`
- 原research Git blob：`d883a65feca8aa32d752512045b08eed8d7e7edf`
- 原research完整SHA-256：`596f0da38d929ad885bcef1400c5d4b7aa519353ab16a7300c7e4316e3a44263`（6829字节）
- 原article完整SHA-256：`0f4483a8007e6ed6c6761a4295ecde1f48c50123b3fde2e55d26ba1139b05d70`（10528字节）

## R1 · The optimum crossing time for the Bridge and Torch problem, given that the crossing times for the group's members are given by the n-th partition in A026791.

- 作者：Peter Kagey
- 发布方：OEIS Foundation
- 版本：A318271 · 2018-08-22条目（历史仅参考）；2026-10-10固定导出
- 原文固定链接：[The optimum crossing time for the Bridge and Torch problem, given that the crossing times for the group's members are given by the n-th partition in A026791.](https://github.com/oeis/oeisdata/blob/a9e08efbe0e8af62bb8a76cde2bb3677e241508b/seq/A318/A318271.seq#L9-L14)
- [既有实读记录（2026-10-25，R1）](https://github.com/linhongcun/video-studio/blob/a1a9821845c83a61a57fbb3f0e10461ef4c55238/episodes-codex/bridge-torch/research.md#L13-L23)

- 原题证据：复用既有26日OEIS固定文件实读证据originalExcerpt的%N原题行；25日article第166行交叉作者与条目身份
- 技术阅读范围：A318271.seq %N题名、%A原条目署名及第9–14行%e四人17分钟路径；不包含本片完整最短性证明
- 镜头对应：01, 08, 09, 10, 11, 12, 16

旧主张：单人时间为1、2、5、10分钟时，一条17分钟安排为“1和2去、1回、5和10去、2回、1和2去”。

适用边界：经典四人参数、17结论和五步路径的外部交叉核对。记录本身没有给出本片模型下完整最优性证明，因此不能用一句“资料说最短”替代本期状态图与下界证书。

## R2 · Lantern & Bridge

- 发布方：PuzzleLearning / LanternNBridgePuzzle
- 版本：README · 2026-08-08固定版本
- 原文固定链接：[Lantern & Bridge](https://github.com/PuzzleLearning/LanternNBridgePuzzle/blob/c40f9bbd7e2f960230ebff554e5ccb65853c8bef/README.md)
- [既有实读记录（2026-10-25，R2）](https://github.com/linhongcun/video-studio/blob/a1a9821845c83a61a57fbb3f0e10461ef4c55238/episodes-codex/bridge-torch/research.md#L25-L35)

- 原题证据：2026-10-26仅题名/署名补查：固定README首两行Setext标题“Lantern & Bridge”；原技术实读25日
- 技术阅读范围：README第1–72行规则、第93–99行四人CLI例、第161–186行状态方法及19/17对照；不采用六人参数或15分钟电量限制
- 镜头对应：01, 02, 03, 04, 05, 06, 07, 13, 14, 15

旧主张：桥最多两人，唯一手电必须随过桥者移动，同行取较慢者耗时；经典1、2、5、10四人例的17分钟结果，与最快者逐一接送的19分钟形成对照。

适用边界：实际规则的公开实现说明及四人例结果交叉核对。该README的主案例是六人1、3、4、6、8、9分钟、答案31，属于另一个例子；本期不把六人参数、31分钟或15分钟手电寿命挪入四人题面。


README本轮题名补查原始完整响应：[保存文件](../../docs/reference-endcards/batch-11/sources-bridge-torch-lantern-readme.md.source)，12037字节，SHA-256 `4efbb278ac5d5d94bdc19e11c0b2eb23e763ad594086c02fddd46badbd909ac1`，Git blob`a503b42919ac8174197d282d9a72d759b8a1dbfc`与旧25日记录一致；只补原题及显式署名检查。

OEIS原题/作者来自已提交[身份核验证据副本](../../docs/reference-endcards/batch-11/sources-bridge-torch-oeis-identity-reused.json)，JSON原字节SHA-256`834b0af9fa174f944c96d9e6821713febb5a72bd58c6053fbb33b75540d86e44`；该SHA不是OEIS源文件响应SHA。Peter Kagey由%A及旧article166行明确，不根据Git作者推断。

## 保留范围

旧article/research全部字节、frontmatter、锚点、两条旧脚注和独立证明完整保留。未引用OEIS外链论文/维基或未看TED；未将外部受限搜索源码当完整枚举，未重跑本期数学检查。root捕获的6025帧Git原片为媒体基线，生产MP4最初缺失，本任务没有重建或检验视频。

只改来源与追加说明，不触及freezer/README/source-sha/脚本/发布episodes/共享/QA，不预记新媒体、上线或用户认可。
