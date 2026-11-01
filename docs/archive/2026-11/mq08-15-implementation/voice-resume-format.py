#!/usr/bin/env python3
"""Resume only prepared timing after a verified narration-preserving heading fix."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
D = Path(sys.argv[1]).resolve()
Q = D / 'voice'
BEFORE = D / 'qa-editorial/assemble-header-format-before'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
change = read(BEFORE / 'change.json')
approval = read(D / 'qa-editorial/editorial-independent.json')
old = read(Q / 'initial-production.json')
assert old['status'] == 'failed' and old['steps'][-1]['step'] == 'assemble'
assert approval['canEnterTTS'] and approval['scriptSHA256'] == sha(D / 'script.md')
assert sha(D / 'script.md') == change['afterScriptSHA256']
narration = ''.join(re.findall(r'^旁白：(.*)$', (D / 'script.md').read_text(), re.M)).encode()
assert hashlib.sha256(narration).hexdigest() == approval['narrationSHA256'] == change['canonicalNarrationSHA256']
assert sha(D / 'voice.wav') == change['voiceBeforeSHA256']
assert sha(Q / 'build.json') == change['buildBeforeSHA256']
assert all(sha(Q / 'takes' / name) == h for name, h in change['takesBefore'].items())
report_path = Q / 'assembly-header-resume.json'
assert not report_path.exists(), 'Preserve every resume attempt'
report = {'startedAtUTC': datetime.now(timezone.utc).isoformat(), 'status': 'in-progress',
          'producerSHA256': sha(Path(__file__)), 'newScriptSHA256': approval['scriptSHA256'],
          'narrationSHA256': approval['narrationSHA256'], 'voiceSHA256': change['voiceBeforeSHA256'],
          'newTTSRequests': 0, 'rebuildAudio': False, 'originalInitialAttemptStatus': 'failed', 'steps': []}


def save():
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


save()
try:
    commands = [('prepare', [sys.executable, str(D / 'prepare.py')]),
                ('assemble', [sys.executable, str(D / 'assemble.py')]),
                ('place', [sys.executable, str(ROOT / 'episodes/_shared/place_v2.py'), '--dir', str(D), '--mode', 'whole']),
                ('onset', [sys.executable, str(ROOT / 'episodes/_shared/label_onset_strict.py'), '--dir', str(D),
                           '--out', str(D / 'onset-header-resume.txt')])]
    for name, command in commands:
        log = Q / ('header-resume-' + name + '.log')
        assert not log.exists()
        with log.open('w') as output:
            result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        report['steps'].append({'step': name, 'exit': result.returncode, 'log': str(log.relative_to(D)), 'logSHA256': sha(log)})
        save()
        assert result.returncode == 0, (name, log)
        assert sha(Q / 'sents.json') == change['sentsBeforeSHA256']
        assert sha(D / 'voice.wav') == change['voiceBeforeSHA256']
        assert sha(Q / 'build.json') == change['buildBeforeSHA256']
        assert all(sha(Q / 'takes' / filename) == h for filename, h in change['takesBefore'].items())
    assert read(D / 'words.json')['scriptSha256'] == approval['scriptSHA256']
    assert sha(D / 'remotion/public/audio/voice.wav') == report['voiceSHA256']
    report.update(status='produced-existing-takes-await-independent-signal-review',
                  bodyFrames=read(D / 'words.json')['durationFrames'], allOriginalTakeBytesUnchanged=True,
                  sourceBuildBytesUnchanged=True, sourceSentsBytesUnchanged=True,
                  finishedAtUTC=datetime.now(timezone.utc).isoformat())
    save()
    print(json.dumps({'slug': read(D / 'episode-config.json')['slug'], 'status': report['status'],
                      'bodyFrames': report['bodyFrames'], 'voiceSHA256': report['voiceSHA256'], 'newTTSRequests': 0}))
except Exception as error:
    report.update(status='failed', error=repr(error), finishedAtUTC=datetime.now(timezone.utc).isoformat())
    save()
    raise
