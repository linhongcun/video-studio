from pathlib import Path
import json
summary=Path('docs/archive/2026-10/leetcode-video-style/final-media-summary.json')
for d in json.loads(summary.read_text()):
 s=d['slug'];meta=json.loads(Path(f'episodes/{s}/meta.json').read_text())
 text=f'''# LC.{d['problemNumber']} 视觉修订

当前入口为[新视觉源码](../../remotion/src/leetcode-style/index.ts)，题目为{meta['title']}，方法为{d['method']}。正文、完整Python页与参考资料页沿现有封面的深蓝/暖金/青色风格。

正式成片SHA-256：`{d['sha256']}`，1920×1080、30fps、{d['frames']}帧。Python完整代码页为帧{d['codeRange'][0]}–{d['codeRange'][1]}，参考资料为{d['referenceRange'][0]}–{d['referenceRange'][1]}，两段各150帧，不互相替换。

新源仍读原模型、分镜和solution，配音时序不动；完整原发布AAC载荷/时间戳/PCM相同。追加资料前后，新正文（含Python页）全部解码帧/PTS相同。旧制作源、原冻结、原标题、创建首发和平台链接保持历史身份。

`baseline-publication.json`保存替换前身份，`article.mdx`为原发布文章的冻结快照；原文、引文与Figure回看时间不改，配图来自新版对应帧。实际输入和媒体回执在本目录，制作与验证方法见[共享说明](../../../_shared/leetcode-video/README.md)，发布状态见[本轮记录](../../../../docs/archive/2026-10/leetcode-video-style/README.md)。

没有新ASR、全片人工听辨、真机或新用户观看认可声明。恢复基线声音须按旧快照Git提交和完整SHA提取，不能使用当前新片代替。
'''
 Path(f'episodes-codex/{s}/revisions/leetcode-style/README.md').write_text(text)
print('Current revision README files written:',len(json.loads(summary.read_text())))
