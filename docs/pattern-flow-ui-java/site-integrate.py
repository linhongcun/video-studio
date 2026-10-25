"""Publish checked D01/D02 revision copies while preserving release history.
Run after BOTH production media QA gates: python3 site-integrate.py --approved
The package version is read for the revision record; it never resets firstRelease.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SPECS={
    'strategy-pattern':{'ep':23,'lessonOrder':1,'firstRelease':'v0.52.0','publishedAt':'2026-10-24','summary':'从同一100元订单的结算操作出发，展开结算、定价策略和选择的职责，理解共同约定与委托，最后对照简短Java实现。'},
    'observer-pattern':{'ep':28,'lessonOrder':2,'firstRelease':'v0.58.0','publishedAt':'2026-10-25','summary':'从订单页面的一次状态操作出发，展开来源、订阅名单和观察者的职责，跟着通知与取消订阅理解协作，再对照简短Java实现。'},
}
FILES=['article.mdx','script.md','research.md','pronunciation.md','storyboard.json','words.json','captions.srt','video.mp4','cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg']
HISTORY_KEYS=['slug','ep','episodePart','lessonOrder','series','publishedAt','firstRelease','sourcePath','platforms','productionIssue','video','poster']

def sha(path):
    d=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(262144),b''):d.update(chunk)
    return d.hexdigest()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approved',action='store_true');args=parser.parse_args()
    assert args.approved,'Wait for root media QA gate before publishing copies'
    version=json.loads((ROOT/'site/package.json').read_text())['version']
    assert re.fullmatch(r'\d+\.\d+\.\d+',version)
    baseline_artifacts=json.loads((HERE/'site-baseline-artifacts.json').read_text())['artifacts']
    today=datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    report={'status':'passed','checkedAtBeijing':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'executedBy':'Codex pattern revision site agent','revisionRelease':'v'+version,'episodes':[]}
    for slug,spec in SPECS.items():
        production=ROOT/'episodes-codex'/slug;canonical=ROOT/'episodes'/slug
        baseline=json.loads((HERE/f'meta-before-{slug}.json').read_text())
        current=json.loads((canonical/'meta.json').read_text())
        for key in HISTORY_KEYS:assert current.get(key)==baseline.get(key),(slug,'history changed',key)
        for key in ['ep','lessonOrder','firstRelease','publishedAt']:assert baseline[key]==spec[key]
        config=json.loads((production/'episode-config.json').read_text());sb=json.loads((production/'storyboard.json').read_text())
        assert config['title']==baseline['title'],'Retain the existing episode title unless root explicitly updates the integration policy'
        frames=sb['meta'].get('finalVideoFrames',sb['meta']['durationInFrames']);fps=sb['meta']['fps'];card=sb['meta']['javaEndCard']
        assert card['kind']=='java-design-pattern'
        assert fps==30 and card['durationInFrames']==150 and card['from']+150==frames
        assert card['from']>=0
        render=json.loads((production/'render-result.json').read_text());video_sha=sha(production/'video.mp4')
        assert video_sha in json.dumps(render),(slug,'video differs from checked render report')
        article=(production/'article.mdx').read_text()
        assert not re.search(r'\b(fontSize|textAnchor|strokeWidth)=',article),'Use the owner-approved native SVG article or explicitly record a derivative'
        for name in FILES:
            src=production/name;
            if name.startswith('cover-'):
                prior=next(row for row in baseline_artifacts if row['slug']==slug and row['file']==name)
                assert sha(src)==prior['sha256'],(slug,'reused cover changed',name)
            assert src.is_file(),(slug,'missing',name)
            shutil.copyfile(src,canonical/name);assert sha(src)==sha(canonical/name)
        meta=dict(current);meta.update(updatedAt=today,summary=spec['summary'],finalVideoFrames=frames,targetDuration=frames/fps,javaEndCard=card)
        for key in HISTORY_KEYS:assert meta.get(key)==baseline.get(key),(slug,'history reset',key)
        (canonical/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        assert all(p.is_file() and p.suffix.lower() not in ['.wav','.png','.tsx','.ts','.js','.jsx'] for p in canonical.iterdir())
        report['episodes'].append({'slug':slug,'metadataBefore':baseline,'metadataAfter':meta,'historyKeysPreserved':HISTORY_KEYS,'frames':frames,'fps':fps,'javaEndCard':card,'articleSource':'article.mdx','files':[{'file':name,'sourceFile':f'episodes-codex/{slug}/{name}','sha256':sha(canonical/name),'bytes':(canonical/name).stat().st_size} for name in FILES]})
    (HERE/'site-copy-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'passed','revisionRelease':'v'+version,'episodes':[{'slug':e['slug'],'frames':e['frames'],'firstRelease':e['metadataAfter']['firstRelease']} for e in report['episodes']]},ensure_ascii=False))
