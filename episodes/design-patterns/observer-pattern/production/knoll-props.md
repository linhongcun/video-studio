# D02 模式主线修订制作说明

基线d515f0d4，10镜20句，正文4292帧/143.07秒；仅09镜13.53秒MQ应用，余下模式129.53秒。Java150帧，总4442帧/148.07秒。10句旧原理take复用、10句pattern新配，来源哈希与映射见voice/observer-first-reuse.json，送模MQ替换M Q，字幕不改。

10镜的因果与状态要求见visual-direction.md。重点预检02动机/03结构、04先明确回看再登记、05先状态与收通知后响应、06关闭取消→07仅记录、09应用另示→10模式回收。Motion events与实际段长/句首一致，视觉与字幕不自动从术语名推断内部词时间。

真实有声正文快照为revisions/observer-first/voiced-body，共享Java追加器用--body-dir显式指定，不读取旧MQ版正文。先从仓根用本期freeze.py冻结并--verify核对，确认负责人停写和独立预检闭合，再从remotion用npm run render；短TMPDIR与/tmp/video-studio-render.lock继续使用。正式媒体另作全解码、响度、实际帧/字幕与纯卡边界复核。

配音、角色动画、封面与配套文章一起反映观察者主体。网站只复制本轮通过检查的发布文件，保留旧身份、只刷新内容修改时间。GitHub主干/Release/Pages按既有持续授权执行，外部平台未新发；检查能力限制如实记录，不以旧技术成功抵消用户对v0.68.4主题偏移的反馈。
