"""Verify canonical D03 delivery after Release-following Pages succeeds.
Ordinary GET requests, no cache query. Hash complete remote video streams without
saving media. D01/D02 checks cover their changed directory/pager, not old media.
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
EP=ROOT/'episodes/adapter-pattern'
DIST=ROOT/'site/dist'
BASE='https://linhongcun.github.io/video-studio/'
SLUG='adapter-pattern'
VERSION=json.loads((ROOT/'site/package.json').read_text())['version']
META=json.loads((EP/'meta.json').read_text())
SB=json.loads((EP/'storyboard.json').read_text())
MANIFEST=json.loads((HERE/'qa-site-copy-manifest.json').read_text())
assert META['firstRelease']==MANIFEST['metadata']['firstRelease']
assert META['publishedAt']==MANIFEST['metadata']['publishedAt']
assert META['sourcePath']=='episodes-codex/adapter-pattern/remotion'
assert META['lessonOrder']==3 and META['draft'] is False
FPS=SB['meta']['fps'];FRAMES=META['finalVideoFrames'];CARD=SB['meta']['javaEndCard']
assert CARD['kind']=='java-design-pattern' and CARD['durationInFrames']==150 and CARD['from']+150==FRAMES
ALL=[]
ACTIVE_AGENTS=[]
for file in (ROOT/'episodes').glob('*/meta.json'):
    m=json.loads(file.read_text())
    if not m.get('draft') and not m.get('archived') and m.get('series')=='design-patterns':ALL.append(m)
    if not m.get('draft') and not m.get('archived') and m.get('series')=='agent':ACTIVE_AGENTS.append(m['slug'])
ALL.sort(key=lambda m:(m['ep'],m.get('lessonOrder',0)))
SERIES=[m['slug'] for m in ALL]
assert SERIES[:3]==['strategy-pattern','observer-pattern',SLUG]
RESULTS=[]
CONTEXT=ssl.create_default_context()

def sha(path):
    d=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(262144),b''):d.update(chunk)
    return d.hexdigest()

def get(name,url,expected=None,body=True):
    request=urllib.request.Request(url,headers={'User-Agent':'video-studio-adapter-delivery-check/1.0'})
    d=hashlib.sha256();count=0;chunks=[]
    with urllib.request.urlopen(request,timeout=90,context=CONTEXT) as response:
        assert response.status==200,(name,response.status)
        assert response.geturl()==url,(name,'unexpected redirect',response.geturl())
        record={'name':name,'url':url,'method':'GET','status':response.status,'contentType':response.headers.get('Content-Type'),'etag':response.headers.get('ETag'),'age':response.headers.get('Age')}
        for chunk in iter(lambda:response.read(262144),b''):
            d.update(chunk);count+=len(chunk)
            if body:chunks.append(chunk)
    record.update(bytes=count,sha256=d.hexdigest())
    if expected:
        record['expectedSha256']=expected;assert d.hexdigest()==expected,(name,'SHA mismatch',d.hexdigest(),expected);record['exactBytesMatch']=True
    RESULTS.append(record)
    return b''.join(chunks) if body else None

def seconds(stamp):
    total=0
    for n in stamp.split(':'):total=total*60+float(n)
    return total

def check_directory(page,slug):
    directory=re.search(r'<nav[^>]*aria-label="设计模式课程目录"[^>]*>(.*?)</nav>',page,re.S).group(1)
    actual=re.findall(r'href="/video-studio/episodes/([^/]+)/"',directory);assert actual==SERIES
    assert re.search(r'<a\b(?=[^>]*href="/video-studio/episodes/'+slug+r'/")(?=[^>]*aria-current="page")[^>]*>',directory)
    pager=re.search(r'<nav[^>]*class="pager(?: [^"]*)?"[^>]*>(.*?)</nav>',page,re.S).group(1)
    actual_pager=re.findall(r'href="/video-studio/episodes/([^/]+)/"',pager)
    i=SERIES.index(slug);expected=SERIES[max(0,i-1):i]+SERIES[i+1:i+2];assert actual_pager==expected
    return {'slug':slug,'directory':actual,'pager':actual_pager}

try:
    url=BASE+'episodes/'+SLUG+'/'
    get('video',url+META['video'],sha(EP/META['video']),body=False)
    get('poster',url+META['poster'],sha(EP/META['poster']),body=False)
    vtt_path=DIST/'episodes'/SLUG/'captions.vtt'
    if vtt_path.is_dir():vtt_path=vtt_path/'index.html'
    vtt=get('captions',url+'captions.vtt',sha(vtt_path)).decode('utf8')
    page=get('episode',url).decode('utf8')
    expected_chapters=[];offset=0;expected_cues=[]
    for scene in SB['scenes']:
        if not expected_chapters or expected_chapters[-1]['id']!=scene['chapterId']:expected_chapters.append({'id':scene['chapterId'],'frame':offset,'start':offset/FPS})
        for shot in scene['shots']:
            for sub in shot.get('subtitles',[]):expected_cues.append({'text':sub['text'],'start':(offset+sub['from'])/FPS,'end':(offset+sub['to']+1)/FPS})
            offset+=shot['durationInFrames']
    assert offset==FRAMES
    chapters=json.loads(html.unescape(re.search(r'data-chapters="([^"]+)"',page).group(1)));assert len(chapters)==len(expected_chapters)
    for actual,expected in zip(chapters,expected_chapters):
        assert actual['id']==expected['id'] and actual['start']==expected['start']
        assert f'id="{expected["id"]}"' in page and f'data-seek="{expected["id"]}"' in page
    cues=[]
    for block in re.split(r'\r?\n\s*\r?\n',vtt.strip())[1:]:
        lines=block.splitlines();a,b=lines[0].split(' --> ');cues.append({'text':'\n'.join(lines[1:]),'start':seconds(a),'end':seconds(b)})
    assert len(cues)==len(expected_cues)==24
    for actual,expected in zip(cues,expected_cues):
        assert actual['text']==expected['text'] and abs(actual['start']-expected['start'])<0.001 and abs(actual['end']-expected['end'])<0.001
    assert all(c['end']<=CARD['from']/FPS+0.001 for c in cues)
    assert META['title'] in page and 'id="java"' in page
    source='https://github.com/linhongcun/video-studio/tree/main/'+META['sourcePath']
    java_source='https://github.com/linhongcun/video-studio/blob/main/episodes-codex/adapter-pattern/demo-java/AdapterDemo.java'
    assert source in html.unescape(page) and java_source in html.unescape(page)
    ld=json.loads(html.unescape(re.search(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',page,re.S).group(1)))
    assert ld['name']==META['title'] and ld['contentUrl']==url+META['video'] and ld['embedUrl']==url
    assert ld['uploadDate'].startswith(META['publishedAt'])
    assert ld['duration']==f'PT{int(FRAMES/FPS//60)}M{int(FRAMES/FPS%60)}S'
    directory_checks=[check_directory(page,SLUG)]
    for previous in ['strategy-pattern','observer-pattern']:
        old=get(previous+'-directory',BASE+'episodes/'+previous+'/').decode('utf8');directory_checks.append(check_directory(old,previous))
    home=get('home',BASE).decode('utf8');assert VERSION in home and '/video-studio/episodes/adapter-pattern/' in home
    series=get('series',BASE+'series/design-patterns/').decode('utf8')
    for slug in SERIES:assert '/video-studio/episodes/'+slug+'/' in series
    for a,b in zip(SERIES,SERIES[1:]):assert series.index('/video-studio/episodes/'+a+'/')<series.index('/video-studio/episodes/'+b+'/')
    library=get('library',BASE+'library/').decode('utf8');assert '/video-studio/episodes/adapter-pattern/' in library
    rss=get('rss',BASE+'rss.xml').decode('utf8');assert url in rss
    for name,document in [('home',home),('library',library),('rss',rss)]:
        for retired in ['agent-intro','agent-tool-execution']:assert '/episodes/'+retired+'/' not in document,(name,'retired Agent entry restored')
    if ACTIVE_AGENTS:
        assert '/video-studio/learn/#agent' in home,'Published Agent track must remain reachable from the home direction entry'
        for active in ACTIVE_AGENTS:
            assert '/episodes/'+active+'/' in library and '/episodes/'+active+'/' in rss
    else:assert '/video-studio/learn/#agent' not in home
    changelog=get('changelog',BASE+'changelog/').decode('utf8');assert 'https://github.com/linhongcun/video-studio/releases/tag/v'+VERSION in changelog
    now=datetime.now(timezone.utc)
    report={'status':'passed','checkedAtUTC':now.isoformat(),'checkedAtBeijing':now.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),'executedBy':'Codex adapter site agent','release':'v'+VERSION,'firstRelease':META['firstRelease'],'publishedAt':META['publishedAt'],'ep':META['ep'],'canonicalQueriesAdded':False,'remoteMediaSaved':False,'fullVideoStreamHashed':True,'results':RESULTS,'chapters':expected_chapters,'finalVideoFrames':FRAMES,'fps':FPS,'durationSeconds':FRAMES/FPS,'subtitleCueCount':len(cues),'lastCueEnd':max(c['end'] for c in cues),'javaEndCard':CARD,'source':source,'javaSource':java_source,'directoryChecks':directory_checks,'retiredAgentEntryLinksAbsent':True,'currentAgentSlugs':ACTIVE_AGENTS,'currentAgentHomeEntry':'/video-studio/learn/#agent' if ACTIVE_AGENTS else None,'scope':'Canonical media and caption byte equality, exact subtitle and chapter data, Java article/source entry and empty-caption card range, D01/D02 affected directory/pager, series/library/RSS and actual Release link. Browser pause/decoded frame evidence is local and separate.'}
    (HERE/'qa-site-online.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'passed','canonicalGetCount':len(RESULTS),'release':'v'+VERSION,'frames':FRAMES,'cueCount':24,'report':str(HERE/'qa-site-online.json')},ensure_ascii=False))
except Exception as exc:
    failure={'status':'failed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'completedGetCount':len(RESULTS),'error':repr(exc),'results':RESULTS};(HERE/('qa-site-online-failed-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')).write_text(json.dumps(failure,ensure_ascii=False,indent=2)+'\n');print(json.dumps(failure,ensure_ascii=False,indent=2));raise
