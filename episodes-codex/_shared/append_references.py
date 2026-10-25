#!/usr/bin/env python3
"""Append a checked reference appendix while retaining the encoded video body.

The body is an explicit, immutable input, separate from the output. Only the
reference cards are encoded. The original AAC track is copied unchanged and
ends at its original endpoint; the visual appendix is silent. No TTS, mixing,
onset detection, old-body freezing, or original storyboard edits happen here.

  python append_references.py append --body original.mp4 \
    --references references.json --output video.mp4 --artifacts revisions/references
  python append_references.py verify --body original.mp4 \
    --references references.json --output video.mp4 --artifacts revisions/references

JSON contract: schemaVersion=1, episode, checkedAt, sources=[{id, organization,
title, version, url, supports:[...], sections, verification:{status:'verified',
checkedAt, evidence}}]. Optional displayTitle/displaySupport shorten the card;
the full title, URL and claim mapping remain in the source JSON and article.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont, __version__ as PILLOW_VERSION


ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / 'episodes/_shared/theme/pageTheme.ts'
MARKER = 'video-studio-reference-appendix:v1:'
DEFAULT_FONT = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
DEFAULT_BOLD = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {command[0]}\n{result.stderr[-6000:]}")
    return result.stdout


def probe(path: Path) -> dict:
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams',
                           '-show_format', '-of', 'json', str(path)]))


def stream(info: dict, kind: str) -> dict:
    matches = [s for s in info['streams'] if s['codec_type'] == kind]
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one {kind} stream, got {len(matches)}')
    return matches[0]


def load_references(path: Path) -> dict:
    doc = json.loads(path.read_text())
    if doc.get('schemaVersion') != 1:
        raise ValueError('references.json requires schemaVersion 1')
    if not isinstance(doc.get('episode'), str) or not doc['episode'].strip():
        raise ValueError('Missing episode')
    date.fromisoformat(doc['checkedAt'])
    refs = doc.get('sources')
    if not isinstance(refs, list) or not refs:
        raise ValueError('sources must be a nonempty list')
    ids = set()
    for ref in refs:
        for key in ('id', 'organization', 'title', 'version', 'sections'):
            if not isinstance(ref.get(key), str) or not ref[key].strip():
                raise ValueError(f'Missing source {key}')
        if ref['id'] in ids:
            raise ValueError(f"Duplicate source id: {ref['id']}")
        ids.add(ref['id'])
        parsed = urlparse(ref.get('url', ''))
        if parsed.scheme != 'https' or not parsed.netloc:
            raise ValueError(f"Source {ref['id']} needs an absolute HTTPS URL")
        if not isinstance(ref.get('supports'), list) or not ref['supports'] or any(
            not isinstance(s, str) or not s.strip() for s in ref['supports']
        ):
            raise ValueError(f"Source {ref['id']} needs concrete supported claims")
        verification = ref.get('verification', {})
        if verification.get('status') != 'verified' or not verification.get('evidence'):
            raise ValueError(f"Source {ref['id']} lacks verified evidence")
        date.fromisoformat(verification['checkedAt'])
    return doc


def palette() -> dict:
    # Read the actual common palette instead of defining another page theme.
    text = THEME.read_text()
    colors = {}
    for key in ('bg', 'ink', 'muted', 'row', 'border', 'success'):
        match = re.search(rf"\b{key}:\s*'(#[0-9A-Fa-f]{{6}})'", text)
        if not match:
            raise ValueError(f'Missing shared page palette key {key}')
        colors[key] = match.group(1)
    return colors


def wrapped(text: str, draw: ImageDraw.ImageDraw, font, width: int) -> list[str]:
    lines = []
    line = ''
    for char in text:
        if char == '\n':
            lines.append(line.rstrip())
            line = ''
        elif line and draw.textlength(line + char, font=font) > width:
            lines.append(line.rstrip())
            line = char.lstrip()
        else:
            line += char
    if line:
        lines.append(line.rstrip())
    return lines


def render_cards(doc: dict, directory: Path, width: int, height: int,
                 font_path: Path, bold_path: Path) -> list[Path]:
    if width < 1280 or height < 720:
        raise ValueError('Reference layout requires at least 1280×720; use a reviewed layout for smaller media')
    colors = palette()
    scale = width / 1920
    if abs(height / width - 9 / 16) > 0.002:
        raise ValueError('This reviewed reference layout expects 16:9 video')
    font = lambda size, bold=False: ImageFont.truetype(
        str(bold_path if bold else font_path), max(1, round(size * scale)), index=2)
    paths = []
    pages = [doc['sources'][i:i + 3] for i in range(0, len(doc['sources']), 3)]
    for page_index, refs in enumerate(pages):
        image = Image.new('RGB', (width, height), colors['bg'])
        draw = ImageDraw.Draw(image)
        xy = lambda x, y: (round(x * scale), round(y * scale))
        draw.text(xy(116, 58), doc.get('heading', '参考资料'),
                  font=font(60, True), fill=colors['ink'])
        draw.text(xy(119, 145), '本片主要依据 · 可核查来源',
                  font=font(28), fill=colors['muted'])
        page_label = f'{page_index + 1} / {len(pages)}'
        draw.text(xy(1698, 90), page_label, font=font(30), fill=colors['muted'])
        for index, ref in enumerate(refs):
            top = 223 + index * 226
            draw.rounded_rectangle((*xy(112, top), *xy(1808, top + 203)),
                                   radius=round(16 * scale), fill=colors['row'])
            draw.text(xy(142, top + 25), f"[{ref['id']}]", font=font(28, True),
                      fill=colors['success'])
            note = f" · {ref['note']}" if ref.get('note') else ''
            label = f"{ref['organization']} · {ref['version']}{note}"
            if draw.textlength(label, font=font(27)) > 1500 * scale:
                raise ValueError(f"COPYFIT source label too wide: {ref['id']}")
            draw.text(xy(263, top + 25), label, font=font(27), fill=colors['muted'])
            title = ref.get('displayTitle', ref['title'])
            lines = wrapped(title, draw, font(38, True), round(1490 * scale))
            if len(lines) > 2:
                raise ValueError(f"COPYFIT title needs a shorter displayTitle: {ref['id']}")
            title_top = top + 69 if len(lines) == 1 else top + 57
            for line_index, line in enumerate(lines):
                draw.text(xy(263, title_top + line_index * 43), line,
                          font=font(38, True), fill=colors['ink'])
            support = ref.get('displaySupport', ref['supports'][0])
            if draw.textlength(support, font=font(28)) > 1480 * scale:
                raise ValueError(f"COPYFIT claim needs a shorter displaySupport: {ref['id']}")
            draw.text(xy(263, top + 151), support, font=font(28), fill=colors['muted'])
        draw.text(xy(119, 973), '可暂停阅读 · 完整链接见配套图文',
                  font=font(29), fill=colors['ink'])
        access = f"资料核验：{doc['checkedAt']}"
        draw.text(xy(1330, 975), access, font=font(25), fill=colors['muted'])
        path = directory / f'references-{page_index + 1:02}.png'
        image.save(path)
        paths.append(path)
    return paths


def frame_rows(path: Path) -> list[list[str]]:
    text = run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
                '-an', '-fps_mode', 'passthrough', '-f', 'framemd5', '-'])
    return [[part.strip() for part in line.split(',')]
            for line in text.splitlines() if line and not line.startswith('#')]


def audio_packets(path: Path) -> list[dict]:
    return json.loads(run([
        'ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_packets',
        '-show_entries', 'packet=pts,dts,duration,size,data_hash',
        '-show_data_hash', 'sha256', '-of', 'json', str(path),
    ]))['packets']


def audio_hash(path: Path) -> str:
    return run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0',
                '-f', 'hash', '-hash', 'sha256', '-']).strip()


def sequence_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def verify_media(body: Path, output: Path, added_frames: int, pages: int,
                 frames_per_page: int, destination: Path) -> dict:
    before, after = probe(body), probe(output)
    bv, fv = stream(before, 'video'), stream(after, 'video')
    ba, fa = stream(before, 'audio'), stream(after, 'audio')
    fields = ('codec_name', 'width', 'height', 'r_frame_rate', 'time_base', 'pix_fmt', 'color_range')
    for key in fields:
        if bv.get(key) != fv.get(key):
            raise ValueError(f'Video stream parameter changed: {key}: {bv.get(key)} -> {fv.get(key)}')
    for key in ('codec_name', 'profile', 'sample_rate', 'channels', 'channel_layout', 'time_base'):
        if ba.get(key) != fa.get(key):
            raise ValueError(f'Audio stream parameter changed: {key}')
    original = frame_rows(body)
    final = frame_rows(output)  # Full decode, including the complete new appendix.
    if final[:len(original)] != original:
        first = next((i for i, (a, b) in enumerate(zip(original, final)) if a != b), None)
        raise ValueError(f'Original decoded body frame/timestamp changed, first index {first}')
    if len(final) != len(original) + added_frames:
        raise ValueError(f'Unexpected frame count {len(final)}, wanted {len(original) + added_frames}')
    for index, row in enumerate(final):
        if int(row[1]) != index or int(row[2]) != index or int(row[3]) != 1:
            raise ValueError(f'Non-continuous output frame timestamp at {index}: {row}')
    card_hashes = []
    for page in range(pages):
        rows = final[len(original) + page * frames_per_page:
                     len(original) + (page + 1) * frames_per_page]
        hashes = {row[-1] for row in rows}
        # Lossy H.264 encodes of a static image may converge by a few pixels;
        # only exact frame count and decodability are asserted here.
        card_hashes.append({'page': page + 1, 'frames': len(rows),
                            'uniqueDecodedHashes': len(hashes),
                            'firstFrameMD5': rows[0][-1], 'lastFrameMD5': rows[-1][-1]})
    old_packets, new_packets = audio_packets(body), audio_packets(output)
    if old_packets != new_packets:
        raise ValueError('Original AAC packet payload/order/PTS/DTS/duration changed')
    old_pcm, new_pcm = audio_hash(body), audio_hash(output)
    if old_pcm != new_pcm:
        raise ValueError('Original decoded audio PCM changed')
    report = {
        'checkedAtUTC': datetime.now(timezone.utc).isoformat(), 'passed': True,
        'bodySHA256': sha(body), 'outputSHA256': sha(output),
        'bodyFrames': len(original), 'appendedFrames': added_frames,
        'finalFrames': len(final), 'fps': bv['r_frame_rate'],
        'bodyFrameMD5RowsSHA256': sequence_hash(original),
        'bodyDecodedFramesAndTimestampsEqual': True,
        'outputVideoTimelineContinuous': True,
        'audioPacketCount': len(old_packets),
        'audioPacketPayloadAndTimingSHA256': sequence_hash(old_packets),
        'audioPacketsAndTimingEqual': True, 'decodedAudioPCM': old_pcm,
        'audioStreamEndsAtOriginalEndpointSeconds': float(fa['duration']),
        'appendixAudio': 'No audio packets added; original AAC stream ends at its original endpoint.',
        'cardPages': card_hashes,
        'scope': 'Full decoded video frame/timestamp comparison plus full AAC packet and PCM comparison. Visual legibility and browser playback are separate checks.',
    }
    dump(destination, report)
    return report


def concatenate_video(body: Path, cards: list[Path], output: Path,
                      temporary: Path, references_sha: str) -> None:
    # The concat demuxer inserts current SPS/PPS at H.264 segment boundaries.
    # Only video is concatenated; the original AAC stream is separately copied.
    video_body = temporary / 'body-video.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(body), '-map', '0:v:0',
         '-c:v', 'copy', '-an', str(video_body)])
    concat = temporary / 'video-concat.txt'
    parts = [video_body, *cards]
    # These paths are our temporary/generated file paths, not user text.
    def quoted(path: Path) -> str:
        return "'" + str(path.resolve()).replace("'", "'\\''") + "'"
    concat.write_text(''.join('file ' + quoted(part) + '\n' for part in parts))
    silent = temporary / 'combined-video.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i',
         str(concat), '-map', '0:v:0', '-c:v', 'copy', '-an', str(silent)])
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(silent), '-i', str(body),
         '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
         '-map_metadata', '1', '-metadata', 'comment=' + MARKER + references_sha,
         '-movflags', '+faststart', str(output)])


def append(args) -> dict:
    body, output = args.body.resolve(), args.output.resolve()
    if body == output:
        raise ValueError('Body and output must be separate paths; keep an immutable original')
    info = probe(body)
    if info.get('format', {}).get('tags', {}).get('comment', '').startswith(MARKER):
        raise ValueError('Input body already has a reference appendix; refusing to append twice')
    bv, ba = stream(info, 'video'), stream(info, 'audio')
    if bv['codec_name'] != 'h264' or ba['codec_name'] != 'aac':
        raise ValueError('This tool supports reviewed H.264/AAC inputs only')
    profile = {'Constrained Baseline': 'baseline', 'Baseline': 'baseline',
               'Main': 'main', 'High': 'high'}.get(bv.get('profile'))
    if not profile:
        raise ValueError(f"Unreviewed H.264 profile: {bv.get('profile')}")
    if bv.get('start_time') != '0.000000' or ba.get('start_time') != '0.000000':
        raise ValueError('Expected original audio/video to start at zero')
    fps = Fraction(bv['r_frame_rate'])
    if Fraction(bv['avg_frame_rate']) != fps:
        raise ValueError('Variable frame rate requires a separately reviewed append workflow')
    page_frames = Fraction(str(args.seconds)) * fps
    if page_frames.denominator != 1 or page_frames < 1:
        raise ValueError('Page duration must be a positive integer number of frames')
    page_frames = int(page_frames)
    doc = load_references(args.references)
    artifacts = args.artifacts.resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    manifest_path = artifacts / 'reference-appendix.json'
    inputs = {
        'bodySHA256': sha(body), 'referencesSHA256': sha(args.references),
        'generatorSHA256': sha(Path(__file__)), 'themeSHA256': sha(THEME),
        'fontSHA256': sha(args.font), 'boldFontSHA256': sha(args.bold_font),
        'secondsPerPage': args.seconds,
    }
    if output.exists():
        if manifest_path.exists():
            previous = json.loads(manifest_path.read_text())
            if previous['inputs'] == inputs and previous['outputSHA256'] == sha(output):
                return {'status': 'already-current', 'manifest': str(manifest_path), **previous}
            if previous['outputSHA256'] != sha(output):
                raise ValueError('Output changed outside this tool; refusing to overwrite it')
        elif sha(output) != inputs['bodySHA256']:
            raise ValueError('Existing output has no receipt and differs from original; refusing overwrite')
    cards = render_cards(doc, artifacts, int(bv['width']), int(bv['height']), args.font, args.bold_font)
    timescale = Fraction(bv['time_base'])
    if timescale.numerator != 1:
        raise ValueError('Expected an integer video track timescale')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='references-', dir=str(artifacts)) as temp:
        temporary = Path(temp)
        card_videos = []
        for index, image in enumerate(cards):
            video = temporary / f'card-{index + 1:02}.mp4'
            command = [
                'ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', str(fps),
                '-i', str(image), '-frames:v', str(page_frames), '-an',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-pix_fmt', bv['pix_fmt'], '-profile:v', profile,
                '-level:v', str(int(bv['level']) / 10),
                '-video_track_timescale', str(timescale.denominator),
                '-color_range', bv.get('color_range', 'pc' if 'yuvj' in bv['pix_fmt'] else 'tv'),
                str(video),
            ]
            run(command)
            card_videos.append(video)
        candidate = temporary / 'candidate.mp4'
        concatenate_video(body, card_videos, candidate, temporary, inputs['referencesSHA256'])
        added = len(cards) * page_frames
        report = verify_media(body, candidate, added, len(cards), page_frames,
                              artifacts / 'reference-appendix-media-check.json')
        # Replace output only after all full-file media checks pass.
        candidate.replace(output)
    total = report['finalFrames']
    manifest = {
        'schemaVersion': 1, 'createdAtUTC': datetime.now(timezone.utc).isoformat(),
        'episode': doc['episode'], 'inputs': inputs,
        'body': str(body), 'references': str(args.references.resolve()),
        'output': str(output), 'outputSHA256': sha(output),
        'bodyFrames': report['bodyFrames'], 'finalVideoFrames': total,
        'fps': str(fps), 'durationSeconds': float(Fraction(total) / fps),
        'appendix': {'kind': 'references', 'from': report['bodyFrames'],
                     'durationInFrames': added, 'framesPerPage': page_frames,
                     'sourceIds': [ref['id'] for ref in doc['sources']],
                     'pages': [{'file': image.name, 'sha256': sha(image)} for image in cards]},
        'audio': report['appendixAudio'],
        'bodyProductionInputs': 'Original narration/storyboard/freeze are retained separately and are not rewritten to claim the body was rerendered.',
        'tools': {'ffmpeg': run(['ffmpeg', '-version']).splitlines()[0],
                  'pillow': PILLOW_VERSION,
                  'fontFaceIndex': 2},
    }
    dump(manifest_path, manifest)
    return {'status': 'appended', **manifest}


def verify(args) -> dict:
    manifest_path = args.artifacts / 'reference-appendix.json'
    manifest = json.loads(manifest_path.read_text())
    load_references(args.references)
    if sha(args.body) != manifest['inputs']['bodySHA256']:
        raise ValueError('Original body SHA changed')
    if sha(args.references) != manifest['inputs']['referencesSHA256']:
        raise ValueError('Reference input SHA changed')
    for key, path in (('generatorSHA256', Path(__file__)), ('themeSHA256', THEME),
                      ('fontSHA256', args.font), ('boldFontSHA256', args.bold_font)):
        if sha(path) != manifest['inputs'][key]:
            raise ValueError(f'Frozen appendix dependency changed: {key}')
    if sha(args.output) != manifest['outputSHA256']:
        raise ValueError('Final media SHA changed')
    for page in manifest['appendix']['pages']:
        if sha(args.artifacts / page['file']) != page['sha256']:
            raise ValueError('Reference card image changed')
    return verify_media(args.body, args.output, manifest['appendix']['durationInFrames'],
                        len(manifest['appendix']['pages']), manifest['appendix']['framesPerPage'],
                        args.artifacts / 'reference-appendix-media-check.json')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('append', 'verify'))
    parser.add_argument('--body', required=True, type=Path)
    parser.add_argument('--references', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--artifacts', required=True, type=Path)
    parser.add_argument('--seconds', type=float, default=5,
                        help='Seconds per page; default 5 with an explicit pause-reading prompt')
    parser.add_argument('--font', type=Path, default=DEFAULT_FONT)
    parser.add_argument('--bold-font', type=Path, default=DEFAULT_BOLD)
    args = parser.parse_args()
    result = append(args) if args.action == 'append' else verify(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
