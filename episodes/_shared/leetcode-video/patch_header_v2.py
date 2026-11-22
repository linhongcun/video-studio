#!/usr/bin/env python3
"""Scoped header-title-v2 revision builder for existing LeetCode episodes.

Replaces only the persistent "算法可视化" header label (x=486..1219, y=44..99)
on regular body frames [0, codeCardFrom) with the frozen FrameV2.tsx problem-title
patch PNG, preserves native color space, stream-copies the complete reference
appendix and original AAC audio bit-for-bit, verifies every frame/audio/PSNR/seam
invariant, and re-extracts video-keyframe article JPGs at their exact original frames.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SHARED = HERE.parent
ROOT = SHARED.parent.parent
sys.path.insert(0, str(SHARED))

from append_references import (  # noqa: E402
    audio_hash,
    audio_packets,
    dump,
    frame_rows,
    probe,
    sha,
    stream,
    verify_media,
)

FPS = 30
PATCH_X, PATCH_Y, PATCH_W, PATCH_H = 486, 44, 734, 56
DEFAULT_REVISION = "header-title-v2"
DEFAULT_BASELINE = "6b1518876a5eab2b0460319c072fa05d0884fdb8"
BJ_TZ = timezone(timedelta(hours=8))

FONT_FILES = (
    "DejaVuSans.ttf",
    "DejaVuSans-Bold.ttf",
    "NotoSansCJK-Regular.ttc",
    "NotoSansCJK-Bold.ttc",
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def run_cmd(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def ff(*args) -> None:
    run_cmd("ffmpeg", "-nostdin", "-v", "error", "-y", *args)


def git_show_bytes(commit: str, rel_path: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{commit}:{rel_path}"])


def git_show_to_file(commit: str, rel_path: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as handle:
        run_cmd("git", "-C", str(ROOT), "show", f"{commit}:{rel_path}", stdout=handle)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def font_fingerprints() -> dict[str, dict[str, str]]:
    fonts_dir = Path.home() / "Library/Fonts"
    out = {}
    for name in FONT_FILES:
        p = fonts_dir / name
        require(p.is_file(), f"Missing required font file: {p}")
        out[name] = {"file": str(p), "sha256": sha(p)}
    return out


def load_episodes(slugs_arg: str | None) -> list[dict]:
    catalog = json.loads((SHARED / "leetcode-covers/catalog.json").read_text(encoding="utf-8"))
    wanted = {s.strip() for s in slugs_arg.split(",") if s.strip()} if slugs_arg else None
    result = []
    for ep in catalog["episodes"]:
        slug = ep["slug"]
        if wanted and slug not in wanted:
            continue
        result.append({
            "slug": slug,
            "number": ep["number"],
            "title": "".join(ep["title"]),
            "method": ep["method"],
        })
    require(bool(result), "No matching LeetCode episodes selected")
    return result


def episode_paths(slug: str, revision: str) -> dict[str, Path]:
    ep_dir = ROOT / "episodes/leetcode" / slug
    prod = ep_dir / "production"
    pub = ep_dir / "publication"
    rev = prod / "revisions" / revision
    return {"ep": ep_dir, "prod": prod, "pub": pub, "rev": rev}


def compute_frozen_inputs(ep: dict, baseline_commit: str, revision: str) -> dict:
    slug = ep["slug"]
    p = episode_paths(slug, revision)
    rel_pub = f"episodes/leetcode/{slug}/publication"
    base_meta = json.loads(git_show_bytes(baseline_commit, f"{rel_pub}/meta.json").decode("utf-8"))
    base_sb = json.loads(git_show_bytes(baseline_commit, f"{rel_pub}/storyboard.json").decode("utf-8"))
    base_video_bytes = git_show_bytes(baseline_commit, f"{rel_pub}/{base_meta['video']}")

    body_frames = int(base_meta["referenceAppendix"]["from"])
    appendix_frames = int(base_meta["referenceAppendix"]["durationInFrames"])
    final_frames = int(base_meta["finalVideoFrames"])
    code_card_from = int(base_sb["meta"]["unvoicedEndCard"]["from"])
    require(body_frames + appendix_frames == final_frames, f"{slug}: inconsistent appendix frames")
    require(0 < code_card_from < body_frames, f"{slug}: invalid codeCardFrom={code_card_from}")

    files = [
        HERE / "FrameV2.tsx",
        HERE / "header-v2.ts",
        HERE / "style-v2.json",
        HERE / "render-header-v2-patches.mjs",
        HERE / "patch_header_v2.py",
        SHARED / "append_references.py",
        p["rev"] / "patch.png",
        p["rev"] / "header-dom-audit.json",
        p["pub"] / "references.json",
        p["pub"] / "storyboard.json",
    ]
    for f in files:
        require(f.is_file(), f"{slug}: missing frozen input {f}")

    return {
        "schemaVersion": 1,
        "slug": slug,
        "revision": revision,
        "baselineCommit": baseline_commit,
        "baselineSourcePath": base_meta["sourcePath"],
        "baselineVideoSHA256": sha_bytes(base_video_bytes),
        "identity": {"number": ep["number"], "title": ep["title"], "method": ep["method"]},
        "patchRect": {"x": PATCH_X, "y": PATCH_Y, "width": PATCH_W, "height": PATCH_H},
        "frameRanges": {
            "patchedBody": [0, code_card_from - 1],
            "codeCard": [code_card_from, body_frames - 1],
            "referenceAppendix": [body_frames, final_frames - 1],
            "bodyFrames": body_frames,
            "appendixFrames": appendix_frames,
            "finalFrames": final_frames,
        },
        "files": {str(f.relative_to(ROOT)): sha(f) for f in files},
        "fonts": font_fingerprints(),
    }


def stream_copy_concat(parts: list[tuple[Path, int]], destination: Path, audio_source: Path) -> None:
    listing = destination.with_suffix(".ffconcat")
    listing.write_text(
        "ffconcat version 1.0\n"
        + "".join(f"file {path.name}\nduration {frames / FPS:.9f}\n" for path, frames in parts),
        encoding="utf-8",
    )
    ff(
        "-f", "concat", "-safe", "1", "-i", str(listing),
        "-i", str(audio_source),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c", "copy", "-map_metadata", "1",
        "-video_track_timescale", "90000",
        "-movflags", "+faststart",
        str(destination),
    )


def extract_frame_rgb(video_path: Path, frame_idx: int, out_png: Path) -> np.ndarray:
    ff(
        "-i", str(video_path),
        "-vf", f"select=eq(n\\,{frame_idx})",
        "-vsync", "0", "-frames:v", "1",
        str(out_png),
    )
    return np.array(Image.open(out_png).convert("RGB"))


def extract_article_jpg(video_path: Path, frame_idx: int, is_bt709_tv: bool, dest_jpg: Path) -> None:
    tmp_png = dest_jpg.with_suffix(".tmp.png")
    vf = f"select=eq(n\\,{frame_idx})"
    if is_bt709_tv:
        vf += ",scale=in_color_matrix=bt709:out_color_matrix=bt601:out_range=pc"
    ff("-i", str(video_path), "-vf", vf, "-vsync", "0", "-frames:v", "1", str(tmp_png))
    Image.open(tmp_png).convert("RGB").save(dest_jpg, format="JPEG", quality=94, subsampling=0)
    tmp_png.unlink(missing_ok=True)


def match_article_figure_frame(baseline_video: Path, existing_jpg: Path, seek_to: float, is_bt709_tv: bool, work_dir: Path) -> tuple[int, float]:
    target = np.array(Image.open(existing_jpg).convert("RGB"), dtype=np.float32)
    center = round(seek_to * FPS)
    # Mask out header top bar when comparing, or compare full image (baseline matches baseline!)
    lo = max(0, center - 15)
    hi = center + 15
    vf = f"trim=start_frame={lo}:end_frame={hi + 1},setpts=PTS-STARTPTS"
    if is_bt709_tv:
        vf += ",scale=in_color_matrix=bt709:out_color_matrix=bt601:out_range=pc"
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(baseline_video), "-vf", vf,
         "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True,
    )
    fb = 1920 * 1080 * 3
    nf = len(proc.stdout) // fb
    best_frame, best_mae = center, 1e9
    # Subsample stride 4 for ultra-fast exact match
    t_sub = target[::4, ::4, :]
    for i in range(nf):
        arr = np.frombuffer(proc.stdout[i * fb:(i + 1) * fb], dtype=np.uint8).reshape(1080, 1920, 3)
        mae = float(np.abs(arr[::4, ::4, :].astype(np.float32) - t_sub).mean())
        if mae < best_mae:
            best_mae = mae
            best_frame = lo + i
    return best_frame, round(best_mae, 3)


def find_article_jpg_figures(pub_dir: Path, slug: str) -> list[tuple[str, float]]:
    article_mdx = (pub_dir / "article.mdx").read_text(encoding="utf-8")
    out = []
    for tag in re.findall(r"<Figure[\s\S]*?/>", article_mdx):
        ms = re.search(r'src="([^"]+)"', tag)
        mt = re.search(r"seekTo=\{([^}]+)\}", tag)
        if not ms or not mt:
            continue
        src = ms.group(1)
        if not src.endswith(".jpg"):
            continue
        name = Path(src).name
        if (pub_dir / "article" / name).is_file():
            out.append((name, float(mt.group(1))))
    return out


def build_exact_bg_yuv_patch(
    baseline_video: Path,
    patch_png: Path,
    sample_frame: int,
    is_bt709_tv: bool,
    out_yuv: Path,
) -> tuple[int, int, int]:
    """Convert patch.png to native YUV420 and pin background bytes to baseline's exact (Y,U,V)."""
    # 1. Sample exact native (Y, U, V) of empty header background at (x=900, y=70) from baseline
    raw_frame = subprocess.check_output([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(baseline_video),
        "-vf", f"select=eq(n\\,{sample_frame})", "-vsync", "0", "-frames:v", "1",
        "-f", "rawvideo", "-pix_fmt", "yuv420p", "-",
    ])
    y_sz = 1920 * 1080
    uv_sz = 960 * 540
    y_plane = np.frombuffer(raw_frame[:y_sz], dtype=np.uint8).reshape(1080, 1920)
    u_plane = np.frombuffer(raw_frame[y_sz:y_sz + uv_sz], dtype=np.uint8).reshape(540, 960)
    v_plane = np.frombuffer(raw_frame[y_sz + uv_sz:y_sz + 2 * uv_sz], dtype=np.uint8).reshape(540, 960)
    y_bg = int(np.median(y_plane[50:90, 880:1080]))
    u_bg = int(np.median(u_plane[25:45, 440:540]))
    v_bg = int(np.median(v_plane[25:45, 440:540]))

    # 2. Convert patch.png to the exact same color matrix/range YUV420
    scale_vf = (
        "format=rgb24,scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p"
        if is_bt709_tv
        else "format=rgb24,scale=in_range=pc:out_range=pc:out_color_matrix=bt470bg,format=yuvj420p"
    )
    raw_patch = subprocess.check_output([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(patch_png),
        "-vf", scale_vf, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-",
    ])
    py_sz = PATCH_W * PATCH_H
    puv_sz = (PATCH_W // 2) * (PATCH_H // 2)
    py = np.frombuffer(raw_patch[:py_sz], dtype=np.uint8).reshape(PATCH_H, PATCH_W).copy()
    pu = np.frombuffer(raw_patch[py_sz:py_sz + puv_sz], dtype=np.uint8).reshape(PATCH_H // 2, PATCH_W // 2).copy()
    pv = np.frombuffer(raw_patch[py_sz + puv_sz:py_sz + 2 * puv_sz], dtype=np.uint8).reshape(PATCH_H // 2, PATCH_W // 2).copy()

    # 3. Pin all pure-background pixels in patch to baseline's exact native (Y_bg, U_bg, V_bg)
    patch_rgb = np.array(Image.open(patch_png).convert("RGB"))
    bg_rgb = patch_rgb[0, 0]
    is_bg = (patch_rgb == bg_rgb).all(axis=2)
    py[is_bg] = y_bg
    is_bg_uv = (
        is_bg[0::2, 0::2] & is_bg[0::2, 1::2] & is_bg[1::2, 0::2] & is_bg[1::2, 1::2]
    )
    pu[is_bg_uv] = u_bg
    pv[is_bg_uv] = v_bg

    out_yuv.write_bytes(py.tobytes() + pu.tobytes() + pv.tobytes())
    return (y_bg, u_bg, v_bg)


def build_episode(ep: dict, baseline_commit: str, revision: str, work_root: Path, threads: int) -> dict:
    slug = ep["slug"]
    p = episode_paths(slug, revision)
    manifest_path = p["rev"] / "source-sha256.json"
    require(manifest_path.is_file(), f"{slug}: missing freeze manifest; run --freeze first")
    expected_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual_manifest = compute_frozen_inputs(ep, baseline_commit, revision)
    require(actual_manifest == expected_manifest, f"{slug}: frozen inputs changed since --freeze")

    work = work_root / slug
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)

    rel_pub = f"episodes/leetcode/{slug}/publication"
    baseline = work / "baseline.mp4"
    git_show_to_file(baseline_commit, f"{rel_pub}/video.mp4", baseline)
    require(sha(baseline) == expected_manifest["baselineVideoSHA256"], f"{slug}: baseline SHA mismatch")

    fr = expected_manifest["frameRanges"]
    code_from = fr["codeCard"][0]
    body_frames = fr["bodyFrames"]
    appendix_frames = fr["appendixFrames"]
    final_frames = fr["finalFrames"]

    b_info = probe(baseline)
    b_vs = stream(b_info, "video")
    pix_fmt = b_vs["pix_fmt"]
    color_range = b_vs.get("color_range", "pc" if "yuvj" in pix_fmt else "tv")
    color_space = b_vs.get("color_space", "bt470bg")
    is_bt709_tv = (color_space == "bt709" and color_range == "tv")
    require(
        is_bt709_tv or (pix_fmt == "yuvj420p" and color_range == "pc" and color_space == "bt470bg"),
        f"{slug}: unexpected color profile {pix_fmt}/{color_range}/{color_space}",
    )

    # 1. Exact stream-copy split at IDR boundary body_frames to preserve reference appendix bit-for-bit
    ff(
        "-i", str(baseline),
        "-map", "0:v:0", "-an", "-c:v", "copy",
        "-f", "segment",
        "-segment_times", f"{body_frames / FPS:.8f}",
        "-segment_time_delta", "0.00005",
        "-segment_format_options", "video_track_timescale=90000",
        "-reset_timestamps", "1",
        str(work / "baseline-%d.mp4"),
    )
    seg0, seg1 = work / "baseline-0.mp4", work / "baseline-1.mp4"
    require(int(stream(probe(seg0), "video")["nb_frames"]) == body_frames, f"{slug}: seg0 frame mismatch")
    require(int(stream(probe(seg1), "video")["nb_frames"]) == appendix_frames, f"{slug}: seg1 frame mismatch")

    # 2. Encode patched body [0 .. body_frames - 1] preserving exact color space & pixel format
    patch_png = p["rev"] / "patch.png"
    sample_body_frame = max(30, round(code_from * 0.25))
    patch_yuv = work / "patch.yuv"
    bg_yuv = build_exact_bg_yuv_patch(baseline, patch_png, sample_body_frame, is_bt709_tv, patch_yuv)
    body_video = work / "body-video.mp4"
    patch_pix_fmt = "yuv420p" if is_bt709_tv else "yuvj420p"
    setparams = (
        "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv"
        if is_bt709_tv
        else "setparams=colorspace=bt470bg:range=pc"
    )
    vf = (
        f"[0:v]trim=start_frame=0:end_frame={body_frames},setpts=PTS-STARTPTS[base];"
        f"[1:v]{setparams}[patch];"
        f"[base][patch]overlay=x={PATCH_X}:y={PATCH_Y}:format=yuv420:repeatlast=1:enable='lt(n,{code_from})',"
        f"format={patch_pix_fmt},setsar=1,settb=1/30,setpts=N[v]"
    )
    if is_bt709_tv:
        color_args = [
            "-pix_fmt", "yuv420p",
            "-color_range", "tv",
            "-colorspace", "bt709",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
        ]
    else:
        color_args = [
            "-pix_fmt", "yuvj420p",
            "-color_range", "pc",
            "-colorspace", "bt470bg",
        ]

    ff(
        "-threads", str(threads), "-i", str(baseline),
        "-f", "rawvideo", "-pix_fmt", patch_pix_fmt, "-video_size", f"{PATCH_W}x{PATCH_H}",
        "-framerate", str(FPS), "-i", str(patch_yuv),
        "-filter_complex_threads", "1",
        "-filter_complex", vf,
        "-map", "[v]", "-an",
        "-c:v", "libx264", "-threads", str(threads),
        "-preset", "medium", "-crf", "12",
        "-profile:v", "high", "-level:v", "4.0",
        *color_args,
        "-r", str(FPS),
        "-video_track_timescale", "90000",
        str(body_video),
    )
    require(int(stream(probe(body_video), "video")["nb_frames"]) == body_frames, f"{slug}: body_video count mismatch")

    # 3. Mux body.mp4 and final video.mp4 (stream-copying appendix & original AAC audio)
    body_mp4 = work / "body.mp4"
    final_mp4 = work / "video.mp4"
    stream_copy_concat([(body_video, body_frames)], body_mp4, baseline)
    stream_copy_concat([(body_video, body_frames), (seg1, appendix_frames)], final_mp4, baseline)

    # 4. Full verification suite
    media_check_path = work / "reference-appendix-media-check.json"
    media = verify_media(body_mp4, final_mp4, appendix_frames, 1, appendix_frames, media_check_path)

    old_rows = frame_rows(baseline)
    new_rows = frame_rows(final_mp4)
    require(len(old_rows) == final_frames and len(new_rows) == final_frames, f"{slug}: total frame count mismatch")
    require(old_rows[body_frames:] == new_rows[body_frames:], f"{slug}: reference appendix decoded frames changed")
    require(all(a[1:4] == b[1:4] for a, b in zip(old_rows, new_rows)), f"{slug}: video timestamps changed")
    require(
        audio_packets(baseline) == audio_packets(final_mp4) and audio_hash(baseline) == audio_hash(final_mp4),
        f"{slug}: original AAC packets or decoded PCM changed",
    )

    # 5. Masked PSNR on ALL body frames [0 .. body_frames) outside patch box
    psnr_log = work / "masked-psnr.log"
    mask_box = f"drawbox=x={PATCH_X}:y={PATCH_Y}:w={PATCH_W}:h={PATCH_H}:color=black:t=fill"
    ff(
        "-threads", str(threads), "-i", str(baseline),
        "-threads", str(threads), "-i", str(final_mp4),
        "-filter_complex_threads", "1",
        "-filter_complex",
        f"[0:v]trim=start_frame=0:end_frame={body_frames},{mask_box},setpts=PTS-STARTPTS[a];"
        f"[1:v]trim=start_frame=0:end_frame={body_frames},{mask_box},setpts=PTS-STARTPTS[b];"
        f"[a][b]psnr=stats_file={psnr_log}",
        "-an", "-f", "null", "-",
    )
    psnr_vals = []
    for row in psnr_log.read_text(encoding="utf-8").splitlines():
        val = next(item.split(":")[1] for item in row.split() if item.startswith("psnr_avg:"))
        psnr_vals.append(99.99 if val == "inf" else float(val))
    require(len(psnr_vals) == body_frames, f"{slug}: PSNR frame count mismatch")
    min_psnr = min(psnr_vals)
    min_codecard_psnr = min(psnr_vals[code_from:body_frames])
    require(min_psnr >= 42.0, f"{slug}: unchanged region min PSNR too low: {min_psnr:.2f} dB")
    require(min_codecard_psnr >= 42.0, f"{slug}: CodeCard min PSNR too low: {min_codecard_psnr:.2f} dB")

    # 6. Seam & visual spot checks on decoded final_mp4
    new_body_img = extract_frame_rgb(final_mp4, sample_body_frame, work / f"{slug}-final-body.png")
    old_body_img = extract_frame_rgb(baseline, sample_body_frame, work / f"{slug}-base-body.png")
    extract_frame_rgb(final_mp4, code_from + 20, work / f"{slug}-final-codecard.png")
    extract_frame_rgb(final_mp4, body_frames + 20, work / f"{slug}-final-refs.png")

    # Verify zero visible rectangle seam around patch borders
    border_pairs = [
        (new_body_img[PATCH_Y - 1, PATCH_X:PATCH_X + PATCH_W], new_body_img[PATCH_Y, PATCH_X:PATCH_X + PATCH_W]),
        (new_body_img[PATCH_Y + PATCH_H - 1, PATCH_X:PATCH_X + PATCH_W], new_body_img[PATCH_Y + PATCH_H, PATCH_X:PATCH_X + PATCH_W]),
        (new_body_img[PATCH_Y:PATCH_Y + PATCH_H, PATCH_X - 1], new_body_img[PATCH_Y:PATCH_Y + PATCH_H, PATCH_X]),
        (new_body_img[PATCH_Y:PATCH_Y + PATCH_H, PATCH_X + PATCH_W - 1], new_body_img[PATCH_Y:PATCH_Y + PATCH_H, PATCH_X + PATCH_W]),
    ]
    seam_means = [round(float(np.abs(a.astype(int) - b.astype(int)).mean()), 4) for a, b in border_pairs]
    median_bg_diff = int(
        np.abs(
            np.median(new_body_img[PATCH_Y - 1, PATCH_X:PATCH_X + PATCH_W], axis=0)
            - np.median(new_body_img[PATCH_Y, PATCH_X:PATCH_X + PATCH_W], axis=0)
        ).max()
    )
    max_seam_mean = max(seam_means)
    require(median_bg_diff == 0, f"{slug}: patch background RGB mismatch vs header (median diff={median_bg_diff})")
    require(max_seam_mean <= 0.6, f"{slug}: visible patch border seam detected (mean RGB diffs={seam_means})")

    # Verify patch area actually changed vs baseline ("算法可视化" replaced with problem title)
    patch_roi_old = old_body_img[PATCH_Y:PATCH_Y + PATCH_H, PATCH_X:PATCH_X + PATCH_W]
    patch_roi_new = new_body_img[PATCH_Y:PATCH_Y + PATCH_H, PATCH_X:PATCH_X + PATCH_W]
    changed_pixels = int((np.abs(patch_roi_old.astype(int) - patch_roi_new.astype(int)).max(axis=2) > 25).sum())
    require(changed_pixels >= 250, f"{slug}: header patch did not visibly change ({changed_pixels} px)")

    # 7. Re-extract any video-keyframe article JPGs at exact original baseline frames
    article_updates = []
    for jpg_name, seek_to in find_article_jpg_figures(p["pub"], slug):
        orig_jpg_path = work / f"baseline-article-{jpg_name}"
        git_show_to_file(baseline_commit, f"{rel_pub}/article/{jpg_name}", orig_jpg_path)
        matched_frame, match_mae = match_article_figure_frame(baseline, orig_jpg_path, seek_to, is_bt709_tv, work)
        new_jpg_path = work / "article" / jpg_name
        new_jpg_path.parent.mkdir(parents=True, exist_ok=True)
        extract_article_jpg(final_mp4, matched_frame, is_bt709_tv, new_jpg_path)
        article_updates.append({
            "file": f"article/{jpg_name}",
            "seekTo": seek_to,
            "matchedFrame": matched_frame,
            "baselineMatchMAE": match_mae,
            "baselineSHA256": sha(orig_jpg_path),
            "newSHA256": sha(new_jpg_path),
        })

    # Re-verify frozen inputs didn't drift during build
    require(compute_frozen_inputs(ep, baseline_commit, revision) == expected_manifest, f"{slug}: inputs changed during build")

    out_vs = stream(probe(final_mp4), "video")
    report = {
        "schemaVersion": 1,
        "passed": True,
        "slug": slug,
        "identity": expected_manifest["identity"],
        "revision": revision,
        "baselineCommit": baseline_commit,
        "baselineVideoSHA256": expected_manifest["baselineVideoSHA256"],
        "bodySHA256": sha(body_mp4),
        "outputSHA256": media["outputSHA256"],
        "outputBytes": final_mp4.stat().st_size,
        "videoProfile": {
            "pix_fmt": out_vs["pix_fmt"],
            "color_range": out_vs.get("color_range"),
            "color_space": out_vs.get("color_space"),
            "color_primaries": out_vs.get("color_primaries"),
            "color_transfer": out_vs.get("color_transfer"),
        },
        "frameRanges": fr,
        "unchangedRegionMinPSNRdB": round(min_psnr, 2),
        "codeCardMinPSNRdB": round(min_codecard_psnr, 2),
        "patchBorderMedianRGBDiff": median_bg_diff,
        "patchBorderMeanRGBDiffs": seam_means,
        "patchBorderMaxMeanRGBDiff": max_seam_mean,
        "matchedBackgroundYUV": list(bg_yuv),
        "patchChangedPixels": changed_pixels,
        "appendixExactDecodedFramesPreserved": True,
        "originalTimestampsPreserved": True,
        "originalAACAndPCMPreserved": True,
        "articleUpdates": article_updates,
        "sampleFrame": sample_body_frame,
    }
    dump(work / "verification.json", report)
    return report


def install_episode(ep: dict, revision: str, work_root: Path, updated_at: str) -> dict:
    slug = ep["slug"]
    p = episode_paths(slug, revision)
    work = work_root / slug
    ver_path = work / "verification.json"
    require(ver_path.is_file(), f"{slug}: missing build verification; run --build first")
    ver = json.loads(ver_path.read_text(encoding="utf-8"))
    require(ver.get("passed") is True, f"{slug}: build verification did not pass")

    final_mp4 = work / "video.mp4"
    media_check = work / "reference-appendix-media-check.json"
    require(sha(final_mp4) == ver["outputSHA256"], f"{slug}: staged video.mp4 SHA mismatch")

    # Install video.mp4 and reference-appendix-media-check.json
    shutil.copy2(final_mp4, p["pub"] / "video.mp4")
    shutil.copy2(media_check, p["pub"] / "reference-appendix-media-check.json")

    # Update publication/reference-appendix.json preserving all verified bibliography fields
    ref_app_path = p["pub"] / "reference-appendix.json"
    ref_app = json.loads(ref_app_path.read_text(encoding="utf-8"))
    ref_app["inputs"]["bodySHA256"] = ver["bodySHA256"]
    ref_app["outputSHA256"] = ver["outputSHA256"]
    ref_app["body"] = f"episodes/leetcode/{slug}/production/revisions/{revision}/body.mp4"
    ref_app["output"] = f"episodes/leetcode/{slug}/publication/video.mp4"
    ref_app["bodyProductionInputs"] = (
        f"Body header label was updated via frozen revision {revision} (FrameV2.tsx problem title "
        f"'{ep['title']}' replacing '算法可视化' on frames 0..{ver['frameRanges']['patchedBody'][1]}); "
        "original narration, AAC/PCM, timing, full Python code card, reference appendix frames and "
        "historical freezes retain their original identities."
    )
    dump(ref_app_path, ref_app)

    # Install re-extracted article JPGs
    for art in ver["articleUpdates"]:
        src_jpg = work / art["file"]
        dst_jpg = p["pub"] / art["file"]
        require(src_jpg.is_file() and sha(src_jpg) == art["newSHA256"], f"{slug}: staged {art['file']} mismatch")
        shutil.copy2(src_jpg, dst_jpg)

    # Update publication/meta.json (keep createdAt, publishedAt, ep, problemNumber, etc.)
    meta_path = p["pub"] / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["updatedAt"] = updated_at
    meta["sourcePath"] = f"episodes/leetcode/{slug}/production/revisions/{revision}"
    dump(meta_path, meta)

    # Write clean revision receipts into production/revisions/<revision>/
    dump(p["rev"] / "verification.json", ver)
    dump(p["rev"] / "render-result.json", {
        "schemaVersion": 1,
        "slug": slug,
        "revision": revision,
        "installedAt": updated_at,
        "baselineCommit": ver["baselineCommit"],
        "baselineVideoSHA256": ver["baselineVideoSHA256"],
        "bodySHA256": ver["bodySHA256"],
        "outputSHA256": ver["outputSHA256"],
        "outputBytes": ver["outputBytes"],
        "articleUpdates": ver["articleUpdates"],
    })
    (p["rev"] / "README.md").write_text(
        f"# LC.{ep['number']}《{ep['title']}》顶部栏视觉修订（`{revision}`）\n\n"
        f"按 [#527](https://github.com/linhongcun/video-studio/issues/527) 批量视觉修订："
        f"仅将正片帧 `0..{ver['frameRanges']['patchedBody'][1]}` 顶部栏 `LC.{ep['number']}` 右侧的「算法可视化」"
        f"替换为基于 `episodes/_shared/leetcode-video/FrameV2.tsx` 真实渲染的算法题名称「{ep['title']}」。\n\n"
        f"- **基线提交**：`{ver['baselineCommit']}`（基线成片 SHA-256：`{ver['baselineVideoSHA256']}`）\n"
        f"- **新版成片 SHA-256**：`{ver['outputSHA256']}`（`{ver['outputBytes']:,}` 字节）\n"
        f"- **完整保真核验**：全部 {ver['frameRanges']['appendixFrames']} 帧参考资料解码帧逐帧一致、全部 AAC 音频包/时序与解码 PCM 逐字节一致、"
        f"全片时间轴一致、补丁外未改区域最低 PSNR `{ver['unchangedRegionMinPSNRdB']} dB`（代码卡 `{ver['codeCardMinPSNRdB']} dB`）、"
        f"补丁接缝中位 RGB 差 `{ver['patchBorderMedianRGBDiff']}`（四边均值最大 `{ver['patchBorderMaxMeanRGBDiff']}`）。\n"
        f"- **历史冻结保护**：既有源码、旧冻结清单及 v1 共享文件保持原字节不变。\n",
        encoding="utf-8",
    )
    return ver


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slugs", help="Comma-separated subset of LeetCode slugs")
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument("--baseline-commit", default=DEFAULT_BASELINE)
    parser.add_argument("--work-dir", type=Path, default=Path("/tmp/leetcode-header-v2-build"))
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--threads", type=int, default=3)
    parser.add_argument("--updated-at", help="ISO 8601 Beijing timestamp for meta.json updatedAt")
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--force-freeze", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()

    episodes = load_episodes(args.slugs)
    updated_at = args.updated_at or datetime.now(BJ_TZ).replace(microsecond=0).isoformat()

    if args.freeze:
        for ep in episodes:
            p = episode_paths(ep["slug"], args.revision)
            manifest = p["rev"] / "source-sha256.json"
            if manifest.exists() and not args.force_freeze:
                raise RuntimeError(f"{ep['slug']}: {manifest} already exists (use --force-freeze only before render)")
            inputs = compute_frozen_inputs(ep, args.baseline_commit, args.revision)
            dump(manifest, inputs)
            print(f"[FROZEN] LC.{ep['number']:<3d} {ep['slug']:<24s} base={inputs['baselineVideoSHA256'][:12]} range=0..{inputs['frameRanges']['patchedBody'][1]}")

    if args.build:
        reports = []
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            futs = {
                pool.submit(build_episode, ep, args.baseline_commit, args.revision, args.work_dir, args.threads): ep
                for ep in episodes
            }
            for fut in as_completed(futs):
                ep = futs[fut]
                rep = fut.result()
                reports.append(rep)
                print(
                    f"[BUILT]  LC.{ep['number']:<3d} {ep['slug']:<24s} "
                    f"psnr={rep['unchangedRegionMinPSNRdB']:.2f}dB code={rep['codeCardMinPSNRdB']:.2f}dB "
                    f"seam={rep['patchBorderMedianRGBDiff']}/{rep['patchBorderMaxMeanRGBDiff']:.3f} arts={len(rep['articleUpdates'])} "
                    f"sha={rep['outputSHA256'][:12]}"
                )
        reports.sort(key=lambda r: r["identity"]["number"])
        dump(args.work_dir / "batch-build-summary.json", {
            "passed": True,
            "count": len(reports),
            "baselineCommit": args.baseline_commit,
            "revision": args.revision,
            "episodes": reports,
        })

    if args.install:
        installed = []
        for ep in episodes:
            rep = install_episode(ep, args.revision, args.work_dir, updated_at)
            installed.append(rep)
            print(f"[INSTALLED] LC.{ep['number']:<3d} {ep['slug']:<24s} sha={rep['outputSHA256'][:12]} arts={len(rep['articleUpdates'])}")
        print(f"Installed {len(installed)} episodes cleanly (updatedAt={updated_at}).")


if __name__ == "__main__":
    main()
