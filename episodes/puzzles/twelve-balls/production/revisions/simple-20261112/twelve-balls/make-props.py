#!/usr/bin/env python3
"""Record the simplified revision measured inputs before encoding."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
assert not(D/'video.mp4').exists(),'Preserve encoded production notes; choose a new revision'
read=lambda n:json.loads((D/n).read_text())
sha=lambda n:hashlib.sha256((D/n).read_bytes()).hexdigest()
b=read('storyboard.json');w=read('words.json');config=read('episode-config.json')
assert not b['meta'].get('provisionalTiming') and not b['meta'].get('pendingAudio')
shots=[s for sc in b['scenes'] for s in sc['shots']]
lines=['# EP.56 twelve-balls · 趣味解题短片重构','','追踪issue #484；保留题面、编号及轻重目标，以当前script/plan确定实际讲解顺序。旧版本媒体、资料核验日期和冻结证据保持历史身份。','','## 实际输入身份','']
for name in ['storyboard.json','covers.json','script.md','voice.wav','words.json','references.json','input-provenance.json']+[str(p.relative_to(D)) for p in sorted((D/'remotion/src').glob('*.ts*'))]:
 lines.append(f'- {name}: {sha(name)}')
lines += ['',f'实测正文{w["durationFrames"]}帧，{len(shots)}镜，1920×1080、30fps。此为句级声学边界，无逐字ASR或全片语义听辨声明。','','## 实际镜头区间','','| 镜 | 画面类型 | from | until | 帧数 |','|---|---|---:|---:|---:|']
for s in shots:lines.append(f'| {s["id"]} | {s["visualType"]} | {s["from"]} | {s["from"]+s["durationInFrames"]} | {s["durationInFrames"]} |')
lines += ['','## 画面约束','','原题12球参与实际比较；未知轻重时不能把较重一侧全部认作异常候选。正常参照只能从已经观察的结果推得，未揭晓前不使用隐藏答案改变球外观。','每镜只突出当前比较及剩余嫌疑；分支切换回到对应前提，已结束实例不延续为第四称。具体动作以本轮Main.tsx、script.md和真实声音窗口为准。','抽象候选容量、完整决策表与称法构造留配套文章，视频不逐条搬演。','','## 封面与资料附录','','沿用上一修订的三比例封面JPG和poster，完整SHA及原始生成身份见input-provenance.coverReuse与cover-style.json，不重放已变化的共享封面目录。',f'正文后默认追加150帧原题/作者静态资料列表，计划总帧{w["durationFrames"]+150}；实际区间、编码与媒体身份以新附录回执和render-result.json为准。','正式编码前先完成来源、类型、实际画面和时序检查，全部写入负责人停写后冻结。实际检查结果另留QA，不由本文件预记通过。','']
(D/'knoll-props.md').write_text('\n'.join(lines))
