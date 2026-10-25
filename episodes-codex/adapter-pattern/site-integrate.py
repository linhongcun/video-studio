"""Integrate checked D03 artifacts after root's formal media gate.
Usage: python3 site-integrate.py --approved --release vX.Y.Z [--published-at YYYY-MM-DD]
The release must be root's final identity and match the current site package.
No D01/D02 metadata or publishing artifacts are modified.
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
FILES=['article.mdx','script.md','research.md','pronunciation.md','storyboard.json','words.json','captions.srt','video.mp4','cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','source-sha256.json','render-result.json','mix-report.json']

def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(262144),b''):digest.update(chunk)
    return digest.hexdigest()

def previous_episodes():
    rows=[]
    for slug,first,published,order in [('strategy-pattern','v0.52.0','2026-10-24',1),('observer-pattern','v0.58.0','2026-10-25',2)]:
        ep=ROOT/'episodes'/slug;meta=json.loads((ep/'meta.json').read_text())
        assert meta['firstRelease']==first and meta['publishedAt']==published and meta['lessonOrder']==order
        assert meta['sourcePath']==f'episodes-codex/{slug}/remotion'
        names=['meta.json','article.mdx','storyboard.json',meta['video'],meta['poster']]
        rows.append({'slug':slug,'metadata':meta,'files':[{'path':str((ep/n).relative_to(ROOT)),'sha256':sha(ep/n)} for n in names]})
    return rows

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approved',action='store_true');parser.add_argument('--release',required=True);parser.add_argument('--published-at');args=parser.parse_args()
    assert args.approved,'Wait for root formal media approval before integration'
    version=json.loads((ROOT/'site/package.json').read_text())['version'];assert re.fullmatch(r'\d+\.\d+\.\d+',version)
    assert args.release=='v'+version,'Use root final release identity, not the provisional plan'
    published=args.published_at or datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat();date.fromisoformat(published)
    before=previous_episodes()
    config=json.loads((HERE/'episode-config.json').read_text());sb=json.loads((HERE/'storyboard.json').read_text());assert config['slug']==SLUG
    frames=sb['meta'].get('finalVideoFrames',sb['meta']['durationInFrames']);fps=sb['meta']['fps'];card=sb['meta']['javaEndCard']
    assert fps==30 and card['kind']=='java-design-pattern' and card['durationInFrames']==150 and card['from']+150==frames
    for name in FILES:assert (HERE/name).is_file(),f'Missing checked source: {name}'
    render=json.loads((HERE/'render-result.json').read_text());video_sha=sha(HERE/'video.mp4');assert video_sha in json.dumps(render),'Video differs from the formal encoded report'
    article=(HERE/'article.mdx').read_text();assert not re.search(r'\b(fontSize|textAnchor|strokeWidth)=',article),'Article SVG presentation must use native attributes'
    assert '{#java}' in article,'Java implementation entry is required'
    assert '/adapter-pattern/demo-java/AdapterDemo.java' in article,'Link the full runnable Java source'
    OUT.mkdir(parents=True,exist_ok=True)
    for name in FILES:shutil.copyfile(HERE/name,OUT/name);assert sha(HERE/name)==sha(OUT/name)
    meta={'slug':SLUG,'ep':config['episode'],'episodePart':config.get('episodePart','设计模式 D03'),'lessonOrder':3,'title':config['title'],
          'summary':'商家为订单发送发货提醒时，业务约定与新服务接口对不上。跟着同一条消息展开使用者、目标约定、适配器与外部服务的职责，理解转换、委托和结果边界，再对照Java实现。',
          'description':'从发货提醒操作进入业务通知约定与外部SDK的差异，沿同一消息演示适配器转换请求、委托已有服务并翻译结果。已受理不等于已送达，接口转换不能补出服务缺少的能力。',
          'tags':['设计模式','适配器模式','代码设计'],'series':'design-patterns','publishedAt':published,'firstRelease':args.release,'video':'video.mp4','poster':'cover-16x9.jpg','draft':False,
          'related':['observer-pattern','strategy-pattern'],'platforms':{},'sourcePath':f'episodes-codex/{SLUG}/remotion','productionIssue':165,'finalVideoFrames':frames,'targetDuration':frames/fps,'javaEndCard':card}
    (OUT/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    assert all(p.is_file() and p.suffix.lower() not in ['.wav','.png','.ts','.tsx','.js','.jsx'] for p in OUT.iterdir())
    assert before==previous_episodes(),'D01/D02 publishing data changed during new episode integration'
    report={'status':'passed','checkedAtBeijing':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'executedBy':'Codex adapter site agent','release':args.release,'metadata':meta,'previousEpisodesPreserved':before,
            'files':[{'file':name,'sourceFile':f'episodes-codex/{SLUG}/{name}','sha256':sha(OUT/name),'bytes':(OUT/name).stat().st_size} for name in FILES],
            'scope':'Only approved D03 publishing artifacts copied. D01/D02 publishing metadata and core artifacts are byte-identical to their current pre-integration state; no production WAV/PNG/source tree copied.'}
    (HERE/'qa-site-copy-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'passed','release':args.release,'ep':meta['ep'],'frames':frames,'publishedAt':published,'videoSha256':video_sha,'previousEpisodesUnchanged':True},ensure_ascii=False))
