#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
/usr/bin/python3 "$SCRIPT_DIR/word_pdf_watermark.py" "$@"

echo
echo "按回车键关闭窗口..."
read -r _
