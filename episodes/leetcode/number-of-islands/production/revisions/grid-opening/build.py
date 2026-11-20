"""Build a scoped visual splice against the pinned LC.200 release."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PRODUCTION = HERE.parent.parent
REMOTION = PRODUCTION / "remotion"
EPISODE = PRODUCTION.parent
ROOT = EPISODE.parents[2]
SHARED = EPISODE.parents[1] / "_shared"
sys.path.insert(0, str(SHARED))
from append_references import (  # noqa: E402
    audio_hash, audio_packets, dump, frame_rows, probe, sha, stream, verify_media,
)

BASE = "821edd3b803fbee61f6537f785f71510b55146d9"
BASE_SHA = "9f7189bd8ae1986c696b1638633689e0ea931e9b6a57e9d010e1bf5c7f49b9c3"
OPENING, CUT, BODY, END, FPS = 395, 500, 5845, 5995, 30


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def command(*args, **kwargs):
    subprocess.run(args, check=True, **kwargs)


def ff(*args):
    command("ffmpeg", "-nostdin", "-v", "error", "-y", *args)


def stream_copy(parts, destination, baseline):
    listing = destination.with_suffix(".ffconcat")
    listing.write_text("ffconcat version 1.0\n" + "".join(
        f"file {path.name}\nduration {frames / FPS:.9f}\n" for path, frames in parts
    ))
    ff("-f", "concat", "-safe", "1", "-i", listing, "-i", baseline,
       "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", "-map_metadata", "1",
       "-video_track_timescale", "90000", "-movflags", "+faststart", destination)


def frozen_inputs():
    src = REMOTION / "src"
    style = SHARED / "leetcode-video"
    paths = [
        HERE / "build.py", REMOTION / "package-lock.json", REMOTION / "remotion.config.ts",
        PRODUCTION / "storyboard.json", PRODUCTION / "covers.json",
        src / "grid-opening.tsx", src / "data.ts", src / "lesson.json",
        src / "leetcode-style/IslandMap.tsx", src / "leetcode-style/theme.ts",
        style / "Frame.tsx", style / "theme.ts", style / "style-v1.json",
        style / "identities-v1.json", SHARED / "append_references.py",
        EPISODE / "publication/references.json",
    ]
    fonts = {}
    for query in ("Noto Sans CJK SC", "Noto Sans CJK SC:style=Bold", "Noto Sans Mono",
                  "Noto Sans Mono:style=Bold", "DejaVu Sans", "DejaVu Sans:style=Bold"):
        path = Path(subprocess.check_output(["fc-match", "-f", "%{file}", query], text=True))
        fonts[query] = {"file": path.name, "sha256": sha(path)}
    return {
        "baselineCommit": BASE, "baselineVideoSHA256": BASE_SHA,
        "files": {str(path.relative_to(ROOT)): sha(path) for path in paths},
        "fonts": fonts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--freeze", action="store_true")
    mode.add_argument("--browser", help="Chrome for Testing executable (render and assemble)")
    args = parser.parse_args()
    manifest = HERE / "source-sha256.json"
    inputs = frozen_inputs()
    if args.freeze:
        require(not manifest.exists(), "Freeze exists; use a new revision for input changes")
        dump(manifest, inputs)
        return
    require(inputs == json.loads(manifest.read_text()), "Frozen input SHA or font changed")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    baseline = out / "baseline.mp4"
    relative = (EPISODE / "publication/video.mp4").relative_to(ROOT)
    with baseline.open("wb") as dest:
        command("git", "-C", ROOT, "show", f"{BASE}:{relative}", stdout=dest)
    require(sha(baseline) == BASE_SHA, "Wrong baseline video")

    opening = out / "opening.mp4"
    render_log = out / "remotion.log"
    with render_log.open("w") as log:
        try:
            command(REMOTION / "node_modules/.bin/remotion", "render", "src/grid-opening.tsx",
                    "GridOpening", opening, f"--browser-executable={args.browser}",
                    "--chrome-mode=chrome-for-testing", "--codec=h264", "--crf=12",
                    "--concurrency=4", "--muted", "--log=warn", cwd=REMOTION,
                    stdout=log, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print(render_log.read_text()[-6000:], file=sys.stderr)
            raise
    require(int(stream(probe(opening), "video")["nb_frames"]) == OPENING, "Opening timing changed")

    # The old opening's GOP crosses the editorial cut. Recompress only the old
    # pictures up to the next IDR; all later pictures, including the appendix, copy through.
    ff("-i", baseline, "-map", "0:v:0", "-an", "-c:v", "copy", "-f", "segment",
       "-segment_times", f"{CUT / FPS:.8f},{BODY / FPS:.8f}", "-segment_time_delta", "0.00005",
       "-segment_format_options", "video_track_timescale=90000", "-reset_timestamps", "1",
       out / "baseline-%d.mp4")
    for i, count in enumerate((CUT, BODY - CUT, END - BODY)):
        require(int(stream(probe(out / f"baseline-{i}.mp4"), "video")["nb_frames"]) == count,
                f"Baseline segment {i} does not split at the expected IDR")
    first = out / "first.mp4"
    filters = (
        "[0:v]scale=out_range=pc,format=yuvj420p,setsar=1,settb=1/30,setpts=N[new];"
        f"[1:v]trim=start_frame={OPENING}:end_frame={CUT},format=yuvj420p,"
        "setsar=1,settb=1/30,setpts=N[bridge];[new][bridge]concat=n=2:v=1:a=0[v]"
    )
    ff("-threads", "2", "-i", opening, "-threads", "2", "-i", baseline,
       "-filter_complex_threads", "1", "-filter_complex", filters, "-map", "[v]", "-an",
       "-c:v", "libx264", "-threads", "4", "-preset", "medium", "-crf", "12",
       "-profile:v", "high", "-level:v", "4.0", "-pix_fmt", "yuvj420p",
       "-color_range", "pc", "-colorspace", "bt470bg", "-r", str(FPS),
       "-video_track_timescale", "90000", first)
    body = out / "body.mp4"
    final = out / "video.mp4"
    parts = [(first, CUT), (out / "baseline-1.mp4", BODY - CUT)]
    stream_copy(parts, body, baseline)
    stream_copy([*parts, (out / "baseline-2.mp4", END - BODY)], final, baseline)

    media_file = out / "reference-appendix-media-check.json"
    media = verify_media(body, final, END - BODY, 1, END - BODY, media_file)
    old_frames, new_frames = frame_rows(baseline), frame_rows(final)
    require(old_frames[CUT:] == new_frames[CUT:], "Post-IDR decoded frame or timestamp changed")
    require(audio_packets(baseline) == audio_packets(final)
            and audio_hash(baseline) == audio_hash(final), "Original AAC/PCM changed")
    require(all(a[1:4] == b[1:4] for a, b in zip(old_frames, new_frames)),
            "Source video timestamps changed")
    stats = out / "bridge-psnr.log"
    ff("-threads", "2", "-i", baseline, "-threads", "2", "-i", final,
       "-filter_complex_threads", "1", "-filter_complex",
       f"[0:v]trim=start_frame={OPENING}:end_frame={CUT},setpts=PTS-STARTPTS[a];"
       f"[1:v]trim=start_frame={OPENING}:end_frame={CUT},setpts=PTS-STARTPTS[b];"
       f"[a][b]psnr=stats_file={stats}", "-an", "-f", "null", "-")
    psnr = [float(next(item.split(":")[1] for item in row.split()
                       if item.startswith("psnr_avg:"))) for row in stats.read_text().splitlines()]
    require(len(psnr) == CUT - OPENING and min(psnr) >= 42, "Same-shot bridge exceeds visual error limit")
    require(inputs == frozen_inputs(), "Production inputs changed during render")
    print(f"{media['finalFrames']} frames; exact original AAC/PCM and frames {CUT}–{END-1}; "
          f"unchanged bridge min PSNR {min(psnr):.2f} dB")
    dump(out / "splice-verification.json", {
        "baselineVideoSHA256": BASE_SHA, "openingRenderedFrames": [0, OPENING - 1],
        "bridgeReencodedFrames": [OPENING, CUT - 1], "bridgeMinimumPSNRdB": round(min(psnr), 2),
        "exactOriginalDecodedFrames": [CUT, END - 1], "originalTimestampsPreserved": True,
        "originalAACAndPCMPreserved": True, "outputSHA256": media["outputSHA256"],
    })
    ff("-i", final, "-t", "18", "-map", "0:v:0", "-map", "0:a:0", "-c", "copy",
       "-movflags", "+faststart", out / "number-of-islands-opening-preview.mp4")


if __name__ == "__main__":
    main()
