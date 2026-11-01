# Daily temperatures 独立封面检查

结论：**BLOCK，仅缺声明海报；六张封面画面PASS。** covers.json声明poster.jpg、来源3x4、1080×1440，但该路径实际不存在，view_image也返回unable to locate image。独立审查没有修改源、图片或海报声明；补齐或统一声明后只需定向复核海报，不需要重做六张封面。

由本批LC42制作代理交叉独立审查，未参与本片创意。逐份实际打开16:9、4:3、3:4的PNG及JPG，共6张；标题、LC.739系列文字、右上水印与图表无裁切、无互相遮挡。图中第3/4/5/6/7天的温度依次35/31/30/32/36，从第3天到第7天才首次更暖，7−3=4，对应“等4天”；不把本次封面陈述核对扩大为重跑算法。

4:3两张实际图主体高亮像素范围均为x346..1080、y149..864，完整包含于x315..1125且y<918；测量用RGB最大值>100并排除y<110的既定右上水印区，结合实际打开图像人工代理观察。水印按声明位于内容区外，未压标题或图表。其余比例关键文字与5个日期/温度同样完整。

冻结清单source-sha256.json共145项，逐文件完整SHA-256只读核对全部匹配；清单本身SHA：`edfb304fb8a2a309e6e36fe3a35d71df36912f877aece9b7b72f5476a5a7ef21`。未再次检查声源、算法、旧媒体，也未重渲或TTS。详细145身份记录见qa-covers.json。

| 文件 | 实际尺寸 | 完整SHA-256 |
| --- | --- | --- |
| cover-16x9.png | 1920×1080 | `1df2f9e1c91ea49f022ebc408f745b38a534672d455ac9423fef01619c87797a` |
| cover-16x9.jpg | 1920×1080 | `93a4d8be2a855b8dd3eaee04ddff90f0896a39245d10571a83d77ea4e5283947` |
| cover-4x3.png | 1440×1080 | `034697cd70eec43092751f07e6f51af036af29321a5826066c33bfa9e126d926` |
| cover-4x3.jpg | 1440×1080 | `25fa5eff2c622e396aad90bf7ae00373cce2edba717b15df1226148d21073fd0` |
| cover-3x4.png | 1080×1440 | `22eb4a12befe149ad70ea367ee79958d663fd1c59170b819c6763aa994fc9920` |
| cover-3x4.jpg | 1080×1440 | `3d3856cdee62a94700ee1a195c8329e2e289bfafe6f8150b97c38e1561bf7d54` |
| poster.jpg（声明） | 1080×1440（声明） | 缺失，无文件SHA |

相关输入完整SHA：

- `covers.json`: `26ce9fa91e844721f7a7f7512eb3140eb12e1a99ce2c99788b227976c340ce0a`
- `remotion/src/Cover.tsx`: `31bb148425d50ae93fcbb1fcd4a34d46bd820b4d70f17378dbe702e7abcf92b6`
- `remotion/src/data.ts`: `c3fdcb4a745916e19ead3b9bf47e8d6305bd9ff427cab9b54769f9771c81a33c`
- `research/trace.json`: `24899e883350b5dc22c5abde8a541118285e9790459d57067cdc0d2bfbaf1c9f`
- `remotion/scripts/covers.mjs`: `67b38f7afeb93e960b1ec46271f99278cc8072475bbb60da8658b6ad23b2eafa`

边界：只审实际静态封面及其来源身份；声明海报尚未能实际查看，不声称成片、动态、ASR、全听、站点或用户观看通过。
