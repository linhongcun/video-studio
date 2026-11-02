#!/usr/bin/env python3
"""Record and verify task-used system font bytes without altering system fonts."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
LEDGER = HERE / 'font-environment.json'
REQUESTS = ['Noto Sans CJK SC:weight=regular', 'Noto Sans CJK SC:weight=demibold',
            'DejaVu Sans Mono:weight=regular', 'DejaVu Sans Mono:weight=bold',
            'DejaVu Sans:weight=bold']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    assert args.snapshot != args.verify
    if args.snapshot:
        assert not LEDGER.exists(), 'Preserve the original production font ledger'
        bindings = []
        files = {}
        for query in REQUESTS:
            result = subprocess.check_output(['fc-match', '-f', '%{file}|%{index}|%{family}|%{style}', query], text=True)
            path, index, family, style = result.split('|')
            p = Path(path)
            bindings.append({'query': query, 'path': path, 'faceIndex': index, 'family': family, 'style': style})
            files[path] = sha(p)
        for path in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                     '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']:
            files[path] = sha(Path(path))
        LEDGER.write_text(json.dumps({'checkedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
                                     'scope': 'Fontconfig selected body/monospace faces plus exact bibliography font bytes; actual glyphs and legibility require image review.',
                                     'bindings': bindings, 'files': files}, ensure_ascii=False, indent=2) + '\n')
    else:
        data = json.loads(LEDGER.read_text())
        for path, expected in data['files'].items():
            assert sha(Path(path)) == expected, path
        for binding in data['bindings']:
            result = subprocess.check_output(['fc-match', '-f', '%{file}|%{index}|%{family}|%{style}', binding['query']], text=True)
            assert result.split('|')[:2] == [binding['path'], binding['faceIndex']]
        print(json.dumps({'passed': True, 'fontFiles': len(data['files']), 'bindings': len(data['bindings']), 'readOnly': True}))


if __name__ == '__main__':
    main()
