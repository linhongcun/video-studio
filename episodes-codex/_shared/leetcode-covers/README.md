# LeetCode 系列封面

现行独立封面入口，覆盖已发布的 LeetCode 系列。视频正文、配音和原冻结源码保持各自历史身份；这些封面通过单独的系列模板生成，不重写已编码视频的 `source-sha256.json`。

## 视觉规则

- 系列固定深蓝 `#0F172A`、暖金题号与强调、青色方法标签、左上 `LeetCode / 算法可视化` 和右上 `IT小村`。
- 题目名称是主标题，最多两行。题号和方法来自当前发布元数据；辅助问句保留本片实际讲解的看点，不添加效果或难度承诺。
- 横版左文右图，竖版上文下图。每题只保留一个稀疏、准确的小例子；楼梯等原题场景直接使用对应对象。
- 尺寸：16:9 为 1920×1080；3:4 为 1080×1440；4:3 为 1440×1080。
- 4:3 使用竖版完整矢量内容，以 0.75 倍居中到 x315..1125，文本和图表底边均小于 y918。水印位置由本模板统一定义，随整版缩放，不临时挪动。
- 站点仍由各期 `meta.poster` 读取横版 `cover-16x9.jpg`；制作与发布目录的 `poster.jpg` 保持竖版副本。

## 生成与安装

依赖：Node、Python 的 Playwright 与 Pillow、`/usr/bin/chromium`、Noto Sans CJK SC 字体。只调用本入口，不依赖已删除旧工程的 `node_modules`。Chromium 直接渲染 SVG，PNG/JPG 来自同一 DOM，JPG quality 94。

仓根执行：

```bash
python3 episodes-codex/_shared/leetcode-covers/render.py --out-dir work/leetcode-covers
```

入口先比对 `catalog.json` 与所有当前已发布 LeetCode 元数据：题号、题名、方法和完整 slug 集合一致才生成。所有三比例实际字体边界、4:3 内容安全区、输出像素尺寸检查通过后写 `render-report.json`，并输出横版总览。逐张实际查看封面，确认图义、文字层级、裁切和小尺寸辨识。

确认产物后执行：

```bash
python3 episodes-codex/_shared/leetcode-covers/render.py --out-dir work/leetcode-covers --install
```

安装前再次核对验收报告、模板输入与实际图片完整 SHA。制作目录安装 PNG/JPG 和竖版 `poster.jpg`，站点目录安装 JPG 和竖版副本；两处各有 `cover-style.json` 记录当前系列源码与三比例完整 SHA。原题目的 Remotion `npm run covers` 保留为历史视频工程入口，会生成旧模板；系列当前封面应使用本入口。

新增题目时扩展 catalog 和 diagrams，沿同一布局生成；先完成本片可靠元数据再纳入目录。图形与示例必须对应本片内容，不因同属一种数据结构而套用错误方法。本轮 LC.42 为前后缀最大值，LC.547 的实线只表示原直接连接。

新模板、catalog、diagram、渲染脚本通过单独完整 SHA 清单记录；单次产物与检查报告放本轮归档目录。原视频冻结清单和旧 QA 不改写来追认本轮封面。
