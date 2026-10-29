#!/usr/bin/env python3
"""Package four finalized peak-series episodes and their twelve checked covers.

Only writes under work/peak-video-style. No rendering, publication metadata
mutation, Git commit, upload or external-platform action occurs. Run after the
parent has installed the final media and metadata.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work/peak-video-style'
RENDERER = ROOT / 'episodes-codex/_shared/peak-video/render.py'
BASELINE = WORK / 'preservation-baseline.json'
BASELINE_COMMIT = 'eea5d8fab1037cb9630a14647cbada564082a74b'
EPISODES = {
    'rate-limit': {'ep': 11, 'body': 3271, 'frames': 3421, 'name': '限流'},
    'idempotency': {'ep': 12, 'body': 2998, 'frames': 3148, 'name': '幂等'},
    'circuit-breaker': {'ep': 13, 'body': 2926, 'frames': 3076, 'name': '熔断'},
    'degradation': {'ep': 14, 'body': 3134, 'frames': 3284, 'name': '降级'},
}
SIZES = ('16x9', '4x3', '3x4')
COLOR = {'pix_fmt': 'yuv420p', 'color_range': 'tv', 'color_space': 'bt709',
         'color_transfer': 'bt709', 'color_primaries': 'bt709'}
ZIP_NAME = 'peak-video-style-20261029.zip'
DELIVERY_BRANCH = 'delivery/peak-video-style-20261029'
DELIVERY_PATH = 'design/peak-video-style-20261029'
CST = timezone(timedelta(hours=8))
MAX_BYTES = 95 * 1024 * 1024


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record(data: bytes) -> dict:
    return {'bytes': len(data), 'sha256': digest(data)}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def state(path: Path) -> dict:
    data = path.read_bytes()
    return {**record(data), 'mtimeNs': path.stat().st_mtime_ns}


def safe_name(name: str) -> str:
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or '\\' in name or '\x00' in name
            or any(part in ('', '.', '..') for part in name.split('/'))
            or ':' in path.parts[0]):
        raise ValueError(f'Unsafe archive path: {name!r}')
    return name


def resolve_output(value: str) -> Path:
    path = Path(value)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(WORK):
        raise ValueError('Package output must stay under work/peak-video-style')
    return path


def first_frame_color(path: Path) -> dict:
    """Probe one decoded frame; complete media checks are receipt-bound below."""
    data = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-read_intervals', '%+#1',
        '-show_frames', '-show_entries',
        'frame=pix_fmt,color_range,color_space,color_transfer,color_primaries',
        '-of', 'json', str(path)], text=True))
    frames = data.get('frames', [])
    if len(frames) != 1:
        raise ValueError(f'Cannot inspect exactly one first decoded frame: {path}')
    return {key: frames[0].get(key) for key in COLOR}


def validate_zip(path: Path, expected: dict[str, bytes]) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != 17 or len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError('Expected exactly four videos, twelve covers and one Chinese README')
        for name in names:
            safe_name(name)
        bad = archive.testzip()
        if bad is not None:
            raise ValueError(f'ZIP CRC mismatch: {bad}')
        actual = {}
        for name in names:
            data = archive.read(name)
            if data != expected[name]:
                raise ValueError(f'ZIP member payload differs: {name}')
            actual[name] = record(data)
    return {'status': 'passed', 'allCRCVerified': True, 'allPathsSafe': True,
            'allEntryBytesAndSHA256EqualSources': True, 'entries': actual}


def package(output: Path) -> dict:
    entries, protected, episodes, updated_times = {}, {}, [], []
    def bind(path: Path, *, external: bool = False) -> bytes:
        path = path.resolve()
        if (not external and not path.is_relative_to(ROOT)) or not path.is_file():
            raise ValueError(f'Missing actual final input: {path}')
        if path not in protected:
            protected[path] = state(path)
        return path.read_bytes()
    preservation = json.loads(bind(BASELINE))
    if preservation.get('baselineCommit') != BASELINE_COMMIT:
        raise ValueError('Independent preservation baseline identity differs')
    # Existing covers and historical freeze files stay byte-identical. Git blob
    # identities cover sparse historical binaries without hydrating old audio.
    for path, row in preservation['coverFiles'].items():
        if digest(bind(ROOT / path)) != row['sha256']:
            raise ValueError(f'Current peak cover input/asset/sidecar changed: {path}')
    for path, row in preservation['sourceSHA256Manifests'].items():
        if digest(bind(ROOT / path)) != row['sha256']:
            raise ValueError(f'Historical source manifest changed: {path}')
    from PIL import Image
    for slug, spec in EPISODES.items():
        revision = ROOT / 'episodes-codex' / slug / 'revisions/peak-style'
        published = ROOT / 'episodes' / slug
        meta_path = published / 'meta.json'
        result_path = revision / 'render-result.json'
        media_path = revision / 'reference-appendix-media-check.json'
        receipt_path = revision / 'reference-appendix.json'
        manifest_path = revision / 'source-sha256.json'
        baseline_path = revision / 'baseline-publication.json'
        style_path = published / 'cover-style.json'
        color_path = revision / 'color-encoding-check.json'
        audio_path = revision / 'baseline-audio-check.json'
        inputs = {path: bind(path) for path in (meta_path, result_path, media_path, receipt_path,
                                               manifest_path, baseline_path, style_path, color_path, audio_path)}
        meta, result, media, receipt, source, baseline, style, color, audio_receipt = [json.loads(inputs[path]) for path in inputs]
        original = baseline['publishedMetadata']
        if baseline.get('baselineCommit') != BASELINE_COMMIT \
                or original != preservation['metadataIdentity'][slug]:
            raise ValueError(f'Frozen original publication identity differs: {slug}')
        if meta.get('slug') != slug or meta.get('ep') != spec['ep'] or meta.get('series') != 'peak':
            raise ValueError(f'Wrong peak-series episode: {slug}')
        allowed_meta = {'updatedAt', 'burnedInCaptions'} | set(result.get('publicationMetadata', {}))
        changed = {key for key in set(meta) | set(original) if meta.get(key) != original.get(key)}
        if not changed <= allowed_meta:
            raise ValueError(f'Original identity/sourcePath/fields changed: {slug}: {changed}')
        for key in ('createdAt', 'publishedAt', 'firstRelease', 'title', 'sourcePath'):
            if meta.get(key) != original.get(key):
                raise ValueError(f'Original metadata field changed: {slug}/{key}')
        updated = datetime.fromisoformat(meta['updatedAt'])
        old_updated = datetime.fromisoformat(original['updatedAt'])
        if updated.tzinfo is None or old_updated.tzinfo is None or updated <= old_updated:
            raise ValueError(f'Actual new timezone-aware video update is not installed: {slug}')
        if meta['updatedAt'] != datetime.fromisoformat(result['createdAtUTC']).astimezone(CST).isoformat(timespec='seconds'):
            raise ValueError(f'Published update time differs from actual final render timestamp: {slug}')
        if meta.get('burnedInCaptions') is not True:
            raise ValueError(f'Final verified burned-in caption identity missing: {slug}')
        if result.get('episode') != slug or result.get('visualRevision') != 'peak-style-v1' \
                or result.get('colorEncoding') != COLOR \
                or result.get('newProductionManifest') != str(manifest_path.relative_to(ROOT)) \
                or result.get('newProductionManifestSHA256') != digest(inputs[manifest_path]):
            raise ValueError(f'Final source/result identity differs: {slug}')
        renderer = bind(RENDERER)
        if source.get('inputs', {}).get(str(RENDERER.relative_to(ROOT))) != digest(renderer):
            raise ValueError(f'Final frozen renderer binding differs: {slug}')
        # Hash the actual frozen source closure, and protect both bytes and
        # mtime during packaging. This does not rerun rendering or media decode.
        for path, expected in source.get('inputs', {}).items():
            if digest(bind(ROOT / path)) != expected:
                raise ValueError(f'Frozen final production input changed: {slug}/{path}')
        for path, expected in source.get('externalInputs', {}).items():
            if digest(bind(Path(path), external=True)) != expected:
                raise ValueError(f'Frozen external font input changed: {slug}/{path}')
        article = bind(published / 'article.mdx')
        if article != bind(revision / 'article.mdx') \
                or digest(article) != preservation['publishedFiles'][f'episodes/{slug}/article.mdx']['sha256']:
            raise ValueError(f'Published article differs from frozen original snapshot: {slug}')
        if result.get('bodyFrames') != spec['body'] or result.get('frames') != spec['frames'] \
                or meta.get('finalVideoFrames') != spec['frames'] \
                or meta.get('referenceAppendix', {}).get('from') != spec['body'] \
                or meta.get('referenceAppendix', {}).get('durationInFrames') != 150:
            raise ValueError(f'Original body + five-second reference timeline differs: {slug}')
        movie_path = revision / 'video.mp4'
        movie = bind(movie_path)
        if result.get('sha256') != digest(movie) or result.get('bytes') != len(movie) \
                or bind(published / 'video.mp4') != movie:
            raise ValueError(f'Installed final MP4 differs from revision/result: {slug}')
        for name in ('render-result.json', 'reference-appendix.json', 'reference-appendix-media-check.json'):
            if bind(published / name) != bind(revision / name):
                raise ValueError(f'Installed publication receipt differs: {slug}/{name}')
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_frames,pix_fmt,color_range,color_space,color_transfer,color_primaries',
            '-of', 'json', str(movie_path)], text=True))['streams'][0]
        for key, expected in {**COLOR, 'codec_name': 'h264', 'width': 1920, 'height': 1080,
                              'r_frame_rate': '30/1', 'avg_frame_rate': '30/1', 'nb_frames': str(spec['frames'])}.items():
            if probe.get(key) != expected:
                raise ValueError(f'Actual final stream field differs: {slug}/{key}: {probe.get(key)}')
        first_color = first_frame_color(movie_path)
        if first_color != COLOR or color.get('decodedFirstFrameColor', {}).get('final') != first_color:
            raise ValueError(f'Actual first decoded frame color differs: {slug}')
        audio = result.get('baselineAudioPreserved', {})
        if audio.get('passed') is not True or audio.get('audioPacketsAndTimingEqual') is not True \
                or audio.get('baselineSHA256') != baseline.get('baselineSHA256') \
                or not audio.get('decodedAudioPCM'):
            raise ValueError(f'Complete baseline AAC/PCM confirmation missing: {slug}')
        if audio_receipt != audio or baseline['baselineSHA256'] != digest(bind(WORK / 'baseline' / f'{slug}.mp4')):
            raise ValueError(f'Whole AAC receipt/baseline byte binding differs: {slug}')
        body_sha = digest(bind(revision / 'body.mp4'))
        if any(row.get('bodySHA256') != body_sha for row in (audio, media)) \
                or receipt.get('inputs', {}).get('bodySHA256') != body_sha:
            raise ValueError(f'Body byte binding differs across full-media receipts: {slug}')
        for key in ('audioPacketCount', 'audioPacketPayloadAndTimingSHA256', 'decodedAudioPCM'):
            if not audio.get(key) or media.get(key) != audio[key]:
                raise ValueError(f'Complete AAC/PCM receipt chain differs: {slug}/{key}')
        if media.get('passed') is not True or media.get('outputSHA256') != digest(movie) \
                or media.get('bodyFrames') != spec['body'] or media.get('finalFrames') != spec['frames'] \
                or any(media.get(key) is not True for key in ('bodyDecodedFramesAndTimestampsEqual',
                    'outputVideoTimelineContinuous', 'audioPacketsAndTimingEqual')):
            raise ValueError(f'Whole appendix/body/audio receipt differs: {slug}')
        if receipt.get('outputSHA256') != digest(movie) or receipt.get('presentation') != 'title-author' \
                or receipt.get('bodyFrames') != spec['body'] or receipt.get('finalVideoFrames') != spec['frames']:
            raise ValueError(f'Final actual reference appendix identity differs: {slug}')
        if receipt.get('episode') != slug or receipt.get('colorEncoding') != COLOR \
                or receipt.get('bibliography') != baseline['publishedReferenceReceipt']['bibliography'] \
                or receipt.get('appendix', {}).get('from') != spec['body'] \
                or receipt.get('appendix', {}).get('durationInFrames') != 150 \
                or receipt.get('inputs', {}).get('referencesSHA256') != digest(bind(ROOT / 'episodes-codex' / slug / 'references.json')):
            raise ValueError(f'Original titles/credits/five-second appendix binding differs: {slug}')
        if color.get('passed') is not True or color.get('output') != COLOR \
                or color.get('allRawToNormalizedPresentationTimesEqual') is not True \
                or color.get('allOriginalPublishedPresentationTimesEqual') is not True:
            raise ValueError(f'Actual color conversion/timeline receipt differs: {slug}')
        if result.get('colorNormalization') != color or color.get('finalFrames') != spec['frames'] \
                or not color.get('presentationTimelineSHA256') \
                or any(color.get('decodedFirstFrameColor', {}).get(stage) != COLOR for stage in ('normalized', 'body', 'final')):
            raise ValueError(f'Full timeline/actual color report chain differs: {slug}')
        if style.get('ep') != spec['ep'] or style.get('style') != 'peak-covers-v1' \
                or style.get('seriesSource') != 'episodes-codex/_shared/peak-covers':
            raise ValueError(f'Installed current peak cover template differs: {slug}')
        if style.get('productionRoot') != f'episodes-codex/{slug}' \
                or meta.get('poster') != style.get('sitePoster') \
                or bind(ROOT / 'episodes-codex' / slug / 'cover-style.json') != inputs[style_path]:
            raise ValueError(f'Current cover production/publication binding differs: {slug}')
        for path, expected in style['sourceSha256'].items():
            if digest(bind(ROOT / style['seriesSource'] / path)) != expected:
                raise ValueError(f'Current cover source binding differs: {slug}/{path}')
        cover_rows = []
        entries[f"EP{spec['ep']:02d}-{spec['name']}.mp4"] = movie
        for size in SIZES:
            path = published / f'cover-{size}.jpg'
            data = bind(path)
            expected = style['covers'][size]
            if digest(data) != expected['jpgSha256']:
                raise ValueError(f'Installed cover differs from cover-style: {slug}/{size}')
            if bind(ROOT / 'episodes-codex' / slug / f'cover-{size}.jpg') != data:
                raise ValueError(f'Production/publication cover bytes differ: {slug}/{size}')
            with Image.open(BytesIO(data)) as image:
                if image.format != 'JPEG' or list(image.size) != expected['dimensions']:
                    raise ValueError(f'Actual cover format/dimensions differ: {slug}/{size}')
            name = f"covers/EP{spec['ep']:02d}/cover-{size}.jpg"
            entries[name] = data
            cover_rows.append({'path': str(path.relative_to(ROOT)), 'zipPath': name,
                               'dimensions': expected['dimensions'], **record(data)})
        if bind(published / 'poster.jpg') != bind(published / 'cover-3x4.jpg'):
            raise ValueError(f'Portrait poster alias differs: {slug}')
        updated_times.append(updated)
        episodes.append({'slug': slug, 'ep': spec['ep'], 'title': meta['title'],
            'updatedAt': meta['updatedAt'],
            'createdAtOriginal': meta['createdAt'], 'publishedAtOriginal': meta['publishedAt'],
            'firstReleaseOriginal': meta['firstRelease'], 'baselineCommit': baseline['baselineCommit'],
            'sourcePathPreserved': meta['sourcePath'], 'frames': spec['frames'], 'bodyFrames': spec['body'],
            'video': {'path': str(movie_path.relative_to(ROOT)), **record(movie)}, 'actualVideoStream': probe,
            'actualFirstDecodedFrameColor': first_color, 'articleBytesPreserved': True,
            'articleSHA256': digest(article), 'completeBaselineAACPCMReceiptMatched': True,
            'completePresentationTimelineReceiptMatched': True,
            'renderResultSHA256': digest(inputs[result_path]), 'sourceManifestSHA256': digest(inputs[manifest_path]),
            'finalMediaReceiptSHA256': digest(inputs[media_path]), 'coverManifestSHA256': digest(inputs[style_path]),
            'covers': cover_rows})
    readme = '高并发、高可用、高性能系列视频与封面交付说明\n\n'
    for item in episodes:
        readme += (f"EP.{item['ep']:02d} {item['title']}\n"
                   f"视频更新时间：{item['updatedAt']}\n原创建：{item['createdAtOriginal']}；原首发：{item['publishedAtOriginal']}（{item['firstReleaseOriginal']}）\n"
                   f"完整视频：1920×1080，30fps，{item['frames']}帧（{item['frames']/30:.3f}秒），含末尾5秒参考资料页。\n\n")
    readme += ('封面、正文动画与资料页统一采用本系列深青蓝、亮青、暖黄、白字与抽象三线标识。\n'
               '保留各期原教学示例、配音、烧录字幕、章节时序与机制边界；视频使用有限范围BT.709编码。\n'
               'EP.11额度先扣后放行；EP.12同支付编号复用结果；EP.13暂停可选故障调用；EP.14搜索少预估而结算仍核验。\n'
               '包内三比例封面可按实际需要选用。此次只更新GitHub站点，没有向外部视频平台重发。\n\n包内文件与完整SHA-256：\n')
    readme += '\n'.join(f'{digest(data)}  {name} ({len(data)}字节)' for name, data in entries.items())
    readme += '\n'
    entries['说明.txt'] = readme.encode('utf-8')
    if len(entries) != 17:
        raise ValueError('Internal package member count differs')
    if sum(map(len, entries.values())) + 65536 > MAX_BYTES:
        raise ValueError('Source payloads exceed conservative 95MiB package budget')
    output.mkdir(parents=True, exist_ok=True)
    package_path = output / ZIP_NAME
    if package_path.exists():
        raise ValueError('ZIP already exists; preserve it and validate it rather than overwrite')
    timestamp = max(updated_times).astimezone(CST).timetuple()[:6]
    with zipfile.ZipFile(package_path, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for name, data in entries.items():
            info = zipfile.ZipInfo(safe_name(name), date_time=timestamp)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    if package_path.stat().st_size > MAX_BYTES:
        raise ValueError('ZIP exceeds conservative 95MiB Git file limit')
    validation = validate_zip(package_path, entries)
    for path, before in protected.items():
        if state(path) != before:
            raise ValueError(f'Production input bytes/SHA/mtime changed during packaging: {path}')
    manifest = {'schemaVersion': 1, 'status': 'packaged-and-verified',
        'createdAt': datetime.now(CST).isoformat(timespec='seconds'), 'episodes': episodes,
        'productionInputsBytesSHA256AndMtimeUnchanged': True, 'protectedInputCount': len(protected),
        'package': {'path': str(package_path.relative_to(ROOT)), 'file': ZIP_NAME,
                    **record(package_path.read_bytes()), 'validation': validation},
        'deliveryPlan': {'status': 'not-published', 'branch': DELIVERY_BRANCH, 'directory': DELIVERY_PATH,
            'immutableURLTemplate': f'https://raw.githubusercontent.com/linhongcun/video-studio/DELIVERY_COMMIT_SHA/{DELIVERY_PATH}/{ZIP_NAME}',
            'note': 'The explicit commit placeholder is a plan until the parent publishes and verifies the actual delivery commit.'}}
    manifest_path = output / 'package-manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'manifest': str(manifest_path.relative_to(ROOT)), **record(manifest_path.read_bytes()),
            'package': {key: value for key, value in manifest['package'].items() if key != 'validation'},
            'members': len(entries), 'protectedInputsUnchanged': len(protected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', default='work/peak-video-style/delivery')
    args = parser.parse_args()
    print(json.dumps(package(resolve_output(args.out_dir)), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
