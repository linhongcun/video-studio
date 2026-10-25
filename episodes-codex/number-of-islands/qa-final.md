# LC.200边界反馈修订成片复核

当前制作侧与独立复核通过；本地网页与发布结果以docs/number-of-islands-boundaries实际记录为准。原v66报告保存在revisions/boundary-before/qa-final.md，不用新结果覆盖用户反馈前的身份与范围。

用户指出首格左/上为何跳过未说明，本轮仅改06第二句与边界可见动画。151项冻结；其他27句take/程序/trace/封面保持，13镜局部时序全等，整体仅+62帧，末卡仍150帧。正式新06为487帧，其他画面按splice-plan复用，整轨新配音与BGM重新混音；splice-result记录实际输入/输出全文SHA。

新MP4 SHA-256 67bf3a409bae9ab78e845cdf21b456953958d92ef5f2d671676e7729bdb248c6，8787142字节，5845帧、1080p30、AAC48kHz，194.837秒；完整解码、实测−16.0LUFS/−3.9dBTP通过。真实06预检26点、最终实际20点确认四向/两次越界/两个拼接处；95唯一帧/96比较maxMAE3.266261<8。全部PTS及5695..5844末150帧/return实际复核通过。

当前证据为qa-boundary-preflight、qa-boundary-audio、qa-boundary-video、qa-boundary-media及qa-media-samples；旧通用报告仍保留其v66具体SHA与适用范围。本轮算法与来源验证按旧不变SHA复用，未重跑65k案例。未声称ASR、全片人工听辨或新的用户认可。
