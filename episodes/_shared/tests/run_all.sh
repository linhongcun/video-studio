#!/bin/sh
# Plain python3 + numpy. place-mode selftest needs ffmpeg and skips that part when it is absent.
set -eu
cd "$(dirname "$0")/../../.."
python3 episodes/_shared/onset_rule.py
python3 episodes/_shared/label_onset_strict.py --selftest
python3 episodes/_shared/place_v2.py --selftest
python3 episodes/_shared/make_knoll_props.py --selftest
python3 episodes/_shared/tests/test_label_onset_strict.py
python3 episodes/_shared/tests/test_place_v2.py
python3 episodes/_shared/tests/test_make_knoll_props.py
echo run_all ok
