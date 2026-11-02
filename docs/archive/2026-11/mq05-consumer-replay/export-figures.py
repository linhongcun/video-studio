#!/usr/bin/env python3
"""Export only the exact integer-frame article locations planned before encoding."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from episode_paths import production_directory, episode_slug


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('production', type=Path)
    args = parser.parse_args()
    d = args.production.resolve()
    assert d == ROOT / 'episodes/message-queue/kafka-consumer-idempotency/production/revisions/consumer-replay-v2' and episode_slug(d) == 'kafka-consumer-idempotency', 'Use this actual nested revision only'
    receipt_path = d / 'article-figures-export.json'
    assert not receipt_path.exists(), 'Preserve earlier export receipt and raw JPEGs before a new attempt'
    plan = json.loads((d / 'article-figure-plan.json').read_text())
    frozen = json.loads((d / 'source-sha256.json').read_text())
    assert frozen['article.mdx'] == sha(d / 'article.mdx')
    assert frozen['article-figure-plan.json'] == sha(d / 'article-figure-plan.json')
    result = json.loads((d / 'render-result.json').read_text())
    assert result['sha256'] == sha(d / 'video.mp4')
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', str(d / 'video.mp4')]))['streams'][0]
    assert all(probe.get(k) == v for k, v in {'color_range': 'tv', 'color_space': 'bt709', 'color_transfer': 'bt709', 'color_primaries': 'bt709'}.items())
    targets = [(d / f['file']).resolve() for f in plan['figures']]
    assert len(set(targets)) == len(targets) and all(p.is_relative_to((d / 'article').resolve()) and not p.exists() for p in targets), 'Preserve existing figures; use a fresh explicit revision'
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
        cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-xerror', '-n', '-i', str(d / 'video.mp4'),
               '-vf', vf, '-frames:v', '1', '-q:v', '2', str(target)]
        run = subprocess.run(cmd, capture_output=True, text=True)
        (target.parent / (target.stem + '.stderr.txt')).write_text(run.stderr)
        rows.append({**fig, 'command': cmd, 'exit': run.returncode, 'stderr': run.stderr,
                     'sha256': sha(target) if target.is_file() else None})
        receipt_path.write_text(json.dumps({'videoSHA256': result['sha256'], 'integerFrameSelection': True,
            'colorConversion': 'limited BT.709 to full BT.601 JPEG pixels', 'visualReviewed': False,
            'figures': rows, 'exporterSHA256': sha(Path(__file__))}, ensure_ascii=False, indent=2) + '\n')
        assert run.returncode == 0 and target.is_file() and target.stat().st_size > 0, ('Frame export failed; raw output retained', n, run.stderr)
    (d / 'article-figures-export.json').write_text(json.dumps(
        {'videoSHA256': result['sha256'], 'integerFrameSelection': True,
         'colorConversion': 'limited BT.709 to full BT.601 JPEG pixels',
         'visualReviewed': False, 'figures': rows, 'exporterSHA256': sha(Path(__file__))}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'production': str(d), 'exported': len(rows)}))


if __name__ == '__main__':
    main()
