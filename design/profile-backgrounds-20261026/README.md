# IT小村 · 主页背景候选

2026-10-26，用户最终选定01「深夜小村」，与「代码小村」头像配套使用。最终交付文件保存在 [`design/brand/it-village-background/`](../brand/it-village-background/)：

- [`background-1500.png`](../brand/it-village-background/background-1500.png)：1500 × 1500纯背景原图。
- [`background.svg`](../brand/it-village-background/background.svg)：矢量原稿。
- [`profile-preview.png`](../brand/it-village-background/profile-preview.png)：头像与资料叠加示意，仅供预览。
- [`it-village-background.zip`](../brand/it-village-background/it-village-background.zip)：最终选型文件包。

本次确认的是选图与文件交付，未实际修改平台主页。

根据用户提供的小红书主页截图，为已选定的「代码小村」头像制作8款背景。沿用深蓝、薄荷与少量暖金，把主要视觉放在右上，昵称、头像、简介和按钮所在区域保持平静，方便白色资料显示。

每款原图均为1500 × 1500 PNG，另保留矢量SVG与前端生成源码。尺寸根据截图中约为方形的可见区域设计，不代表平台官方尺寸要求；实际上传时可按平台预览调整位置。所有下载原图均不含文字、头像、平台界面或水印。

| 编号 | 名称 | 方向 |
|---|---|---|
| 01 | 深夜小村 | 屋檐、微光与连接路径 |
| 02 | 知识星图 | 稀疏节点与知识联系 |
| 03 | 工程蓝图 | 格网与等距结构 |
| 04 | 算法花园 | 有机曲线与递归层次 |
| 05 | 暮色小村 | 暖夕光、山峦与村落 |
| 06 | 像素夜航 | 紫蓝星空与像素村庄 |
| 07 | 流光曲面 | 墨绿流光与柔和曲线 |
| 08 | 纸上原理 | 折页与层叠地形 |

- `png/`：8款可直接上传的纯背景原图。
- `svg/`：对应的矢量图形。
- `profile-previews/`：叠加已选头像、白色资料和按钮的布局示意，仅用于选图。
- `contact-sheet.png` / `profile-contact-sheet.png`：原图 / 主页示意的编号总览。
- `index.html`：离线对比页，切换原图与叠加、点开放大对比、下载纯背景。图片均内嵌，无需联网。
- `it-village-backgrounds-8.zip`：图片、示意图、对比页及源码的完整包。
- `it-village-backgrounds-png.zip`：仅8张纯背景PNG的轻量包，方便直接保存到手机。

叠加预览是按截图重建的布局示意，并非平台截图或实际修改的主页；没有修改任何平台账号背景。示意中不复刻账号ID、年龄和位置等资料。

重新生成：在仓库根目录运行 `node design/profile-backgrounds-20261026/build.mjs`，再运行 `python3 design/profile-backgrounds-20261026/export.py`。完整包内也可直接运行 `node build.mjs` 与 `python3 export.py`，叠加预览所需头像已保存在 `preview-avatar.svg`。重新导出需本地Chromium和Python Playwright；已经生成的图片、SVG和对比页无需这些依赖。
