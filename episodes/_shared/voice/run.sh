#!/bin/sh
# Voice step after the takes are picked (EP.14 voice/final.sh, plus build and shot_frames).
#   sh episodes/_shared/voice/run.sh EPDIR            # build -> asr -> words/cues -> checks
#   sh episodes/_shared/voice/run.sh EPDIR --no-asr   # reuse voice/asr.json (same takes, same build)
# Needs voice/sents.json, voice/picks.json, voice/takes/, voice/cue_tests.json.
# Logs go to EPDIR/voice/*.log and step times to EPDIR/voice/times.txt. Exit is non-zero on the first failing step.
set -eu
EP=$(cd "$1" && pwd); shift
V="$(cd "$(dirname "$0")" && pwd)"; L="$EP/voice"; T="$L/times.txt"
ASR=1; [ "${1:-}" = "--no-asr" ] && ASR=0
step() { n=$1; shift; echo "$n $(date +%T)" >> "$T"; "$@" > "$L/$n.log" 2>&1 || { echo "FAIL $n (see voice/$n.log)"; exit 1; }; echo "$n end $(date +%T)" >> "$T"; }
step build python3 "$V/build.py" --dir "$EP"
if [ $ASR = 1 ]; then step asr python3 "$V/asr.py" --dir "$EP"; step asr_full python3 "$V/asr_full.py" --dir "$EP"; fi
step onsets python3 "$V/onsets.py" --dir "$EP"
step lastword python3 "$V/lastword_fix.py" --dir "$EP"
step cues_rule python3 "$V/cues_rule.py" --dir "$EP"
step shot_frames python3 "$V/shot_frames.py" --dir "$EP"
step selfcheck python3 "$V/selfcheck.py" --dir "$EP"
step sandhi_yi python3 "$V/sandhi.py" --dir "$EP" 一
step sandhi_bu python3 "$V/sandhi.py" --dir "$EP" 不
step sandhi_verdict python3 "$V/sandhi_verdict.py" --dir "$EP"
if [ -f "$L/probe.in" ]; then echo "probe $(date +%T)" >> "$T"; python3 "$V/probe.py" --dir "$EP" < "$L/probe.in" > "$L/probe.log" 2>&1; fi
echo "voice ok: $EP/voice.wav $(python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()[:8])" "$EP/voice.wav")"
