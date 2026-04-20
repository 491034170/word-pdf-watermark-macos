#!/bin/zsh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_DIR/dist"
OUT_APP="$OUT_DIR/Word转PDF加水印.app"
ICON_SOURCE="$REPO_DIR/assets/Word转PDF加水印.icns"
RESOURCE_DIR="$OUT_APP/Contents/Resources"
PYTHON_BIN="$(command -v python3)"

if [[ -z "$PYTHON_BIN" ]]; then
  echo "未找到 python3，无法构建 App。" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
rm -rf "$OUT_APP"
osacompile -o "$OUT_APP" "$REPO_DIR/launcher.applescript"
mkdir -p "$RESOURCE_DIR/python-libs"

cp "$REPO_DIR/word_pdf_watermark.py" "$RESOURCE_DIR/word_pdf_watermark.py"
cp "$REPO_DIR/requirements.txt" "$RESOURCE_DIR/requirements.txt"

if [[ -f "$ICON_SOURCE" ]]; then
  cp "$ICON_SOURCE" "$OUT_APP/Contents/Resources/applet.icns"
fi

"$PYTHON_BIN" - <<'PY' "$RESOURCE_DIR/python-libs"
import importlib.util
import shutil
import sys
from pathlib import Path

target = Path(sys.argv[1])
target.mkdir(parents=True, exist_ok=True)
for package_name in ("pypdf", "reportlab"):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        raise SystemExit(f"缺少依赖包：{package_name}")
    if spec.submodule_search_locations:
        source = Path(next(iter(spec.submodule_search_locations)))
        destination = target / source.name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
    else:
        source = Path(spec.origin)
        shutil.copy2(source, target / source.name)
PY

echo "已生成：$OUT_APP"
