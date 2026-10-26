# 布隆过滤器最终检查

本地制作、实际成片、网站与正式线上验收均已完成；PR#340合并、v0.71.0 Release、Release后Pages成功。10项canonical内容身份与两视口正式播放检查通过，issue#300已completed关闭。实际证据见release.md及publication-evidence.json。

- **媒体身份：**5891帧/196.3666667秒/1920×1080/30fps，SHA-256 `5b95e463dc5d95e7666de2c6fdf1c4c482bcdb6ca47faec835b040b917307143`，10,312,433字节；正文5741帧，资料150帧。
- **资料与教学：**两项片尾原题/连续原文及四份官方固定正文已独立重取核验；13镜26句叙事/前置复核，模型140668项断言通过。见qa-source-independent、qa-script-independent、qa-model。
- **动态：**最终283真实计时PNG/DOM、3段无字幕连续预演通过，实际位值/目录23996项及链接几何/语义2926项独立核验通过。修后另实看4张新PNG及20张新clip解码帧；原检查的复用范围与两类失败历史独立保留，见qa-motion-independent及qa-revisions。
- **声音：**31候选中选26句，真实来源/裁尾/整轨重放通过；最终AAC与混音源对应，逐句漂移0，实测−16.02 LUFS/−3.67 dBTP。body/final双声道PCM一致，704个尾填充样本另记；未执行ASR、语义或全片人工听辨。见qa-voice及qa-encoded-voice-content。
- **实际MP4：**完整解码0错误、5891帧PTS连续、150冻结输入逐项匹配，正文与最终8972 AAC包载荷/时间一致。独立实看38张实际编码图、root另看4张；未称实时全片观看。资料首中末与字幕边界清楚，见qa-video-independent/qa-video-root-view。
- **网站：**12文件复制与最终媒体全文SHA一致；125页/46索引、47日期和17参考资料通过、30历史暂缓。两视口86项检查、26条VTT精确文字/毫秒、8次章节点击、参考卡首边界/中末/全屏、两SVG/Python及入口通过，保留902个既有发布文件。首轮浏览器中点采帧定位问题只修QA工具，源媒体未变；失败/诊断均保留。见qa-site-browser、qa-site-code-scroll及delivery-copy。

本次仅GitHub仓库与Pages，无外部平台投稿，也没有本片用户观看结论。150项编码输入清单SHA为 `f7f978e13b703c7cc57e9182615e1448f8dc8c9269424c0394ff4ae81a0ff7f9`，检查结果不用于改写冻结或追认未使用的输入。
