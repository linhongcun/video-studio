# EP.01 当前技术细节稿：动态复核

当前5406帧、17镜。独立实际预检见[本轮报告](qa-depth-motion-independent.md)及对应JSON；原12镜检查已留在revisions/technical-depth-v2/qa-motion.md，不用于追认当前媒体。

本轮以最终Scenes fc8bccf4…72c3为源，三段连续无字幕预演覆盖三次握手、TLS到HTTP交换、资源获取到解析绘制与版本边界。07/16标签只改入场条件，运动不变范围用精确差异证明复用，并实际复看最终cue相邻图。03的canvas描述修正不改声音或像素，证据见voice/depth-visual-consistency-proof.json。

预检实际拦截并修正：13图片已返回却在15重新加载、开放SVG路径默认填充形成黑楔、DOM规则线穿字、07/16术语标签晚于元数据cue。实际失败及修后证据保留在revisions/technical-depth-v2/；不把最初预演当最终源。

以上是动态表达与时序检查，正式MP4另验，不声称正常速率全片人工播放、逐字ASR或听辨，也不代表用户已观看认可本次修改。
