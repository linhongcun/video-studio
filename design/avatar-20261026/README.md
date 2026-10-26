# IT小村 · 头像候选集

## 最终选型（2026-10-26）

用户已选定 **01「代码小村」** 作为新头像：深蓝背景、薄荷色屋檐与代码括号，将「小村」名称和技术内容结合。源码保留在 [`symbols.mjs`](symbols.mjs)；后续品牌头像使用以此选型为依据。

最终交付目录为 [`design/brand/it-village-avatar/`](../brand/it-village-avatar/)，包含 [`avatar-1024.png`](../brand/it-village-avatar/avatar-1024.png)、[`avatar-512.png`](../brand/it-village-avatar/avatar-512.png)、[`avatar-256.png`](../brand/it-village-avatar/avatar-256.png)、[`avatar.svg`](../brand/it-village-avatar/avatar.svg) 和 [`it-village-avatar.zip`](../brand/it-village-avatar/it-village-avatar.zip)。本记录仅确认选型，平台账号头像与网站 logo 的实际替换另行记录。

## 候选保留

围绕项目的技术可视化定位制作的 12 款候选：代码与学习、系统连接与算法、亲和的讲解者，以及品牌字标。沿用项目深蓝、薄荷与少量暖金，加入几款浅色、紫色与朱红探索。所有方案均为代码绘制，编号只用于选择，不会出现在头像原图中。

打开 `index.html` 可以筛选方向、切换圆形/方形预览、放大与下载。页面自带全部 SVG 和 PNG 导出逻辑，无需联网、安装依赖或启动站点。`contact-sheet.png` 为 12 款编号总览。

| 编号 | 名称 | 方向 |
|---|---|---|
| 01 | 代码小村 | 代码括号与屋檐 |
| 02 | 翻开原理 | 延续站点书本意象 |
| 03 | 代码开演 | 代码与播放键 |
| 04 | 逻辑生长 | 分支与连接节点 |
| 05 | 技术村民 | 戴眼镜的技术讲解者 |
| 06 | 括号小友 | 花括号笑脸 |
| 07 | 像素村民 | 像素风程序员 |
| 08 | 好奇小鸮 | 阅读与好奇心 |
| 09 | 电路村标 | 「村」字与电路 |
| 10 | 小村朱印 | 「小村」中文印章 |
| 11 | 几何 IT | 大写 IT 与负形切口 |
| 12 | 连线 IT | IT 字母与分支路径 |

`png/` 中每款为 1024 × 1024 的不透明方形 PNG，适合上传后由平台圆裁；`svg/` 为相同图形的矢量原稿。关键图形保留圆裁安全空间。`review/small-sizes.png` 展示 32 / 48 / 64 / 96 px 的效果；`review/checks.json` 为实际导出和交互检查结果。

修改与重新生成：

```sh
node design/avatar-20261026/build.mjs
python3 design/avatar-20261026/export.py
```

`symbols.mjs`、`characters.mjs`、`typography.mjs` 分别保留三个方向的 SVG 源码。浏览器导出脚本使用 Python Playwright 和系统 Chromium，仅重新导出时需要。

09、10 的中文字形来自 Noto Sans CJK SC Bold，采用 SIL Open Font License 1.1；最终 SVG 已将字形转换为路径，不依赖接收者安装字体。许可全文见 `FONT-LICENSE.txt`。

项目阅读与同步基线：`4213a233c4c242b04453b8c1215031dc421c2398`，已 fetch 并确认与当时的 `origin/main` 一致。候选稿保存在独立设计目录；01 已选定，其余方案保留供追溯。
