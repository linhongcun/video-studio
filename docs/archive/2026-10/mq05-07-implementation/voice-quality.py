#!/usr/bin/env python3
"""Generate only explicitly flagged, same-text alternatives and preserve the previous assembly."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('production', type=Path)
    ap.add_argument('--take', required=True, choices=['b', 'c', 'd'])
    args = ap.parse_args()
    d = args.production.resolve()
    q = d / 'voice'
    take = args.take
    approval = json.loads((d / 'qa-editorial/editorial-independent.json').read_text())
    narration = ''.join(re.findall(r'^旁白：(.*)$', (d / 'script.md').read_text(), re.M)).encode()
    assert approval['canEnterTTS'] and approval['scriptSHA256'] == sha(d / 'script.md')
    assert approval['narrationSHA256'] == hashlib.sha256(narration).hexdigest()
    sents = {s['id']: s for s in json.loads((q / 'sents.json').read_text())}
    jobs_path = q / ('jobs-quality-' + take + '.json')
    jobs = json.loads(jobs_path.read_text())
    changed = {row[0] for row in jobs}
    assert len(changed) == len(jobs)
    for sid, candidate, text in jobs:
        assert candidate == take and text == sents[sid]['tts'], 'Alternatives must retain the exact approved TTS request text'
        assert not (q / 'takes' / (sid + '-' + take + '.wav')).exists()
    previous = json.loads((q / 'picks.json').read_text())
    untouched = {sid: sha(q / 'takes' / (sid + '-' + previous.get(sid, 'a') + '.wav')) for sid in sents if sid not in changed}
    folder = q / 'candidates' / ('before-quality-' + take)
    assert not folder.exists()
    folder.mkdir(parents=True)
    for rel in ['voice.wav', 'words.json', 'storyboard.json', 'voice/picks.json', 'voice/build.json']:
        shutil.copyfile(d / rel, folder / Path(rel).name)
    report_path = q / ('quality-' + take + '-production.json')
    report = {'startedAtUTC': datetime.now(timezone.utc).isoformat(), 'status': 'in-progress',
              'producerSHA256': sha(Path(__file__)), 'narrationSHA256': approval['narrationSHA256'],
              'scriptSHA256': sha(d / 'script.md'), 'parameterSHA256': sha(q / 'params.json'),
              'previousVoiceSHA256': sha(d / 'voice.wav'), 'sameTextCandidateIds': sorted(changed), 'steps': []}

    def save():
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def run(name, command):
        log = q / ('quality-' + take + '-' + name + '.log')
        assert not log.exists()
        with log.open('w') as output:
            result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        report['steps'].append({'step': name, 'command': command, 'exit': result.returncode,
                                'log': str(log.relative_to(d)), 'logSHA256': sha(log)})
        save()
        assert result.returncode == 0, (name, log)

    save()
    try:
        run('generate', [sys.executable, str(ROOT / 'episodes/_shared/voice/gen.py'), '--dir', str(d), '--jobs', jobs_path.name])
        for sid in changed:
            p = q / 'takes' / (sid + '-' + take + '.wav')
            assert p.is_file() and json.loads(p.with_suffix('.txt.json').read_text()) == sents[sid]['tts']
            previous[sid] = take
        (q / 'picks.json').write_text(json.dumps(previous, ensure_ascii=False, indent=2) + '\n')
        run('build', [sys.executable, str(ROOT / 'episodes/_shared/voice/build.py'), '--dir', str(d)])
        run('assemble', [sys.executable, str(d / 'assemble.py')])
        run('place', [sys.executable, str(ROOT / 'episodes/_shared/place_v2.py'), '--dir', str(d), '--mode', 'whole'])
        run('onset', [sys.executable, str(ROOT / 'episodes/_shared/label_onset_strict.py'), '--dir', str(d), '--out', str(d / ('onset-quality-' + take + '.txt'))])
        assert sha(d / 'script.md') == report['scriptSHA256']
        assert sha(q / 'params.json') == report['parameterSHA256']
        assert all(sha(q / 'takes' / (sid + '-' + previous.get(sid, 'a') + '.wav')) == h for sid, h in untouched.items())
        assert sha(d / 'voice.wav') == sha(d / 'remotion/public/audio/voice.wav')
        report.update(status='produced-await-independent-signal-review', voiceSHA256=sha(d / 'voice.wav'),
                      bodyFrames=json.loads((d / 'storyboard.json').read_text())['meta']['durationInFrames'],
                      otherSelectedTakeCount=len(untouched), otherSelectedTakeBytesUnchanged=True,
                      finishedAtUTC=datetime.now(timezone.utc).isoformat(),
                      scope='Targeted same-text signal-risk alternatives; does not assert old takes had semantic errors or claim ASR/full semantic listening.')
        save()
        print(json.dumps({'episode': d.name, 'candidate': take, 'bodyFrames': report['bodyFrames'], 'voiceSHA256': report['voiceSHA256']}), flush=True)
    except Exception as exc:
        report.update(status='failed', error=repr(exc), finishedAtUTC=datetime.now(timezone.utc).isoformat())
        save()
        raise


if __name__ == '__main__':
    main()
