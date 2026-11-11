"""Read the encoded artifact and write bounded factual QA; never mutate production inputs."""
from pathlib import Path
import collections,datetime,hashlib,json,subprocess
D=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
video=D/'video.mp4';words=json.loads((D/'words.json').read_text());receipt=json.loads((D/'reference-appendix.json').read_text());result=json.loads((D/'render-result.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));vs=next(s for s in probe['streams']if s['codec_type']=='video');aus=next(s for s in probe['streams']if s['codec_type']=='audio')
frames=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,width,height,pix_fmt,color_range,color_space,color_transfer,color_primaries','-of','json',str(video)]))['frames']
body=words['durationFrames'];total=body+150;digest=sha(video);assert len(frames)==int(vs['nb_frames'])==receipt['finalVideoFrames']==result['frames']==total
assert receipt['bodyFrames']==body and result['publicationMetadata']['referenceAppendix']['from']==body
assert digest==receipt['outputSHA256']==result['sha256'];assert(vs['width'],vs['height'],vs['r_frame_rate'])==(1920,1080,'30/1');assert int(aus['sample_rate'])==48000
want={'pix_fmt':'yuv420p','color_range':'tv','color_space':'bt709','color_transfer':'bt709','color_primaries':'bt709'}
violations=[{'frame':i,'fields':{k:f.get(k)for k,v in want.items()if f.get(k)!=v}}for i,f in enumerate(frames)if any(f.get(k)!=v for k,v in want.items())];assert not violations,violations[:2]
pts=[float(f['best_effort_timestamp_time'])for f in frames];maxerror=max(abs(t-i/30)for i,t in enumerate(pts));assert maxerror<.00001 and all(b>a for a,b in zip(pts,pts[1:]))
mix=json.loads((D/'remotion/out/mix-report.json').read_text());assert abs(mix['final_LUFS']+16)<=.3 and mix['true_peak_dBTP']<=-2
report={'status':'passed-encoded-frame-and-identity-checks','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'video.mp4','sha256':digest,'bytes':video.stat().st_size,'bodyFrames':body,'finalFrames':total,'durationSeconds':total/30,'video':{k:vs.get(k)for k in ['codec_name','width','height','r_frame_rate',*want]},'audio':{k:aus.get(k)for k in ['codec_name','sample_rate','channels','duration']},'allVideoFramesInspected':len(frames),'allFrameColorFields':want,'allFrameColorViolations':violations,'PTS':{'first':pts[0],'last':pts[-1],'strictlyIncreasing':True,'maxAbsoluteErrorFromNOver30':maxerror},'mix':{'finalLUFS':mix['final_LUFS'],'truePeakDBTP':mix['true_peak_dBTP']},'referenceFramesInclusive':[body,total-1],'referenceDurationFrames':150,'limitations':['Metadata, everydecodedvideo-framePTS andcolors, completeartifactSHA andreceipt/mixidentity only.','No semantic listening, wordASR, realtime viewing orinteractiveplayerreview is claimed. Independentvisualreview isseparate.']}
(D/'qa/final-media-technical.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':report['status'],'sha256':digest,'frames':total,'report':'qa/final-media-technical.json'}))
