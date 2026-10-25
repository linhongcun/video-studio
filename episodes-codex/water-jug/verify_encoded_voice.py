#!/usr/bin/env python3
"""Read-only P03 audio content QA; this does not recognize speech or produce media.

Compare actual decoded AAC with voice.wav, then audit the intentional mixed
signal against premix plus the known constant-mode music source. Estimate lag
with FFT on a short probe; validate the complete aligned track and all actual
sentence sample ranges. No full-track brute-force lag scan or decoded files.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import wave

import numpy as np
from scipy.signal import correlate, correlation_lags

EPISODE = Path(__file__).resolve().parent
ROOT = EPISODE.parents[1]
SR = 48000
CHUNK = 262144
CRITERIA = {
    'minimumUnmixedWholeCorrelation': .99,
    'minimumUnmixedSentenceCorrelation': .98,
    'maximumAbsoluteUnmixedSampleOffset': 0,
    'maximumUnmixedAbsoluteGainDB': 1.0,
    'maximumMixedAbsoluteSampleOffset': 240,
    'maximumSentenceOffsetDeviationSamples': 2,
    'minimumMixedVoiceWholeCorrelation': .90,
    'minimumMixedVoiceSentenceCorrelation': .85,
    'minimumMixedTwoSourceWholeCorrelation': .995,
    'minimumMixedTwoSourceSentenceCorrelation': .99,
    'maximumMixedVoiceGainVariationDB': 1.0,
    'expectedVoiceAboveMusicRMSDB': 12.0,
    'voiceAboveMusicRMSDBTolerance': 2.0,
    'maximumAACPaddingSamples': 1024,
}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for part in iter(lambda: source.read(1024*1024), b''):
            digest.update(part)
    return digest.hexdigest()


def audio_stream(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)],
                            capture_output=True, text=True, check=True)
    streams = [s for s in json.loads(result.stdout)['streams'] if s['codec_type'] == 'audio']
    assert len(streams) == 1, (path, 'Expected exactly one audio stream')
    return {k: streams[0].get(k) for k in ['index','codec_name','sample_rate','channels',
            'channel_layout','start_time','duration','time_base','duration_ts']}


def decode(path, channel=None):
    command = ['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-vn']
    if channel is not None:
        command += ['-af',f'pan=mono|c0=c{channel}']
    command += ['-ac','1','-ar',str(SR),'-f','f32le','-']
    result = subprocess.run(command, capture_output=True, check=True)
    return np.frombuffer(result.stdout, dtype='<f4'), command


def moments(*arrays):
    n = len(arrays[0])
    assert n and all(len(a) == n for a in arrays)
    sums = np.zeros(len(arrays)); products = np.zeros((len(arrays),len(arrays)))
    for start in range(0,n,CHUNK):
        block = np.asarray([a[start:start+CHUNK] for a in arrays], dtype=np.float64)
        sums += block.sum(axis=1)
        products += block @ block.T
    return n,sums,products


def db(value):
    return 20*math.log10(value) if value > 0 else None


def fit_one(reference, decoded):
    n,s,p = moments(reference,decoded)
    gain = p[0,1]/p[0,0]
    covariance = p[0,1]-s[0]*s[1]/n
    denominator = math.sqrt(max(0,(p[0,0]-s[0]**2/n)*(p[1,1]-s[1]**2/n)))
    return dict(samples=n,correlation=float(covariance/denominator),fittedGain=float(gain),
                fittedGainDB=db(gain),residualRMSE=math.sqrt(max(0,p[1,1]-2*gain*p[0,1]+gain*gain*p[0,0])/n))


def fit_two(voice, music, mixed):
    n,s,p = moments(voice,music,mixed)
    coefficients = np.linalg.solve(p[:2,:2],p[:2,2])
    a,b = coefficients
    prediction_sum = a*s[0]+b*s[1]
    prediction_square = a*a*p[0,0]+2*a*b*p[0,1]+b*b*p[1,1]
    covariance = a*p[0,2]+b*p[1,2]-prediction_sum*s[2]/n
    denominator = math.sqrt(max(0,(prediction_square-prediction_sum**2/n)*(p[2,2]-s[2]**2/n)))
    residual_square = max(0,p[2,2]-2*(a*p[0,2]+b*p[1,2])+prediction_square)
    ratio = a*a*p[0,0]/(b*b*p[1,1]) if b else math.inf
    return dict(samples=n,reconstructedCorrelation=float(covariance/denominator),
                voiceFittedGain=float(a),voiceFittedGainDB=db(a),musicFittedGain=float(b),
                musicFittedGainDB=db(b),residualRMSE=math.sqrt(residual_square/n),
                voiceAboveMusicRMSDB=float(10*math.log10(ratio)),
                voiceInputSquareSum=float(p[0,0]),musicInputSquareSum=float(p[1,1]))


def offset(reference, decoded, start=0, end=None, center=0, radius=4800):
    end = min(len(reference), start+30*SR) if end is None else end
    decoded_start = max(0,start+center-radius)
    decoded_end = min(len(decoded),end+center+radius)
    x,y = reference[start:end],decoded[decoded_start:decoded_end]
    values = correlate(y,x,method='fft')
    lags = correlation_lags(len(y),len(x))+decoded_start-start
    candidates = np.flatnonzero(np.abs(lags-center) <= radius)
    assert len(candidates)
    return int(lags[candidates[np.argmax(values[candidates])]])


def aligned(reference, decoded, lag):
    ref_from,dec_from = max(0,-lag),max(0,lag)
    n = min(len(reference)-ref_from,len(decoded)-dec_from)
    assert n > 0
    return reference[ref_from:ref_from+n],decoded[dec_from:dec_from+n],dict(
        sampleOffset=lag,referenceCompareFrom=ref_from,decodedCompareFrom=dec_from,
        commonAlignedSamples=n,uncomparedReferenceSamples=len(reference)-n,
        uncomparedDecodedSamples=len(decoded)-n)


def compare(reference, decoded, sentences):
    lag = offset(reference,decoded)
    x,y,coverage = aligned(reference,decoded,lag)
    rows = []
    for sentence in sentences:
        a,b = sentence['startSample'],sentence['endSample']
        assert a+lag >= 0 and b+lag <= len(decoded), (sentence['id'],'Uncovered speech samples')
        local = offset(reference,decoded,a,b,center=lag,radius=16)
        rows.append(dict(id=sentence['id'],startSample=a,endSample=b,sampleOffset=local,
                         offsetDeviationSamples=local-lag,**fit_one(reference[a:b],decoded[a+lag:b+lag])))
    return dict(**coverage,whole=fit_one(x,y),sentenceCount=len(rows),
                minimumSentenceCorrelation=min(r['correlation'] for r in rows),sentences=rows)


def frozen_snapshot():
    manifest = json.loads((EPISODE/'source-sha256.json').read_text())
    actual = {relative:sha(EPISODE/relative) for relative in manifest}
    assert manifest == actual, 'Frozen production inputs differ from their manifest'
    return actual


def main():
    before = frozen_snapshot()
    reference_path = EPISODE/'voice.wav'
    premix_path = EPISODE/'remotion/out/voice.mp4'
    mixed_path = EPISODE/'video.mp4'
    bgm_path = ROOT/'episodes/_shared/music/Wallpaper.mp3'
    report_path = EPISODE/'remotion/out/mix-report.json'
    for path in [premix_path,mixed_path,report_path]:
        assert path.is_file(), f'Actual completed media required: {path}'
    words = json.loads((EPISODE/'words.json').read_text())
    build = json.loads((EPISODE/'voice/build.json').read_text())
    sentences = build['sentences']
    config = json.loads((EPISODE/'episode-config.json').read_text())
    assert len(sentences) == 2*config['shotCount']
    assert sha(reference_path) == words['audioSha256']
    with wave.open(str(reference_path)) as handle:
        assert (handle.getframerate(),handle.getnchannels(),handle.getsampwidth()) == (SR,1,2)
        reference = np.frombuffer(handle.readframes(handle.getnframes()),'<i2').astype(np.float32)/32768
    assert len(reference) == words['durationFrames']*1600
    pre_meta,mix_meta = audio_stream(premix_path),audio_stream(mixed_path)
    assert int(pre_meta['channels']) in [1,2] and int(mix_meta['channels']) == 2
    assert int(pre_meta['sample_rate']) == int(mix_meta['sample_rate']) == SR
    premix,pre_command = decode(premix_path)
    unmixed = compare(reference,premix,sentences)
    failures = []
    def require(condition,reason):
        if not condition: failures.append(reason)
    require(unmixed['sampleOffset'] == 0,'Premix has a nonzero sample offset')
    require(unmixed['uncomparedReferenceSamples'] == 0,'Premix does not cover the entire reference')
    require(0 <= len(premix)-len(reference) <= CRITERIA['maximumAACPaddingSamples'],'Unexpected premix sample count/padding')
    require(unmixed['whole']['correlation'] >= CRITERIA['minimumUnmixedWholeCorrelation'],'Premix whole correlation is low')
    require(unmixed['minimumSentenceCorrelation'] >= CRITERIA['minimumUnmixedSentenceCorrelation'],'A premix sentence correlation is low')
    require(abs(unmixed['whole']['fittedGainDB']) <= CRITERIA['maximumUnmixedAbsoluteGainDB'],'Premix gain differs materially')
    require(all(abs(r['offsetDeviationSamples']) <= 2 for r in unmixed['sentences']),'Premix sentence offsets drift')
    mixed,mix_command = decode(mixed_path)
    pre_reference = premix[:len(reference)]
    mixed_voice = compare(pre_reference,mixed,sentences)
    mix_lag = mixed_voice['sampleOffset']
    require(abs(mix_lag) <= CRITERIA['maximumMixedAbsoluteSampleOffset'],'Mixed track delay exceeds 5ms')
    require(mixed_voice['whole']['correlation'] >= CRITERIA['minimumMixedVoiceWholeCorrelation'],'Voice-to-mix whole correlation is low')
    require(mixed_voice['minimumSentenceCorrelation'] >= CRITERIA['minimumMixedVoiceSentenceCorrelation'],'A mixed sentence lost voice correlation')
    require(all(abs(r['offsetDeviationSamples']) <= 2 for r in mixed_voice['sentences']),'Mixed sentence offsets drift')
    music,_ = decode(bgm_path)
    assert len(music) >= len(premix), 'This P03 audit assumes the known 220s music needs no loop'
    fade = np.ones(len(premix),np.float32)
    fade[:SR] = np.linspace(0,1,SR)
    fade[-2*SR:] *= np.linspace(1,0,2*SR)
    music_reference = music[:len(premix)]*fade
    start = mixed_voice['referenceCompareFrom']; n = mixed_voice['commonAlignedSamples']
    final_start = mixed_voice['decodedCompareFrom']
    whole_fit = fit_two(pre_reference[start:start+n],music_reference[start:start+n],mixed[final_start:final_start+n])
    two_rows = []
    for sentence in sentences:
        a,b = sentence['startSample'],sentence['endSample']
        two_rows.append(dict(id=sentence['id'],**fit_two(pre_reference[a:b],music_reference[a:b],mixed[a+mix_lag:b+mix_lag])))
    minimum_two = min(r['reconstructedCorrelation'] for r in two_rows)
    gain_variation = max(abs(r['voiceFittedGainDB']-whole_fit['voiceFittedGainDB']) for r in two_rows)
    voice_energy = sum(r['voiceInputSquareSum'] for r in two_rows)*whole_fit['voiceFittedGain']**2
    music_energy = sum(r['musicInputSquareSum'] for r in two_rows)*whole_fit['musicFittedGain']**2
    speech_ratio = 10*math.log10(voice_energy/music_energy)
    require(whole_fit['reconstructedCorrelation'] >= CRITERIA['minimumMixedTwoSourceWholeCorrelation'],'Known-source mix reconstruction is low')
    require(minimum_two >= CRITERIA['minimumMixedTwoSourceSentenceCorrelation'],'A sentence fails known-source reconstruction')
    require(whole_fit['voiceFittedGain'] > 0 and whole_fit['musicFittedGain'] > 0,'Voice or intended music contribution missing')
    require(gain_variation <= CRITERIA['maximumMixedVoiceGainVariationDB'],'Voice gain varies materially between sentences')
    require(abs(speech_ratio-12) <= 2,'Known speech-window music level is not approximately 12dB below voice')
    mix_report = json.loads(report_path.read_text())
    require(mix_report['mode']=='constant' and abs(mix_report['voice_minus_bgm_rms_speech_dB']-12)<=.5,'Production mix settings differ from the audited contract')
    channel_checks = []
    for channel in range(2):
        native_pre,_ = decode(premix_path,channel=channel if int(pre_meta['channels'])==2 else 0)
        native_mix,_ = decode(mixed_path,channel=channel)
        native_music,_ = decode(bgm_path,channel=channel)
        assert len(native_music) >= len(premix)
        channel_voice = fit_one(reference,native_pre[:len(reference)])
        channel_fit = fit_two(native_pre[start:start+n],native_music[start:start+n]*fade[start:start+n],native_mix[final_start:final_start+n])
        require(channel_voice['correlation'] >= .99 and channel_voice['fittedGain'] > 0,f'Premix channel {channel} does not contain the source voice')
        require(channel_fit['reconstructedCorrelation'] >= .99 and channel_fit['voiceFittedGain'] > 0 and channel_fit['musicFittedGain'] > 0,f'Mixed channel {channel} does not match the known sources')
        channel_checks.append(dict(channel=channel,premixVersusMonoSource=channel_voice,mixedKnownSources=channel_fit))
    after = frozen_snapshot(); assert before == after
    result = dict(checkedAtUTC=datetime.now(timezone.utc).isoformat(),executor='/root/horse_voice',
        scope='Numerical waveform and source-content consistency only. No ASR, pronunciation, voice-isolation or listening claim.',
        reference='voice.wav',referenceSHA256=sha(reference_path),referenceSamples=len(reference),sampleRate=SR,
        unmixed='remotion/out/voice.mp4',unmixedSHA256=sha(premix_path),unmixedStream=pre_meta,
        mixed='video.mp4',mixedSHA256=sha(mixed_path),mixedStream=mix_meta,
        decodeCommands=[pre_command,mix_command],lagProbeSamples=min(len(reference),30*SR),
        lagSearchSamples=[-4800,4800],perSentenceLagSearchRadius=16,
        offsetConvention='decoded[t + sampleOffset] corresponds to reference[t]; positive means decoded is delayed.',
        unmixedComparison=unmixed,mixedVersusPremix=mixed_voice,
        intentionalMixModel=dict(bgm='episodes/_shared/music/Wallpaper.mp3',bgmSHA256=sha(bgm_path),
            constantMode=True,fadeInSamples=SR,fadeOutSamples=2*SR,loopRequired=False,
            note='Known BGM is longer than this episode. Regression estimates gains; it does not rerun production normalization or limiting.',
            whole=whole_fit,minimumSentenceReconstructedCorrelation=minimum_two,
            maximumSentenceVoiceGainDeviationDB=gain_variation,speechWindowVoiceAboveMusicRMSDB=speech_ratio,sentences=two_rows),
        nativeChannelChecks=channel_checks,productionMixReport=mix_report,criteria=CRITERIA,
        failures=failures,passed=not failures,frozenInputsChecked=len(before),frozenInputsUnchanged=True,
        limitations=['AAC is lossy and may include codec tail padding.',
            'Final loudnorm/alimiter may cause a fixed small delay; the actual delay is reported separately.',
            'Waveform/source matching cannot determine spoken words, numerical pronunciation or human understanding.',
            'The two-source regression checks this constant-mode known-music mix; it is not blind source separation.'])
    (EPISODE/'qa-encoded-voice-content.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],frames=words['durationFrames'],unmixedOffset=unmixed['sampleOffset'],
        unmixedWholeCorrelation=unmixed['whole']['correlation'],unmixedMinimumSentenceCorrelation=unmixed['minimumSentenceCorrelation'],
        mixedOffset=mix_lag,mixedKnownSourceCorrelation=whole_fit['reconstructedCorrelation'],
        minimumMixedSentenceKnownSourceCorrelation=minimum_two,speechWindowVoiceAboveMusicRMSDB=speech_ratio,failures=failures),ensure_ascii=False))
    if failures: raise SystemExit(1)


def selftest():
    rng = np.random.default_rng(20261025)
    x = rng.normal(size=50000).astype(np.float32)
    delayed = np.concatenate([np.zeros(37,np.float32),x*1.25,np.zeros(100,np.float32)])
    assert offset(x,delayed,end=30000,radius=100)==37
    fit = fit_one(x,delayed[37:37+len(x)])
    assert fit['correlation'] > .999999 and abs(fit['fittedGain']-1.25)<1e-6
    z = rng.normal(size=len(x)).astype(np.float32)
    fit = fit_two(x,z,.8*x+.2*z)
    assert fit['reconstructedCorrelation'] > .999999 and abs(fit['voiceFittedGain']-.8)<1e-6 and abs(fit['musicFittedGain']-.2)<1e-6
    print('FFT offset convention and one/two-source fits passed synthetic numerical self-checks; no media read or written.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selftest',action='store_true')
    args=parser.parse_args()
    if args.selftest:selftest()
    else:main()
