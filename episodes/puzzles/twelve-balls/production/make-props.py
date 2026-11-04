#!/usr/bin/env python3
"""Generate P06 producer notes from measured inputs before encoding."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
assert not(D/'video.mp4').exists(),'Preserve encoded production notes'
read=lambda n:json.loads((D/n).read_text())
sha=lambda n:hashlib.sha256((D/n).read_bytes()).hexdigest()
b=read('storyboard.json');w=read('words.json');model=read('model-data.json')
assert not b['meta'].get('provisionalTiming') and not b['meta'].get('pendingAudio')
shots=[s for sc in b['scenes']for s in sc['shots']]
lines=['# EP.56 twelve-balls · 根据剩余候选安排下一称','','本期新制作，无上一冻结版。沿用紫色puzzles Frame/theme与球号，全部比较、候选、正常球来源由本期模型和实际时序驱动。','','## 输入身份','']
for name in ['storyboard.json','covers.json','script.md','voice.wav','words.json','model-data.json','references.json']+[str(p.relative_to(D))for p in sorted((D/'remotion/src').glob('*.ts*'))]:
 lines.append(f'- {name}: {sha(name)}')
lines+=['',f'实测正文{w["durationFrames"]}帧，{len(shots)}镜，1920×1080、30fps。下表绝对区间右端不含；局部帧从本镜0算。声学句界不代表逐字ASR。','','## canvas区间','','| 镜 | id | from | until | 帧数 |','|---|---|---:|---:|---:|']
for s in shots:lines.append(f'| {s["scriptShot"]} | {s["id"]} | {s["from"]} | {s["from"]+s["durationInFrames"]} | {s["durationInFrames"]} |')
lines+=['','所有镜为canvas，无浏览器或DevTools。比较区是题目左右编号球组，不做拟真仪器。12个实体球保持同号、同初始外观；候选轻／重标签是当前可能性，不是提前公开的真值。','','## 状态与动作','',
'首称1234:5678三路各8候选；先预览再实际首左重。只有该结果之后9—12正常。构造第二称时，盘外留4重／7轻／8轻；左125、右36尚不同数，不能提交比较；右补已推知正常9才成为合法3对3。第二称三路候选L3／R2／B3。',
'主例6轻：第2称左重后仅1重／2重／6轻，第三1:2平衡推出6轻。各次结果提交才增加已称次数，构造预测不算已称。',
'09／10从首左重分叉恢复另一个第二结果；11首右重整体翻轻重及左右结果、物理分组和球号不换，以6重RRB作另输入对照。12恢复首平衡后1—8正常、9—12未知，第二9,10,11:1,2,3；13二平衡12:1判轻重；14二不平衡先确定方向，再9:10，以另输入9轻BRR演示。各支都从对应前提恢复，不混作主例第四称。',
'实际动作边界读取storyboard.voice的localStart/localEnd，句内视觉分段不是逐词ASR；具体属性与位置见本期Main和配套模型源码。默认字幕和hideSubtitles/auditLayout预演分别复核。','','## 全树与正常参照','']
for n in model['nodes']:lines.append(f'- 前缀{n["prefix"]or"起点"}：{n["left"]} vs {n["right"]}；已知正常{n["knownNormal"]}；显式正常参照{n["normalReferences"]}。')
lines+=['','BBB／LRR／RLL不可达；两次最多9叶不足24，三次27容量不自动证明存在性；构造24条路径与符号消去证明见研究及模型。','','## 封面与附录','',
'三比例实际spec／sourceSHA／几何／图审见covers.json、cover-style.json及qa/covers-review。旧八期文件保护结果另留本期QA，不重写旧冻结。',
f'正文收束后默认附150帧title-author静态资料页，计划总帧{w["durationFrames"]+150}；两项完整原题与署名不截断，R1五作者不缩成et al.，不显示日期、URL、摘录或暂停提示。实际最终区间与SHA由reference-appendix/render-result记录。',
'本文说明输入与画法；实际预检、成片、引用和线上结果另留QA，不在编码前预记通过。','']
(D/'knoll-props.md').write_text('\n'.join(lines))
