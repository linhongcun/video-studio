# MQ05–MQ07封面输入

只扩展本批三个实际新选题，沿原Kafka不可变style-v1、背景与品牌布局。启动核对发现原catalog及renderer已被旧冻结清单引用，因此采用独立目录，不修改原目录的任何输入，也不重生成或安装旧四期封面。

`catalog.json`仅对应EP45/MQ05、EP46/MQ06、EP47/MQ07。渲染允许对应草稿身份；安装仍核对EP、原题、sourcePath、episodePart与已检查图像SHA，不会使草稿公开。具体机制图服从本期示例，实际文字、三比例与4:3安全区另审。

从仓根执行：

```sh
python3 episodes-codex/_shared/kafka-covers-mq05-07/render.py --out-dir docs/archive/2026-10/mq05-07-implementation/covers
```

实际审图并通过后再用同一命令加`--install`。本目录及实际读取的原style/background/logo/许可进入各新期冻结输入；不据此改写旧封面回执或认领未执行的正文与媒体验收。
