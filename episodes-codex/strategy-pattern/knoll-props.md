# 制作说明：策略模式设计思想版

当前11镜22句、四章，完整重排为语言无关的职责与协作，实际时长由自然配音和必要动作停留决定。旧v0.54.4语法版的报告与时序存于revisions/v0.54.4，媒体/音轨/工程由不可变tag恢复；不复用旧版已通过的思想结论。

## 内容与来源

按script/plan及visual-direction构图：稳定结算流程、独立定价策略、外侧选择，原价100元先会员90元，再重置选活动80元。共同业务约定允许不同实现替换，结算把变化的定价交给所选策略；图示对象和数据保持不同身份。无代码、语言标识、函数参数、分单位或密集类图。首术语策略模式在04第一句，以共享声学起音显示至少63帧。

共享实现仍用episodes/_shared/voice与episodes-codex/_shared的prep/gen/build/assemble/place/strict/check，不另写配音整轨、起音或混音算法。新take后缀idea，必要idea2；旧beginner/a/b/c保留。字幕逐字对应真实录音源文本，词兼容包络不冒充逐字识别。

## 预检、编码与复核

npx tsc检查后，用既有qa.mjs生成全11镜真实时序无字幕预演和关键03/06/07连续片及05/08状态图。报告记录最终props、源SHA、provisional:false和COPYFIT；人员实际查看关键中间态。共同流程与策略来回动作完整，尤其06结果返回后继续、07先重置再替换、08关系回收、09前提限定。

生产源停写、思想与动态预检闭合后冻结，再以短TMPDIR=/workspace/strategy-tmp和/tmp/video-studio-render.lock执行原npm run render；共享Wallpaper混音目标-16LUFS。三尺寸原封面短文案仍符合‘把变化的规则独立出来’，复用完整SHA相同原件，不重复制作。

最终执行冻结核对、shared check_encoded、完整解码/PTS、实际成片字幕与过程复核，再复制同一媒体接入网站。保留slug/四章ID/firstRelease，合并Release后部署并以canonical普通GET流式完整核对视频/海报/VTT及章目录/系列/RSS/更新日志；通过后completed关闭#163。能力限制如实记录，不将独立审读当作新手实验或用户认可。平台未新发。
