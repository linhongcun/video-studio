"""Check the28 retained sentence takes; no voice generation or timing algorithm."""
from pathlib import Path
import argparse
import hashlib
import json

D = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_reuse(*, require_prepared=True, require_new_takes=False):
    provenance = json.loads((D / 'input-provenance.json').read_text())
    rule = provenance['voiceReuse']
    reused, replaced = rule['reusedSentences'], rule['replaceSentenceIds']
    assert len(reused) == rule['reusedSentenceCount'] == 28
    assert set(replaced) == {'12-first-balanced-1', '12-first-balanced-2'}
    picks = json.loads((D / 'voice/picks.json').read_text())
    for sid, row in reused.items():
        assert picks.get(sid, 'a') == row['take'], f'Reused selected take changed: {sid}'
        for relative, expected in row['files'].items():
            path = D / relative
            assert path.is_file() and digest(path) == expected, f'Reused take bytes changed: {relative}'
    if require_prepared:
        sentences = json.loads((D / 'voice/sents.json').read_text())
        by_id = {s['id']: s for s in sentences}
        assert len(sentences) == len(by_id) == 30 and set(by_id) == set(reused) | set(replaced)
        for sid, row in reused.items():
            assert by_id[sid]['text'] == row['text'], f'Only12 narration may change: {sid}'
            assert by_id[sid]['tts'] == row['tts'], f'Reused TTS wording changed: {sid}'
        for sid in replaced:
            assert by_id[sid]['text'] != rule['replacementBaselineTexts'][sid], f'New12 narration is not finalized: {sid}'
            assert picks.get(sid) != 'a', f'Use a distinct new take label for12: {sid}'
    if require_new_takes:
        for sid in replaced:
            for suffix in ('.wav', '.txt.json'):
                path = D / 'voice/takes' / (sid + '-' + picks[sid] + suffix)
                assert path.is_file(), f'Missing actual replacement take: {path.name}'
    return {'reusedSentenceCount': 28, 'replacedSentenceIds': replaced,
            'scope': 'Exact retained input takes, selected labels and narration text only. New whole-WAV identity and timing are measured after shared build; no listening or media QA claim.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup-only', action='store_true', help='Check copied28 takes before new script preparation')
    parser.add_argument('--require-new-takes', action='store_true')
    args = parser.parse_args()
    print(json.dumps(validate_reuse(require_prepared=not args.setup_only,
                                   require_new_takes=args.require_new_takes),
                     ensure_ascii=False, indent=2))
