# LC.1 公开资料与独立推导

访问日期：2026-10-25（北京时间）。制作选题为[issue #75](https://github.com/linhongcun/video-studio/issues/75)。以下区分题面、语言语义、成本模型与本期独立证明；不把文稿核验当作配音、动画、成片或学习效果已经通过。

## R1 官方题面

- 来源：[LeetCode 1. Two Sum](https://leetcode.com/problems/two-sum/description/)与[力扣1. 两数之和](https://leetcode.cn/problems/two-sum/description/)。
- 实际获取：通过可用网页工具分别打开并读取中英文正文、三组示例及约束；不是仅看搜索摘要。两种语言的题意相符。
- 页面日期：题面未标发表或更新时间，不以版权年份推断。
- 支持主张：输入整数数组及目标值，返回和为目标的两个元素下标；输入保证恰有一组有效答案，同一元素不能用两次，返回下标的先后顺序不限。数组长度为2..10000，元素及目标均在-10^9..10^9范围。
- 官方第三例的两个数值相同，仍分别来自不同位置，因此“不能用同一元素两次”不等于“两个值不能相同”。
- 短引：英文题面写“not use the same element twice”。
- 用在：开头输入、限制、目标、返回值，重复值与不同下标的区分。主片两组数组是本片自选教学输入，不称为官方例子。

## R2 Python字典语义

- 来源：[Python Built-in Types — Mapping types](https://docs.python.org/3/builtins/stdtypes.html#mapping-types-dict)。
- 实际获取：实际打开官方内置类型文档并定位字典取值、赋值、成员测试条目。
- 页面日期：本次页面显示2026-10-24更新；这是所见文档元数据，不表示算法提出日期，也不据此推断平台使用的Python小版本。
- 支持主张：`key in d`检查键是否存在；`d[key]`取对应值；`d[key] = value`写入映射。同一个键再次赋值会更新其对应值。
- 用在：数值→原下标的表、`need in seen`与`seen[x] = i`。本片展示表中的行只是便于阅读，不将字典查找画成逐行线性扫描。

## R3 平均复杂度与边界

- 来源：[Python — Time complexity of operations on built-in types](https://docs.python.org/3/builtins/time-complexity.html#dict-frozendict)；[Python Design and History FAQ — Dictionaries](https://docs.python.org/3/faq/design.html#how-are-dictionaries-implemented-in-cpython)。
- 实际获取：实际打开官方复杂度页与FAQ，读取字典章节及限制。没有把不可见的第三方Wiki重定向页作为已读出处。
- 页面日期：本次官方复杂度页显示2026-10-24更新；未将此日期解释为复杂度定理的新发现。
- 支持主张：CPython内置字典以可扩展哈希表实现；查找的O(1)是平均成本，写入还涉及扩容的摊还成本。成本表假定键的哈希、比较为O(1)，分布适当；大量碰撞时单次操作可为O(n)。它不是所有Python实现或任意键类型都无条件满足的最坏保证。
- 用在：视频简写“平均时间O(n)”与文章边界。本题整数范围按常见单位成本模型处理；额外最多保存n个键值对，所以额外空间O(n)。

## 官方题解访问限制

实际打开了[官方editorial地址](https://leetcode.com/problems/two-sum/editorial/)，工具只取得登录、导航与编辑器空壳，没有题解正文。因此不能写“已读官方一次遍历题解”；本期解法正确性与轨迹由下述独立论证和实际提交源执行核对支撑。

## 本期独立正确性论证

从左到右处理下标i时，表里只记录严格早于i的位置；每个已出现的数值保留一个已见原下标即可。令当前数为x，要找的伙伴值为`target-x`。如果表里存在该值，取到的下标j必有j<i，因此不会复用当前位置，且两数之和满足目标。

未找到时，才把当前数及下标加入表。对真实答案的两个位置a<b，当处理到b时，a的数值已经在表里，因而能命中。若相同数值的旧条目被更晚的已见位置覆盖，表中仍保留一个合法的更早位置，足以找到一组有效答案；不需声称必须保留最早下标。官方恰一解条件使输出唯一的一对下标（次序不限）。

“先查再存”使表不会包含当前下标，尤其当`target == 2*x`时，不会把当前一个元素与自己配对。两个不同位置恰好值相同则完全合法。

## 自选教学轨迹

主例`nums=[3,8,11,6,15], target=9`：依次查找缺少的6、1、-2均未记录，分别存入3→0、8→1、11→2；到下标3的6时需要3，命中3→0，返回`[0,3]`。下标4的15无需继续访问。原数组不删除、不排序，下标不重排。

独立重置例`nums=[3,8,3], target=6`：首次遇到3时表为空，不能返回`[0,0]`；先查失败再存3→0。最后遇到下标2的3时命中旧3，返回`[0,2]`，说明相同数值可以来自两个不同位置。两例的表和目标必须明确重置。

## 执行核验状态

`research/verify_algorithm.py`已直接加载实际`solution.py`。值域-2..2、长度2..5、目标-4..4共35,100个枚举场景中，只将符合官方“恰一解”的7,465组计入实现核验，全部通过；零解或多解场景不冒充官方条件用例。另9个显式例及1个长度10,000例通过。核对了返回位置不同、目标和、输入不变，显示JSON及文章唯一Python块与执行源逐字相同。有限用例不能替代上面的证明，也不能证明动画、音轨或初学者理解已经合格；实际SHA与结果见`research/algorithm-verification.json`。

## 片尾参考资料

2026-10-26为已验收原片整理title-author清单，3项、一页5秒，只显示原题与作者或机构。R1 Two Sum、R2 Built-in Types、R3 Time complexity of operations on built-in types的技术阅读身份均保留为本片2026-10-25，不更改题面、字典语义、成本模型及独立算法证明。

本轮只补核Python原题与出版机构：从官方CPython固定commit `c436e8d83597c6f8c1bc7e37812c98d46670c29a`完整GET `Doc/builtins/stdtypes.rst`、`Doc/builtins/time-complexity.rst`、`Doc/copyright.rst`，原题分别取第8行Built-in Types与第4行Time complexity of operations on built-in types。当前映射小节含dict及frozendict，故不把旧脚注缩写当成完整章节题名，也不将frozendict扩展进视频讲解。出版机构Python Software Foundation依据官方版权页，仅作为机构身份，不推定文献个人作者。旧技术读日为25日，题名／机构补核为26日；固定源SHA只代表26日实际取得的完整响应，不追记为25日原页hash。

本轮没有请求LeetCode中英文题面或editorial，不把原先未取得的题解正文记为成功。片中算法正确性继续依据本期独立不变式证明与已有实际执行记录，而非官方题解。旧全文、脚注及锚点完整保留；完整标题、逐论点旧读记录、基线研究Git blob／SHA与26日元数据请求见[本轮证据](../../docs/reference-endcards/batch-9/sources-two-sum.json)，完整书目见[references.md](references.md)。
