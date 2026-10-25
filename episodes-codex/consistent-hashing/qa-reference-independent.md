# EA01：片尾参考资料独立复核

结果：**PASS（限本次追加范围）**。可继续网站交付。

- 复核者：hash_final_media；时间：2026-10-25T22:46:13.578034+08:00
- 新成片6031帧 / 30fps，画面201.033333秒，10,338,139字节。
- 新媒体SHA256：`855461d25d2f05407676541e7b3ef498a6067eeac871d7d94be68e11be1ba9da`。
- 卡片5881–6030，共150帧/5秒，1页，列R1/R2并显示暂停阅读提示。

## 保持证明与正文复用

原5881帧正文SHA256 `5a54624a31f293fb2b68161ed9875a184a992fc322996a5a010d3fca61d3242e`；已独立核对不可变body.mp4与Git `c80faaefa7750dd8facebc0dc65658ca56400a4d:episodes/consistent-hashing/video.mp4` 对象。
在独立QA目录调用共享追加工具verify成功：全部5881张正文解码像素及PTS相同，全部9191个AAC包内容/PTS相同，解码PCM相同；6031帧视频时间轴连续。原146项正文输入保持不变。

因此复用[原正式成片独立复核](qa-video-independent.md)中实际查看25张正文图的结论。没有将旧5881帧检查器套用6031帧，也未改原QA报告或冻结清单。

## 实际新帧查看

- 帧5880，body last frame：`global-05880.png`，SHA256 `11a324df25701308956847bafb5382ca702e97c47b10b41c79c5954b43332f0d`。
- 帧5881，reference card first frame：`global-05881.png`，SHA256 `d67c78c71d38fb6872d26635a5038afe7e39f83f161795343de6b10f607ebc31`。
- 帧5900，reference card sample：`global-05900.png`，SHA256 `b32e0be051a0e58ac7996fa3cd3a177336f98c5ee4641660febcc150d7ee9111`。
- 帧5955，reference card sample：`global-05955.png`，SHA256 `b414a3b88a400d953901709386953ccc80ba8038a15b327847c3bd1ec4c428f3`。
- 帧6030，reference card final frame：`global-06030.png`，SHA256 `d469e055e2304c3398c5ac83e3462ebed8eb7ee3176d0af29a4639fc13334d6d`。

## 内容与版式

- 5880仍为正确正文收束；5881直接进入参考资料卡，没有覆盖原尾句或将卡夹入正文。
- 参考资料标题、1/1页码、“可暂停阅读”和“完整链接见配套图文”提示清楚，背景、机构、版本与文字未裁切或相互覆盖。
- R1显示NGINX、持续维护文档、核验2026-10-25，短标题和支持论点对应研究R1；不将访问日期误写成官方发布时间。
- R2显示Apache Cassandra、5.0文档、核验2026-10-25；Token Ring/vnodes短标题及顺时针定位/同物理节点多位置支持关系准确。
- 5900、5955、6030卡片内容与首帧保持可读，实际末帧仍为完整参考资料，无黑帧或恢复正文字幕。
- references.json/references.md保存完整原题名、URL和论点映射；既有article.mdx参考资料含两条可点击完整链接，R3仅用于文章边界故不在视频卡中冒充主线依据。

未发现需返工问题。独立数值证明输出在`remotion/out/reference-independent/reference-appendix-media-check.json`；保留根原receipt/media-check不覆盖。

## 能力边界

- 本轮实际查看5张新MP4编码帧，只针对追加边界及参考卡首/中/末，正文25图结论通过全前缀保持证明复用；没有声称重新全片实时观看。
- 没有重新配音、混音、渲染正文或重写146项正文冻结清单。
- 未重新联网读取官方正文，本轮来源映射核对沿用2026-10-25的research.md真实读取记录，不新增访问日期。
- 网站发布与线上完整SHA核验仍由根任务另行完成。
