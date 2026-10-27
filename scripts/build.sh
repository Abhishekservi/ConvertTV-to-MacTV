#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
project=${1:-launcher}
case "$project" in launcher|airplay) ;; *) echo "Usage: $0 [launcher|airplay] [debug|release]" >&2; exit 2;; esac
variant=${2:-debug}
case "$variant" in debug) task=assembleDebug ;; release) task=assembleRelease ;; *) echo 'Variant must be debug or release' >&2; exit 2;; esac
exec "$ROOT/airplay/gradlew" -p "$ROOT/$project" "$task"
