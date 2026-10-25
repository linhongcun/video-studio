"""Publish the checked observer core plus its separately verified references."""
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
APPENDIX = HERE/'revisions/observer-first/reference-appendix'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approved', action='store_true', help='Core and appendix media QA completed')
    parser.add_argument('--release', required=True)
    args = parser.parse_args()
    assert args.approved
    assert args.release == 'v'+json.loads((ROOT/'site/package.json').read_text())['version']
    sb = json.loads((HERE/'storyboard.json').read_text())
    core = json.loads((HERE/'render-result.json').read_text())
    final = json.loads((HERE/'render-result-final.json').read_text())
    appendix = json.loads((APPENDIX/'reference-appendix.json').read_text())
    check = json.loads((APPENDIX/'reference-appendix-media-check.json').read_text())
    assert sha(HERE/'video.mp4') == core['sha256'] == appendix['inputs']['bodySHA256']
    assert sha(HERE/'video-with-references.mp4') == final['sha256'] == appendix['outputSHA256']
    assert sha(HERE/'references.json') == appendix['inputs']['referencesSHA256']
    assert check['passed'] and check['bodyDecodedFramesAndTimestampsEqual'] and check['audioPacketsAndTimingEqual']
    assert sb['meta']['durationInFrames'] == appendix['bodyFrames']
    frames = appendix['finalVideoFrames']
    assert frames == appendix['bodyFrames'] + appendix['appendix']['durationInFrames'] == final['frames']
    metadata = json.loads((OUT/'meta.json').read_text())
    identity = {k: metadata.get(k) for k in ['slug','ep','createdAt','publishedAt','firstRelease','platforms']}
    files = ['article.mdx','script.md','research.md','pronunciation.md','storyboard.json','words.json',
             'captions.srt','render-result.json','mix-report.json','source-sha256.json','video.mp4',
             'cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','references.json',
             'reference-appendix.json','reference-appendix-media-check.json']
    source_files = {n: HERE/n for n in files}
    source_files.update({'video.mp4': HERE/'video-with-references.mp4',
                         'render-result.json': HERE/'render-result-final.json',
                         'reference-appendix.json': APPENDIX/'reference-appendix.json',
                         'reference-appendix-media-check.json': APPENDIX/'reference-appendix-media-check.json'})
    for name, source in source_files.items():
        shutil.copyfile(source, OUT/name)
        assert sha(source) == sha(OUT/name)
    metadata.update(
        summary='从订单变化讲清观察者的动机、角色、订阅通知和退出，理解职责分离与取舍，最后简述框架事件和MQ的实战对应。',
        description='保留订单17、摘要和变化记录案例，以一次已付款通知和退出后的发货通知讲清观察者模式的共同约定、职责与协作；代码简述，MQ仅为短实战映射。',
        tags=['设计模式','观察者模式','事件通知'], related=['strategy-pattern'],
        updatedAt=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
        finalVideoFrames=frames, targetDuration=frames/30,
        javaEndCard=sb['meta']['javaEndCard'], revisionIssue=305,
        referenceAppendix={'kind':'references','from':appendix['bodyFrames'],
                           'durationInFrames':appendix['appendix']['durationInFrames'],
                           'sources':'references.json','manifest':'reference-appendix.json'},
    )
    assert all(metadata.get(k) == v for k,v in identity.items())
    (OUT/'meta.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    report = {'status':'passed','release':args.release,'originalIdentityPreserved':identity,
              'frames':frames,'coreFrames':appendix['bodyFrames'],
              'files':{n:sha(OUT/n) for n in files},
              'sourceFiles':{n:str(p.relative_to(HERE)) for n,p in source_files.items()},
              'metadata':metadata,'scope':'Core storyboard/voice remain immutable; published media includes a separately checked150-frame reference appendix.'}
    (HERE/'site-copy-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    shutil.copyfile(HERE/'site-copy-manifest.json',OUT/'site-copy-manifest.json')
    print(json.dumps({'status':'passed','release':args.release,'frames':frames,'videoSha256':final['sha256']}))
