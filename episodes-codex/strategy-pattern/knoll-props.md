# 制作说明：策略模式新手版

本轮为13镜26句、四章的完整教学重排，全新自然配音和动画。实际时长由共享句级装配输出，不变速压缩。当前布局和因果顺序见visual-direction.md；旧16镜/三镜拼接报告保留在revisions/v0.54.1，仅作历史。

## 生产输入

使用episodes/_shared/voice的prep/gen/build及共享assemble_sentence_episode、place_v2、label_onset_strict和check_sentence_episode，不另写配音整轨或起音算法。选定新take后，voice.wav与remotion/public/audio/voice.wav必须为同一实体内容；storyboard/words/captions均基于真实句级时序。

本轮只有会员/活动两个函数，输入10000分（100元），输出9000/8000分（90/80元）。参数与函数身份由demo/beginner-evidence.json的实际执行观察支撑。核心逻辑摘录显式标注省略校验，完整现有demo保留在图文。

## 视觉与品牌

页身引用共享深色主题，中文Noto Sans CJK SC、代码Noto Sans Mono，右上IT小村、片尾IT小村·原创。规则身份与金额结果始终区分；参数解释期间停止金额动画。章节id保留why/delegate/change/boundary及旧正文URL。首术语策略模式位于04第一句，按共享声学起音显示至少63帧。

封面标题和同一100元/规则可换流程稳定的内容仍适用，沿用已上线三尺寸原件及完整SHA；本轮不重新生成不同的封面。正文代码最多两处布局，不含额外代码附录。无比喻、假窗、装饰进度条或密集类图。

## 预检与编码

本期remotion下运行npx tsc --noEmit；用scripts/qa.mjs生成全13镜真实时序图与06–10关键连续无字幕片。实际检查composition.props的hideSubtitles:true/showSubtitles:false、源SHA、COPYFIT与中间动作，不能只看命令参数。

全体生产输入停写、编辑和动态检查闭合后冻结，正式渲染使用TMPDIR=/workspace/strategy-tmp与/tmp/video-studio-render.lock。执行npm run render调用既有Remotion编码和共享Wallpaper混音，目标-16 LUFS。冻结后若生产源变化，停止排队/编码并重新检查和冻结。

正式MP4完成共享check_encoded_episode、完整解码、真实帧/过渡及字幕核对，再复制同一媒体接入站点。发布按持续授权合并、Release后部署，普通canonical GET流式完整哈希核对视频/海报/VTT和章节/系列/RSS/更新日志，随后completed关闭#163。执行范围和ASR/听辨能力限制如实记录。
