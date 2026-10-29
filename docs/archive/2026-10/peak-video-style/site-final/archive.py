"""Archive exact final site evidence without changing the app or source checkout."""
from pathlib import Path
from datetime import datetime, timezone
import copy,gzip,hashlib,json,shutil,subprocess
ROOT=Path('/workspace/work/video-studio');BASE=ROOT/'work/peak-video-style/siteqa';DEST=ROOT/'docs/archive/2026-10/peak-video-style/site-final'
CANDIDATE='1a26027d7d6e2f4c50574604b8f37b56ecb7b7b4'
SLUGS=['rate-limit','idempotency','circuit-breaker','degradation']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def cp(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def gz(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(gzip.compress(src.read_bytes(),mtime=0))
d=json.loads((BASE/'attempt-2-image-document-favicon/browser/report.json').read_text());m=json.loads((BASE/'mobile/report.json').read_text());nav=json.loads((BASE/'trace-navigation.json').read_text());hydration=json.loads((BASE/'static-hydration.json').read_text())
assert d['candidate']==m['candidate']==nav['candidate']==hydration['candidate']==CANDIDATE
assert m['status']=='passed' and d['status']=='failed'
views=copy.deepcopy(d['views']+m['views']);lessons=[row for view in views for row in view['episodes']]
assert len(lessons)==8 and all('nativeCaptions'in row and 'overflow'in row for row in lessons)
assert [row['slug']for row in views[0]['episodes']]==[row['slug']for row in views[1]['episodes']]==SLUGS
assert not m['views'][0]['applicationErrors']
assert not [event for event in nav['events']if event['kind']=='response' and event['status']>=400]
assert all(event['kind']=='requestfailed' and event['reason']=='net::ERR_ABORTED' or event['kind']=='console' and event['location']['url']=='http://127.0.0.1:4327/favicon.ico' and event['document'].endswith('.jpg') for event in nav['events'])
assert all(row['distMatchesFullCandidateBytes'] and row['fullHTTPBytesMatch']for row in hydration['allTrackedPublicAssets'])
assert len(hydration['allTrackedPublicAssets'])==5
DEST.mkdir(parents=True,exist_ok=True)
for src_dir,target in [(BASE/'attempt-2-image-document-favicon/browser','desktop'),(BASE/'mobile','mobile')]:
 for path in src_dir.iterdir():cp(path,DEST/target/path.name)
for filename in ['build.py','helpers.py','check-site.py','archive.py','build.json','candidate.txt','static-hydration.json','trace-navigation.py','trace-navigation.json']:
 cp(BASE/filename,DEST/filename)
for filename in ['build.log','preview.log','mobile.log','trace-navigation.log']:gz(BASE/filename,DEST/(filename+'.gz'))
gz(BASE/'attempt-2-image-document-favicon/browser.log',DEST/'desktop.log.gz')
for attempt in ['attempt-1-superseded-figure-export','attempt-3-native-image-zoom']:
 for path in (BASE/attempt).rglob('*'):
  if path.is_file():
   rel=path.relative_to(BASE/attempt)
   if path.suffix=='.log':gz(path,DEST/'attempts'/attempt/Path(str(rel)+'.gz'))
   else:cp(path,DEST/'attempts'/attempt/rel)
a=DEST/'attempts/attempt-2-image-document-favicon'
for filename in ['check-site.py','helpers.py','trace-navigation.py','trace-navigation.json']:cp(BASE/'attempt-2-image-document-favicon'/filename,a/filename)
cp(BASE/'attempt-2-image-document-favicon/browser/report.json',a/'report.json')
gz(BASE/'attempt-2-image-document-favicon/browser.log',a/'browser.log.gz')
write(a/'scope.json',{'candidate':CANDIDATE,'originalStatus':'failed','allFourDesktopLessonChecksCompleted':True,'failureScope':'Final broad console assertion found five generic 404 messages after all lesson checks. Missing tracked favicon-32.png and apple-touch-icon.png were then hydrated exactly; fresh detailed catalog/eight-image replay found no app resource errors and one origin-root favicon.ico fallback.','screenshotsArchivedIn':'../../desktop/','originalReportNotRewritten':True,'noAppChanges':True})
for view,source in zip(views,['desktop/report.json','mobile/report.json']):view['evidenceSource']=source
corepaths=['site/src',*[f'episodes/{slug}'for slug in SLUGS],'episodes-codex/_shared/peak-video']
trees={p:subprocess.check_output(['git','rev-parse',f'{CANDIDATE}:{p}'],cwd=ROOT,text=True).strip()for p in corepaths}
counts={'lessonViews':len(lessons),'videoChapterUIClicks':sum(len(row['chapterSeeks'])for row in lessons),'articleChapterUIClicks':sum(len(row['articleChapterSeeks'])for row in lessons),'figureThemeSeekAndOriginalViewChecks':sum(len(row['figureThemes'])for row in lessons),'sourceQuoteKeyboardOpenSourceLinkEscapeChecks':sum(len(row['sourceQuotes'])for row in lessons),'desktopSourceQuoteHoverPinChecks':sum(len(row['sourceQuotes'])for row in views[0]['episodes']),'playKPauseChecks':len(lessons),'nativeFullscreenEnterExitChecks':len(lessons),'nativeCaptionLifecycleChecks':len(lessons),'freshFullHTTPMediaResponses':len(d['httpMedia']),'trackedPublicAssetFullHTTPResponses':5,'browserScreenshots':len(d['screenshots'])+len(m['screenshots'])}
report={'status':'passed-with-observed-native-image-favicon-fallback','candidate':CANDIDATE,'baseline':d['baseline'],'siteVersion':'0.91.1','assembledAtUTC':datetime.now(timezone.utc).isoformat(),'build':json.loads((BASE/'build.json').read_text()),'acceptanceBasis':'Four unchanged desktop lesson views completed all per-lesson checks before a broad console assertion; a fresh detailed navigation replay after exact sparse-static hydration plus four complete mobile views establish final app-resource scope. Original interrupted/failed reports remain unchanged.','views':views,'episodes':m['episodes'],'httpMedia':d['httpMedia'],'counts':counts,'assetTreeSHA':trees,'staticHydration':'static-hydration.json','freshNavigationReplay':'trace-navigation.json','sourceReports':[{'file':'desktop/report.json','originalStatus':d['status']},{'file':'mobile/report.json','originalStatus':m['status']}],'auxiliaryObserved404':[event for event in nav['events']if event['kind']=='console'],'colour':{'point':[1880,1040],'bodyBrowserRGBA':[11,42,50,255],'referenceBrowserRGBA':[12,43,51,255],'maximumVideoCanvasChannelDifferenceFromFFmpeg':max(row[key]['maximumChannelDifferenceFromFFmpeg']for row in lessons for key in ['bodyColour','referenceColour']),'figureBadgePoint':[760,40],'figureBrowserRGB':[97,223,222],'exactMoviePNGRGB':[97,222,223],'maximumFigureDifferenceFromMoviePNG':1,'allFigureBrowserPixelsEqualPublishedJPEGDecode':True},'limits':['Local complete HTTP checks; no canonical online deployment claim.','390×844 is mobile/touch viewport simulation; native Fullscreen API retains portrait letterboxing. Embedded bibliography is small at portrait width, with no control overlap; physical-device landscape readability is not claimed.','Standalone JPG opens the native browser image viewer at natural width and may zoom/scroll beyond the mobile viewport. Article pages remain subject to strict horizontal overflow checks.','Origin-root /favicon.ico requested by a standalone JPG document returns404 outside the deployed /video-studio/ base; retained explicitly rather than claimed absent.','No full-film listening, ASR, physical-device test or new user viewing approval.']}
write(DEST/'report.json',report);write(DEST/'summary.json',{k:report[k]for k in ['status','candidate','siteVersion','counts','colour','acceptanceBasis','limits']})
# Exact files actually inspected through view_image, all original screenshots.
reviewed_main_desktop=['rate-limit-fullscreen-1440.png','idempotency-fullscreen-1440.png','circuit-breaker-fullscreen-1440.png','degradation-fullscreen-1440.png','rate-limit-figure-light-1440.png','rate-limit-figure-dark-1440.png','rate-limit-source-1-1440.png','series-1440.png','rate-limit-ffmpeg-references.png','idempotency-ffmpeg-references.png','circuit-breaker-ffmpeg-references.png','degradation-ffmpeg-references.png','degradation-ffmpeg-body.png']
reviewed_child_desktop=[f'{slug}-figure-{theme}-1440.png'for slug in SLUGS[1:]for theme in ['light','dark']]+[f'{slug}-references-1440.png'for slug in SLUGS]+['circuit-breaker-source-2-1440.png']
reviewed_mobile=[f'{slug}-{kind}-390.png'for slug in SLUGS for kind in ['fullscreen','references','figure-light','figure-dark']]+['rate-limit-source-1-390.png','series-390.png']
entries=[]
for reviewer,folder,files in [('Codex siteqa','desktop',reviewed_main_desktop),('Codex siteqa/qa_review','desktop',reviewed_child_desktop),('Codex siteqa','mobile',reviewed_mobile)]:
 for filename in files:
  path=DEST/folder/filename;assert path.is_file();entries.append({'reviewer':reviewer,'file':str(path.relative_to(DEST)),'sha256':sha(path),'method':'view_image of original PNG; no contact sheet'})
assert len({e['file']for e in entries})==42
write(DEST/'actual-image-review.json',{'candidate':CANDIDATE,'reviewedImageCount':42,'images':entries,'findings':['All four body Fullscreen screenshots show the intended dark teal/cyan header family and a single burned caption while the native track is disabled.','All eight desktop and all eight mobile light/dark Figure screenshots fit the article column with visible captions, seek and original-image links; corrected JPEG hue matches the actual movie PNG.','Desktop bibliography titles/identities are clear above native controls without native/narration caption remnants. Mobile portrait embedded bibliography stays unobscured but is small; no physical/landscape readability claim.','Desktop/mobile SourceQuote examples keep quotation, explanation, identity, location and focused source link within the viewport.','Series/catalog and article screenshots show no unexpected clipping or overlapping app controls.'],'limits':report['limits']})
manifest=[{'file':str(path.relative_to(DEST)),'bytes':path.stat().st_size,'sha256':sha(path)}for path in sorted(DEST.rglob('*'))if path.is_file() and path.name!='artifact-manifest.json']
write(DEST/'artifact-manifest.json',{'candidate':CANDIDATE,'files':manifest})
print(json.dumps({'archive':str(DEST),'counts':counts,'reviewedImages':42,'files':len(manifest),'bytes':sum(x['bytes']for x in manifest)},ensure_ascii=False))
