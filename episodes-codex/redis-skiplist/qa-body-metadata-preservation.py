#!/usr/bin/env python3
"""Independent dependency proof for applying the old body QA to metadata-only SB.

Does not overwrite the original 231-sample/2-clip report or approve the new card.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, re, shutil

D = Path(__file__).resolve().parent
R = D.parents[1]
B = D / 'qa-revisions/reference-policy-adaptation'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def canonical(v): return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def differences(a, b, path='$'):
    if type(a) != type(b): return [{'path': path, 'old': a, 'new': b}]
    if isinstance(a, dict):
        return sum((differences(a.get(k), b.get(k), path + '.' + str(k)) for k in sorted(set(a) | set(b))), [])
    if isinstance(a, list):
        if len(a) != len(b): return [{'path': path + '.length', 'old': len(a), 'new': len(b)}]
        return sum((differences(x, y, path + '[' + str(i) + ']') for i, (x, y) in enumerate(zip(a, b))), [])
    return [] if a == b else [{'path': path, 'old': a, 'new': b}]

def main():
    assertions = Counter()
    def check(v, name):
        assertions[name] += 1
        if not v: raise AssertionError(name)
    before = load(B / 'before-snapshot.json')
    producer = load(D / 'qa-reference-policy-adaptation.json')
    old_render = load(D / 'qa-preflight-evidence/samples.json')
    old_gate = load(D / 'qa-preflight.json')
    old_sb, new_sb = load(B / 'storyboard.json'), load(D / 'storyboard.json')
    old_words, new_words = load(B / 'words.json'), load(D / 'words.json')
    old_script, new_script = (B / 'script.md').read_text(), (D / 'script.md').read_text()
    check(sha(B / 'storyboard.json') == old_render['sourceSHA']['episodes-codex/redis-skiplist/storyboard.json'] == '66da8fe0d4a9d7cd9ff021e4d4c90be44ebecddef8485868ce88eef63fc7c04f', 'original-SB-is-exact-old-render-input')
    check(old_gate['inputs']['storyboard.json'] == sha(B / 'storyboard.json'), 'original-preflight-remains-old-input-bound')
    for p, h in before['archivedOriginalBytes'].items(): check(sha(B / p) == h, 'archived-original-bytes-preserved')
    for p, h in before['immutableSHA256'].items(): check(sha(R / p) == h, 'independent-current-immutable-file-SHA')
    check(producer['status'] == 'passed-bounded-metadata-preservation-awaiting-independent-review' and producer['newStoryboardSHA256'] == sha(D / 'storyboard.json'), 'producer-proof-current-input-bound')
    sb_diff = differences(old_sb, new_sb)
    words_diff = differences(old_words, new_words)
    check([r['path'] for r in sb_diff] == ['$.meta.timingSource'], 'only-unread-storyboard-metadata-changed')
    check([r['path'] for r in words_diff] == ['$.scriptSha256'], 'only-words-full-script-identity-changed')
    check(new_words['scriptSha256'] == sha(D / 'script.md'), 'new-words-script-identity-correct')
    check(old_sb['scenes'] == new_sb['scenes'], 'every-complete-scene-exact')
    for k in ['width', 'height', 'fps']:
        check(old_sb['meta'][k] == new_sb['meta'][k], 'Root-actually-read-meta-field-unchanged')
    check((new_sb['meta']['width'], new_sb['meta']['height'], new_sb['meta']['fps']) == (1920, 1080, 30), 'actual-body-format-preserved')
    check(sum(s['durationInFrames'] for c in new_sb['scenes'] for s in c['shots']) == 4482, 'Root-actual-summed-duration-preserved')
    check(old_sb['meta']['covers'] == new_sb['meta']['covers'] == load(D / 'covers.json'), 'full-covers-alias-and-SB-copy-preserved')
    check(sha(D / 'remotion/src/placeholders/storyboard.json') == sha(D / 'storyboard.json'), 'physical-placeholder-exact-new-storyboard')
    check(sha(B / 'remotion/src/placeholders/storyboard.json') == sha(B / 'storyboard.json'), 'archived-placeholder-exact-old-storyboard')
    old_phrase = '默认含原始题名/可选连续原文参考资料附录'
    new_phrase = '默认含原题与机构参考资料列表'
    check(old_script.replace(old_phrase, new_phrase) == new_script and old_script.count(old_phrase) == 1, 'script-only-one-non-narrated-prolog-phrase')
    narrations = lambda t: re.findall(r'^旁白：(.*)$', t, re.M)
    old_lines, new_lines = narrations(old_script), narrations(new_script)
    check(old_lines == new_lines and len(new_lines) == 10, 'all-ten-narration-lines-byte-identical')
    sentences = [p for line in new_lines for p in re.split(r'(?<=[。！？])', line) if p]
    prepared = load(D / 'voice/sents.json')
    check(len(sentences) == 20 and sentences == [s['text'] for s in prepared], 'independently-parsed20sentences-match-real-TTS-input')
    check((B / 'voice/sents.json').read_bytes() == (D / 'voice/sents.json').read_bytes(), 'all20prepared-and-TTS-request-strings-byte-identical')
    check((B / 'captions.srt').read_bytes() == (D / 'captions.srt').read_bytes(), 'physical-SRT-byte-identical')
    wav = sha(D / 'voice.wav')
    check(wav == sha(D / 'remotion/public/audio/voice.wav') == '0c48b0538985b74cce8e31e8ed6f45196ae03d6b2cdc09886b26eba2b9932805', 'actual-voice-and-public-voice-exact-original')
    preserved_body_sources = {}
    for p, h in old_render['sourceSHA'].items():
        if p.endswith('/storyboard.json'): continue
        check(sha(R / p) == h, 'each-other-rendered-body-source-byte-identical')
        preserved_body_sources[p] = h
    # Verify the actual import/read contract; no production algorithm is used.
    main_source = (D / 'remotion/src/Main.tsx').read_text()
    root_source = (D / 'remotion/src/Root.tsx').read_text()
    check('storyboard.scenes' in main_source and 'timingSource' not in main_source + root_source, 'actual-Main-Root-do-not-read-changed-metadata')
    check(all('storyboard.meta.' + k in root_source for k in ['width', 'height', 'fps']), 'actual-Root-read-contract-explicit')
    witness_path = D / 'remotion/out/body-metadata-preservation/witness.json'
    witness = load(witness_path)
    check(witness['status'] == 'passed' and [r['frame'] for r in witness['frames']] == [2072, 3134, 3798], 'three-actual-witness-renders-completed')
    check(witness['sourceSHA']['episodes-codex/redis-skiplist/storyboard.json'] == sha(D / 'storyboard.json'), 'witness-read-new-storyboard')
    target = D / 'qa-preflight-evidence/metadata-preservation';target.mkdir(exist_ok=True)
    evidence = []
    for row in witness['frames']:
        check(row['byteIdenticalToOriginalFinalPreflight'] and row['sha256'] == row['oldSHA256'] == sha(row['file']), 'new-SB-actual-witness-PNG-byte-identical')
        check(row['actualDOMViolations'] == 0, 'new-SB-actual-witness-DOM-clean')
        out = target / Path(row['file']).name;shutil.copy2(row['file'], out)
        evidence.append({'frame': row['frame'], 'retained': str(out.relative_to(D)), 'sha256': sha(out), 'oldOriginalSHA256': row['oldSHA256']})
    shutil.copy2(witness_path, target / 'witness.json')
    canonical_sb = load(B / 'canonical-assembled-current-metadata-storyboard.json')
    raw_diffs = differences(old_sb, canonical_sb)
    check(len(raw_diffs) == 11 and all(r['path'] == '$.meta.timingSource' or re.fullmatch(r'\$\.scenes\[\d+\]\.shots\[\d+\]\.timing\.source', r['path']) for r in raw_diffs), 'canonical-assembly-difference-is-only-provenance-descriptions')
    for p, h in witness['sourceSHA'].items():check(sha(R / p) == h, 'rendered-source-still-unchanged-at-final-check')
    report = {'status': 'passed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(), 'scope': 'Independent preservation proof applying original body-only231-DOM/2-clip QA to a new storyboard whose only changed value is unread meta.timingSource.', 'approvedForSourceFreezeAndFullRender': True, 'oldFullStoryboardSHA256': sha(B / 'storyboard.json'), 'newFullStoryboardSHA256': sha(D / 'storyboard.json'), 'oldFullScriptSHA256': sha(B / 'script.md'), 'newFullScriptSHA256': sha(D / 'script.md'), 'oldWordsSHA256': sha(B / 'words.json'), 'newWordsSHA256': sha(D / 'words.json'), 'actualStoryboardDifferences': sb_diff, 'actualWordsDifferences': words_diff, 'scenesExact': True, 'scenesCanonicalSHA256': canonical(new_sb['scenes']), 'actualRootMetadata': {k: new_sb['meta'][k] for k in ['width', 'height', 'fps']}, 'actualBodyFrames': 4482, 'actualRenderReadContract': ['Main:complete storyboard.scenes and all shot/voice/cue/subtitle contents', 'Root:storyboard.scenes shot durations plus meta.width,height,fps', '@covers:complete unchanged covers.json', 'Audio:unchanged physical public/audio/voice.wav', 'All other18 previously bound body dependencies remain byte-identical'], 'preservedBodySourceSHA256': preserved_body_sources, 'narrationLinesByteIdentical': 10, 'narrationSentencesExact': 20, 'TTSRequestBytesExact': True, 'actualVoiceSHA256': wav, 'archivedOriginalFilesRehashed': len(before['archivedOriginalBytes']), 'immutableFilesIndependentlyRehashed': len(before['immutableSHA256']), 'assertionsExecuted': sum(assertions.values()), 'assertionsByCategory': dict(assertions), 'actualWitnesses': evidence, 'witnessReportSHA256': sha(target / 'witness.json'), 'producerProofSHA256': sha(D / 'qa-reference-policy-adaptation.json'), 'originalBodyQARetainedWithOldIdentity': {p: sha(D / p) for p in ['qa-preflight.json', 'qa-dom-independent.json', 'qa-motion-independent.json', 'qa-preflight-evidence/samples.json']}, 'canonicalRawAssemblySHA256': sha(B / 'canonical-assembled-current-metadata-storyboard.json'), 'canonicalRawAssemblyProvenanceDifferenceCount': len(raw_diffs), 'mustFixRemaining': [], 'notClaimed': ['The old QA reports have not been rebound or rewritten to claim rendering newSB.', 'No new TTS or repeated231-frame/2-clip full preflight.', 'This body proof does not approve the changed reference card; it requires its own actual bibliography/receipt/final-media QA.', 'No final encoded-film or human full listening conclusion.'], 'checkerSHA256': sha(__file__), 'witnessRendererSHA256': sha(D / 'qa-body-metadata-preservation.mjs')}
    (D / 'qa-body-metadata-preservation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (D / 'qa-body-metadata-preservation.md').write_text('独立正文依赖保留证明通过，可冻结并渲染。\n\n旧SB66da与新SB ed3c的完整递归差异只有未被Main/Root读取的meta.timingSource。全部scenes、真实尺寸/帧率、4482帧、covers、18项其他实际渲染依赖均保持；25份旧快照与168个约束文件已重新计算SHA。旁白10行/20句及全部真实TTS请求字节相同，voice/public WAV仍为0c48，字幕与句窗未动。\n\n新SB实际渲染2072、3134、3798三帧，PNG与旧最终预检对应图逐字节一致，真实DOM无违规。证据保留于qa-preflight-evidence/metadata-preservation。原231时点/2clips报告继续保留66da输入身份，不伪称重渲新SHA。新参考卡须独立审查，此证明只覆盖正文；不替代最终成片与声音复验。\n')
    print(json.dumps({'status': report['status'], 'assertions': report['assertionsExecuted'], 'newStoryboardSHA256': report['newFullStoryboardSHA256'], 'actualPNGByteWitnesses': 3, 'approvedForFreeze': True}))
if __name__ == '__main__': main()
