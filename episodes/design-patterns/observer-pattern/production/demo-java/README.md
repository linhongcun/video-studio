# D02原例的Java实现与暂停代码卡

本期仍是同一程序内的订单17：待付款→已付款→已发货。Order维护状态和接收者名单，OrderObserver约定接收OrderChange事实；SummaryObserver保存最后收到的状态，ChangeLogObserver追加收到的变化。第一次双方收到已付款，取消摘要后第二次只有变化记录收到已发货；摘要保留已付款历史，不能再当作实时状态。

完整程序为[ObserverDemo.java](ObserverDemo.java)，自行定义观察者接口，没有使用已弃用的java.util.Observer。结构图、Java名称与视频业务对象一一对应。

## 本例的明确政策

单进程、单线程，不在订阅时补发历史；相同状态不通知；同一接收者不能重复登记。来源先更新状态，再依登记顺序同步处理通知开始时的名单快照。取消影响之后的事件，不撤销当前已经取出的通知名单。List.copyOf复制接收者引用的集合，不深复制观察者对象。

接收者异常向外传播，停止剩余通知；来源状态不回滚，没有自动重试或持久化。通知期间再次改来源状态会在修改前被拒绝。完整程序用finally恢复通知中的标记；短卡省略这类防护逻辑。这些是本实现选择，不是观察者模式的统一顺序、并发或故障保证；示例也没有实现生产订单状态机或真实支付/发货服务。

## 实际运行与只读复核

从仓库根运行：

```sh
python3 episodes-codex/observer-pattern/demo-java/verify.py
```

默认不改任何已冻结的源/卡/结果文件，只在临时目录编译、运行和比对。明确修改并审读源码后，才使用`--write-artifacts`刷新卡及记录。

本机OpenJDK21.0.12.1包含jdk.compiler模块，没有独立javac启动器；验证器实际通过`java --module jdk.compiler/com.sun.tools.javac.Main`编译完整程序与VerifyObserver，再运行两者。8类行为涵盖主线、零观察者、无补发/无变化不发、同步次序、通知中取消的快照政策、接收者错误中断、重入拒绝及重复订阅拒绝。实际命令、源码SHA和输出见[verified-results.json](verified-results.json)。

## 卡片与完整程序的关系

`remotion/src/java-card.json`含21行关键节选：事件与共同接口、Order内先改状态/通知的语句、main内订阅/取消/再次变化。每段保留源码中的上下文注释；源SHA、行范围和缩进移除逐行可复查，分段间只有空白分隔。卡片不是独立完整程序，Order字段、生命周期处理与两个具体观察者的完整方法均在源文件中。

视频结构图先解释两种具体响应，卡中用SummaryObserver、ChangeLogObserver的实际创建与使用连接图和实现；不把省略的类定义伪装成全部代码，也不逐行口播语法。运行验证不代表画面或观众学习效果已验收。

## 实际阅读的Java21官方资料

访问日期：2026-10-25（北京时间）。本次读取以下相关正文/方法，不从旧Python的实现推导Java保证。

- [JLS21第9章Interfaces](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html)：接口提供共同类型、类声明实现及接口类型引用的说明，支持OrderObserver与两个具体实现的关系。
- [List Java21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html)：有序集合说明、Unmodifiable Lists及copyOf(Collection)完整方法说明。copyOf保留传入集合迭代顺序，原集合后续增删不会反映在返回列表中；不等于对象深复制、并发安全或业务可靠投递。

- [Objects Java21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Objects.html)：实际读取requireNonNull的两个方法说明及构造器示例，用于拒绝必需的空引用。
