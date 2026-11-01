#!/usr/bin/env bash
set -euo pipefail
example_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mq08_classes="${MQ08_CLASSES_DIR:-/tmp/mq08-example-classes}"
mkdir -p -- "$mq08_classes"
if command -v javac >/dev/null 2>&1; then
  compiler=(javac)
  language=(--release 17)
else
  compiler=(java -m jdk.compiler/com.sun.tools.javac.Main)
  # Some managed JREs include jdk.compiler but omit ct.sym, so --release is unavailable.
  language=(-source 17 -target 17 -Xlint:-options)
fi
if [[ "${1:-}" == "test-core" ]]; then
  "${compiler[@]}" "${language[@]}" -d "$mq08_classes" "$example_dir/Mq08Core.java" "$example_dir/Mq08CoreTest.java"
  exec java -cp "$mq08_classes" Mq08CoreTest
fi
: "${KAFKA_HOME:?Set KAFKA_HOME to a freshly verified Kafka 4.4.0 distribution}"
[[ -f "$KAFKA_HOME/libs/kafka-clients-4.4.0.jar" ]] || { echo 'Kafka 4.4.0 client library missing' >&2; exit 2; }
"${compiler[@]}" "${language[@]}" -cp "$KAFKA_HOME/libs/*" -d "$mq08_classes" "$example_dir/Mq08Core.java" "$example_dir/Mq08Worker.java"
exec java -cp "$mq08_classes:$KAFKA_HOME/libs/*" Mq08Worker "$@"
