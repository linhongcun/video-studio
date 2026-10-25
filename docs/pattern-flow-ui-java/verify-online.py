"""Verify both revised canonical episodes after Release-following Pages success.
Ordinary GET only, no cache-busting queries. Full remote video streams are hashed
without saving remote media; local checked media supplies expected bytes/SHA.
"""
import hashlib
import html
import json
from pathlib import Path
import re
import ssl
import urllib.request
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DIST=ROOT/'site/dist'
BASE='https://linhongcun.github.io/video-studio/'
SLUGS=['strategy-pattern','observer-pattern']
VERSION=json.loads((ROOT/'site/package.json').read_text())['version']
RESULTS=[]
CONTEXT=ssl.create_default_context()

def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(262144),b''):digest.update(chunk)
    return digest.hexdigest()

def get(name,url,expected=None,body=True):
    request=urllib.request.Request(url,headers={'User-Agent':'video-studio-pattern-revision-check/1.0'})
    digest=hashlib.sha256();count=0;chunks=[]
    with urllib.request.urlopen(request,timeout=90,context=CONTEXT) as response:
        assert response.status==200,(name,response.status)
        assert response.geturl()==url,(name,'unexpected redirect',response.geturl())
        record={'name':name,'url':url,'method':'GET','status':response.status,'contentType':response.headers.get('Content-Type'),'etag':response.headers.get('ETag'),'age':response.headers.get('Age')}
        for chunk in iter(lambda:response.read(262144),b''):
            digest.update(chunk);count+=len(chunk)
            if body:chunks.append(chunk)
    record.update(bytes=count,sha256=digest.hexdigest())
    if expected:
        record['expectedSha256']=expected;assert digest.hexdigest()==expected,(name,'SHA mismatch',digest.hexdigest(),expected);record['exactBytesMatch']=True
    RESULTS.append(record)
    return b''.join(chunks) if body else None

def seconds(value):
    total=0
    for n in value.split(':'):total=total*60+float(n)
    return total

