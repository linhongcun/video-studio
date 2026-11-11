#!/usr/bin/env python3
"""Directed identity supplement; preserves earlier audio QA and all production bytes."""
from pathlib import Path
import datetime
import hashlib
import json
import os

OUT = Path(__file__).resolve().parent
ROOT = next(p for p in OUT.parents if (p / 'AGENTS.md').is_file())
EP = ROOT / 'episodes/puzzles/twelve-balls/production/revisions/logic-20261111/twelve-balls'
OLD_SCOPE = 'Pending independent narration review. Onlyshot12 is proposed for newvoice and movement; original inputs preserved atsource andselected baseline bytes. NoTTS orfreeze performed.'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


prior_paths = [OUT / f for f in ['audio-check.json', 'check-audio.py', 'README.md']]
prior_hashes = {p.name: sha(p) for p in prior_paths}
prior = json.loads((OUT / 'audio-check.json').read_text())
provenance_path = EP / 'input-provenance.json'
current_bytes = provenance_path.read_bytes()
current = json.loads(current_bytes)
reconstructed = dict(current)
reconstructed['scope'] = OLD_SCOPE
old_bytes = (json.dumps(reconstructed, ensure_ascii=False, indent=2) + '\n').encode()
reconstructed_sha = hashlib.sha256(old_bytes).hexdigest()
scope_only = reconstructed_sha == prior['inputProvenanceSHA256']
freeze_path = EP / 'source-sha256.json'
freeze = json.loads(freeze_path.read_text())
checks = []


def check(path, expected, category):
    actual = sha(path)
    relative = os.path.relpath(path, EP)
    frozen = freeze.get(relative) if category != 'retained-original-input' else None
    checks.append({
        'path': str(path.relative_to(ROOT)), 'category': category,
        'priorSHA256': expected, 'currentSHA256': actual,
        'unchangedSincePriorAudioQA': expected == actual,
        'frozenEntrySHA256': frozen,
        'currentMatchesFrozenEntry': actual == frozen if frozen is not None else None,
    })


check(EP / 'script.md', prior['scriptSHA256'], 'script')
check(EP / 'voice/jobs-logic.json', prior['jobsSHA256'], 'new-take-jobs')
check(EP / 'voice/build.json', prior['assembly']['buildSHA256'], 'assembled-build-metadata')
check(EP / 'voice.wav', prior['assembly']['wholeAudioSHA256'], 'whole-audio')
check(ROOT / 'episodes/_shared/voice/common.py', prior['sharedCutImplementationSHA256'], 'shared-cut-implementation')
for take in prior['newTakeChecks']:
    for rel, expected in take['hashes'].items():
        check(EP / rel, expected, 'new-take-input')
    check(EP / f"voice/sentences/{take['sentence']}.wav", take['assemblyCheck']['inputSentenceSHA256'], 'new-assembled-sentence')
source = ROOT / prior['baselineProduction']
for take in prior['retainedTakeChecks']:
    for f in take['files']:
        check(EP / f['relative'], f['revisionSHA256'], 'retained-revision-input')
        check(source / f['relative'], f['originalSHA256'], 'retained-original-input')

reuse = current['voiceReuse']
reuse_identity = {
    'newSentenceIdsMatchPrior': sorted(reuse['replaceSentenceIds']) == sorted(t['sentence'] for t in prior['newTakeChecks']),
    'retainedSentenceCountMatchesPrior': reuse['reusedSentenceCount'] == prior['summary']['retainedTakeCount'],
    'retainedIdsMatchPrior': sorted(reuse['reusedSentences']) == sorted(t['sentence'] for t in prior['retainedTakeChecks']),
    'voiceReuseFieldBytesUnchangedViaExactPriorReconstruction': scope_only,
}
current_sha = hashlib.sha256(current_bytes).hexdigest()
unchanged = all(c['unchangedSincePriorAudioQA'] for c in checks)
frozen_matches = all(c['currentMatchesFrozenEntry'] is not False for c in checks)
original_retained = prior_hashes == {p.name: sha(p) for p in prior_paths}
report = {
    'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Directed SHA and provenance-field identity check after producer updated scope prose before freezing. No signal recomputation, ASR, TTS or semantic listening.',
    'priorAudioReport': 'audio-check.json',
    'priorArtifactsSHA256': prior_hashes,
    'priorArtifactsUnchangedBySupplement': original_retained,
    'priorProvenanceSHA256': prior['inputProvenanceSHA256'],
    'currentProvenanceSHA256': current_sha,
    'previousScopeSource': 'Original full scope string supplied by production agent visual_qa; accepted only after in-memory reconstruction reproduced the prior full-file SHA.',
    'previousScope': OLD_SCOPE, 'currentScope': current['scope'],
    'reconstructionSerialization': "json.dumps(current with only scope restored, ensure_ascii=False, indent=2) + newline; memory only",
    'reconstructedPreviousProvenanceSHA256': reconstructed_sha,
    'onlyScopeChangedConfirmedByExactPreviousHash': scope_only,
    'voiceReuseIdentity': reuse_identity,
    'currentFreezeManifest': str(freeze_path.relative_to(ROOT)),
    'currentFreezeManifestSHA256': sha(freeze_path),
    'freezeProvenanceEntrySHA256': freeze.get('input-provenance.json'),
    'currentProvenanceMatchesFrozenEntry': freeze.get('input-provenance.json') == current_sha,
    'identityChecks': checks,
    'identityFileCount': len(checks),
    'allPreviouslyCheckedAudioInputsUnchanged': unchanged,
    'allPresentRelevantFreezeEntriesMatch': frozen_matches,
    'priorBoundedAudioResultsRemainApplicable': bool(scope_only and unchanged and frozen_matches and original_retained and all(reuse_identity.values())),
    'asrRequestedThisSupplement': False, 'semanticListeningPerformed': False,
    'semanticVerdict': 'Still unverified; earlier historical Unsupported model evidence is unchanged and was not requested again.',
}
report['pass'] = report['priorBoundedAudioResultsRemainApplicable'] and report['currentProvenanceMatchesFrozenEntry']
(OUT / 'provenance-supplement.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['priorProvenanceSHA256', 'currentProvenanceSHA256', 'onlyScopeChangedConfirmedByExactPreviousHash', 'identityFileCount', 'allPreviouslyCheckedAudioInputsUnchanged', 'currentFreezeManifestSHA256', 'currentProvenanceMatchesFrozenEntry', 'priorArtifactsUnchangedBySupplement', 'pass']}, ensure_ascii=False, indent=2))
