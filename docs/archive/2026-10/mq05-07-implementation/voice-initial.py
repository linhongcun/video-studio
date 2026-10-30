#!/usr/bin/env python3
"""Produce a new episode's first takes only after exact independent editorial approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('production', type=Path)
    args = ap.parse_args()
    d = args.production.resolve()
    q = d / 'voice'
    q.mkdir(exist_ok=True)
    report_path = q / 'initial-production.json'
    assert not report_path.exists(), 'Preserve this initial attempt; handle any failure with a new explicit attempt'
    approval = json.loads((d / 'qa-editorial/editorial-independent.json').read_text())
    script = (d / 'script.md').read_bytes()
    narration = ''.join(re.findall(r'^旁白：(.*)$', script.decode(), re.M)).encode()
    assert approval['canEnterTTS'] is True and not approval['blockers']
    assert approval['scriptSHA256'] == hashlib.sha256(script).hexdigest()
    assert approval['narrationSHA256'] == hashlib.sha256(narration).hexdigest()
    assert not list((q / 'takes').glob('*.wav')), 'Initial production must start from new takes'
    report = {'startedAtUTC': datetime.now(timezone.utc).isoformat(), 'status': 'in-progress',
              'editorialApproval': str((d / 'qa-editorial/editorial-independent.json').relative_to(ROOT)),
              'scriptSHA256': sha(d / 'script.md'), 'narrationSHA256': approval['narrationSHA256'],
              'voiceParametersSHA256': sha(q / 'params.json'), 'steps': []}

    def save():
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def run(name, command):
        log = q / ('initial-' + name + '.log')
        assert not log.exists()
        with log.open('w') as output:
            result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        report['steps'].append({'step': name, 'command': command, 'exitCode': result.returncode,
                                'log': str(log.relative_to(d)), 'logSHA256': sha(log)})
        save()
        assert result.returncode == 0, ('Failed production step', name, log)

    save()
    try:
        run('prepare', [sys.executable, str(d / 'prepare.py')])
        sents = json.loads((q / 'sents.json').read_text())
        assert len(sents) == approval['sentences']
        assert ''.join(s['text'] for s in sents).encode() == narration
        prepared = json.loads((q / 'script-narration-sha256.json').read_text())
        assert prepared['narrationSHA256'] == approval['narrationSHA256']
        jobs = [[s['id'], 'a', None] for s in sents]
        (q / 'jobs-initial.json').write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + '\n')
        run('generate', [sys.executable, str(ROOT / 'episodes/_shared/voice/gen.py'), '--dir', str(d), '--jobs', 'jobs-initial.json'])
        takes = []
        for s in sents:
            p = q / 'takes' / (s['id'] + '-a.wav')
            assert p.is_file() and p.stat().st_size > 44, ('Missing generated take', s['id'])
            assert json.loads(p.with_suffix('.txt.json').read_text()) == s['tts']
            takes.append({'sentence': s['id'], 'take': 'a', 'sha256': sha(p)})
        (q / 'picks.json').write_text(json.dumps({s['id']: 'a' for s in sents}, ensure_ascii=False, indent=2) + '\n')
        report['generatedTakes'] = takes
        save()
        run('build', [sys.executable, str(ROOT / 'episodes/_shared/voice/build.py'), '--dir', str(d)])
        run('assemble', [sys.executable, str(d / 'assemble.py')])
        run('place', [sys.executable, str(ROOT / 'episodes/_shared/place_v2.py'), '--dir', str(d), '--mode', 'whole'])
        run('onset', [sys.executable, str(ROOT / 'episodes/_shared/label_onset_strict.py'), '--dir', str(d), '--out', str(d / 'onset-initial.txt')])
        assert sha(d / 'script.md') == report['scriptSHA256']
        assert sha(q / 'params.json') == report['voiceParametersSHA256']
        assert sha(d / 'voice.wav') == sha(d / 'remotion/public/audio/voice.wav')
        board = json.loads((d / 'storyboard.json').read_text())
        report.update(status='initial-produced-await-independent-signal-review', voiceSHA256=sha(d / 'voice.wav'),
                      bodyFrames=sum(sc['durationInFrames'] for sc in board['scenes']),
                      finishedAtUTC=datetime.now(timezone.utc).isoformat(),
                      scope='New initial takes and measured shared assembly; no ASR/full semantic listening, dynamic, freeze or final-media acceptance claim.')
        save()
        print(json.dumps({'episode': d.name, 'status': report['status'], 'sentences': len(takes), 'bodyFrames': report['bodyFrames']}, ensure_ascii=False), flush=True)
    except Exception as exc:
        report.update(status='failed', error=repr(exc), finishedAtUTC=datetime.now(timezone.utc).isoformat())
        save()
        raise


if __name__ == '__main__':
    main()
