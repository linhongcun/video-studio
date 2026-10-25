#!/usr/bin/env python3
"""Plan and encode a reviewed mixture of fresh Remotion intervals and old pictures.

This tool never creates narration, judges visual equivalence, changes a freeze, or
renders Remotion. Run --plan-only before clips exist, render its commands, obtain
an independent visual-reuse review, run --plan-only again, then freeze all inputs
listed by the plan. --run reads that frozen plan without rewriting it.

Default episode layout:
  revisions/approach-first/baseline.json
  revisions/approach-first/before/{plan.json,source-sha256.json,voice/build.json}
  remotion/out/approach-baseline/{video.mp4,storyboard.json,voice.wav,src/}

The old mixed movie supplies pictures only. The sole audio input is the new
48kHz mono voice.wav produced by the repository's shared voice/build.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import wave

VERSION = 1
CARD_SLUG = 'code-card'
METHOD = 'Reviewed slug-mapped picture splice; new shared-build narration only.'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def relative(path, episode):
    import os
    return os.path.relpath(path, episode)


def resolved(path, episode):
    return (episode / path).resolve()


def probe(path):
    data = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))
    videos = [stream for stream in data['streams'] if stream['codec_type'] == 'video']
    require(len(videos) == 1, f'{path}: expected exactly one video stream')
    return videos[0]


def check_video(path, frames, width=1920, height=1080):
    video = probe(path)
    require(int(video['nb_frames']) == frames, f'{path}: frame count must be {frames}, got {video.get("nb_frames")}')
    require(video['r_frame_rate'] == '30/1', f'{path}: expected 30fps')
    require((video['width'], video['height']) == (width, height), f'{path}: expected {width}x{height}')


def table(plan_path, storyboard_path):
    plan, storyboard = read(plan_path), read(storyboard_path)
    shots = [shot for scene in storyboard['scenes'] for shot in scene['shots']]
    require(len(plan) == len(shots), f'{plan_path}: plan/storyboard count mismatch')
    require(storyboard['meta']['fps'] == 30, 'Only 30fps production inputs are supported')
    require((storyboard['meta']['width'], storyboard['meta']['height']) == (1920, 1080), 'Only 1080p inputs are supported')
    rows, slugs, ids, cursor = [], set(), set(), 0
    for item, shot in zip(plan, shots):
        sid = f'{int(item["id"]):02d}'
        slug = item['slug']
        require(sid == f'{int(shot["id"]):02d}', f'{slug}: plan/shot ID mismatch')
        require(slug not in slugs and sid not in ids, f'Duplicate plan slug or ID: {slug}/{sid}')
        require(shot['from'] == cursor and shot['durationInFrames'] > 0, f'{slug}: noncontinuous storyboard')
        slugs.add(slug); ids.add(sid)
        rows.append(dict(slug=slug, id=sid, shot=shot))
        cursor += shot['durationInFrames']
    require(cursor == storyboard['meta']['durationInFrames'], 'Storyboard total mismatch')
    card = storyboard['meta']['unvoicedEndCard']
    require(card['kind'] == 'full-python-solution' and card['durationInFrames'] == 150, 'Expected a complete 150-frame Python card')
    require(card['from'] + 150 == cursor, 'Python card must cover the final 150 frames')
    require(shots[-1]['from'] + shots[-1]['codeCardFrom'] == card['from'], 'Last shot/card boundary mismatch')
    for row in rows:
        row['bodyFrames'] = row['shot'].get('codeCardFrom', row['shot']['durationInFrames'])
        require(row['bodyFrames'] > 0, f'{row["slug"]}: empty narrative segment')
    return rows, storyboard


def captions(shot):
    result = []
    for item in shot['subtitles']:
        end = item.get('to', item['from'] + item.get('duration', 0) - 1)
        require(end >= item['from'], 'Invalid subtitle range')
        if 'duration' in item:
            require(item['duration'] == end - item['from'] + 1, 'Invalid subtitle duration')
        result.append(dict(text=item['text'], start=item['from'], end=end))
    return result


def cues(shot):
    # IDs contain scene numbers and legitimately change after insertion. The
    # semantic cue and its exact local appearance time must remain unchanged.
    terms = []
    for element in shot.get('elements', []):
        if element.get('cueText'):
            terms.append((element['cueText'], element['appearFrame']))
    return dict(frames=shot.get('cueFrames', {}), terms=sorted(terms))


def selected(build_path, manifest, episode):
    rows = read(build_path)['sentences']
    by_shot = {}
    for row in rows:
        path = f'voice/takes/{row["id"]}-{row["take"]}.wav'
        require(path in manifest, f'{build_path}: selected take is not in its source freeze: {path}')
        by_shot.setdefault(row['shot'], []).append(dict(
            id=row['id'], text=row['text'], tts=row['tts'], takePath=path,
            takeSha256=manifest[path], startFrame=row['startFrame'], endFrame=row['endFrame']))
    return by_shot


def reuse_check(old, new, old_sentences, new_sentences, allow_tail):
    a, b = old['shot'], new['shot']
    prefix = f'{new["id"]}/{new["slug"]}: '
    require(a['visualType'] == b['visualType'], prefix + 'visualType differs; render this shot')
    require(a['narration'] == b['narration'], prefix + 'narration differs; render this shot')
    require(cues(a) == cues(b), prefix + 'local semantic cue times differ; render this shot')
    delta = new['bodyFrames'] - old['bodyFrames']
    require(delta == 0 or (allow_tail and abs(delta) == 1), prefix + f'body length differs by {delta}; render or explicitly review a one-frame tail adjustment')
    old_caps, new_caps = captions(a), captions(b)
    require(len(old_caps) == len(new_caps), prefix + 'subtitle count differs')
    for index, (first, second) in enumerate(zip(old_caps, new_caps)):
        require(first['text'] == second['text'] and first['start'] == second['start'], prefix + 'subtitle text/start differs')
        expected = first['end'] + (delta if index == len(old_caps) - 1 else 0)
        require(second['end'] == expected, prefix + 'internal subtitle timing differs')
    require(old_caps[-1]['end'] == old['bodyFrames'] - 1 and new_caps[-1]['end'] == new['bodyFrames'] - 1, prefix + 'final subtitle does not cover body hold')
    require(len(old_sentences) == len(new_sentences) == len(old_caps), prefix + 'selected sentence count differs')
    sentence_proof = []
    for index, (first, second) in enumerate(zip(old_sentences, new_sentences)):
        require(first['text'] == old_caps[index]['text'] and second['text'] == new_caps[index]['text'], prefix + 'build sentence/subtitle text differs')
        for field in ['text', 'tts', 'takeSha256']:
            require(first[field] == second[field], prefix + f'selected sentence {field} differs; render this shot')
        sentence_proof.append(dict(oldId=first['id'], newId=second['id'], sha256=first['takeSha256'], oldTake=first['takePath'], newTake=second['takePath']))
    if delta:
        boundary = min(old['bodyFrames'], new['bodyFrames']) - 1
        for shot in [a, b]:
            require(max(part['localEnd'] for part in shot['voice']) < boundary,
                    prefix + 'tail adjustment could cut narration; render this shot')
    return dict(tailFrameAdjustment=delta, selectedSentences=sentence_proof,
                checks='Exact narration, visualType, local subtitles, semantic cues and selected take SHA; only explicitly allowed final hold may differ by one frame.')


def visual_sources(episode):
    # Include imported data/assets and alias/package configuration, not merely
    # TS/JS. The placeholder storyboard is a timing copy, separately bound to the
    # real storyboard, and is refreshed by the standard freezer after planning.
    placeholder = episode / 'remotion/src/placeholders/storyboard.json'
    paths = sorted(p for p in (episode / 'remotion/src').rglob('*') if p.is_file() and p != placeholder)
    paths += [p for name in ['remotion/remotion.config.ts', 'remotion/package.json', 'remotion/package-lock.json', 'covers.json']
              if (p := episode / name).is_file()]
    shared_theme = episode.parents[1] / 'episodes/_shared/theme/pageTheme.ts'
    if shared_theme.is_file():
        paths.append(shared_theme)
    return {relative(path, episode): sha(path) for path in paths}


def source_manifest(path):
    manifest = read(path)
    require(isinstance(manifest, dict), f'{path}: invalid source manifest')
    return manifest


def check_voice(path, storyboard):
    total = storyboard['meta']['durationInFrames']
    card = storyboard['meta']['unvoicedEndCard']
    with wave.open(str(path)) as audio:
        require((audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) == (48000, 1, 2), f'{path}: expected 48k mono 16-bit voice')
        require(audio.getnframes() == total * 1600, f'{path}: audio sample/frame count mismatch')
        audio.setpos(card['from'] * 1600)
        require(not any(audio.readframes(150 * 1600)), f'{path}: Python card overlaps narration')


def parse_selectors(value, rows):
    requested = [str(item).strip() for item in value if str(item).strip()]
    result = set()
    for item in requested:
        item = str(item)
        matches = [row['slug'] for row in rows if item in {row['id'], row['slug'], row['id'] + '-' + row['slug']}]
        require(len(matches) == 1, f'Unknown or ambiguous rendered shot selector: {item}')
        result.add(matches[0])
    return result


def make_plan(args):
    episode = args.episode.resolve()
    revision = episode / 'revisions/approach-first'
    before = (args.before or revision / 'before').resolve()
    baseline = (args.baseline or episode / 'remotion/out/approach-baseline').resolve()
    baseline_record = (args.baseline_record or revision / 'baseline.json').resolve()
    review_path = (args.review or revision / 'visual-reuse-review.json').resolve()
    current_manifest_path = episode / 'source-sha256.json'
    plan_path = (args.plan or episode / 'approach-remix-plan.json').resolve()
    old_manifest_path = before / 'source-sha256.json'
    current_manifest = source_manifest(current_manifest_path)
    frozen_paths = {resolved(name, episode) for name in current_manifest}
    previous_plan = read(plan_path) if plan_path.is_file() else None
    previous_clips = {}
    if isinstance(previous_plan, dict) and previous_plan.get('schemaVersion') == VERSION and previous_plan.get('method') == METHOD:
        previous_clips = {resolved(clip['path'], episode): clip['sha256'] for clip in previous_plan.get('clips', [])}
    old_manifest = source_manifest(old_manifest_path)
    info = read(baseline_record)
    old_video, old_sb_path, old_voice = [baseline / name for name in ['video.mp4', 'storyboard.json', 'voice.wav']]
    for path in [old_video, old_sb_path, old_voice]:
        require(sha(path) == info['sha256'][path.name], f'Baseline SHA mismatch: {path}')
    require(sha(old_manifest_path) == info['sourceManifestSha256'], 'Original freeze snapshot differs from baseline record')
    for path, key in [(before / 'plan.json', 'plan.json'), (before / 'voice/build.json', 'voice/build.json')]:
        require(sha(path) == old_manifest[key], f'Baseline metadata SHA mismatch: {path}')
    old_visual_files = []
    for name, expected in old_manifest.items():
        if name.startswith('remotion/src/'):
            path = baseline / 'src' / name.removeprefix('remotion/src/')
            require(path.is_file() and sha(path) == expected, f'Baseline visual source snapshot mismatch: {path}')
            old_visual_files.append(path)
    require(old_visual_files, 'Baseline visual source snapshot is required for independent review')
    require(sha(baseline / 'src/Main.tsx') == info['mainSourceSha256'], 'Baseline Main source differs from baseline record')
    old_rows, old_sb = table(before / 'plan.json', old_sb_path)
    new_rows, new_sb = table(episode / 'plan.json', episode / 'storyboard.json')
    require(sha(old_sb_path) == old_manifest['storyboard.json'], 'Baseline storyboard is not the frozen original')
    require(sha(old_voice) == old_manifest['voice.wav'], 'Baseline voice is not the frozen original')
    check_voice(old_voice, old_sb); check_voice(episode / 'voice.wav', new_sb)
    require(read(episode / 'voice/build.json')['summary']['sha'] == sha(episode / 'voice.wav'), 'Current voice build hash mismatch')
    old_selected = selected(before / 'voice/build.json', old_manifest, episode)
    # A new freeze is intentionally created after the plan. For planning, obtain
    # take identities from actual files, rather than an obsolete prior freeze.
    new_build = read(episode / 'voice/build.json')
    new_take_hashes = {}
    for row in new_build['sentences']:
        name = f'voice/takes/{row["id"]}-{row["take"]}.wav'
        new_take_hashes[name] = sha(episode / name)
    new_selected = selected(episode / 'voice/build.json', new_take_hashes, episode)
    changes = read(args.changes.resolve()) if args.changes else {}
    selectors = [q for q in (args.render_shots or '').split(',') if q] + changes.get('renderShots', [])
    rendered = parse_selectors(selectors, new_rows)
    mappings = changes.get('reuseMap', {})
    old_by_slug = {row['slug']: row for row in old_rows}
    new_by_slug = {row['slug']: row for row in new_rows}
    require(set(mappings) <= set(new_by_slug), 'reuseMap includes an unknown new slug')
    require(set(mappings.values()) <= set(old_by_slug), 'reuseMap includes an unknown old slug')
    used_old = set(); atoms = []
    for row in new_rows:
        atom = dict(kind='fresh' if row['slug'] in rendered else 'reuse', slug=row['slug'], id=row['id'],
                    targetFrom=row['shot']['from'], targetFrames=row['bodyFrames'])
        if atom['kind'] == 'reuse':
            source_slug = mappings.get(row['slug'], row['slug'])
            require(source_slug in old_by_slug, f'{row["id"]}/{row["slug"]}: new slug must be listed in --render-shots')
            require(source_slug not in used_old, f'Old slug mapped more than once: {source_slug}')
            used_old.add(source_slug)
            old = old_by_slug[source_slug]
            proof = reuse_check(old, row, old_selected[f'{old["id"]}-{old["slug"]}'],
                                new_selected[f'{row["id"]}-{row["slug"]}'], args.allow_tail_frame_adjustment)
            atom.update(sourceSlug=source_slug, sourceFrom=old['shot']['from'], sourceFrames=old['bodyFrames'], proof=proof)
        atoms.append(atom)
    old_card, new_card = old_sb['meta']['unvoicedEndCard'], new_sb['meta']['unvoicedEndCard']
    render_card = args.render_card or changes.get('renderCard', False)
    for field in ['codeSource', 'displaySource']:
        require(sha(episode / new_card[field]) == new_card[field + 'Sha256'], 'Current solution/card source hash mismatch')
        if not render_card:
            require(old_card[field + 'Sha256'] == new_card[field + 'Sha256'], 'Changed Python solution requires --render-card')
    atoms.append(dict(kind='fresh' if render_card else 'reuse', slug=CARD_SLUG, id=CARD_SLUG,
                      sourceSlug=CARD_SLUG, sourceFrom=old_card['from'], sourceFrames=150,
                      targetFrom=new_card['from'], targetFrames=150,
                      proof=dict(codeSourceSha256=new_card['codeSourceSha256'], displaySourceSha256=new_card['displaySourceSha256'], tailFrameAdjustment=0)))
    segments, cursor = [], 0
    for atom in atoms:
        require(atom['targetFrom'] == cursor, 'Noncontinuous splice atoms')
        cursor += atom['targetFrames']
        if atom['kind'] == 'fresh' and segments and segments[-1]['kind'] == 'fresh':
            segments[-1]['shots'].append(atom['slug']); segments[-1]['ids'].append(atom['id'])
            segments[-1]['targetFrames'] += atom['targetFrames']
        elif atom['kind'] == 'fresh':
            segments.append(dict(kind='fresh', shots=[atom['slug']], ids=[atom['id']], targetFrom=atom['targetFrom'], targetFrames=atom['targetFrames']))
        else:
            segments.append(atom)
    require(cursor == new_sb['meta']['durationInFrames'], 'Splice total mismatch')
    inputs = [old_video, old_sb_path, old_voice, baseline_record, old_manifest_path, before / 'plan.json', before / 'voice/build.json',
              episode / 'storyboard.json', episode / 'voice.wav', episode / 'voice/build.json', episode / 'plan.json',
              episode / new_card['codeSource'], episode / new_card['displaySource'], Path(__file__).resolve()]
    inputs += old_visual_files
    if args.changes:
        inputs.append(args.changes.resolve())
    for name in new_take_hashes:
        inputs.append(episode / name)
    clips = []; clip_paths = set()
    for segment in segments:
        if segment['kind'] != 'fresh':
            continue
        key = segment['ids'][0] if len(segment['ids']) == 1 else segment['ids'][0] + '-' + segment['ids'][-1]
        path = resolved(changes.get('clipPaths', {}).get(key, f'remotion/out/approach-{key}.mp4'), episode)
        require(path.suffix.lower() == '.mp4', 'Fresh render outputs must be MP4 files')
        require(path not in inputs and path not in {episode / 'video.mp4', current_manifest_path, plan_path}, f'Fresh clip would overwrite an input: {path}')
        if path in frozen_paths:
            require(path in previous_clips and previous_clips[path] and sha(path) == previous_clips[path],
                    f'Fresh clip path is another frozen input: {path}')
        require(path not in clip_paths, f'Fresh intervals must have distinct clip files: {path}')
        clip_paths.add(path)
        command = ['./node_modules/.bin/remotion', 'render', 'src/index.ts', 'Main', relative(path, episode / 'remotion'),
                   f'--frames={segment["targetFrom"]}-{segment["targetFrom"] + segment["targetFrames"] - 1}',
                   '--codec=h264', '--crf=18', '--concurrency=2', '--browser-executable=/usr/bin/chromium', '--bundle-cache=false']
        clip = dict(key=key, path=relative(path, episode), frames=segment['targetFrames'],
                    frameRange=[segment['targetFrom'], segment['targetFrom'] + segment['targetFrames'] - 1],
                    sha256=sha(path) if path.is_file() else None, command=command,
                    commandCwd='remotion', shellCommand=shlex.join(command))
        segment['clipKey'] = key; clips.append(clip)
        if path.is_file():
            inputs.append(path)
    visual = visual_sources(episode)
    inputs += [resolved(name, episode) for name in visual]
    review_template = dict(reviewedBy='REQUIRED: independent reviewer identity', baselineVideoSha256=sha(old_video),
                           approvedReuseSlugs=[item['slug'] for item in atoms if item['kind'] == 'reuse'],
                           currentVisualSourcesSHA256=visual,
                           notes='REQUIRED: identify reviewed unchanged helpers/data/scene branches and actual same-frame evidence; this tool does not determine visual equivalence.')
    if review_path.is_file():
        inputs.append(review_path)
    output = (args.output or episode / 'remotion/out/voice-approach.mp4').resolve()
    protected = {resolved(name, episode) for name in current_manifest} | {current_manifest_path, plan_path, episode / 'video.mp4'}
    require(output not in inputs and output not in protected, 'Output must not overwrite a frozen input, plan or canonical final media')
    return dict(schemaVersion=VERSION, method=METHOD,
                fps=30, width=1920, height=1080, frames=cursor, segments=segments, atoms=atoms, clips=clips,
                inputSHA256={relative(path, episode): sha(path) for path in sorted(set(inputs))},
                visualSourceSHA256=visual, visualReview=relative(review_path, episode), reviewTemplate=review_template,
                baselineVideo=relative(old_video, episode), voice='voice.wav', output=relative(output, episode),
                planOptions=dict(renderShots=args.render_shots or '', changes=relative(args.changes.resolve(), episode) if args.changes else None,
                                 renderCard=args.render_card, allowTailFrameAdjustment=args.allow_tail_frame_adjustment,
                                 before=relative(before, episode), baseline=relative(baseline, episode), baselineRecord=relative(baseline_record, episode)),
                freezeRequirements=dict(instructions='After clips and independent review exist, regenerate --plan-only, then freeze this plan plus every inputSHA256 path. source-sha256.json itself is not an input to the plan, preventing a hash cycle.',
                                        files=[relative(args.plan.resolve() if args.plan else episode / 'approach-remix-plan.json', episode)] + sorted({relative(path, episode) for path in inputs})),
                limitations=['Selected raw take SHA equality is checked; global voice normalization may differ, so old/new full-track PCM equality is not claimed.',
                             'The independent review must establish visual equivalence. Metadata equality alone never proves reused scene code is unchanged.',
                             'Old mixed audio and all changed-clip audio are discarded. Shared BGM mixing must run after this voice-only output.'])


def validate_review(plan, episode):
    path = resolved(plan['visualReview'], episode)
    require(path.is_file(), f'Independent visual reuse review is missing: {path}')
    review = read(path)
    require(review.get('reviewedBy') and not review['reviewedBy'].startswith('REQUIRED'), 'An actual independent reviewer is required')
    require(review.get('notes') and not review['notes'].startswith('REQUIRED'), 'Actual visual review notes/evidence are required')
    require(review.get('baselineVideoSha256') == plan['inputSHA256'][plan['baselineVideo']], 'Review is bound to another baseline video')
    require(review.get('currentVisualSourcesSHA256') == plan['visualSourceSHA256'] == visual_sources(episode), 'Review visual source bindings differ')
    required = {atom['slug'] for atom in plan['atoms'] if atom['kind'] == 'reuse'}
    approved = review.get('approvedReuseSlugs', [])
    require(len(approved) == len(set(approved)) and required <= set(approved), 'Every reused shot/card requires explicit visual approval')
    adjusted = [atom['slug'] for atom in plan['atoms'] if atom['kind'] == 'reuse' and atom['proof'].get('tailFrameAdjustment')]
    require(not adjusted or review.get('approvedTailFrameAdjustments') == {atom['slug']: atom['proof']['tailFrameAdjustment'] for atom in plan['atoms'] if atom['slug'] in adjusted}, 'Tail-frame adjustments require explicit per-shot review approval')


def run_plan(args):
    episode = args.episode.resolve()
    plan_path = (args.plan or episode / 'approach-remix-plan.json').resolve()
    plan = read(plan_path)
    require(plan['schemaVersion'] == VERSION, 'Unsupported plan version')
    manifest_path = episode / 'source-sha256.json'
    manifest = source_manifest(manifest_path)
    for name, expected in manifest.items():
        path = resolved(name, episode)
        require(path.is_file() and sha(path) == expected, f'Current frozen input differs: {name}')
    require(manifest.get(relative(plan_path, episode)) == sha(plan_path), 'The splice plan must be included in the current freeze')
    for name, expected in plan['inputSHA256'].items():
        path = resolved(name, episode)
        require(path.is_file() and sha(path) == expected, f'Planned input differs: {name}')
        require(manifest.get(name) == expected, f'Planned input is not in current source freeze: {name}')
    # Recompute semantic constraints from current inputs, without saving anything.
    options = plan['planOptions']
    planned_args = argparse.Namespace(**vars(args))
    for field, key in [('render_shots', 'renderShots'), ('render_card', 'renderCard'), ('allow_tail_frame_adjustment', 'allowTailFrameAdjustment')]:
        setattr(planned_args, field, options[key])
    for field, key in [('before', 'before'), ('baseline', 'baseline'), ('baseline_record', 'baselineRecord'), ('changes', 'changes')]:
        setattr(planned_args, field, resolved(options[key], episode) if options[key] else None)
    planned_args.review = resolved(plan['visualReview'], episode)
    planned_args.output = resolved(plan['output'], episode)
    rebuilt = make_plan(planned_args)
    require(rebuilt == plan, 'Current semantic inputs/options no longer reproduce the frozen plan')
    validate_review(plan, episode)
    for clip in plan['clips']:
        require(clip['sha256'], f'Clip was missing when plan was frozen: {clip["path"]}')
        check_video(resolved(clip['path'], episode), clip['frames'])
    old_video = resolved(plan['baselineVideo'], episode)
    old_sb = read(resolved(plan['planOptions']['baseline'], episode) / 'storyboard.json')
    check_video(old_video, old_sb['meta']['durationInFrames'])
    output = resolved(plan['output'], episode)
    result_path = episode / 'approach-remix-result.json'
    require(relative(result_path, episode) not in manifest, 'The result report is an output and must not be in the input freeze')
    require(not output.exists() or args.overwrite_output, f'Output already exists; use --overwrite-output deliberately: {output}')
    inputs = [old_video] + [resolved(clip['path'], episode) for clip in plan['clips']] + [episode / 'voice.wav']
    require(output not in inputs, 'Output aliases an input')
    reused = [segment for segment in plan['segments'] if segment['kind'] == 'reuse']
    graph = []
    if reused:
        graph.append(f'[0:v]split={len(reused)}' + ''.join(f'[old{i}]' for i in range(len(reused))))
    clip_indices = {clip['key']: index + 1 for index, clip in enumerate(plan['clips'])}
    labels = []; reuse_index = 0
    for index, segment in enumerate(plan['segments']):
        label = f's{index}'; labels.append(f'[{label}]')
        if segment['kind'] == 'fresh':
            source = f'[{clip_indices[segment["clipKey"]]}:v]'
            graph.append(source + f'trim=end_frame={segment["targetFrames"]},setpts=N/(30*TB),setsar=1[{label}]')
        else:
            source = f'[old{reuse_index}]'; reuse_index += 1
            start, length = segment['sourceFrom'], segment['sourceFrames']
            graph.append(source + f'trim=start_frame={start}:end_frame={start + length},setpts=N/(30*TB),'
                         f'tpad=stop_mode=clone:stop=1,trim=end_frame={segment["targetFrames"]},setpts=N/(30*TB),setsar=1[{label}]')
    graph.append(''.join(labels) + f'concat=n={len(labels)}:v=1:a=0,setpts=N/(30*TB)[video]')
    command = ['ffmpeg', '-y' if args.overwrite_output else '-n', '-v', 'error']
    for path in inputs:
        command += ['-i', str(path)]
    command += ['-filter_complex_threads', '1', '-filter_complex', ';'.join(graph), '-map', '[video]',
                '-map', f'{len(inputs) - 1}:a:0', '-frames:v', str(plan['frames']), '-r', '30', '-fps_mode', 'cfr',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-threads', '2', '-pix_fmt', 'yuv420p',
                '-video_track_timescale', '30000', '-c:a', 'aac', '-b:a', '192k', '-t', f'{plan["frames"] / 30:.10f}',
                '-movflags', '+faststart', str(output)]
    freeze_sha = sha(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True)
    check_video(output, plan['frames'])
    pts = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                            '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(output)]))['frames']
    require(len(pts) == plan['frames'], 'Decoded PTS count mismatch')
    require(all(abs(float(item['best_effort_timestamp_time']) - index / 30) < 2e-6 for index, item in enumerate(pts)), 'Output PTS are not continuous 30fps')
    for name, expected in plan['inputSHA256'].items():
        require(sha(resolved(name, episode)) == expected, f'Input changed during encoding: {name}')
    require(sha(manifest_path) == freeze_sha, 'Current freeze changed during encoding')
    for name, expected in manifest.items():
        require(sha(resolved(name, episode)) == expected, f'Frozen input changed during encoding: {name}')
    result = dict(status='passed', frames=plan['frames'], fps=30, lastPTS=(plan['frames'] - 1) / 30,
                  output=relative(output, episode), sha256=sha(output), planSha256=sha(plan_path), sourceFreezeSha256=freeze_sha,
                  command=command, segments=plan['segments'],
                  checks='Frozen current/old inputs, semantic/local-time/take constraints, explicit visual approval, clip identities/formats/counts, output count and continuous PTS passed.',
                  audio='Only the new shared-build voice.wav is mapped. This is a voice-only intermediate; run the shared BGM mixer next.')
    save(result_path, result)
    print(json.dumps({key: result[key] for key in ['status', 'frames', 'lastPTS', 'output', 'sha256']}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episode', type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan-only', action='store_true')
    mode.add_argument('--run', action='store_true')
    parser.add_argument('--render-shots', default='', help='Comma-separated NEW IDs or unique slugs which must be freshly rendered')
    parser.add_argument('--changes', type=Path, help='Optional JSON: renderShots, reuseMap, clipPaths, renderCard')
    parser.add_argument('--render-card', action='store_true')
    parser.add_argument('--allow-tail-frame-adjustment', action='store_true', help='Permit at most one final hold frame; independent review must approve each actual delta')
    parser.add_argument('--before', type=Path)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--baseline-record', type=Path)
    parser.add_argument('--review', type=Path)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--overwrite-output', action='store_true')
    args = parser.parse_args()
    try:
        if args.run:
            run_plan(args)
        else:
            plan = make_plan(args)
            path = (args.plan or args.episode.resolve() / 'approach-remix-plan.json').resolve()
            require(path not in [resolved(name, args.episode.resolve()) for name in plan['inputSHA256']], 'Plan path aliases an input')
            require(path != args.episode.resolve() / 'source-sha256.json', 'Plan must not overwrite the source freeze')
            protected = {resolved(name, args.episode.resolve()) for name in read(args.episode.resolve() / 'source-sha256.json')}
            if path in protected:
                previous = read(path)
                require(isinstance(previous, dict) and previous.get('schemaVersion') == VERSION and previous.get('method') == plan['method'], 'Plan must not overwrite a different frozen input')
            save(path, plan)
            print(json.dumps(dict(plan=str(path), frames=plan['frames'], clips=[{key: clip[key] for key in ['key', 'frameRange', 'path', 'sha256', 'shellCommand']} for clip in plan['clips']],
                                  reusedSlugs=plan['reviewTemplate']['approvedReuseSlugs'], reviewTemplate=plan['reviewTemplate'],
                                  freezeRequirements=plan['freezeRequirements']), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError, wave.Error) as error:
        parser.exit(1, f'remix_approach: {error}\n')


if __name__ == '__main__':
    main()
