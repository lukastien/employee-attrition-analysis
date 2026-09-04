#!/usr/bin/env bash
# Fix XGBoost OpenMP loading on macOS when Homebrew libomp is not installed.
# Downloads a libomp bottle into .deps/ and patches the local venv xgboost dylib.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This helper is only needed on macOS."
  exit 0
fi

PYTHON="${PYTHON:-.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  echo "Create a venv first: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

BOTTLE_URL="https://ghcr.io/v2/homebrew/core/libomp/blobs/sha256:63919c47ac15a3031c77de66ba76ac52fcd068f24faa4038680f60fae1bbdb47"
mkdir -p .deps/libomp
curl -fsSL -H "Authorization: Bearer QQ==" -o .deps/libomp/libomp.tar.gz "$BOTTLE_URL"
tar -xzf .deps/libomp/libomp.tar.gz -C .deps/libomp
LIBOMP="$(find .deps/libomp -name libomp.dylib | head -1)"
XGB_LIB="$($PYTHON -c 'import xgboost, pathlib; print(pathlib.Path(xgboost.__file__).parent / \"lib\")')"
cp "$LIBOMP" "$XGB_LIB/libomp.dylib"
install_name_tool -change @rpath/libomp.dylib @loader_path/libomp.dylib "$XGB_LIB/libxgboost.dylib"
"$PYTHON" -c "import xgboost; print('XGBoost OK', xgboost.__version__)"
