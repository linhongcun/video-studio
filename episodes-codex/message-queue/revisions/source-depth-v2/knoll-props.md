# MQ01 source-depth-v2制作说明

身份保留EP10 / message-queue / 原题与旧封面，批次#443。13镜26句，4章；最后参考资料title-author无旁白5秒，每页最多4项。正文依同源model.json及真实storyboard.json，禁止改字号/动作时在正式编码中继续写源。

正文入口remotion/src/index.ts→Root→Main。Main按cueFrames与voice.localEnd计算动作窗口：04编码/入缓冲/发送，05P0日志编号/追加，08Fetch携0及返回，09解码文本/客户端position1/poll交给应用/JSON字段卡，10应用调用，11另存业务完成，12页面查业务。媒体实际格式1920×1080/30fps H264/AAC48k；默认入口把Remotion full-range BT601像素转换为limited BT709，再混音、追加同色资料卡。

新takes来自共享MiMo脚本，24a/2b；源SHA与声音能力边界在voice/input-provenance.json、substitutions.md和独立QA。原两份风险a保留；不改共享cut阈值。词级ASR与全片人工语义听辨未执行，不预记通过。

文章图位按最终新声轨在编码前定稿，article-figure-plan.json用整数帧与秒数；最终MP4产生后root抽图。当前图文件未产生，不能写已验收。

本期只写独立revision，旧声源/冻结/旧媒体保持。源完成后由独立QA/root放行冻结与正式编码，本制作agent不调用freeze.py或默认render。freeze-inputs.json明确额外执行源/原始出处/图位；实际freeze交root。
