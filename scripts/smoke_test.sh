#!/bin/zsh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d /tmp/word-pdf-watermark-smoke.XXXXXX)"
INPUT_PDF="$TMP_DIR/input.pdf"
OUTPUT_PDF="$TMP_DIR/input_带水印.pdf"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

cd "$REPO_DIR"

python3 - <<'PY' "$INPUT_PDF"
from pathlib import Path
from reportlab.pdfgen import canvas
import sys

sample = Path(sys.argv[1])
c = canvas.Canvas(str(sample))
c.drawString(72, 760, 'Smoke test input PDF')
c.save()
print(sample)
PY

python3 word_pdf_watermark.py --no-ui --watermark 'CI Smoke Test' "$INPUT_PDF"

test -f "$OUTPUT_PDF"
python3 - <<'PY' "$OUTPUT_PDF"
from pathlib import Path
from pypdf import PdfReader
import sys

output = Path(sys.argv[1])
reader = PdfReader(str(output))
assert len(reader.pages) == 1, f'Unexpected page count: {len(reader.pages)}'
print(output)
PY

echo "Smoke test passed: $OUTPUT_PDF"
