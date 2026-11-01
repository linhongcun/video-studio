# D01原例的Java实现与暂停代码卡

本期保留原价100元、会员九折90元、活动八折80元的原例。一次计算只使用一个策略，活动重新从原价100元计算，不把会员价再打折。这里验证设计关系的一种实现，不是生产促销引擎。

完整程序为[StrategyDemo.java](StrategyDemo.java)：选择方在main中选具体策略，Checkout显式持有PricingStrategy并委托，MemberPricing和CampaignPricing分别承担定价。金额使用BigDecimal的元单位，输入为非负且最多两位小数；计算结果向零舍入至分。对本例非负金额，这与旧Python整数分示例的向下截断相同。它是本例金额政策，不是所有定价系统的通用规则。

## 实际运行与只读复核

从仓库根运行：

```sh
python3 episodes-codex/strategy-pattern/demo-java/verify.py
```

默认只读检查源码/代码卡并在临时目录编译、运行，不改已冻结的结果文件。明确修改并审读源码后，才使用同一命令的`--write-artifacts`刷新卡和运行记录。

本机Java为OpenJDK21.0.12.1，虽未安装javac启动器，运行时包含jdk.compiler模块；验证器实际使用`java --module jdk.compiler/com.sun.tools.javac.Main`编译完整程序和独立整数分参照检查器，再运行两者。实际源码SHA、命令、编译器版本与输出在[verified-results.json](verified-results.json)。

已验证100元分别为90/80、原价未变且不叠加；0至20000分的20001个输入分别检查两种规则，共40002个参照比较；负数、超过两位小数、空金额及空策略拒绝。此运行证据只支持本例实现，不替代思想、画面或学习效果检查。

## 卡片与完整程序的关系

`remotion/src/java-card.json`为实际渲染源，含21行关键节选。显示的非空代码均来自StrategyDemo.java，记录源SHA、行范围与移除公共缩进的映射；验证器逐行比对。卡内可见两个实现、共同接口、Checkout持有/委托及main的外侧选择。

卡片标题明确标节选，未展示外层类、import和金额校验/舍入帮助方法。不能把它称为整套可复制编译程序；完整文件才是编译入口。代码卡提供暂停查看，不逐行口播语法。

## 实际阅读的Java21官方资料

访问日期：2026-10-25（北京时间）。本次读取正文和对应API方法说明，不以旧Python运行结果当Java语义保证。

- [JLS21第9章Interfaces](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html)：§9开头关于共同接口类型、类声明实现及接口类型引用的说明；用于本例PricingStrategy与具体策略的关系。
- [BigDecimal Java21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/math/BigDecimal.html)：类说明、字符串构造器说明、multiply(BigDecimal)、setScale(int,RoundingMode)；用于十进制金额、乘法、显式舍入，以及原BigDecimal不可变的边界。只采用这些内容，不声称精度政策由策略模式规定。
- [RoundingMode Java21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/math/RoundingMode.html)：DOWN常量定义及示例。其方向是向零；仅在本例非负输入范围内等同向下截断。

- [Objects Java21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Objects.html)：实际读取requireNonNull的两个方法说明及构造器示例，用于拒绝必需的空引用。

本例仅保留核心设计关系：`Checkout.total` 负责按共同约定委托定价并返回，`main` 演示输入与显示，未实现完整产品 UI。
