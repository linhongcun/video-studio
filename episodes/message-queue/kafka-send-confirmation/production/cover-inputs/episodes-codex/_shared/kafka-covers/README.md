# Kafka 消息队列系列封面

消息队列方向统一围绕Apache Kafka，保持现有message-queue路径与历史EP。固定暖炭灰、橙色强调、冰蓝辅助、Noto字体、Kafka身份标识与稳定MQ编号；题名和具体机制图随单集替换。MQ编号取规划索引，不是发布顺序，当前核心为MQ01–08和MQ15，不将MQ15改成MQ09。新题可继续扩展编号。

`catalog.json`只收已发布或本轮重制的实际单集，逐字核对meta原题/EP；`productionRoot`指当前制作修订，不能默认写回旧父工程。安装时必须已接入对应Kafka媒体的sourcePath和episodePart，防止给旧RabbitMQ视频只换Kafka封面。当前MQ01按日志追加、消费保留和业务完成边界表达，不沿用RabbitMQ逐条ACK删除。

`style-v1.json`是正文与封面共用的不可变配色/字体契约；新增题扩展catalog不修改它，旧片冻结不绑定会增长的catalog。需换基础视觉时另建版本。背景图像生成只提供无事实的静态边角装饰；具体图和文字由SVG绘制。Kafka原始SVG取既有[middleware-identity](../middleware-identity/NOTICE.md)，原字节与浅色衬底保持，来源与MIT许可随完整输入SHA追溯，不表示官方授权或背书。

仓根运行（Node、Python Playwright/Pillow、系统Chromium、Noto Sans CJK SC）：

```bash
python3 episodes-codex/_shared/kafka-covers/render.py --out-dir work/kafka-covers
```

实际封面生成1920×1080、1080×1440和1440×1080三比例SVG/PNG/JPG。4:3完整居中缩放0.75倍竖版，内容x315..1125、底边y<918；水印同版缩放。横版文字也保留底部空间，此边界不保证所有原生控件状态完全无遮挡。

另按`plan-layout.json`的9个已规划主题和三位编号MQ100检查30份文字排版，不生成未来8期真实封面、不安装或上站，也不证明其机制图已经完成。当前标题/问题最多两行，所有新增文字必须通过真实字体检查，不能截断或无限缩小。未来题库变化时先同步issue规划再扩展，旧取消条目不恢复为待制。

逐份实际检查图义、字号与裁切后：

```bash
python3 episodes-codex/_shared/kafka-covers/render.py --out-dir work/kafka-covers --install
```

安装重新核对输入、9个SVG/PNG/JPG和媒体元数据绑定，制作修订安装7图、站点安装4图，两处成对cover-style.json。其他系列与旧冻结源保持。正文制作读取不可变style-v1与本轮冻结背景副本，原视频保留在历史修订，不靠改名伪装Kafka内容。
