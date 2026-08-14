#!/usr/bin/env bash
# test with:
# ( source support/python27/test/test.sh; )
project_root=$(git rev-parse --show-toplevel)
script_dir=$project_root/support/python27/test
build_home=$(realpath "$script_dir/..")
temp_dir=$(mktemp -d)

declare -p script_dir
declare -p build_home
declare -p project_root
declare -p temp_dir

set -euo pipefail

docker build -t prova $build_home

mkdir $temp_dir/workspace
git clone $project_root/.git $temp_dir/workspace

docker run -w=/home/tester/workspace\
      -v=$temp_dir/workspace:/home/tester/workspace -i prova bash << COMMANDS
set -x
virtualenv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/pytest
COMMANDS
echo status_code=$?
