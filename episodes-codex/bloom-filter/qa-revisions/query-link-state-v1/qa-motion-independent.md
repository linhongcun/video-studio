# 布隆过滤器真实动态独立复核

结论：**needs-fix，阻断正式编码**。实际查看20张真实计时PNG，覆盖全部13镜；对3段已完成、隐藏字幕的真实MP4按事件用ffmpeg解码并实看42帧，组成21组前后相邻对照。未发现除此问题组外的必须修改项。

## 必须修改：等待与明确拒绝混用叉号

- 08镜local230–341：067三个位置已读到1，状态为可能存在，但放行前仍有灰色叉；local342才切为查库箭头。见pair-11-probe067-position15与pair-12-067-forward-to-catalog。
- 12镜local403–422：位图和目录101/205已恢复，灰色拒绝叉仍在。见pair-third-03-restore-bits-and-catalog。
- 13镜local292–441：同步期间明确暂不拦截，路径却仍画红叉。见pair-third-05-start-maintenance与pair-third-06-repair-write-bit2。

上述是同一个QueryFooter状态表达问题：未执行/等待、写入、恢复不能表现为明确拦截。需单独表达blocked状态，仅真正读0拒绝或明确错误拦截反例保留叉号。文字、音轨、位值和目录状态无需因本问题更改。已通知root及源码owner。

## 其余实际观察

位值和下标分开，三路位置固定；写入抵达后才改位，共享3号仍1。001实际先12=1再2=0停，第三路保持未探测；067最终回库确认没有记录。09来源层明确用于解释，随后退去，位数组不保存owner。11另状态容量示意变密并恢复五位基线。12错误清3确实误伤仍存在的205，结束同时恢复位图与目录。13漏同步危险、补写2号0→1及最终放行确认001均清楚。

## 身份与能力范围

旧最终samples.json已归档至qa-motion-independent-evidence/preflight-manifest-reviewed-original.json；20张已看PNG另存original-pngs，3clip完整SHA、所有实际解码帧/前后对照图、18项来源SHA与观察清单见JSON。状态结论只绑定这份旧manifest，不把后续修后源码或媒体追认为本轮已看。没有全片实时观看、听辨或ASR；没有检查成片、资料附录和网站。
