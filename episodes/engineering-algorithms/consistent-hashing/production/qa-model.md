# 一致性哈希模型独立核验

结果：**PASS**。检查时间：2026-10-25T21:30:00.433150+08:00。

只核验示意数学模型与供动画读取的数据，不代表产品实测、数据迁移、请求负载测试、音视频复核或观众学习效果。

## 固定输入与结论

- 空间为整数0…99；顺时针选择第一个位置≥键哈希值的token，尾部回绕；每键单份物理归属。
- 原环A@20、B@50、C@85保持不动，加入D@70只接管(50,70]：50仍属B，70属于D，71仍属C。86…99回绕A。
- 同批10个键：取余3→4改变8个；原环加入D仅K06(56)、K07(64)由C改归D，共2个。比例仅属于这组样本。
- 虚拟节点是另一组预先配置示例，不是把原环原地转换。新D@10/34/88分别接管(5,10]、(28,34]、(82,88]，从B/A/C取得5/6/6个整数点。
- 虚拟节点加入前A33/B30/C37，加入后A27/B25/C31/D17；不承诺正好均匀。
- 热键K06(56)在虚拟新环仍单独归C；模型中的10000次示意请求全部归同一物理节点，不是流量实测。

## 独立方法与覆盖

生产模型采用排序后继与二分查找；核验oracle独立最小化模空间顺时针距离，不调用生产查找。区间期待值另用开闭端点不等式求集合。

- `fixture_and_all_100_positions`：pass
- `exhaustive_single_token_rings_spaces_2_to_9`：pass
- `exhaustive_virtual_rings_spaces_3_to_7_up_to_3_tokens`：pass
- `invalid_topologies_are_explicitly_rejected`：pass
- `deterministic_json_matches_generator`：pass

覆盖计数：

- assertions: 53662
- singleTokenTopologies: 1012
- basePositionComparisons: 8148
- singleNodeJoins: 4052
- singleNodeRemovals: 4052
- virtualTopologies: 830
- virtualTokenJoins: 5704
- virtualTokenRemovals: 2120
- virtualPhysicalNodeRemovals: 1060
- rejectedInvalidTopologies: 5

## 文件指纹

- `model.py`：`afb582eb13a119197e947e1deda09ab6fbd4b1a5ddaf9053a2c1416963f81336`
- `model.json`：`b5cf59ec258441d113ae1a4f27f366fb04769c80d6e64fc0d0a54eb19d05728b`
- `verify_model.py`：`e842f17c11a20c1c36e56325c3093ee20626671a624a7c8c4cfe6facdbe6e1d7`

## 能力边界

- Exhaustive checks cover the stated finite topology ranges, not every possible hash space or real product implementation.
- Integer interval counts are exact for this 100-position example; physical load and traffic are not measured.
- 8/10 and 2/10 are sample results, not universal migration percentages or a claimed theoretical expectation.
- Virtual tokens use a separate preconfigured example and do not demonstrate an in-place conversion from the single-token ring.
