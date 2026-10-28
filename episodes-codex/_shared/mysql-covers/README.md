# MySQL系列封面

本轮覆盖EP.15索引、EP.16事务、EP.17锁、EP.18复制。系列显示名统一为MySQL，内部`database`分类ID、原slug、EP编号和问题式单集原题保持，新增单集沿此入口扩展。

固定墨绿底、薄荷绿强调、暖白大标题、数据库圆柱几何标识、真实EP编号及右上IT小村。与前版数据库封面保持同一家族的字体、配色和构图；新增MySQL题名与具体范围。圆柱只标识本片的MySQL实例，内部记录、锁和事务状态继续独立表达，不把几何符号当作官方产品logo。

四片背景均为MySQL 8.4；索引、事务和锁采用InnoDB。索引的小图是逻辑定位示意，不是物理行号或性能实测，不保证每次查询更快；事务限定同一数据库内修改；锁限定显式事务、主键精确找到已存在记录，获得锁后仍判断库存；复制采用单主异步场景，接收不等于应用，不把主库提交当作副本已更新。

背景图片按字节复用原独立模板的无文字生成素材，没有新生成机制事实；真实文本和示意由确定SVG绘制。旧`database-covers/`全部源、封面输入SHA与历史记录保留原字节，本目录独立登记当前六项输入及新图片SHA。

尺寸与布局：1920×1080、1440×1080、1080×1440；横版左文右图，竖版上文下图。4:3将完整竖版以0.75倍居中，内容x315..1125且底边y<918；水印随同版缩放。横版文字同样在y918之上。范围另占一行，不截短主标题或缩小原有文字隐藏溢出。

仓根运行，依赖Node、Python Playwright/Pillow、系统Chromium和Noto Sans CJK SC：

```bash
python3 episodes-codex/_shared/mysql-covers/render.py --out-dir work/mysql-video-style/covers
```

入口核对全部已发布`database`集合、真实EP与完整原题，生成12组三比例SVG/PNG/JPG并检查实际字体、组别间距、像素尺寸及安全区。实际逐图查看并通过后才安装：

```bash
python3 episodes-codex/_shared/mysql-covers/render.py --out-dir work/mysql-video-style/covers --install
```

安装再次核对已验收报告、六项输入和完整图片SHA。制作目录接入PNG/JPG，发布目录接入JPG；双方保存`cover-style.json`和竖版poster。站点海报仍为横版`cover-16x9.jpg`；旧`covers.json`、Cover.tsx、默认旧封面命令及旧冻结不改写。安装与视频接入由本轮负责者统一执行，不能将渲染通过当作已经安装或上线。
