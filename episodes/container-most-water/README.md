# LC.11 · 题意先于解法

当前修订先介绍题目，再解释方法。前两镜用可视例子交代输入、选择与限制、目标和返回值；第03镜以后保留既有讲解，完整Python片尾仍5秒并提示暂停。对应原制作issue与历史发布见release.md；用户对旧主体的认可不能作为新开头观看结论。

当前6734帧/30fps（约3:44），44句字幕，四章精确时间来自storyboard。题意预检、实际成片、输入冻结/完整解码/音量和12采样保真通过，见qa-final.md及qa-problem-first-*.json/md。网页及v0.54.2实际完整媒体/字幕/章节和真实Release条目核验通过，见本轮报告、online-verification.json与release.md。

本次按package脚本render:opener只重渲前两镜，再用共享remix_opener.py复用已验收正文，最后使用共享mix_bgm；配音仍由共享voice/build生成。实际来源与命令在opener-remix-plan.json，最终媒体SHA在render-result.json。完整重建仍可用本期npm run render。

快速复用所需旧输入在ignored remotion/out/problem-first-baseline。若缓存不存在，按revisions/problem-first/baseline.json里的commit与videoPath/storyboardPath，用git show恢复video.mp4和storyboard.json并核对完整SHA；不能改清单认可其它旧媒体。前2镜范围须按真实新分镜更新，正文变动超过镜尾1帧时helper会拒绝复用。

本次不重复未改程序的穷举验证或全部旧页面矩阵；没有可用逐字ASR/全片人工听辨结论。历史说明、QA和上线结果保存在revisions/problem-first/before-*与Git历史。
