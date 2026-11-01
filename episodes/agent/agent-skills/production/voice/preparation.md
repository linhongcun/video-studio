# 配音准备

本期仅复用仓内`episodes/_shared/voice/prep.py`、`gen.py`、`build.py`，通过薄包装`../assemble.py`调用共享句级装配，再用共享铺轨与起音检查。未复制TTS、裁尾、起音或混音算法。

`params.json`保持正常语速，句内停顿0.4秒、镜间0.7秒、末尾停留1.5秒；最短镜头225帧仅作布局下限，实际按文稿与录音时长。真峰值参数用于共享整轨构建，不冒充成片测量。

文稿为`### N slug`及`旁白：`单行格式，每镜恰好两句完整旁白并以。？！结束；plan的每个cue位于所选句子的真实开头。导演确认最终稿后，已记录script/plan/pronunciation身份再准备sents与请求TTS。

最终选段为19个a、4个b、1个c，共24句，整轨5648帧。配音来源、声学复核、共享装配/铺轨/起音和能力边界见`substitutions.md`、`qa-audio-inputs.json`；不把句级包络称为逐字ASR，也不把来源核对冒充全片人工听辨。
