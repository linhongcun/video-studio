# 音频独立预检：每日温度栈入门修订

结论：**PASS**，无阻塞。仅绑定最终源voice SHA256 `2e74f1cb78ef53d53879298261a5414f4517fc02028cc85847accc2d88ef9c43`：48kHz、单声道16位、8,515,200样本、5322帧／177.4秒，public副本逐字节相同。当前165项冻结全部匹配，清单SHA256 `55d6446ec6919227ce5e327633fe18a42af9eec8fb198c275f37917b357f94a7`。

- 原28句在新32句中各复用一次，text/tts、旧picks及84个所选raw/WAV/txt文件同时匹配旧冻结和新stack-primer副本；仅4句为新旁白。用共享prep解析逻辑只读复核稿件→句表→选take→build映射。
- 最终32句均实际通过一次共享load/cut及build保留端点核验：尾切舍入值、保留样本数全匹配；32个句音轨PCM与最终整轨对应切片全等。审计首遍在全部cut/PCM与局部时序核验之后遇到复用段统计误期望（12正文段之外另列了代码卡），修正统计后仅继续检查与写报告，未重复32次cut；执行范围和原脚本身份见JSON。
- 起始14400样本、31处句间隙和尾部补齐均为零PCM。普通镜内间隙16800样本、镜间33600样本；05-monotone后额外159样本／3.3125ms，使该处间隙33759样本，真实为静默。原28句start/end样本仅按0或1,254,400样本平移，14个原镜的局部字幕、cue、持续帧数保持；12个正文复用段及单列150帧卡均无±1帧放宽。
- 当前整轨wholeplace绑定2e74f1cb／58c57a02，0offset、violations为空。共享起音报告为3个术语cue全部通过：新“栈”−2.77帧、新“单调”−2.18帧、复用“单调栈”−2.11帧；4句新增旁白不等于4个术语起音测量。有效证据是 `voice/place-stack-primer.json` 与 `label-onset-stack-primer.txt`，旧同名通用报告仍属于历史身份。
- 源轨实际EBU128测量为−16.0 LUFS／−2.2 dBTP，0个满幅PCM削波；build记录无内部dropout，最大相邻句响度差0.3 LU。程序卡5172..5321完整150帧／5秒，240000个源voice样本全零，正文字幕最后5171帧、最后发言边界5126.59625帧。这里的零PCM指源voice，不能预先声称最终AAC含BGM混音静音。

初次fdbd5c78声轨是未编码中间装配，相关build/SB/params/manifest保存在 `revisions/stack-primer-phase-alignment/`；本报告不将其当作最终身份。旧4538帧声音及媒体QA保留在 `revisions/stack-primer-before/`。本轮没有重跑算法大穷举，没有ASR、逐句人耳全听或新成片媒体通过声明；原程序/trace核心7项与封面/代码卡字节保留证据可复用，research.md仅追加本轮说明。完整数值与SHA见JSON。

## 190项冻结与默认资料卡入口的范围补充

音频范围复用 **PASS**：原165清单精确保存在 `revisions/stack-primer-top-marker-before/source-sha256.json`；现190清单SHA256 `e54764b15f88c50219a9cd4275f5b64339aa4539fea909a2b5bc57fb7910235b` 全项匹配，新增25、删除0、既有变更6项（文章、package、StackPrimer、freeze、QA脚本与正文render包装）。其中StackPrimer只修正运动中栈顶标记的指向，其余接入资料卡默认入口、实际clip/旧基线和共享实现。

原20个直接证据中19个字节不变，唯画面remix-plan重新绑定了视觉源及实际媒体依赖；其正文5322帧、voice.wav及所有tail调整为0保持。全部32句的96个raw/WAV/txt身份和7共享实现全保持，不再执行cut或声学预检。源voice、words、SB、params、起音及句文件与前述通过身份相同；有效证据映射在JSON的scopeRebindHistory／activeAudioSourceScope，顶层原始QA身份完整保留。

正文仍为5322帧，Python卡仍5172..5321。资料卡另从5322起150帧、最终5472帧；源voice与正文SB不延长，也不要求资料卡有新增音频包。本附录只批准音频范围复用，最终编码媒体及资料卡实际检查另见独立媒体QA。
