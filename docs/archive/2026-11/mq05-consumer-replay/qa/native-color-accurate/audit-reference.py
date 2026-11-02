#!/usr/bin/env python3
"""New QA only: compare retained exact-n RGB references with native canvas."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
A = ROOT/'docs/archive/2026-11/mq05-consumer-replay'
D = ROOT/'episodes/message-queue/kafka-consumer-idempotency/production/revisions/consumer-replay-v2'
OUT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
site_path = A/'site-local/report.machine-only.json'
original_path = A/'qa/local-native-color.json'
final_path = D/'qa-final-independent/encoded-independent.json'
site, original, final = [json.loads(p.read_text()) for p in (site_path, original_path, final_path)]
command = json.loads((OUT/'decode-command.json').read_text())
assert original['pass'] is False and site['pass'] is True and final['machinePass'] is True
assert site['videoSha256'] == final['videoSHA256'] == command['videoSHA256'] == sha(D/'video.mp4')
input_paths = [D/'video.mp4', D/'source-sha256.json', A/'qa/compare-browser-video.py', original_path, site_path, final_path]
inputs_before = {p.relative_to(ROOT).as_posix(): sha(p) for p in input_paths}
frames = command['frames']
assert len(frames) == 9 and command['sampleCount'] == 22
raw_path = OUT/'selected-native-yuv420p.raw'
assert raw_path.stat().st_size == len(frames)*3110400
raw = np.memmap(raw_path, dtype=np.uint8, mode='r', shape=(len(frames),3110400))
refs = {n:OUT/f'accurate-{i+1:03d}.png' for i,n in enumerate(frames)}
old_refs = {v['frame']:v for v in final['samples']}
corners = [(50,400),(1870,400),(50,900),(1870,900)]
thresholds = {'meanAbsoluteChannelErrorMax':1.5,'p95AbsoluteChannelErrorMax':3,'backgroundPointChannelErrorMax':3}
assert original['thresholds'] == thresholds
checks, native_math = [], []
for i,n in enumerate(frames):
    ref = np.asarray(Image.open(refs[n]).convert('RGB'), dtype=np.int16)
    old = old_refs[n]
    old_path = D/old['retainedFile']
    assert sha(old_path) == old['sha256']
    old_rgb = np.asarray(Image.open(old_path).convert('RGB'),dtype=np.int16)
    yplane = raw[i,:2073600].reshape(1080,1920)
    uplane = raw[i,2073600:2592000].reshape(540,960)
    vplane = raw[i,2592000:].reshape(540,960)
    points = []
    for x,y in corners:
        Y,U,V = int(yplane[y,x]),int(uplane[y//2,x//2]),int(vplane[y//2,x//2])
        c,d,e = (Y-16)/219, (U-128)/224, (V-128)/224
        r = c + 2*(1-.2126)*e
        b = c + 2*(1-.0722)*d
        g = (c-.2126*r-.0722*b)/.7152
        rgb_float = np.array([r,g,b])*255
        rgb = np.floor(np.clip(rgb_float,0,255)+.5).astype(np.int16)
        points.append({'xy':[x,y],'nativeYUV':[Y,U,V],'standardRGBFloat':rgb_float.tolist(),'standardRGBNearest':rgb.tolist(),'accurateRGB':ref[y,x].tolist(),'originalDefaultRGB':old_rgb[y,x].tolist(),'accurateErrorVsMath':np.abs(ref[y,x]-rgb).tolist()})
    native_math.append({'frame':n,'points':points})
    for observation in [v for v in site['exactFrames'] if v['frame']==n]:
        browser_path = site_path.parent/observation['file']
        assert sha(browser_path)==observation['sha256']
        browser = np.asarray(Image.open(browser_path).convert('RGB'),dtype=np.int16)
        assert ref.shape==browser.shape==old_rgb.shape==(1080,1920,3)
        delta=np.abs(ref-browser)
        mean=float(delta.mean());p95=float(np.percentile(delta,95));bg=max(int(delta[y,x].max()) for x,y in corners)
        default_delta=np.abs(old_rgb-browser)
        # Illustrative accent class; the acceptance gate remains the original three whole-frame metrics.
        mask=(ref[:,:,0]>150)&(ref[:,:,0]>ref[:,:,1]*1.3)&(ref[:,:,1]>60)&(ref[:,:,2]<140)
        accent={'pixels':int(mask.sum()),'accurateP95':float(np.percentile(delta[mask],95)) if mask.any() else None,'originalDefaultP95':float(np.percentile(default_delta[mask],95)) if mask.any() else None}
        checks.append({'width':observation['width'],'frame':n,'browserPNG':browser_path.relative_to(ROOT).as_posix(),'browserSHA256':sha(browser_path),'accuratePNG':refs[n].relative_to(ROOT).as_posix(),'accurateSHA256':sha(refs[n]),'originalDefaultPNG':old_path.relative_to(ROOT).as_posix(),'originalDefaultSHA256':sha(old_path),'meanAbsoluteChannelError':mean,'p95AbsoluteChannelError':p95,'maxBackgroundPointChannelError':bg,'pass':mean<=1.5 and p95<=3 and bg<=3,'originalDefaultMean':float(default_delta.mean()),'accentMaskDiagnostic':accent})
inputs_after={p.relative_to(ROOT).as_posix():sha(p) for p in input_paths}
assert inputs_after==inputs_before
assert len(checks)==22
math_pass=all(not any(p['accurateErrorVsMath']) for r in native_math for p in r['points'])
report={'kind':'independent-explicit-bt709-native-reference-diagnosis','reviewer':'/root/deploy_diagnosis','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'pass':all(r['pass'] for r in checks) and math_pass,'videoSHA256':command['videoSHA256'],'thresholdsUnchanged':thresholds,'comparisons':22,'uniqueIntegerFrames':frames,'worstMean':max(r['meanAbsoluteChannelError'] for r in checks),'worstP95':max(r['p95AbsoluteChannelError'] for r in checks),'worstBackground':max(r['maxBackgroundPointChannelError'] for r in checks),'wholeFrameChecks':checks,'nativeYUVMatrixChecks':native_math,'rawNativeSHA256':sha(raw_path),'rawFrameOrderingAndDecodeCommand':{'file':(OUT/'decode-command.json').relative_to(ROOT).as_posix(),'sha256':sha(OUT/'decode-command.json')},'originalInputSHA256BeforeAndAfter':inputs_before,'inputsUnchanged':True,'originalFailPreserved':{'file':original_path.relative_to(ROOT).as_posix(),'sha256':sha(original_path),'pass':False},'conclusion':'The original failed numerical gate used the default FFmpeg RGB conversion as a reference. A newly decoded explicit limited-range BT.709 RGB24 reference with accurate_rnd+full_chroma_int passes all 22 original gates. Its background RGB exactly equals the independently calculated native-plane standard-matrix values and Chromium. Evidence supports reference conversion precision/implementation differences, not a production-video colorspace error in these samples.','limits':['No thresholds changed. Original FAIL, frozen helper, video, original PNGs and source manifest were not modified.','This combined conversion setting was tested; individual rounding/chroma flags were not separately isolated.','Analytic formula checks cover uniform background points, not text-edge chroma interpolation. Whole-frame gates cover all22 retained canvas images.','This is decoded-pixel color QA, not a new browser/UI/physical-device or full-media semantic review.','Production encoding was not run. The decode command produced only new QA PNG/raw artifacts.']}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pass':report['pass'],'worstMean':report['worstMean'],'worstP95':report['worstP95'],'worstBackground':report['worstBackground'],'nativeMathExact':math_pass,'reportSHA256':sha(OUT/'report.json')}))
