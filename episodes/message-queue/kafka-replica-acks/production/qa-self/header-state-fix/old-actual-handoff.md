# MQ15 作者停写交接

生产输入已停写，实际5460帧/182秒。精确SHA、局限及报告见[actual-handoff.json](actual-handoff.json)。Main的sceneTiming(s)/stateAt(s,f)导出真实句界阈值；[actual-state-timing.json](actual-state-timing.json)列每个阈值的首整数帧。模型39态、5来源与原始实测范围各自区分。

作者实际看107无字幕PNG（9接触表、4图位全尺寸）及34烧录字幕PNG（3接触表、2全尺寸），3连续短窗共1696帧/56.53秒完整video+AAC解码，71个每24n的连续解码时点逐张接触表实看。短窗实际无字幕，inputProps与resolvedcomposition.props均关闭；有原声，未冒称全片逐字听辨。sourceMain/board/voice身份始终相同，可由独立复核员亲自解码/看图后有界复用。

四图位1621/3281/3732/4964，seconds=frame/30；文章seekTo9位小数对应整数n。实际JPEG尚未生成，正式成片后root抽取再独立逐张验。

重点：B2物理1与Leader已知0；下一Fetch1抵达后才已知1。B3同链后HW1，但回执在途仍pending，抵达网站才成功。ISR3不能只等2；稳定ISR2/1各自空日志重置。故障时原主离线字节保留，不画数据副本投票。末镜原创水印与正文边界清楚。

独立QA请freshbundle，读取data-model-state和各replica物理/已知/记录属性，查关键相邻帧、四图位与动态；不要把作者或Broker实验通过转记独立动态通过。生产源/board/voice不由本作者继续改，若有阻塞先停ownedworker再保存失败源图、定向修复。

文章唯一MDX格式修复：原1<2加行内代码标记；根实际parser失败、原文章/初版handoff均保留在article-mdx-fix。现已用站点真实parseArticle复核8引用/4图语法及refs5sources通过，articleSHA867a1c09…cd120。正文四身份不变，无须重渲不导入MDX的正文预演。
