#!/usr/bin/env python3
"""Recompute the bounded reference-policy adaptation proof; never generate audio/video."""
from pathlib import Path
import ast
import datetime
import hashlib
import importlib.util
import json
import re
import subprocess

A = Path(__file__).resolve().parent
D = A.parents[1]
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
BEFORE = json.loads((A / 'before-snapshot.json').read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def value_sha(v):
    return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def diff(a, b, path='$'):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        return sorted([path + '.' + k for k in a.keys() ^ b.keys()] +
                      [q for k in a.keys() & b.keys()
                       for q in diff(a[k], b[k], path + '.' + k)])
    if isinstance(a, list):
        return [path + '.length'] if len(a) != len(b) else [
            q for i, (x, y) in enumerate(zip(a, b)) for q in diff(x, y, f'{path}[{i}]')]
    return [] if a == b else [path]


def narration(script):
    shots = re.findall(r'^旁白：(.*)$', script, re.M)
    sentences = [s for shot in shots for s in re.findall(r'[^。？！]+[。？！]?', shot) if s.strip()]
    assert len(shots) == 10 and len(sentences) == 20
    return sentences


for f, expected in BEFORE['archivedOriginalBytes'].items():
    assert sha(A / f) == expected, ('Archive changed', f)
unchanged = {f: sha(ROOT / f) for f in BEFORE['immutableSHA256']}
assert unchanged == BEFORE['immutableSHA256'], diff(BEFORE['immutableSHA256'], unchanged)
old_script = (A / 'script.md').read_text()
new_script = (D / 'script.md').read_text()
old_phrase = '默认含原始题名/可选连续原文参考资料附录'
new_phrase = '默认含原题与机构参考资料列表'
assert old_script.count(old_phrase) == 1
assert new_script == old_script.replace(old_phrase, new_phrase)
assert narration(old_script) == narration(new_script)
assert (D / 'voice/sents.json').read_bytes() == (A / 'voice/sents.json').read_bytes()
sents = read(D / 'voice/sents.json')
assert [q['text'] for q in sents] == narration(new_script)
ledger = read(D / 'voice/script-narration-sha256.json')
narration_sha = hashlib.sha256(''.join(narration(new_script)).encode()).hexdigest()
assert narration_sha == ledger['narrationSHA256'] == read(A / 'voice/script-narration-sha256.json')['narrationSHA256']
assert ledger['scriptSHA256'] == sha(D / 'script.md')
old_words, new_words = read(A / 'words.json'), read(D / 'words.json')
assert diff(old_words, new_words) == ['$.scriptSha256']
assert new_words['scriptSha256'] == sha(D / 'script.md')
old_sb, new_sb = read(A / 'storyboard.json'), read(D / 'storyboard.json')
assert diff(old_sb, new_sb) == ['$.meta.timingSource']
assert old_sb['scenes'] == new_sb['scenes']
assert (D / 'storyboard.json').read_bytes() == (D / 'remotion/src/placeholders/storyboard.json').read_bytes()
assert new_sb['meta']['timingSource'] == (
    f"voice.wav {sha(D / 'voice.wav')[:8]} + words.json {sha(D / 'words.json')[:8]} + script.md {sha(D / 'script.md')[:8]}")
for key, expected in {'fps': 30, 'width': 1920, 'height': 1080,
                      'durationInFrames': 4482, 'finalVideoFrames': 4482}.items():
    assert old_sb['meta'][key] == new_sb['meta'][key] == expected
assert old_sb['meta']['covers'] == new_sb['meta']['covers'] == read(D / 'covers.json')
for f in ['captions.srt', 'voice/shot_frames.json', 'voice/cues.json', 'voice/cue_tests.json']:
    assert (D / f).read_bytes() == (A / f).read_bytes(), f
approvals = {}
for f in ['qa-technical-independent.json', 'qa-script-independent.json']:
    report = read(D / f)
    assert report['status'] == 'approved-for-tts'
    assert report['scriptSHA256'] == sha(A / 'script.md')
    assert (D / f).read_bytes() == (A / f).read_bytes()
    approvals[f] = {'SHA256': sha(D / f), 'actualApprovedScriptSHA256': report['scriptSHA256'],
                    'historicalBytesAndIdentityPreserved': True}
refs = read(D / 'references.json')
assert refs['presentation'] == 'title-author'
assert all('author' not in s and s['organization'] == 'Redis' for s in refs['sources'])
old_refs = read(A / 'references.json')
assert refs['sources'] == old_refs['sources']
assert diff(old_refs, refs) == ['$.presentation', '$.scope']
appender_path = ROOT / 'episodes-codex/_shared/append_references_bibliography.py'
spec = importlib.util.spec_from_file_location('policy_appender', appender_path)
appender = importlib.util.module_from_spec(spec)
spec.loader.exec_module(appender)
loaded = appender.load_references(D / 'references.json')
bibliography = appender.bibliography(loaded)
assert bibliography == [{'id': 'R1', 'title': 'Redis sorted sets', 'credit': 'Redis'},
                        {'id': 'R2', 'title': 't_zset.c', 'credit': 'Redis'}]
checks = []
commands = [['node', str(ROOT / 'site/scripts/check-references.mjs'), '--sources', str(D)]]
commands += [['python3', str(D / f), '--help'] for f in ['freeze.py', 'sync_site.py', 'verify_published.py']]
for command in commands:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    checks.append({'argv': command, 'exitCode': result.returncode, 'stdout': result.stdout,
                   'stderr': result.stderr})
for f in ['freeze.py', 'sync_site.py', 'verify_published.py']:
    ast.parse((D / f).read_text(), filename=f)
spec = importlib.util.spec_from_file_location('policy_freezer', D / 'freeze.py')
freezer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(freezer)
extras = freezer.production_extras()
for name in ['append_references_bibliography.py', 'append_references_original.py', 'append_references.py']:
    assert ROOT / 'episodes-codex/_shared' / name in extras
current_files = ['script.md', 'storyboard.json', 'words.json', 'references.json', 'references.md',
                 'README.md', 'knoll-props.md', 'freeze.py', 'sync_site.py', 'verify_published.py',
                 'voice/input-provenance.json', 'voice/script-narration-sha256.json',
                 'remotion/src/placeholders/storyboard.json']
report = {
    'status': 'passed-bounded-metadata-preservation-awaiting-independent-review',
    'checkedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'EP40 new bibliography policy only; no TTS, voice build, audio placement, freeze, formal video render or publication. Card preview and independent PNG witnesses are separate reviews.',
    'archive': str(A.relative_to(D)), 'rawBeforeSnapshotSHA256': sha(A / 'before-snapshot.json'),
    'oldScriptSHA256': sha(A / 'script.md'), 'newScriptSHA256': sha(D / 'script.md'),
    'oldStoryboardSHA256': sha(A / 'storyboard.json'), 'newStoryboardSHA256': sha(D / 'storyboard.json'),
    'oldWordsSHA256': sha(A / 'words.json'), 'newWordsSHA256': sha(D / 'words.json'),
    'currentSHA256': {f: sha(D / f) for f in current_files},
    'scriptChange': {'kind': 'one non-narrated prolog phrase only', 'old': old_phrase, 'new': new_phrase,
                     'all20NarrationSentencesExact': True, 'narrationSHA256': narration_sha,
                     'preparedSentencesAndTTSRequestStringsByteIdentical': True,
                     'preparedSentsSHA256': sha(D / 'voice/sents.json')},
    'sharedCommandsActuallyRun': ['episodes/_shared/voice/prep.py --dir episodes-codex/redis-skiplist',
                                 'episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/redis-skiplist'],
    'canonicalAssemblyBoundedProjection': read(A / 'canonical-assemble-bounded-projection.json'),
    'canonicalRawOutputSHA256': sha(A / 'canonical-assembled-current-metadata-storyboard.json'),
    'finalStoryboardChangedFields': diff(old_sb, new_sb), 'wordsChangedFields': diff(old_words, new_words),
    'allScenesExact': True, 'oldAndNewScenesCanonicalSHA256': value_sha(new_sb['scenes']),
    'allSentenceCueSubtitleAndShotWindowsExact': True,
    'voiceSHA256': sha(D / 'voice.wav'), 'physicalPublicVoiceSHA256': sha(D / 'remotion/public/audio/voice.wav'),
    'bodyFrames': 4482, 'bodySeconds': 149.4, 'fps': 30, 'width': 1920, 'height': 1080,
    'coversExact': True, 'physicalPlaceholderByteIdentical': True,
    'captionsSRTByteIdentical': True, 'immutableInputCount': len(unchanged),
    'immutableSHA256': unchanged, 'originalTTSApprovals': approvals,
    'originalVoiceAndBodyQA': 'Original reports remain unchanged and bound to their actual704f script/66da storyboard identities. This report derives applicability only from exact preserved body objects, timing and PCM identity; it does not pretend earlier reviews used the new SHA.',
    'referencePolicy': {'presentation': refs['presentation'], 'layout': appender.LAYOUT,
                        'bibliography': bibliography, 'sourceCount': len(refs['sources']),
                        'pages': (len(refs['sources']) + 3) // 4, 'secondsPerPage': 5,
                        'appendixFrames': 150, 'finalExpectedFrames': 4632,
                        'researchSourceItemsAndQuotesExact': True,
                        'explicitPersonalAuthors': 0,
                        'generatorSHA256': sha(appender_path), 'dependencies': appender.dependencies()},
    'checks': checks, 'freezeProducerExtrasCount': len(extras),
    'readyForIndependentMetadataPreservationReview': True,
    'notClaimed': ['New full-script TTS approval', 'ASR or interior word alignment',
                   'new audio or repeated semantic listening', 'new independent PNG witnesses',
                   'final video or bibliography card visual approval', 'freeze/render/publication completion']}
assert report['voiceSHA256'] == report['physicalPublicVoiceSHA256'] == '0c48b0538985b74cce8e31e8ed6f45196ae03d6b2cdc09886b26eba2b9932805'
(D / 'qa-reference-policy-adaptation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
(D / 'qa-reference-policy-adaptation.md').write_text(
    '# EP40 参考资料显示策略适配\n\n'
    '已通过有界元数据保留检查，待独立复核及新资料卡预览。采用 `title-author`，每页最多4项、默认5秒；本期2项均显示 Redis 机构，共150帧。引文、定位、版本和核验日仍保留在研究记录，视频列表只显示原题和机构。\n\n'
    f'旧 full script `{report["oldScriptSHA256"]}` → 新 `{report["newScriptSHA256"]}`。只改非口播前言的一处片尾说明，20句旁白与全部 TTS 请求字节不变。旧 script、SB66da、words、来源记录与旧审批原字节在归档中。\n\n'
    f'新 storyboard `{report["newStoryboardSHA256"]}`，唯一变动是 `meta.timingSource`；10镜完整 scenes、所有句窗/cue/字幕、封面、4482帧、30fps及1920×1080完全相同。共享 assemble 原始输出也保留；其中10个历史 shot.timing.source 被有界恢复为真实原始704f生成身份，避免改写历史来源。新 words 仅改 scriptSha256。\n\n'
    f'配音及实体公开 WAV SHA 均为 `{report["voiceSHA256"]}`；字幕SRT及{len(unchanged)}项约束文件逐字节相同。未重新 TTS、build、铺轨、冻结、正式渲染或发布。旧两份 TTS 审批和声轨/正文报告保留其实际旧 SHA，未改写成新 SHA 审批。\n\n'
    '新模式来源检查、bibliography 验证、三入口语法/帮助与三层 renderer 冻结输入声明均实际通过。独立帧复现、资料卡实看和最终编码属于后续独立闸门。完整 SHA、原始快照、命令回执和字段差异见同名 JSON。\n')
print(json.dumps({'status': report['status'], 'scriptSHA256': report['newScriptSHA256'],
                  'storyboardSHA256': report['newStoryboardSHA256'],
                  'proofSHA256': sha(D / 'qa-reference-policy-adaptation.json'),
                  'immutableFiles': len(unchanged)}, ensure_ascii=False))
