# P02 桥与手电筒：资料核验

核验日期：2026-10-25（北京时间）。对应[#206](https://github.com/linhongcun/video-studio/issues/206)。本期给定四人单独过桥时间1、2、5、10分钟，视频围绕最快者接送19分钟与两慢者同行17分钟的完整过程；数学模型和最短值独立核验见[research-math.md](research-math.md)。

本期制作基线由主任务同步，当前读取到的HEAD为`28b347dbf0399a0c094f1a7023f10501472506f2`；本资料任务不切换分支、不提交，也不改变共享规范。

## 网络与执行范围

已读取`cloud-environment-runtime`技能、网络说明和执行环境的`/etc/codex/network-policy.json`；环境状态为`observations_current: true`、网络`restricted/enforced`。本期指定范围内，公开资料统一通过GitHub connector读取，包含官方OEIS数据在GitHub的公开原始记录。

`oeis.org`、`ed.ted.com`等主站不在当前执行环境允许目标内，未通过shell、改代理或其他路径尝试绕过。本轮不将这些主站记作制作核验来源。下面引用的是实际读到的GitHub文件，不是只从题目issue转录链接；没有发生的网络拒绝也不伪造为已收到的报错。未观看TED影片，不将其记作教学画面已复核。

## S1：OEIS公开原始记录中的四人17分钟例子

- 主张：单人时间为1、2、5、10分钟时，一条17分钟安排为“1和2去、1回、5和10去、2回、1和2去”。
- 来源：OEIS Foundation维护的`oeis/oeisdata`仓库，`seq/A318/A318271.seq`第9—14行。
- 固定链接：[A318271.seq @ a9e08efbe0e8af62bb8a76cde2bb3677e241508b](https://github.com/oeis/oeisdata/blob/a9e08efbe0e8af62bb8a76cde2bb3677e241508b/seq/A318/A318271.seq#L9-L14)
- 实际读取方式：GitHub connector的`fetch_file`，先读默认分支全文，再以文件最后变更提交固定ref重读第1—16行。
- 文件Git blob SHA：`de347d758cccb0af8a70b6776725b8d49a2ef49c`。
- 页面/记录日期：序列始建2018-08-22，当前记录首行标`Sep 25 2026 10:50:16`；GitHub该文件最后提交日期为2026-10-10。访问日期：2026-10-25（北京时间）。不把原题说成2026年新题。
- 短引："When the crossing times are [1,2,5,10], the minimum total time for the group to cross is 17 minutes."
- 支持范围：经典四人参数、17结论和五步路径的外部交叉核对。记录本身没有给出本片模型下完整最优性证明，因此不能用一句“资料说最短”替代本期状态图与下界证书。
- 用在：题面、合法17分钟演示和文章资料脚注。记录中列出的外部论文、维基等链接本轮未打开，不记作已读。

## S2：2026年公开实现说明中的题目规则与19/17对照

- 主张：桥最多两人，唯一手电必须随过桥者移动，同行取较慢者耗时；经典1、2、5、10四人例的17分钟结果，与最快者逐一接送的19分钟形成对照。
- 来源：`PuzzleLearning/LanternNBridgePuzzle`，`README.md`。
- 固定链接：[README.md @ c40f9bbd7e2f960230ebff554e5ccb65853c8bef](https://github.com/PuzzleLearning/LanternNBridgePuzzle/blob/c40f9bbd7e2f960230ebff554e5ccb65853c8bef/README.md)
- 读取范围：第1—72行的规则；第93—99行的四人CLI例；第161—186行的状态方法和经典19/17对照。也读过该ref对应README全文及相关提交说明。
- 文件Git blob SHA：`a503b42919ac8174197d282d9a72d759b8a1dbfc`。
- 页面日期：该次提交2026-08-08，GitHub文件修改时间同日。访问日期：2026-10-25（北京时间）。
- 短引："a pair moves at the slower one's speed"。
- 支持范围：实际规则的公开实现说明及四人例结果交叉核对。该README的主案例是六人1、3、4、6、8、9分钟、答案31，属于另一个例子；本期不把六人参数、31分钟或15分钟手电寿命挪入四人题面。
- 用在：规则段、最快者接送的直觉与改进动机；19和17的具体数值及合法动作另由本期程序复算。

## S3：外部源码只作为状态表示参考，不冒充完整枚举

- 来源：同一公开仓库的[`bridge_puzzle.py`固定ref](https://github.com/PuzzleLearning/LanternNBridgePuzzle/blob/c40f9bbd7e2f960230ebff554e5ccb65853c8bef/bridge_puzzle.py)。
- 文件Git blob SHA：`104f226029d5015fd5e2a857149f8ff00efe18c1`。实际读取第1—185行；访问日期2026-10-25（北京时间）。
- 核验发现：其`solve()`在去程尽量只枚举2人、返程只枚举1人。它与README所概括的全状态思想有关，但已经使用一种路线形状约简。
- 适用边界：不能直接拿该实现声称已枚举本题所有单人去程和双人返程，也不能未经证明照搬“这个约简不影响最优值”。本期`verify_math.py`自行枚举往返均1或2人的全部112条合法边，不执行或依赖该外部源码。
- 该资料提及的历史原型有人员移除错误；本期不复用其原型代码，也不把历史30分钟错误答案放入本片。

## S4：旧资料，仅参考的不同参数变体

- 来源：公开建模作者hakank的[`minizinc/bridge_and_torch_problem.mzn`](https://github.com/hakank/hakank/blob/2823c48d3d2e5d86acb3b8e6951172499c8946b0/minizinc/bridge_and_torch_problem.mzn)。
- 读取：GitHub connector实际读取全文；文件日期2017-07-30，访问2026-10-25（北京时间），按项目规则标**旧资料，仅参考**。
- 内容：其注释采用1、2、5、8分钟，目标15分钟；这是不同的参数例子。另有将初态也算一行的“6 steps”记法，不能当本期6次完整过桥。
- 不采用为本片主论证或参数来源，也不采用其求解目标。保留此条只说明曾核查过变体差异，避免把8与10、15与17混用。

## 本期自己的精确推导与可核验数字

以下数字均为明确定义模型的穷尽计算或简单加法，不是外部实测性能：

- 19分钟：2＋1＋5＋1＋10，逐步合法性见`qa-math.json.routes.intuitive19`。
- 17分钟：2＋1＋10＋2＋2，逐步合法性见`qa-math.json.routes.demonstration17`；另一条17路径见`otherOptimal17`。
- 32个语法状态、30个可达状态、112条有向合法移动、2条最短路径，来自本期独立完整构图；这些统计不是外部源码的统计。
- 最优值17既有可行路线，又有30个整数势值、全部112个逐边不等式构成的下界证书；Dijkstra与独立构图的Floyd–Warshall交叉检查，见[verify_math.py](verify_math.py)和[research-math.md](research-math.md)。

视频先讲题目、完整演示直觉安排，再从同一分叉状态解释两位慢者同行；只回收本期方法与17结果。文章可展示完整精确核验，但片尾不追加证明、不口头引流，不把两条路线对照冒充任意参数下的通用贪心证明。
