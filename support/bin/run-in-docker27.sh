#!/usr/bin/env bash
SCRIPT_DIR="$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SUPPORT_DIR="$(cd -- "$SCRIPT_DIR/.." &> /dev/null && pwd )"
ROOT_DIR="$(cd -- "$SUPPORT_DIR/.." &> /dev/null && pwd )"
set -euo pipefail

docker build -t trash-cli-local-27 \
    -f "$SUPPORT_DIR"/run-in-docker27/Dockerfile \
    "$ROOT_DIR"

docker run -it \
    -v "tmp_dir:/tmp" \
    trash-cli-local-27

