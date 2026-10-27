# 趣味推理系列封面

现行独立系列入口，覆盖P01赛马、P02过桥、P03量水、P04三门、P05鸡蛋，并可按同一规范扩展新增题。已有视频、文章、配音和旧封面冻结源保持各自身份；本入口单独记录当前封面输入与输出SHA。

## 视觉规范

- 固定紫黑底 `#171326`、浅紫 `#C7A4FF`、暖珊瑚 `#FF9E8B`，中文「趣味推理」、P编号与右上「IT小村」。与LeetCode蓝金模板通过颜色和上题下图的构图区分。
- 题名作为主信息，下一行是贴合本题的一句问题。下方保留一幅较大、稀疏的题目对象图，不把完整证明或全部步骤压在封面里。
- 背景 `background.png` 由图像生成工具专门生成，无文字、数字或题目事实；题名、条件和真实示意均由确定的SVG源码绘制，避免生成图中的文字和数量误差。
- 16:9=1920×1080，3:4=1080×1440，4:3=1440×1080。4:3以0.75倍完整居中放入竖版，内容保持x315..1125、底边y<918。水印随同版缩放，固定在本模板的header位置。
- 横版全部文字也保持底边y<918，为播放器底部控件预留空间；图框背景可继续延伸，关键题设与注记保持可读。
- 站点仍读取各期 `meta.poster` 的横版，`poster.jpg` 是竖版副本。旧 `covers.json` 和Remotion封面命令保留历史身份，不用于覆盖当前系列封面。

## 生成与安装

运行依赖：Node、Python Playwright/Pillow、`/usr/bin/chromium` 和Noto Sans CJK SC。无需旧制作工程的node_modules。仓根执行：

```bash
python3 episodes-codex/_shared/puzzles-covers/render.py --out-dir work/puzzles-covers
```

入口先比对全部已发布puzzles集合、episodePart与当前完整题名，再生成三比例SVG/PNG/JPG。实际DOM检查文字边界、序号/题名/问句间距、4:3中心及底部安全区，所有图片按实际尺寸核对后写 `render-report.json`。逐份实际看图，确认题设、图义、文字层级与裁切。

验收通过后：

```bash
python3 episodes-codex/_shared/puzzles-covers/render.py --out-dir work/puzzles-covers --install
```

安装再次核对已验收报告与全部输入、图片完整SHA。制作目录安装PNG/JPG，站点目录安装JPG；两处均有竖版副本及 `cover-style.json`。原视频冻结清单不改写。

新增题按可靠的发布元数据扩展catalog和题图。赛马区分总25匹与单场最多5匹；过桥保留手电和人数约束；容器符号不作为按高度读水量的刻度；三门问题保留主持人知道奖品、必开未选空门的条件，不无条件套概率；鸡蛋的后续探测须在前次未碎的前提下继续。
