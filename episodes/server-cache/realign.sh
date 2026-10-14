#!/bin/sh
# 2026-10-14（Miyazaki）：EP8 没有重配音，沿用现有 timing.json；gen → 标签时机修正 → validate → fullshow。给了路径则先拷成 timing.mimo.json 再 map_timing
set -e; cd "$(dirname "$0")"; export PYTHONDONTWRITEBYTECODE=1
if [ -n "$1" ]; then cp "$1" timing.mimo.json; fi
for i in 1 2 3; do
  python3 -B map_timing.py >/dev/null && python3 -B gen.py >/dev/null
  rc=0; python3 -B ../_audit/labelfix.py . || rc=$?
  [ $rc = 3 ] || break
done
[ $rc = 0 ] || [ $rc = 3 ] || exit $rc
python3 -B gen.py | tail -1 && python3 -B ../_audit/labelfix.py . >/dev/null; python3 -B validate.py && python3 -B ../_audit/fullshow.py .
