# P05二分开头修订声音交付

只改03／04四句，其余20句保留原处理后PCM和句WAV原字节。当前音轨SHA为`012e92bda809c774e80917c5502b3e58c5d565cb83e77e18f712d2910b57ff0f`，5569帧、8,910,400样本、185.6333秒。voice/build.json、sents.json、picks.json已按新稿就绪；本工序不调用整片assemble、freeze或render，由root接手。

## 实际处理及来源

- 先核对双审放行的五稿完整SHA。仅四条新sid进入正常冰糖共享gen，全部正文和标点保持原文；候选增加的“好。”仅用于共享裁尾。无speed或后期变速。
- 新03两句为03-binary-limit-1/2；04仍为04-late-break-cost-1/2，使用独立revision命名，没有复用或覆盖旧04的a候选。
- 新候选共7份：4A、2B、1C。最终03首句revisionC、03第二句revisionA、04第一句revisionA、04第二句revisionB。所有raw、48kHz WAV、实际请求、风格jobs及原始文件时间均在持久mini内，顶层voice/takes另有实体副本供标准冻结器使用。
- 原03首句A／B raw低声间隔0.58／0.67秒，改选同文C；原04末句A为0.73秒，改选同文B。原A共享build中两句为0.55／0.72秒，失败候选与build／gzip日志均保留。
- 所选B末句raw低声间隔仍0.53秒，原始warning原样保留；实际选定四句共享处理后为0.39／0.21／0.32／0.45秒，inner_dropouts为空。没有降低0.5秒诊断线或预写语义听辨。7份请求正文与对应sents一致，raw到48kHz转换逐样本精确一致。

## 仅新块共享build，原20句不再经过DSP

持久mini在voice/binary-mini，参数为lead=1/30秒、句内0.45秒、镜间0.8秒、tail=0.8秒，其他响度／峰值参数沿用本期。共享build产出1234帧，先核对第一帧PCM全零再移除，得到1233帧新块。

薄包装build_binary_voice.py只按整帧读取、拼接PCM和偏移metadata，实际TTS、裁尾、归一化、限幅及起音仍由共享实现负责。旧区间为半开[755,1676)，共921帧；新块为[755,1988)，共1233帧，delta=+312帧（10.4秒）。前两镜755帧完整不动，旧05–12全部后缀统一+312帧，镜内相对时序与声音速度保持。没有对拼接后的整轨归一化、限幅、淡化或变速。

原完整WAV已按固定SHA实体保存到revisions/binary-opening/baseline/voice.wav，原build／sents／picks／words／storyboard等摘要与根的不可变baseline manifest核对。原20份所选take文件还逐项匹配原133项冻结清单；原29份候选不覆盖。旧input-provenance.json及script-narration-sha256.json保持原字节和原生成时间，当前四句来源及当前稿摘要另存binary-input-provenance.json、binary-narration-sha256.json，没有把原20句追认为新生成。

## 自检结果

`python3 episodes-codex/egg-drop/build_binary_voice.py --verify`只读核对完整WAV等于「原前缀＋共享新块＋原后缀」；20个旧句PCM、20个旧句WAV文件、前后两大PCM区均逐字节相同。全部24句按当前sents顺序和实际take建立metadata，原05–12样本／帧窗只加统一整数312帧。

全轨ebur128实测−16.1LUFS、真峰值−2.1dB，邻句响度差最大0.3LU，拼接处最大逐样本跳变约0.001221。末尾仍为原97,367零样本／2.0284792秒。源WAV不为调整0.1LU重做归一化；最终成片由共享混音处理响度。

`build_binary_voice.py`默认只重建持久mini再拼接，可复现当前WAV；`--compose-only`只消费已检查的新块，`--verify`不写文件。原始失败候选、记录和旧成片来源不改写。详细20句前后窗口与PCM完整SHA在binary-opening-composition.json，测量在binary-audio-inputs.json，候选在binary-mini/voice/qa-candidates.json，实际冻结依赖清单在binary-dependencies.json。不要对混合新旧generation目录直接运行旧版全目录candidate审计；新mini审计入口为binary-mini/audit.py。

## 能力与后续

ASRPerformed=false、semanticListeningPerformed=false、fullHumanListeningPerformed=false。检查证明的是输入、源文件、实际PCM和时序来源，不证明五十／二十五／零到二十四或多音字实际逐字发音均正确。

root负责最终共享assemble、whole place、句首／0cue／sentence检查、placeholder与public实体副本同步，以及新冻结。冻结需纳入薄wrapper、持久mini的实际输入与take、原完整WAV及metadata；binary-dependencies.json列出19项明确依赖及42个持久mini文件。正式媒体稳定后再做全轨／24句AAC与双声道已知BGM模型检查，本交付不提前认可旧编码成片。
