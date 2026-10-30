#!/usr/bin/env python3
"""Export only the exact integer-frame article locations planned before encoding."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('production', type=Path)
    args = parser.parse_args()
    d = args.production.resolve()
    plan = json.loads((d / 'article-figure-plan.json').read_text())
    frozen = json.loads((d / 'source-sha256.json').read_text())
    assert frozen['article.mdx'] == sha(d / 'article.mdx')
    assert frozen['article-figure-plan.json'] == sha(d / 'article-figure-plan.json')
    result = json.loads((d / 'render-result.json').read_text())
    assert result['sha256'] == sha(d / 'video.mp4')
    rows = []
    for fig in plan['figures']:
        n = fig['frame']
        assert type(n) is int and 0 <= n < result['bodyFrames']
        assert abs(fig['seconds'] - n / 30) < 1e-8
        target = (d / fig['file']).resolve()
        assert target.is_relative_to((d / 'article').resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        vf = (f"select=eq(n\\,{n}),"
              'scale=in_range=tv:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt601,format=yuvj420p')
        with tempfile.TemporaryDirectory(prefix='frame-export-', dir=target.parent) as work:
            fresh = Path(work) / target.name
            cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-xerror', '-y', '-i', str(d / 'video.mp4'),
                   '-vf', vf, '-frames:v', '1', '-q:v', '2', str(fresh)]
            subprocess.run(cmd, check=True)
            assert fresh.is_file() and fresh.stat().st_size > 0, ('No matching decoded frame', n)
            fresh.replace(target)
        rows.append({**fig, 'sha256': sha(target), 'command': cmd})
    (d / 'article-figures-export.json').write_text(json.dumps(
        {'videoSHA256': result['sha256'], 'integerFrameSelection': True,
         'colorConversion': 'limited BT.709 to full BT.601 JPEG pixels',
         'visualReviewed': False, 'figures': rows}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'production': str(d), 'exported': len(rows)}))


if __name__ == '__main__':
    main()
