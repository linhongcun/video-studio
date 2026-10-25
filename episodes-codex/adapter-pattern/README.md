# 设计模式D03：适配器模式（v0.63.0已上线）

从订单17的发货提醒操作进入，用同一收件人和内容说明业务通知约定、适配器与外部服务的协作；明确已受理不等于已送达。产品页、服务与示例均为教学，不向外发送消息。Java只在片尾关键节选，完整实现另附。

开工前已从干净main同步，基线见startup.json。自身依赖按锁fresh npm ci，不引用已删除工程；先独立审稿/预演，冻结后才正式编码。GitHub站点按持续授权完成后发布，外部平台不新发。


## 当前可复现入口

脚本/计划已独立审读，Java源码与21行节选同源，12组行为实际运行通过。12镜24句、4章；正文5121帧，Java静默150帧，总5271帧/175.7秒，正文仍是语言无关的职责与协作。音轨已完成，独立动态门已通过，166项输入已冻结；正式完整渲染与独立媒体复核通过，v0.63.0网站接入、构建及两视口章节/字幕/Java/SVG/三期导航已通过；Release后Pages成功，11个普通GET的线上完整媒体/海报/24句字幕/四章/目录与真实更新日志核验通过，#165已completed关闭。

```sh
python3 episodes-codex/adapter-pattern/demo-java/verify.py
python3 episodes-codex/_shared/append_java_endcard.py verify episodes-codex/adapter-pattern
python3 episodes-codex/adapter-pattern/freeze.py
python3 episodes-codex/adapter-pattern/freeze.py --verify
```

freeze先走原有共享Java正文/零尾检查器和冻结入口，再纳入本期sources实际出处证据；不修改被旧片固定的共享实现。原声正文留在helper默认的revisions/flow-ui-java/voiced-body，这是本期首次制作快照，不表示沿用旧片。最终派生稿不要再次运行正文装配覆盖尾卡。

正式渲染只在所有owner停写、独立真实动态门与冻结成功后，从本期remotion目录用短TMPDIR和共享锁执行npm run render；混音后复制out/mix-report.json到期根，再运行共享check_encoded_episode.py。版本和站点首发数据在媒体通过后按最新main确定，具体接入/本地浏览器/线上入口见site-README.md。

实际发布、并行版本处理和首次线上检查修正见[交付记录](release.md)、[线上完整核验](qa-site-online.json)。本期尚无用户观看反馈。
