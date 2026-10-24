#!/usr/bin/env python3
"""Audit this revision's local splice; never alter the encoded input media."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

EPISODE = Path(__file__).resolve().parent
BASE_SHA256 = "f9cdfa3b10e0d26baa57ad64a71b34e31860a0304ad6b619a92f346bf3e8ec15"
AVCC_SHA256 = "42f49f4a3b3674b9d3ff7f48ce3665a33b56fcba28e1ff74bff7154e6a3cc29d"
BASE_PCM_SHA256 = "e97780ba8cc1641d2731410056aa86f42c8aa6f120615783fc460d8a91221dd1"
TOTAL_FRAMES, CUT_FRAME, TICKS = 2864, 237, 3000
CUT_PTS, TAIL_FRAMES, AUDIO_PACKETS = CUT_FRAME * TICKS, 2627, 4476
VIDEO_FIELDS = ("codec_name", "profile", "codec_tag_string", "width", "height",
                "pix_fmt", "level", "color_range", "color_space", "chroma_location",
                "sample_aspect_ratio", "r_frame_rate", "avg_frame_rate", "time_base",
                "has_b_frames", "nal_length_size", "extradata_size")
PACKET_FIELDS = ("pts", "dts", "duration", "size", "flags", "data_hash")


class SpliceError(RuntimeError):
    pass


def need(condition, message):
    if not condition:
        raise SpliceError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command(args, strict_stderr=True):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    need(result.returncode == 0, f"Command failed ({result.returncode}): {args}\n{result.stderr[-6000:]}")
    if strict_stderr:
        need(not result.stderr.strip(), f"Command emitted diagnostics: {args}\n{result.stderr[-6000:]}")
    return result.stdout


def probe(path):
    return json.loads(command(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                               "-show_data", "-of", "json", path]))


def stream(data, kind):
    matches = [s for s in data["streams"] if s["codec_type"] == kind]
    need(len(matches) == 1, f"Expected one {kind} stream, found {len(matches)}")
    return matches[0]


def unhex(dump):
    chunks = []
    for line in dump.splitlines():
        if ":" in line:
            # ffprobe uses a two-space delimiter before the printable ASCII.
            chunks.append(bytes.fromhex(line.split(":", 1)[1].strip().split("  ", 1)[0]))
    return b"".join(chunks)


def avcc(video):
    value = unhex(video["extradata"])
    need(len(value) == int(video["extradata_size"]), "Malformed AVC extradata dump")
    return value


def packets(path, selector):
    return json.loads(command([
        "ffprobe", "-v", "error", "-select_streams", selector, "-show_packets",
        "-show_data_hash", "sha256", "-show_entries",
        "packet=pts,dts,duration,size,flags,data_hash,side_data_list", "-of", "json", path
    ]))["packets"]


def packet_view(packet, shift=0, audio=False):
    view = {k: packet.get(k) for k in PACKET_FIELDS}
    for key in ("pts", "dts"):
        if view[key] is not None:
            view[key] -= shift
    if audio:
        view["skip_samples"] = [
            {key: item.get(key) for key in
             ("skip_samples", "discard_padding", "skip_reason", "discard_reason")}
            for item in packet.get("side_data_list", [])
            if item.get("side_data_type") == "Skip Samples"
        ]
    return view


def frames(path):
    return json.loads(command([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=pts,best_effort_timestamp,key_frame,pict_type",
        "-of", "json", path
    ]))["frames"]


def require_timeline(video_packets, count, label):
    need(len(video_packets) == count, f"{label}: expected {count} packets")
    need(sorted(p["pts"] for p in video_packets) == list(range(0, count * TICKS, TICKS)),
         f"{label}: presentation timestamps contain gaps, overlaps or shifts")
    need([p["dts"] for p in video_packets] == list(range(-2 * TICKS, (count - 2) * TICKS, TICKS)),
         f"{label}: decode timestamps do not preserve the two-frame delay")
    need(all(p["duration"] == TICKS for p in video_packets), f"{label}: unexpected packet duration")


def idr_at(path, pts):
    data = json.loads(command([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-read_intervals",
        f"{pts / 90000:.9f}%+#1", "-show_packets", "-show_entries",
        "packet=pts,dts,flags,data", "-show_data", "-of", "json", path
    ]))["packets"]
    need(len(data) == 1 and data[0]["pts"] == pts, f"No exact boundary packet at PTS {pts}")
    packet = data[0]
    need("K" in packet["flags"], "Boundary packet is not marked as a keyframe")
    raw, offset, kinds = unhex(packet["data"]), 0, []
    while offset < len(raw):
        need(offset + 4 <= len(raw), "Truncated H.264 NAL length")
        length = int.from_bytes(raw[offset:offset + 4], "big")
        offset += 4
        need(length > 0 and offset + length <= len(raw), "Invalid H.264 NAL length")
        kinds.append(raw[offset] & 31)
        offset += length
    need(5 in kinds, f"Boundary is not an IDR (NAL types {kinds})")
    return {"pts": pts, "dts": packet["dts"], "nalTypes": kinds}


def same_video_config(base_video, other_video, label):
    differences = {key: [base_video.get(key), other_video.get(key)]
                   for key in VIDEO_FIELDS if base_video.get(key) != other_video.get(key)}
    need(not differences, f"{label}: incompatible video stream configuration: {differences}")
    need(avcc(base_video) == avcc(other_video), f"{label}: AVC extradata differs; splice blocked")


def frozen_inputs(episode, base):
    manifest_path = episode / "source-sha256.json"
    need(manifest_path.is_file(), "Freeze source-sha256.json before composing this revision")
    manifest = json.loads(manifest_path.read_text())
    paths = {(episode / rel).resolve(): expected for rel, expected in manifest.items()}
    for required in (base, episode / "compose-revision.py", episode / "check-splice.py"):
        need(required.resolve() in paths, f"Required splice input is absent from freeze: {required}")
    for path, expected in paths.items():
        need(path.is_file() and sha(path) == expected, f"Frozen input changed: {path}")
    return {"sha256": sha(manifest_path), "inputCount": len(paths)}


def safe_report_path(path, episode, base, opening, output):
    protected = {p.resolve() for p in (base, opening, output, episode / "source-sha256.json",
                                      episode / "compose-revision.py", episode / "check-splice.py")}
    manifest = episode / "source-sha256.json"
    if manifest.is_file():
        protected.update((episode / rel).resolve() for rel in json.loads(manifest.read_text()))
    need(path.resolve() not in protected, "Report path conflicts with media or a frozen production input")


def preflight(base, opening):
    need(base.is_file() and opening.is_file(), "Base video and rendered opening must both exist")
    need(base.resolve() != opening.resolve(), "Opening cannot be the original whole video")
    need(sha(base) == BASE_SHA256, "Original V2 MP4 SHA differs; this splice plan is no longer applicable")
    base_probe, head_probe = probe(base), probe(opening)
    need(len(base_probe["streams"]) == 2, "Original V2 must have exactly two streams")
    need(len(head_probe["streams"]) == 1, "Opening must contain video only (--muted)")
    bv, hv = stream(base_probe, "video"), stream(head_probe, "video")
    need(bv["codec_name"] == "h264" and bv["nal_length_size"] == "4", "Expected AVC with four-byte NAL lengths")
    need(int(bv["nb_frames"]) == TOTAL_FRAMES and int(hv["nb_frames"]) == CUT_FRAME,
         "Base/opening frame count differs from the approved 2864/237-frame plan")
    need(hv["time_base"] == "1/90000" and int(hv["duration_ts"]) == CUT_PTS,
         "Opening must be exactly 7.9 seconds in time base 1/90000")
    same_video_config(bv, hv, "Opening")
    need(hashlib.sha256(avcc(bv)).hexdigest() == AVCC_SHA256, "Original AVC configuration changed")
    original_packets, head_packets = packets(base, "v:0"), packets(opening, "v:0")
    require_timeline(original_packets, TOTAL_FRAMES, "Original")
    require_timeline(head_packets, CUT_FRAME, "Opening")
    tail = [p for p in original_packets if p["pts"] >= CUT_PTS]
    need(len(tail) == TAIL_FRAMES and tail[0]["pts"] == CUT_PTS, "Unexpected original tail boundary")
    original_audio = packets(base, "a:0")
    need(len(original_audio) == AUDIO_PACKETS, "Original AAC packet count changed")
    ba = stream(base_probe, "audio")
    need((ba["codec_name"], ba["sample_rate"], ba["channels"]) == ("aac", "48000", 2),
         "Expected original 48 kHz stereo AAC")
    head_frames = frames(opening)
    need([f["pts"] for f in head_frames] == list(range(0, CUT_PTS, TICKS)),
         "Rendered opening did not decode to exactly frames 0..236")
    boundary = idr_at(base, CUT_PTS)
    need(boundary["dts"] == CUT_PTS - 2 * TICKS, "Original IDR has an unexpected decode timestamp")
    return {"baseProbe": base_probe, "headProbe": head_probe, "baseVideoPackets": original_packets,
            "headVideoPackets": head_packets, "tailPackets": tail, "audioPackets": original_audio,
            "evidence": {"baseSha256": BASE_SHA256, "openingSha256": sha(opening),
                         "avcExtradataSha256": AVCC_SHA256, "boundary": boundary,
                         "openingFrames": CUT_FRAME, "tailPackets": len(tail),
                         "originalAudioPackets": len(original_audio), "headDecodePassed": True,
                         "tools": {tool: command([tool, "-version"]).splitlines()[0]
                                   for tool in ("ffmpeg", "ffprobe")}}}


def check_tail(base_state, tail):
    data = probe(tail)
    need(len(data["streams"]) == 1, "Extracted tail must contain video only")
    video = stream(data, "video")
    same_video_config(stream(base_state["baseProbe"], "video"), video, "Extracted tail")
    need(int(video["nb_frames"]) == TAIL_FRAMES, "Extracted tail frame count differs")
    actual = packets(tail, "v:0")
    require_timeline(actual, TAIL_FRAMES, "Extracted tail")
    expected = [packet_view(p, CUT_PTS) for p in base_state["tailPackets"]]
    need([packet_view(p) for p in actual] == expected,
         "Extracted tail changed packet payloads, PTS/DTS, durations or keyframe flags")
    return {"sha256": sha(tail), "packets": len(actual), "packetPayloadAndTimingMatch": True}


def pcm_hash(path):
    text = command(["ffmpeg", "-v", "error", "-xerror", "-i", path, "-map", "0:a:0",
                    "-c:a", "pcm_s16le", "-f", "hash", "-hash", "sha256", "-"])
    need(text.startswith("SHA256="), "Unexpected decoded PCM hash output")
    return text.strip().split("=", 1)[1]


def boundary_hashes(path, last_frame):
    first = CUT_FRAME - 2
    text = command([
        "ffmpeg", "-v", "error", "-xerror", "-i", path, "-map", "0:v:0", "-an",
        "-vf", f"select=between(n\\,{first}\\,{last_frame})", "-frames:v", str(last_frame - first + 1),
        "-fps_mode", "passthrough", "-c:v", "rawvideo", "-pix_fmt", "yuvj420p",
        "-f", "framehash", "-hash", "sha256", "-"
    ])
    values = {}
    for line in text.splitlines():
        if line and not line.startswith("#"):
            fields = [f.strip() for f in line.split(",")]
            values[int(fields[2])] = fields[-1]
    need(set(values) == set(range(first, last_frame + 1)), "Boundary decode returned unexpected frame timestamps")
    return values


def check_output(base, opening, output, state=None):
    state = state or preflight(base, opening)
    need(output.is_file(), "Spliced output does not exist")
    data = probe(output)
    need(len(data["streams"]) == 2, "Spliced MP4 must contain exactly video and original AAC")
    video, audio = stream(data, "video"), stream(data, "audio")
    same_video_config(stream(state["baseProbe"], "video"), video, "Spliced output")
    need(int(video["nb_frames"]) == TOTAL_FRAMES and int(video["duration_ts"]) == TOTAL_FRAMES * TICKS,
         "Spliced frame count or video duration changed")
    video_packets = packets(output, "v:0")
    require_timeline(video_packets, TOTAL_FRAMES, "Spliced output")
    need([packet_view(p) for p in video_packets] ==
         [packet_view(p) for p in state["headVideoPackets"] + state["tailPackets"]],
         "Spliced video packet payloads or timestamps differ from head + original tail")
    original_audio = state["audioPackets"]
    actual_audio = packets(output, "a:0")
    need(len(actual_audio) == AUDIO_PACKETS and
         [packet_view(p, audio=True) for p in actual_audio] ==
         [packet_view(p, audio=True) for p in original_audio],
         "Original AAC packets, PTS/DTS, durations, flags or skip-sample metadata changed")
    original_stream = stream(state["baseProbe"], "audio")
    audio_fields = ("codec_name", "profile", "sample_rate", "channels", "channel_layout", "time_base",
                    "start_pts", "duration_ts", "nb_frames", "extradata")
    need(all(audio.get(k) == original_stream.get(k) for k in audio_fields), "AAC stream layout or edit-list duration changed")
    decoded = frames(output)  # Full video decode, including diagnostics from ffprobe.
    need([f["pts"] for f in decoded] == list(range(0, TOTAL_FRAMES * TICKS, TICKS)),
         "Decoded output has missing, duplicate or shifted presentation frames")
    need(decoded[CUT_FRAME]["key_frame"] == 1, "Decoded splice boundary is not a keyframe")
    need(idr_at(output, CUT_PTS)["dts"] == CUT_PTS - 2 * TICKS, "Output IDR decode time changed")
    original_pcm, actual_pcm = pcm_hash(base), pcm_hash(output)
    need(original_pcm == actual_pcm == BASE_PCM_SHA256, "Decoded audio PCM differs from the approved original")
    old_boundary = boundary_hashes(base, CUT_FRAME + 2)
    head_boundary = boundary_hashes(opening, CUT_FRAME - 1)
    new_boundary = boundary_hashes(output, CUT_FRAME + 2)
    expected_boundary = {**head_boundary, **{k: v for k, v in old_boundary.items() if k >= CUT_FRAME}}
    need(new_boundary == expected_boundary, "Decoded boundary frames do not match rendered head + original tail")
    return {**state["evidence"], "outputSha256": sha(output), "outputBytes": output.stat().st_size,
            "frames": len(decoded), "videoTimeBase": video["time_base"],
            "videoDurationTs": int(video["duration_ts"]), "wholeVideoPacketMatch": True,
            "tailPacketsUnchanged": TAIL_FRAMES, "audioPacketsUnchanged": len(actual_audio),
            "audioPcmSha256": actual_pcm, "audioPcmMatch": True,
            "audioStartPts": audio["start_pts"], "audioDurationTs": audio["duration_ts"],
            "originalAudioPriming": packet_view(original_audio[0], audio=True),
            "originalAudioLastPacket": packet_view(original_audio[-1], audio=True),
            "decodedBoundaryFrameHashes": new_boundary, "boundaryDecodeMatch": True,
            "fullVideoDecodePassed": True, "fullAudioDecodePassed": True,
            "limitations": "Automated splice and decoded-boundary checks; no new human listening or teaching-expression review."}


def write_report(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def parser(description):
    result = argparse.ArgumentParser(description=description)
    result.add_argument("--base", type=Path, default=EPISODE.parent / "agent-intro-v2/video.mp4")
    result.add_argument("--opening", type=Path, default=EPISODE / "remotion/out/opening.mp4")
    result.add_argument("--output", type=Path, default=EPISODE / "video.mp4")
    result.add_argument("--report", type=Path, default=EPISODE / "qa-splice.json")
    result.add_argument("--preflight-only", action="store_true", help="Validate frozen inputs and opening; do not compose")
    return result


def main():
    args = parser(__doc__).parse_args()
    report = {"checkedAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "status": "blocked",
              "mode": "preflight" if args.preflight_only else "check-existing-output"}
    report_path_safe = False
    try:
        safe_report_path(args.report, EPISODE, args.base, args.opening, args.output)
        report_path_safe = True
        report["freeze"] = frozen_inputs(EPISODE, args.base)
        state = preflight(args.base, args.opening)
        report["checks"] = state["evidence"] if args.preflight_only else check_output(args.base, args.opening, args.output, state)
        need(report["freeze"] == frozen_inputs(EPISODE, args.base), "Frozen manifest changed during validation")
        report["status"] = "passed"
    except (SpliceError, OSError, ValueError, KeyError) as error:
        report["error"] = str(error)
    if report_path_safe:
        write_report(args.report, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