try:
    episodes=[]
    for slug in SLUGS:
        ep=ROOT/'episodes'/slug;meta=json.loads((ep/'meta.json').read_text());before=json.loads((HERE/f'meta-before-{slug}.json').read_text())
        for key in ['ep','lessonOrder','firstRelease','publishedAt','sourcePath','platforms']:assert meta.get(key)==before.get(key),(slug,key)
        sb=json.loads((ep/'storyboard.json').read_text());fps=sb['meta']['fps'];card=sb['meta']['javaEndCard'];frames=meta['finalVideoFrames']
        assert card['durationInFrames']==150 and card['from']+150==frames
        url=BASE+'episodes/'+slug+'/'
        get(slug+'-video',url+meta['video'],sha(ep/meta['video']),body=False)
        get(slug+'-poster',url+meta['poster'],sha(ep/meta['poster']),body=False)
        vtt_path=DIST/'episodes'/slug/'captions.vtt'
        if vtt_path.is_dir():vtt_path=vtt_path/'index.html'
        vtt=get(slug+'-captions',url+'captions.vtt',sha(vtt_path)).decode('utf8')
        page=get(slug+'-page',url).decode('utf8')
        expected_chapters=[];offset=0;expected_cues=[]
        for scene in sb['scenes']:
            if not expected_chapters or expected_chapters[-1]['id']!=scene['chapterId']:expected_chapters.append({'id':scene['chapterId'],'frame':offset,'start':offset/fps})
            for shot in scene['shots']:
                for sub in shot.get('subtitles',[]):expected_cues.append({'text':sub['text'],'start':(offset+sub['from'])/fps,'end':(offset+sub['to']+1)/fps})
                offset+=shot['durationInFrames']
        assert offset==frames
        chapters=json.loads(html.unescape(re.search(r'data-chapters="([^"]+)"',page).group(1)))
        assert len(chapters)==len(expected_chapters)
        for actual,expected in zip(chapters,expected_chapters):
            assert actual['id']==expected['id'] and actual['start']==expected['start']
            assert f'id="{expected["id"]}"' in page and f'data-seek="{expected["id"]}"' in page
        cues=[]
        for block in re.split(r'\r?\n\s*\r?\n',vtt.strip())[1:]:
            lines=block.splitlines();start,end=lines[0].split(' --> ');cues.append({'text':'\n'.join(lines[1:]),'start':seconds(start),'end':seconds(end)})
        assert len(cues)==len(expected_cues)
        for actual,expected in zip(cues,expected_cues):
            assert actual['text']==expected['text']
            assert abs(actual['start']-expected['start'])<0.001 and abs(actual['end']-expected['end'])<0.001
        assert all(c['end']<=card['from']/fps+0.001 for c in cues),'Old cue overlaps Java card'
        assert 'id="java"' in page and 'Java' in page,'Java article entry missing'
        assert meta['title'] in page
        source='https://github.com/linhongcun/video-studio/tree/main/'+meta['sourcePath'];assert source in html.unescape(page)
        directory=re.search(r'<nav[^>]*aria-label="设计模式课程目录"[^>]*>(.*?)</nav>',page,re.S).group(1)
        directory_slugs=re.findall(r'href="/video-studio/episodes/([^/]+)/"',directory);assert directory_slugs==SLUGS
        current=re.search(r'<a\b(?=[^>]*href="/video-studio/episodes/'+slug+r'/")(?=[^>]*aria-current="page")[^>]*>',directory);assert current
        pager=re.search(r'<nav[^>]*class="pager(?: [^"]*)?"[^>]*>(.*?)</nav>',page,re.S).group(1)
        other=SLUGS[1-SLUGS.index(slug)];assert '/video-studio/episodes/'+other+'/' in pager
        ld=json.loads(html.unescape(re.search(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',page,re.S).group(1)))
        assert ld['name']==meta['title'] and ld['contentUrl']==url+meta['video'] and ld['embedUrl']==url
        assert ld['duration']==f'PT{int(frames/fps//60)}M{int(frames/fps%60)}S'
        episodes.append({'slug':slug,'firstRelease':meta['firstRelease'],'publishedAt':meta['publishedAt'],'updatedAt':meta['updatedAt'],'frames':frames,'fps':fps,'durationSeconds':frames/fps,'chapters':expected_chapters,'subtitleCueCount':len(cues),'lastCueEnd':max(c['end'] for c in cues),'javaEndCard':card,'javaArticleEntry':True,'source':source,'seriesOrder':directory_slugs})
    home=get('home',BASE).decode('utf8');assert VERSION in home and 'data-series="design-patterns"' in home
    series=get('series',BASE+'series/design-patterns/').decode('utf8')
    for slug in SLUGS:assert '/video-studio/episodes/'+slug+'/' in series
    assert series.index('/video-studio/episodes/strategy-pattern/')<series.index('/video-studio/episodes/observer-pattern/')
    library=get('library',BASE+'library/').decode('utf8')
    rss=get('rss',BASE+'rss.xml').decode('utf8')
    for e in episodes:
        assert BASE+'episodes/'+e['slug']+'/' in rss
        assert '/video-studio/episodes/'+e['slug']+'/' in library
    changelog=get('changelog',BASE+'changelog/').decode('utf8');assert 'https://github.com/linhongcun/video-studio/releases/tag/v'+VERSION in changelog
    now=datetime.now(timezone.utc)
    report={'status':'passed','checkedAtUTC':now.isoformat(),'checkedAtBeijing':now.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),'executedBy':'Codex pattern revision site agent','revisionRelease':'v'+VERSION,'canonicalQueriesAdded':False,'remoteMediaSaved':False,'fullVideoStreamsHashed':True,'results':RESULTS,'episodes':episodes,'scope':'Full canonical media and caption byte equality, all caption timing, exact chapters/anchors, Java article entry and empty-caption card range, both preserved release histories, source/series/library/RSS and actual Release link. Browser Java-card pause/decoded frame evidence is local and recorded separately.'}
    (HERE/'online-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'passed','canonicalGetCount':len(RESULTS),'revisionRelease':'v'+VERSION,'episodes':[{'slug':e['slug'],'frames':e['frames'],'cueCount':e['subtitleCueCount']} for e in episodes],'report':str(HERE/'online-verification.json')},ensure_ascii=False))
except Exception as exc:
    print(json.dumps({'status':'failed','completedGetCount':len(RESULTS),'error':str(exc),'results':RESULTS},ensure_ascii=False,indent=2));raise
