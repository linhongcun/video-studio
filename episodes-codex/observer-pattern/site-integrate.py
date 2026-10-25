"""Copy this checked revision, preserving the lesson's original publishing identity."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT/'episodes/observer-pattern'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approved', action='store_true', help='Media QA actually completed')
    parser.add_argument('--release', required=True)
    args = parser.parse_args()
    assert args.approved
    assert args.release == 'v'+json.loads((ROOT/'site/package.json').read_text())['version']
    sb = json.loads((HERE/'storyboard.json').read_text())
    encoded = json.loads((HERE/'render-result.json').read_text())
    assert sha(HERE/'video.mp4') == encoded['sha256']
    metadata = json.loads((OUT/'meta.json').read_text())
    original_identity = {key: metadata.get(key) for key in ['slug', 'ep', 'createdAt', 'publishedAt', 'firstRelease', 'platforms']}
    files = ['article.mdx','script.md','research.md','pronunciation.md','storyboard.json',
             'words.json','captions.srt','render-result.json','mix-report.json','source-sha256.json','video.mp4','cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg']
    for name in files:
        shutil.copyfile(HERE/name, OUT/name)
        assert sha(HERE/name) == sha(OUT/name)
    frames = sb['meta']['durationInFrames']
    metadata.update(
        summary='从订单变化讲清观察者的动机、角色、订阅通知和退出，理解职责分离与取舍，最后简述框架事件和MQ的实战对应。',
        description='保留订单17、摘要和变化记录案例，以一次已付款通知和退出后的发货通知讲清观察者模式的共同约定、职责与协作；代码简述，MQ仅为短实战映射。',
        tags=['设计模式','观察者模式','事件通知'],
        related=['strategy-pattern'],
        updatedAt=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
        finalVideoFrames=frames, targetDuration=frames/30,
        javaEndCard=sb['meta']['javaEndCard'], revisionIssue=305,
    )
    assert all(metadata.get(k) == v for k, v in original_identity.items())
    (OUT/'meta.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    report = {'status':'passed','release':args.release,'originalIdentityPreserved':original_identity,
              'frames':frames,'files':{name:sha(OUT/name) for name in files},'metadata':metadata}
    (HERE/'site-copy-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    shutil.copyfile(HERE/'site-copy-manifest.json', OUT/'site-copy-manifest.json')
    print(json.dumps({'status':'passed','release':args.release,'frames':frames,'videoSha256':encoded['sha256']}))
