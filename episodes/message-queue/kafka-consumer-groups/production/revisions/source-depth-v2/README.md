# MQ02 source-depth-v2 · 分配表怎样决定读取

<!-- mq-source-depth-current-status -->
当前：本修订已随v0.96.1更新原页面，通过非作者成片、本地及原生线上复核，重制#443已completed关闭。完整媒体SHA与实际检查范围见[批次记录](../../../../docs/archive/2026-10/mq-source-depth-remake/README.md)。下文保留制作阶段记录。
<!-- /mq-source-depth-current-status -->

批次#443，基线923305b49cea1b18d7fc7e4dd8ac70ad830bc673。保留EP42、kafka-consumer-groups与原标题《多个消费者：分工处理，还是每人一份？》，旧封面和旧制作输入不改。本目录为独立源码深度重制，当前只到预检阶段；未经root统一放行不冻结、不正式编码或发布。

实际来源与因果见research.md、source-execution-map.md、references.json；无静态成员、无机架偏好，显式classic+Range，members排序是member-id而非client.id。源码真实运行在experiment/，有限模型与动画另有独立身份。

## 本地制作

所有命令从仓根执行。TTS为非确定性操作，已有选定takes不可为普通复核重复生成。

```bash
node episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/check-references.mjs --sources episodes-codex/kafka-consumer-groups/revisions/source-depth-v2
python3 episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/experiment/run_experiment.py --libs /tmp/mq-source-depth-runtime/kafka_2.13-4.4.0/libs
python3 episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/model.py
python3 episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes-codex/kafka-consumer-groups/revisions/source-depth-v2
python3 episodes/_shared/voice/gen.py --dir episodes-codex/kafka-consumer-groups/revisions/source-depth-v2 --jobs jobs-b.json
python3 episodes/_shared/voice/build.py --dir episodes-codex/kafka-consumer-groups/revisions/source-depth-v2
python3 episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/kafka-consumer-groups/revisions/source-depth-v2 --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/kafka-consumer-groups/revisions/source-depth-v2
python3 episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/verify.py
npm --prefix episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/remotion run check:types
```

声音最终4926帧/164.2秒、26句，01-1/04-1/10-2选择同文b，其余23a。早期4981帧装配候选未采用，不沿用其检查当成本期最终通过。无ASR/全片人工语义听辨声明；声学检查与来源/图义/上线分别记录。

```bash
node episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/qa/self-preview.mjs
```

自审输出39张实际PNG与07/09有界静音无字幕clip，失败/修订按真实来源另存。预演端口4342，正式独立QA以最终源/真实voice/board重新bundle，不用静帧代替动态观看。article-figure-plan.json保存已定稿整数帧，最终媒体后由root导出正确BT709→BT601 JPEG，不改冻结制作稿追认。

root完成独立检查、统一放行后才执行本期freeze.py与render-final.sh；这些入口已接实际limitedBT709和title-author默认资料附录，当前尚未运行。全部产物仅本目录或/tmp，无git/站点/共享脚本写入。
