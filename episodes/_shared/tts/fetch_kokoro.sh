#!/usr/bin/env bash
# 下载第二期配音用的 Kokoro-82M v1.0（sherpa-onnx 打包版）并建 Python 环境。模型约 330MB，不进仓库。
# 用法：bash episodes/_shared/tts/fetch_kokoro.sh   → episodes/_shared/tts/models/kokoro-multi-lang-v1_0/ 与 episodes/_shared/tts/.venv/
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
M=kokoro-multi-lang-v1_0
SHA_MODEL=b40f62b166ac8164b0627ef48a0b358eda0985e272fb03ef5252e7206305da11
mkdir -p "$here/models"
if [ ! -f "$here/models/$M/model.onnx" ]; then
  curl -fL -o "$here/models/$M.tar.bz2" "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/$M.tar.bz2"
  python3 -c "import tarfile,sys;tarfile.open(sys.argv[1]).extractall(sys.argv[2])" "$here/models/$M.tar.bz2" "$here/models"
  rm "$here/models/$M.tar.bz2"
fi
echo "$SHA_MODEL  $here/models/$M/model.onnx" | sha256sum -c -
if [ ! -x "$here/.venv/bin/python" ]; then
  python3 -m venv "$here/.venv"
  "$here/.venv/bin/pip" install -q "sherpa-onnx==1.13.8" "soundfile" "numpy"
fi
echo "ok: $here/models/$M  python: $here/.venv/bin/python"
