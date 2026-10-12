# EP.03 DNS 素材（gen_assets.py 生成，无文字，配色同第二期）
| 文件 | 用途 | 可动画的 id |
|---|---|---|
| phonebook.svg | 电话簿（phonebook-2）：左页青色“名字”行、右页橙色“号码”行 | pageL, pageR, cover, spine |
| notebook.svg | 小本子（cache、ttl-3、recap-1） | cover, page, bookmark, check（命中时画勾） |
| hosts-note.svg | hosts 便签（cache） | paper, fold, tape |
| hourglass.svg | 沙漏 = TTL（ttl-2），属性 drain 0→1：sand-top 缩小、sand-bottom 增高、stream 在 drain=1 时消失 | sand-top, sand-bottom, stream |
| globe.svg | 地球（iterative 根服务器图标、iterative-2 大图、recap-1） | earth |
| anycast-dots.svg | 叠在 globe 上的许多小亮点＝任播节点示意（不代表数量） | dots |
复用（Remotion 内已有组件）：浏览器/服务器统一卡片（无窗口圆点，标签 36px，时序图列标题 40px）、路线箭头 drawProgress、字幕层。
