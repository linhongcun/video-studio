# D03适配器模式：站点交付检查

执行者：Codex adapter site agent。版本v0.62.0，实际检查时间2026-10-25T03:19:51.801Z；构建基线bfc3f8fed45dc71d7ef96bdfa420299e0af15776。

根正式媒体放行后接入14份同字节发布文件及新meta，包括当前source-sha256/render-result/mix-report，未复制制作WAV、PNG或源码。D01/D02原元数据、文章、分镜、视频和海报在接入及检查后完整SHA不变；两期首发身份仍为v0.52.0/v0.58.0。新D03为EP31、顺序3、首发v0.62.0/2026-10-25。

当前稳定树完成一次最终build、一次当前历史路径回归、1440浅色与390深色两个浏览器用例。四章共8次实际seek及短静音播放通过，最大误差约0.000000667秒。24句字幕每句文字和全部起止时间与冻结分镜一致；VTT完整SHA b0433f6c8f787c9c5e3384ebc94d44baa4da92254e8171dc851bd4b9a7fc748b。媒体和海报在制作/发布/构建/HTTP四处完整SHA一致。

5271帧、175.7秒，Java卡5121帧起150帧。卡区0.1/2.5/4.8秒均完整加载24cue、mode=showing且activeCues=0；真实解码后可暂停并导出1920×1080帧。页面截图恢复原生字幕默认disabled，没有用disabled空轨冒充卡区检查。

正文#java和完整AdapterDemo.java链接可用；两张SVG在两视口的computed字号/锚点与全部文字bbox通过，页面无水平溢出。D01→D02→D03目录、D02前后课、首页/系列/资料库/RSS通过，当前38个发布页面保留，已撤下Agent输出与空系列未恢复。

实际打开8张图：两SVG各桌面/窄屏、Java原始解码卡、桌面/窄屏播放器和窄屏Java正文。文字与角色清楚、没有截断；查看范围与SHA见qa-site-visual-review.json。未声称全片听辨、ASR、用户认可或学习实验。

本机build拉取GitHub Releases失败并正常降级外链，未将其记成正式Release条目已通过。根发布Release并完成Pages后，运行site-verify-online.py核验11个canonical普通GET、完整视频流SHA与真实版本条目。
