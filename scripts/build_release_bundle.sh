#!/bin/zsh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:-v1.0.0}"
VERSION_NAME="${VERSION#v}"
DIST_DIR="$REPO_DIR/dist"
APP_NAME="Word转PDF加水印.app"
APP_PATH="$DIST_DIR/$APP_NAME"
ZIP_NAME="word-pdf-watermark-macos-${VERSION_NAME}.zip"
ZIP_PATH="$DIST_DIR/$ZIP_NAME"
CHECKSUM_PATH="$DIST_DIR/SHA256SUMS.txt"

mkdir -p "$DIST_DIR"
"$REPO_DIR/scripts/build_applet.sh"
rm -f "$ZIP_PATH" "$CHECKSUM_PATH"

ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_PATH"
(
  cd "$DIST_DIR"
  shasum -a 256 "$ZIP_NAME" > "$CHECKSUM_PATH"
)

echo "已生成发布包：$ZIP_PATH"
echo "校验文件：$CHECKSUM_PATH"
