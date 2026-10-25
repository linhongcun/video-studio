"""Integrate a checked revision of the already published D03 episode.
Usage: python3 site-integrate.py --approved --release vX.Y.Z [--updated-at YYYY-MM-DD]
firstRelease v0.63.0 and publishedAt are immutable. The release is only the new
revision identity; root selects it after synchronizing main and checking tags.
"""
import argparse
from datetime import datetime,date
import hashlib
import json
from pathlib import Path
import re
import shutil
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SLUG='adapter-pattern'
OUT=ROOT/'episodes'/SLUG
PREVIOUS=HERE/'revisions/business-boundary-v2/previous-site'
FILES=['article.mdx','script.md','research.md','pronunciation.md','storyboard.json','words.json','captions.srt','video.mp4','cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','source-sha256.json','render-result.json','mix-report.json']
HISTORY=['slug','ep','episodePart','lessonOrder','series','publishedAt','firstRelease','sourcePath','platforms','productionIssue','video','poster','related']

def sha(path):
    d=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(262144),b''):d.update(chunk)
    return d.hexdigest()

def protected_episodes():
    rows=[]
    for slug in ['strategy-pattern','observer-pattern','agent-skills','monty-hall']:
        ep=ROOT/'episodes'/slug;meta=json.loads((ep/'meta.json').read_text())
        if slug in ['strategy-pattern','observer-pattern']:
            assert meta['firstRelease']=={'strategy-pattern':'v0.52.0','observer-pattern':'v0.58.0'}[slug]
        names=['meta.json','article.mdx','storyboard.json',meta['video'],meta['poster']]
        rows.append({'slug':slug,'metadata':meta,'files':[{'path':str((ep/n).relative_to(ROOT)),'sha256':sha(ep/n)} for n in names]})
    return rows

def other_metadata():
    return [{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted((ROOT/'episodes').glob('*/meta.json')) if p.parent.name!=SLUG]

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approved',action='store_true');parser.add_argument('--release',required=True);parser.add_argument('--updated-at');args=parser.parse_args()
    assert args.approved,'Wait for formal media QA before integrating the revision'
    version=json.loads((ROOT/'site/package.json').read_text())['version'];assert re.fullmatch(r'\d+\.\d+\.\d+',version)
    assert args.release=='v'+version,'Use root final revision release identity'
    baseline=json.loads((PREVIOUS/'published-meta/meta.json').read_text());current=json.loads((OUT/'meta.json').read_text())
    assert baseline['firstRelease']=='v0.63.0'
    for key in HISTORY:assert current.get(key)==baseline.get(key),(key,'published identity changed')
    assert args.release!=baseline['firstRelease'],'A revision must not reuse the published debut tag'
    updated=args.updated_at or datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat();date.fromisoformat(updated)
    assert updated>=baseline['publishedAt']
    before=protected_episodes();before_metadata=other_metadata()
    config=json.loads((HERE/'episode-config.json').read_text());sb=json.loads((HERE/'storyboard.json').read_text());card_source=json.loads((HERE/'remotion/src/java-card.json').read_text())
    assert config['slug']==SLUG and config['episode']==baseline['ep']
    frames=sb['meta'].get('finalVideoFrames',sb['meta']['durationInFrames']);fps=sb['meta']['fps'];card=sb['meta']['javaEndCard']
    assert fps==30 and card['kind']=='java-design-pattern' and card['durationInFrames']==150 and card['from']+150==frames
    assert sum(len(sh.get('subtitles',[])) for scene in sb['scenes'] for sh in scene['shots'])==config['shotCount']*2
    for name in FILES:assert (HERE/name).is_file(),f'Missing checked source: {name}'
    video_sha=sha(HERE/'video.mp4');render=json.loads((HERE/'render-result.json').read_text());assert video_sha in json.dumps(render),'Video differs from formal encoded report'
    article=(HERE/'article.mdx').read_text();assert not re.search(r'\b(fontSize|textAnchor|strokeWidth)=',article),'Article SVG requires native presentation attributes'
    assert '{#java}' in article
    java_source=card_source['sourceFile'];assert java_source.startswith('demo-java/') and java_source.endswith('.java') and (HERE/java_source).is_file()
    assert '/adapter-pattern/'+java_source in article,'Link the complete Java source used by the card'
    assert '/adapter-pattern/demo-java/AdapterDemo.java' in article,'Link the retained Java contract/implementation dependency'
    for name in FILES:shutil.copyfile(HERE/name,OUT/name);assert sha(HERE/name)==sha(OUT/name)
    meta=dict(current);meta.update(title=config['title'],updatedAt=updated,
        summary='沿订单17的发货提醒，先按业务需求组织通知约定，再看适配器怎样转换委托，以及外部SDK升级时哪些调整留在集成边界，理解符合业务表达与隔离外部变化的收益。',
        description='保留同一发货提醒案例，讲适配器如何让已有通知能力按业务约定使用，并用外部SDK升级前后对照说明维护边界。业务语义不变、所需能力仍满足时，技术差异可局部化；适配器可承担防腐转换职责，不能凭包装名称判断模式。',
        finalVideoFrames=frames,targetDuration=frames/fps,javaEndCard=card)
    for key in HISTORY:assert meta.get(key)==baseline.get(key),(key,'revision reset published identity')
    (OUT/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    assert all(p.is_file() and p.suffix.lower() not in ['.wav','.png','.ts','.tsx','.js','.jsx'] for p in OUT.iterdir())
    assert before==protected_episodes(),'D01/D02/Skills/P04 core publishing files changed'
    assert before_metadata==other_metadata(),'Other episode metadata changed'
    report={'status':'passed','checkedAtBeijing':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'executedBy':'Codex adapter revision site agent','mode':'published-episode-revision','release':args.release,'revisionRelease':args.release,
        'metadataBefore':current,'metadata':meta,'historyFieldsPreserved':HISTORY,'previousPublishedSite':'revisions/business-boundary-v2/previous-site','previousEpisodesPreserved':before,'otherMetadataPreserved':before_metadata,
        'javaSource':java_source,'files':[{'file':name,'sourceFile':f'episodes-codex/{SLUG}/{name}','sha256':sha(OUT/name),'bytes':(OUT/name).stat().st_size} for name in FILES],
        'scope':'Only approved D03 revision artifacts copied. Debut/date and existing identities retained; D01/D02/Skills/P04 core files and every other metadata file preserved byte-for-byte.'}
    (HERE/'qa-site-copy-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'passed','revisionRelease':args.release,'firstRelease':meta['firstRelease'],'publishedAt':meta['publishedAt'],'updatedAt':updated,'frames':frames,'videoSha256':video_sha,'otherEpisodesUnchanged':True},ensure_ascii=False))
