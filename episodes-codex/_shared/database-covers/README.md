# 数据库系列封面

当前数据库四期（索引、事务、锁、主从复制）的独立封面入口，新增题按同一规范扩展。旧视频、配音、文章、元数据、Cover/covers与冻结清单保持原身份；本入口单独记录当前系列封面的输入与输出SHA。

固定墨绿底、薄荷绿强调、暖白大标题、数据库圆柱标识、真实EP编号及右上IT小村。横版左题名右机制图，竖版上文下图。题名用于定位主题，问题和边界只对应本片已有内容。通用数据库符号表示组件身份，内部记录与状态各自表达，不将所有数据库说成MySQL。

背景由图像生成工具制作，没有文字、数据或机制事实；实际文字与示意均使用确定的SVG绘制。索引只表达定位对应记录，不凭空扩展B+树；事务限定同一数据库，锁后仍判断库存，主从复制保持异步延迟边界。

三比例：1920×1080、1440×1080、1080×1440。4:3完整居中放入0.75倍竖版，内容x315..1125且底边y<918；水印随同一版缩放。横版文字底边同样小于918，为底部控件预留图像空间。原生控件的具体叠层仍按实际页面复核，图像边界指标不等于所有设备完全无遮挡。

仓根运行：

```bash
python3 episodes-codex/_shared/database-covers/render.py --out-dir work/database-covers
```

依赖Node、Python Playwright/Pillow、系统Chromium和Noto Sans CJK SC，不使用已删除制作工程的node_modules。入口核对全部已发布database集合、真实EP与完整原题，再生成三比例SVG/PNG/JPG，检查实际字体、间距、像素尺寸和安全区。逐份实际查看图义及布局后安装：

```bash
python3 episodes-codex/_shared/database-covers/render.py --out-dir work/database-covers --install
```

安装前再次核对已验收的六份输入与图片完整SHA。制作目录接入PNG/JPG、站点目录接入JPG，两处均有竖版poster副本和cover-style.json。站点继续读取meta.poster的横版，不更换原视频或刷新内容日期。

新增题扩展catalog和diagram，并以真实发布元数据核对；不要用旧期Remotion封面命令覆盖当前模板。来源、生成输入和新产物分别追溯，旧冻结清单不改写。
