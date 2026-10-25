#!/usr/bin/env python3
"""Exercise Java-tail retention and rejection using saved genuine body fixtures.

Runs exclusively in temporary copies. The historical voiced media and production
inputs remain unchanged. These checks do not test speech recognition or learning.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
HELPER = Path(__file__).with_name('append_java_endcard.py')
REQUIRED = [
    'voice.wav', 'words.json', 'storyboard.json', 'script.md', 'plan.json',
    'episode-config.json', 'captions.srt', 'voice/build.json',
    'voice/params.json', 'voice/sents.json', 'voice/picks.json',
    'voice/shot_frames.json', 'covers.json',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(action, directory, expected_success=True):
    result = subprocess.run([sys.executable, str(HELPER), action, str(directory)], capture_output=True, text=True)
    assert (result.returncode == 0) == expected_success, (action, result.returncode, result.stdout, result.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slugs', nargs='*', default=['strategy-pattern', 'observer-pattern'])
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for slug in args.slugs:
        fixture = ROOT/'episodes-codex'/slug/'revisions/flow-ui-java/baseline'
        paths = {name: fixture/name if (fixture/name).is_file() else fixture/'source'/name for name in REQUIRED}
        original = {name: sha(path) for name, path in paths.items()}
        with tempfile.TemporaryDirectory(prefix='java-tail-fixture-') as temporary:
            directory = Path(temporary)
            for name in REQUIRED:
                target = directory/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(paths[name], target)
            public = directory/'remotion/public/audio/voice.wav'
            public.parent.mkdir(parents=True)
            shutil.copyfile(directory/'voice.wav', public)
            invoke('append', directory)
            passed = json.loads((directory/'qa-java-endcard.json').read_text())
            # A second append must verify and retain every final byte.
            final_files = ['voice.wav', 'words.json', 'storyboard.json', 'voice/shot_frames.json', 'captions.srt']
            before = {name: sha(directory/name) for name in final_files}
            invoke('append', directory)
            assert before == {name: sha(directory/name) for name in final_files}
            failures = []
            def reject(name, mutate):
                path = directory/name
                saved = path.read_bytes()
                mutate(path)
                result = invoke('verify', directory, expected_success=False)
                path.write_bytes(saved)
                failures.append({'mutation': name, 'rejected': True, 'reason': result.stderr.strip().splitlines()[-1]})
            def nonzero_tail(path):
                data = bytearray(path.read_bytes())
                data[-2:] = b'\x01\x00'
                path.write_bytes(data)
            reject('voice.wav', nonzero_tail)
            def change_json(path, mutate):
                value = json.loads(path.read_text())
                mutate(value)
                path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
            reject('storyboard.json', lambda p: change_json(p, lambda x: x['scenes'][-1]['shots'][-1]['subtitles'][-1].update(to=x['scenes'][-1]['shots'][-1]['subtitles'][-1]['to']+150)))
            reject('storyboard.json', lambda p: change_json(p, lambda x: x['scenes'][0]['shots'][0]['voice'][0].update(localStart=x['scenes'][0]['shots'][0]['voice'][0]['localStart']+1)))
            reject('words.json', lambda p: change_json(p, lambda x: x['shots'][0]['sentences'][0].update(endFrame=x['shots'][0]['sentences'][0]['endFrame']+1)))
            reject('storyboard.json', lambda p: change_json(p, lambda x: x['meta'].update(unvoicedEndCard={'kind':'full-python-solution','from':passed['bodyFrames'],'durationInFrames':150})))
            reject('revisions/flow-ui-java/voiced-body/script.md', lambda p: p.write_text(p.read_text()+'\nmutated saved body\n'))
            invoke('verify', directory)
            assert before == {name: sha(directory/name) for name in final_files}
            rows.append({'slug':slug,'fixturePaths':{name:str(path.relative_to(ROOT)) for name,path in paths.items()},'fixtureSHA256':original,'bodyFrames':passed['bodyFrames'],'finalFrames':passed['finalFrames'],'tailFrames':passed['javaCardFrames'],'prefixPCMExact':passed['prefixPCMExact'],'silentTailAllZero':passed['silentTailAllZero'],'idempotentAppendExact':True,'negativeCases':failures,'fixtureUnchanged':original=={name:sha(path) for name,path in paths.items()}})
    report={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'executor':'/root/observer_voice','helperSHA256':sha(HELPER),'testSHA256':sha(Path(__file__)),'scope':'Genuine historical body fixtures in temporary directories; positive append/verify/idempotence and six deliberate corruption rejections per episode. No live production inputs mutated.','episodes':rows,'passed':all(row['fixtureUnchanged'] and len(row['negativeCases'])==6 for row in rows)}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'episodes':len(rows),'negativeCases':sum(len(row['negativeCases']) for row in rows),'passed':report['passed']}))


if __name__ == '__main__':
    main()
