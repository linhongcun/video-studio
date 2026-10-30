# MQ03 · source-depth-v2

<!-- mq-source-depth-current-status -->
当前：本修订已正式冻结、编码，并通过非作者成片及本地网页复核。完整媒体SHA、实际范围和发布进度见[批次记录](../../../../docs/archive/2026-10/mq-source-depth-remake/README.md)。下文保留制作阶段记录；GitHub上线状态以后续实际回执为准。
<!-- /mq-source-depth-current-status -->

保留 EP43、`kafka-log-replay`、原标题《Kafka日志重放：消息读过了，为什么还能重读？》与已发布封面。本目录是源码深度重制的新输入；基线 `923305b49cea1b18d7fc7e4dd8ac70ad830bc673`，只在本目录制作，不替换旧源或发布目录。

12镜24句沿订单7042的同一E01走完：原日志保留字节 → 读取后客户端位置前进 → 旧内存退出 → 查询已保存的committed → 新位置对象 → `this.position = position;` → `position.offset`进入Fetch → 再读同一记录。正文只有恢复赋值和请求实参两处源码窗口。初始committed=0明确是本例预先保存；commit1对照回到共同起点，只增加提交成功条件；retention对照删除整个符合条件的旧封闭段，不展开自动reset。

固定 Apache Kafka / Java客户端4.4.0、commit `1156b2752aaa28eafc0b4c4d387e63356793268d`。本轮2026-10-30实际复读、原始获取与本轮复用范围分别见 [research.md](research.md) 和 `sources/*evidence*.json`；官方原题按源码文件名与Apache Kafka机构核验，文章保留完整原文链。`model.json`含23份深拷贝快照、101个有限断言，符号载荷SHA不冒充实际Kafka磁盘格式。根的Kafka4.4/RF1、手动assign(P0)隔离位置实验支持位置分离/恢复读取，不证明影片业务、retention或动态组实验。

正文实际装配为 **4602帧 / 153.4秒**，整轨SHA-256 `486e6876c1139746f206cf854f5996a8d314d95f64d782b82e02c2dc6a6e27e4`。24句全新配音：11-retention-1原a短尾、12-recap-1原a满幅样本分别保留，仅同文补b，其余22个a保持；[voice/substitutions.md](voice/substitutions.md)记录声学事实，未当作听辨错字或失真。最后一句替换只增加末镜7帧，前11镜与四图位未变。

生产者类型、PNG与短片自查已完成，生产输入已停写交接；独立动态QA、根统一冻结及正式整片编码尚待放行。预演输出不是最终video.mp4。正式默认正文烧录字幕；只在预演中显式传false并重新解析composition关闭字幕，不改Root默认值。附录沿用共享title-author引擎与Kafka样式，limited BT.709；本地适配器身份已修正为MQ03。四个文章图位在 [article-figure-plan.json](article-figure-plan.json) 与MDX中定稿，正式编码后由根按整数帧提图并显式709→601导出JPEG。

生产者自查及修正保留在 `qa/`：来源raw链接预检纠正、09/11完成标题守卫、预演composition已解析props导致字幕文件名不实、04算式与对象框挤近的现场与定向修正。原始3段短片实际有字幕，已保留并改为`with-subtitles`；真正的无字幕连续窗单独编码核验。未受04守卫影响的11镜只按精确源差异复用，不把旧片笼统称作最终完整验收。具体实看范围以 `qa/self-review.json` 为准。

本目录从现行MQ04借用生产脚本/锁图并fresh npm ci。共享voice/build/onset、附录与色彩实现未复制算法；嵌套ROOT按AGENTS定位，来源薄适配器显式传真实slug。`freeze-inputs.json`声明实际共享style、Kafka references适配器、字体环境ledger、模型、原始证据与本地包装器；没有执行freeze。

从本目录可进行检查与预演：

```bash
python3 build_model.py
node check-references.mjs --sources .
cd remotion
npm run check:types
npm exec remotion studio src/index.ts -- --port=4343 --no-open
```

`build_model.py`会重写本目录模型/检查输出，交QA停写后不要重跑。共享装配或配音重建同样会改输入，需要按实际变化重新审查。`freeze.py`、`render-final.sh`和正式 `npm run render`仅供根统一放行后执行，本轮生产者没有调用。发布、站点、版本、GitHub及批次#443由根处理。
