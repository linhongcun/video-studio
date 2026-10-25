# 观察者模式站点检查

执行者：Codex observer_site agent。首发身份v0.58.0；4979帧，约2分46秒。

最终媒体接入后，在最新协作主干上完成生产构建与历史学习路径回归，36个发布页面保留。1440浅色、390深色两个视口实际点击全部5章，共10次精确seek并短暂静音播放；最大seek误差约0.000000667秒。24句字幕文字及全部起止时间与冻结分镜对应，浏览器载入全部cue；视频、海报的制作/发布/构建/HTTP完整SHA一致。D01↔D02、目录、系列、资料库、首页与RSS检查通过。

实际看图发现MDX内SVG的camelCase属性未生效。原冻结文章不改，只生成article-site.mdx派生稿：24处fontSize、1处textAnchor、3处strokeWidth改为原生属性。完整转换和哈希见site-article-derivation.json，接入清单按sourceFile核对。随后只重做一次构建和两图×两视口的真实DOM/字体/居中/线宽/bbox检查，复用未改变的媒体、章节和字幕验收。

首轮图形QA曾把glyph墨迹bbox的中心当排版锚点，390px下约0.105px的字形栅格差导致断言失败；诊断后改验原生x与computed text-anchor，并继续检查所有字形bbox不出界。未为通过该断言改文章或媒体，失败证据保留。

实际打开并检查4张修后SVG图、2张最终播放器图；文字可读、共同约定居中、取消后历史摘要清楚，默认原生字幕关闭。早先捕到的buffering状态图保留，未用来证明视觉通过。最终6张查看范围及SHA见site-visual-review.json。119冻结输入逐项核对均未变。

本地构建拉取GitHub Releases时失败并降级外链，未将其记作Release验证；生产部署后应由verify-online.py核验真实Release条目及完整线上媒体。未声称全片听辨、ASR、用户认可或初学者学习实验。
