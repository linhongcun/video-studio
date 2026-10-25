"""Copy checked D02 publishing artifacts only; never copy production WAV/PNG/code.
Run after root's media QA gate: python3 site-integrate.py --approved --release vX.Y.Z
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SLUG = 'observer-pattern'
OUT = ROOT / 'episodes' / SLUG

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approved', action='store_true', help='Production media QA has actually passed')
    parser.add_argument('--release', required=True)
    args = parser.parse_args()
    assert args.approved, 'Wait for actual media QA before copying publishing artifacts'
    version = json.loads((ROOT / 'site/package.json').read_text())['version']
    assert args.release == 'v' + version, 'Choose the actual current release identity first'
    config = json.loads((HERE / 'episode-config.json').read_text())
    sb = json.loads((HERE / 'storyboard.json').read_text())
    result = json.loads((HERE / 'render-result.json').read_text())
    frames = sb['meta'].get('finalVideoFrames', sb['meta']['durationInFrames'])
    fps = sb['meta']['fps']
    assert frames > 0 and fps == 30
    assert config['episode'] == 28 and config['slug'] == SLUG
    files = ['article.mdx', 'script.md', 'research.md', 'pronunciation.md', 'storyboard.json',
             'words.json', 'captions.srt', 'video.mp4', 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']
    source_files = {name: ('article-site.mdx' if name == 'article.mdx' else name) for name in files}
    for name in files:
        assert (HERE / source_files[name]).is_file(), f'Missing checked source: {source_files[name]}'
    derivation = json.loads((HERE / 'site-article-derivation.json').read_text())
    assert digest(HERE / 'article.mdx') == derivation['baselineSha256']
    assert digest(HERE / 'article-site.mdx') == derivation['derivedSha256']
    video_sha = digest(HERE / 'video.mp4')
    assert video_sha in json.dumps(result), 'Current video must match the encoded-media report'
    OUT.mkdir(parents=True, exist_ok=True)
    for name in files:
        shutil.copyfile(HERE / source_files[name], OUT / name)
        assert digest(HERE / source_files[name]) == digest(OUT / name)
    today = datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    metadata = {
        'slug': SLUG, 'ep': 28, 'episodePart': '设计模式 D02', 'lessonOrder': 2,
        'title': config['title'],
        'summary': '同一笔订单变化后，摘要刷新、变化记录追加。跟着订阅、通知和取消订阅，理解来源与接收者怎样按共同约定协作，以及这种分工的收益和成本。',
        'tags': ['设计模式', '观察者模式', '代码设计'], 'series': 'design-patterns',
        'publishedAt': today, 'firstRelease': args.release, 'video': 'video.mp4', 'poster': 'cover-16x9.jpg',
        'draft': False, 'related': ['strategy-pattern'],
        'description': '订单先改变状态，再通知当前订阅者；摘要和变化记录各自响应。摘要取消订阅后保留旧显示，下一次仅变化记录收到通知，借此说明观察者模式的职责、共同约定和适用边界。',
        'platforms': {}, 'sourcePath': f'episodes-codex/{SLUG}/remotion', 'productionIssue': 164,
        'finalVideoFrames': frames, 'targetDuration': frames / fps,
    }
    (OUT / 'meta.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    assert all(p.is_file() and p.suffix.lower() not in ['.wav', '.png', '.ts', '.tsx', '.js'] for p in OUT.iterdir())
    report = {
        'checkedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(), 'status': 'passed',
        'executedBy': 'Codex observer_site agent', 'release': args.release,
        'approvedProductionMediaCopied': True, 'frames': frames, 'fps': fps,
        'articleDerivation': derivation,
        'files': [{'file': name, 'sourceFile': source_files[name], 'bytes': (OUT / name).stat().st_size, 'sha256': digest(OUT / name)} for name in files],
        'metadata': metadata,
        'scope': 'Publishing artifact copies are byte-identical. Production WAV, PNG and source code stay in episodes-codex.'
    }
    (HERE / 'site-copy-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': 'passed', 'files': len(files), 'release': args.release, 'videoSha256': video_sha}))
