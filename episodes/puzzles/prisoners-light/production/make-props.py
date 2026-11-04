#!/usr/bin/env python3
"""Generate P10 production notes from its final measured inputs before encoding."""
from pathlib import Path
import hashlib
import json

D = Path(__file__).resolve().parent
assert not (D / 'video.mp4').exists(), 'Preserve encoded production notes'
read = lambda name: json.loads((D / name).read_text())
sha = lambda name: hashlib.sha256((D / name).read_bytes()).hexdigest()
b = read('storyboard.json')
w = read('words.json')
m = read('model-data.json')
assert not b['meta'].get('provisionalTiming') and not b['meta'].get('pendingAudio')
shots = [s for scene in b['scenes'] for s in scene['shots']]
assert len(shots) == 14 and w['durationFrames'] == 6056
lines = ['# EP.57 prisoners-light · 一次成功发送对应一个不同的人', '',
         '本期为新制作，保留当前趣味推理紫色Frame与字体。主例是0号计数员及1、2、3号发送者的12访教学序列，协议与人物可见信息由本期模型驱动。', '',
         '## 输入身份', '']
names = ['storyboard.json', 'covers.json', 'script.md', 'voice.wav', 'words.json',
         'model-data.json', 'references.json']
names += [str(p.relative_to(D)) for p in sorted((D / 'remotion/src').glob('*.ts*'))]
for name in names:
    lines.append(f'- {name}: {sha(name)}')
lines += ['', f'实测正文{w["durationFrames"]}帧，14镜28句，1920×1080、30fps。声学句界和视觉分段不代表逐字ASR。', '',
          '## 实测镜头区间', '', '| 镜 | id | from | until | 帧数 |',
          '|---|---|---:|---:|---:|']
for s in shots:
    lines.append(f'| {s["scriptShot"]} | {s["id"]} | {s["from"]} | {s["from"] + s["durationInFrames"]} | {s["durationInFrames"]} |')
lines += ['', '## 同一12访主例', '',
          '灯初始已知灭，状态保留；仅计数员关灯接收。发送者只在自己未成功发过且灯灭时开灯；遇亮不耗资格，成功发过后不再开灯。编号人物不复制成第二个实体，0号人物与灯态0通过中文标签区分。', '',
          '| 事件 | 当前访者 | 动作 | 灯：前→后 | 计数：前→后 |',
          '|---|---:|---|---|---|']
for step in m['mainExample']['steps']:
    before, after = step['before'], step['after']
    light = lambda value: '亮' if value else '灭'
    lines.append(f'| {step["id"]} | {step["actorId"]} | {step["action"]} | {light(before["light"])}→{light(after["light"])} | {before["count"]}→{after["count"]} |')
lines += ['',
          'e07全体实际上都已来过，不等于计数员已有充分证据；e12关灯、累计3份后才显示宣布。观察→实际开关→本人记忆或计数→提交稳定态的动作分别推进；稳定态保留真实declared，确认标题另由显示门控制，不篡改权威模型状态。',
          '全体已发标记与pendingSenderForAudit只属于教学／审计视角。访者只能知道自己角色、本人发送记忆及当前灯；计数员只保留累计份数，不能读取他人记忆或识别发送者。', '',
          '## 推广与保证', '',
          '推广到100人时，发送者99人、计数员1人，目标99份；本人在场不需要第100份。每人最多贡献一次、每次亮灯至多接收一次，已发数＝已收数＋当前待收信号数。',
          '安全性与活性分开：公平每人无限次保证亮灯终能被接收、灭灯时未发者终能发送；有限99轮最终完成，但任意有限前缀都可继续延迟某人，因此无统一访问次数或天数上限。初态未知不适用此阈值，不主张最优期望耗时。', '',
          '## 图文与资料页', '',
          '文章Figure在冻结前由当前真实时序定帧，最终JPEG从同一成片准确整数帧做limited709到full601像素转换；实际导出与看图结果另留QA。',
          '正文之后默认接150帧原题／作者资料列表，计划总6206帧；不朗读、不截题名、不加日期、URL、摘录或暂停提示。正式最终范围、媒体SHA和独立检查以render-result及实际QA为准。',
          '本文说明实际输入与画法，不预记成片、网站、语义听辨或用户观看认可。', '']
(D / 'knoll-props.md').write_text('\n'.join(lines))
