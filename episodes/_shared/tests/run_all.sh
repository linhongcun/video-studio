#!/bin/sh
# Plain python3 + numpy. place-mode selftest needs ffmpeg and skips that part when it is absent.
# test_voice.py needs ffmpeg + scipy + soundfile and skips when they are absent (no network, no TTS, no whisper).
# secret_scan.py runs last and fails on anything that looks like a key in tracked or unignored files.
set -eu
cd "$(dirname "$0")/../../.."
python3 episodes/_shared/onset_rule.py
python3 episodes/_shared/label_onset_strict.py --selftest
python3 episodes/_shared/place_v2.py --selftest
python3 episodes/_shared/make_knoll_props.py --selftest
python3 episodes/_shared/tests/test_label_onset_strict.py
python3 episodes/_shared/tests/test_place_v2.py
python3 episodes/_shared/tests/test_make_knoll_props.py
python3 episodes/_shared/tests/test_voice.py
python3 episodes/_shared/tests/secret_scan.py
echo run_all ok
