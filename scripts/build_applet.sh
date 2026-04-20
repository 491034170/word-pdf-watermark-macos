#!/bin/zsh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_DIR/dist"
OUT_APP="$OUT_DIR/Word转PDF加水印.app"
ICON_SOURCE="$REPO_DIR/assets/Word转PDF加水印.icns"

mkdir -p "$OUT_DIR"
rm -rf "$OUT_APP"
osacompile -o "$OUT_APP" "$REPO_DIR/launcher.applescript"

if [[ -f "$ICON_SOURCE" ]]; then
  cp "$ICON_SOURCE" "$OUT_APP/Contents/Resources/applet.icns"
fi

echo "已生成：$OUT_APP"
