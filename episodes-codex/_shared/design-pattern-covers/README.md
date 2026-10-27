# 设计模式系列封面

策略、观察者、适配器采用独立系列模板；后续新增模式沿本入口扩展。固定暖砂底、靛蓝文字、蓝色职责模块及橙色连接，模块标识、D编号和IT小村保持稳定。横版题名在上、职责图在下，竖版重新排布图形；大标题定位模式，问题对应当前视频，机制示意保留原片职责与边界。

背景由图像生成工具制作，无文字和机制事实；具体文字和职责图由确定SVG生成。策略每次选择一种算法；观察者通知当前订阅者，MQ不是封面主体；适配器转换并委托外部能力，业务约定是契约，不画成运行中转节点。图中具体订单及数值标明教学示例。旧视频、配音、文章、元数据、Cover/covers和冻结清单不改写，当前封面使用独立源码SHA与cover-style.json追溯。

尺寸：1920×1080、1080×1440、1440×1080。4:3完整居中放入0.75倍竖版，内容位于x315..1125、底边y<918；水印随版缩放。横版文字底边同样小于918，预留图像底部空间，此指标不代表所有设备的原生播放器控件均无遮挡。

仓根运行（Node、Python Playwright/Pillow、系统Chromium、Noto Sans CJK SC）：

```bash
python3 episodes-codex/_shared/design-pattern-covers/render.py --out-dir work/design-pattern-covers
```

入口先核对完整已发布design-patterns集合、真实EP、D编号/课程顺序与完整原题，再渲染三比例SVG/PNG/JPG，检查实际文字边界及间距。逐图查看图义、字号和裁切后安装：

```bash
python3 episodes-codex/_shared/design-pattern-covers/render.py --out-dir work/design-pattern-covers --install
```

安装前再次核对已检查六份输入与图片SHA。制作目录安装PNG/JPG，站点目录安装JPG；两处均有竖版poster.jpg和cover-style.json。站点继续用meta.poster的横版，不改变首发日期、视频与历史平台链接。

新增题同步扩展catalog与diagram、按实际发布元数据校验，再更新输入清单；不要用旧Remotion封面命令覆盖当前系列模板。
