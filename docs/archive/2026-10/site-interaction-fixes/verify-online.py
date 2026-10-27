import argparse, concurrent.futures, hashlib, json, pathlib, re, time, urllib.request, urllib.error
from datetime import datetime, timezone

parser=argparse.ArgumentParser()
parser.add_argument('--expected-commit', required=True)
parser.add_argument('--output', default='/tmp/grok-online-verification.json')
args=parser.parse_args()
root=pathlib.Path(__file__).resolve().parents[4]
baseline=json.loads((root/'docs/archive/2026-10/site-interaction-fixes/preservation-baseline.json').read_text())
base='https://linhongcun.github.io/video-studio/'
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'base':base,'expectedCommit':args.expected_commit,'version':'0.82.0','media':[],'pages':[],'errors':[]}

def fetch(path, allow404=False):
    url=base+path
    for attempt in range(3):
        try:
            response=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'video-studio-interaction-verification','Cache-Control':'no-cache'}),timeout=60)
            return response.status,dict(response.headers),response.read()
        except urllib.error.HTTPError as e:
            if allow404 and e.code==404:return e.code,dict(e.headers),e.read()
            if attempt==2:raise
        except Exception:
            if attempt==2:raise
        time.sleep(1)

def media(item):
    path,expected=item
    status,headers,data=fetch(path)
    actual=hashlib.sha256(data).hexdigest()
    assert status==200 and actual==expected['sha256'],(path,status,actual,expected['sha256'])
    return {'path':path,'status':status,'size':len(data),'sha256':actual,'acceptRanges':headers.get('Accept-Ranges',headers.get('accept-ranges'))}

def page(slug):
    status,_,data=fetch(f'episodes/{slug}/');html=data.decode()
    assert status==200 and '0.82.0' in html,(slug,'version')
    nav=re.search(r'<nav\b[^>]*class="source-links"[^>]*>(.*?)</nav>',html,re.S)
    assert nav,(slug,'top sources')
    links=re.findall(r'href="([^"]+)"',nav[1]);assert len(links)==3,(slug,links)
    assert all(re.search(r'/(blob|tree)/'+args.expected_commit+r'/',link) for link in links),(slug,'source commit',links)
    assert len(re.findall(r'<a[^>]*href="https://raw.githubusercontent.com/linhongcun/video-studio/'+args.expected_commit+r'/',html))==2,(slug,'raw sources')
    track=re.search(r'<track\b[^>]*>',html);assert track and re.search(r'\bdefault(?:\s|=|>)',track[0]),(slug,'default captions')
    vttstatus,_,vtt=fetch(f'episodes/{slug}/captions.vtt');assert vttstatus==200 and vtt.startswith(b'WEBVTT') and b'-->' in vtt,(slug,'VTT')
    if slug=='distributed-tx':
        crumb=re.search(r'<nav[^>]*aria-label="面包屑"[^>]*>(.*?)</nav>',html,re.S)
        assert crumb and '系统原理' in crumb[1] and '/series/distributed/' in crumb[1] and '/tags/' not in crumb[1]
    return {'slug':slug,'status':status,'sourceLinks':links,'vttStatus':vttstatus,'defaultCaptions':True}

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    futures={pool.submit(media,item):item[0] for item in baseline['media'].items()}
    for f in concurrent.futures.as_completed(futures):
        try:report['media'].append(f.result())
        except Exception as e:report['errors'].append({'path':futures[f],'error':str(e)})
    futures={pool.submit(page,slug):slug for slug in baseline['metadata']}
    for f in concurrent.futures.as_completed(futures):
        try:report['pages'].append(f.result())
        except Exception as e:report['errors'].append({'slug':futures[f],'error':str(e)})

try:
    _,_,logdata=fetch('changelog/');log=logdata.decode()
    assert 'v0.82.0' in log and '完整记录见 GitHub Release' in log and 'details class="archive"' in log
    assert not re.search(r'\]\(https?://|\bSHA\b|冻结',log)
    report['changelog']={'status':200,'includesRelease':True,'releaseCount':log.count('完整记录见 GitHub Release'),'literalMarkdown':False}
    for path in ['404.html','nonexistent-interaction-check/','missing/deep/page/']:
        status,_,body=fetch(path,allow404=True)
        assert status==(200 if path=='404.html' else 404),(path,status)
        assert '这条路暂时走不通。' in body.decode() and 'missing-page-search' in body.decode()
    report['custom404']={'pageStatus':200,'missingPathsStatus':404,'nestedPathStatus':404}
    for path in ['', 'library/']:
        _,_,data=fetch(path);html=data.decode();cards=re.findall(r'<a\b[^>]*class="card"[^>]*>.*?</a>',html,re.S)
        assert cards and all(len(re.findall(r'<time\b',c))==1 for c in cards)
        assert all(re.search(r'>\d{4}-\d{2}-\d{2}</time>',c) and '创建于' not in c and '修改于' not in c for c in cards)
    _,_,learn=fetch('learn/');assert b'class="series-directory"' in learn
    report['cardsAndSeries']={'singleDayDates':True,'fixedSeriesDirectory':True}
    for file in ['script.md','storyboard.json']:
        url=f'https://raw.githubusercontent.com/linhongcun/video-studio/{args.expected_commit}/episodes/message-queue/{file}'
        with urllib.request.urlopen(url,timeout=30) as response:data=response.read();assert response.status==200
        assert hashlib.sha256(data).hexdigest()==hashlib.sha256((root/'episodes/message-queue'/file).read_bytes()).hexdigest()
    report['rawFiles']={'messageQueueScriptAndStoryboard':'HTTP 200, complete SHA-256 matches checked-out published files'}
except Exception as e:report['errors'].append({'extraChecks':str(e)})
report['passed']=not report['errors'] and len(report['media'])==98 and len(report['pages'])==49
pathlib.Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'media':len(report['media']),'pages':len(report['pages']),'errors':report['errors'],'output':args.output},ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
