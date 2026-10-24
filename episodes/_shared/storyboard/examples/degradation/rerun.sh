#!/bin/sh
# Rebuild historical EP.14 v0.45.0 (degradation-v1) from pinned fixture inputs.
#   sh episodes/_shared/storyboard/examples/degradation/rerun.sh [OUTDIR]      (default OUTDIR: a new mktemp dir)
# Expect: layout ok / covers ok / frames 5152 …, validate 检查 6623 项，错误 0 (onset 91/91), strict 91 cues, 0 fail,
# storyboard sha256 6265993b…, covers sha256 8cb7aafb…, cmp silent against the immutable fixture.
set -eu
cd "$(dirname "$0")/../../../../.."
S=episodes/_shared/storyboard; EX=$S/examples/degradation; EP=episodes/_shared/tests/fixtures/degradation-v0.45.0; M=$EX/repo-inputs.json
O=${1:-$(mktemp -d)}; mkdir -p "$O"
python3 -B -c 'import sys; sys.path.insert(0, "episodes/_shared/tests"); from degradation_fixture import historical_degradation; historical_degradation()'
python3 -B $S/layout.py --spec $EX/layout_spec.py --episode-dir $EP --inputs $M --out "$O/layout.json"
python3 -B $S/make_covers.py --spec $EX/covers_spec.py --out "$O/covers.json"
python3 -B $S/build_sb.py --spec $EX/build_spec.py --episode-dir $EP --inputs $M --layout "$O/layout.json" --covers "$O/covers.json" --out "$O/storyboard.json"
python3 -B $S/validate.py --spec $EX/validate_spec.py --episode-dir $EP --inputs $M --storyboard "$O/storyboard.json" --covers "$O/covers.json" --report "$O/validate.txt"
python3 -B episodes/_shared/label_onset_strict.py --storyboard "$O/storyboard.json" --wav $EP/remotion/public/audio/voice.wav --words-json $EP/words.json --out "$O/strict.txt" | tail -1
sha256sum "$O/storyboard.json" "$O/covers.json"
cmp "$O/storyboard.json" $EP/storyboard.json
cmp "$O/covers.json" $EP/covers.json
echo "rerun ok -> $O"
