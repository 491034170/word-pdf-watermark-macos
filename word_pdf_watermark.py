#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Optional

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas


DEFAULT_WATERMARK = "仅供内部使用"
SUPPORTED_INPUTS = {".doc", ".docx", ".dot", ".dotx", ".rtf", ".pdf"}


def run_osascript(*lines: str) -> str:
    result = subprocess.run(
        ["/usr/bin/osascript", *sum([["-e", line] for line in lines], [])],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def choose_files() -> list[Path]:
    output = run_osascript(
        'set selectedFiles to choose file with prompt "请选择 Word 或 PDF 文件" with multiple selections allowed true',
        'set fileList to ""',
        'repeat with oneFile in selectedFiles',
        'set fileList to fileList & POSIX path of oneFile & linefeed',
        'end repeat',
        'return fileList',
    )
    return [Path(line) for line in output.splitlines() if line.strip()]


def prompt_watermark(default_text: str) -> str:
    result = subprocess.run(
        [
            "/usr/bin/osascript",
            "-e",
            'set dialogResult to display dialog "请输入水印文字" default answer (system attribute "WATERMARK_DEFAULT") buttons {"取消", "确定"} default button "确定"',
            "-e",
            "return text returned of dialogResult",
        ],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "WATERMARK_DEFAULT": default_text},
    )
    return result.stdout.strip()


def show_message(title: str, message: str) -> None:
    try:
        subprocess.run(
            [
                "/usr/bin/osascript",
                "-e",
                'display dialog (system attribute "MESSAGE_BODY") with title (system attribute "MESSAGE_TITLE") buttons {"好"} default button "好"',
            ],
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "MESSAGE_BODY": message, "MESSAGE_TITLE": title},
        )
    except subprocess.CalledProcessError:
        print(f"{title}: {message}")


def find_soffice() -> Path:
    candidates = [
        Path("/opt/homebrew/bin/soffice"),
        Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("没有找到 LibreOffice 的 soffice 命令。")


def pick_font(text: str) -> str:
    if any(ord(char) > 127 for char in text):
        font_name = "STSong-Light"
        try:
            pdfmetrics.getFont(font_name)
        except KeyError:
            pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        return font_name
    return "Helvetica-Bold"


def build_watermark_overlay(width: float, height: float, text: str):
    buffer = BytesIO()
    watermark_canvas = canvas.Canvas(buffer, pagesize=(width, height))
    font_name = pick_font(text)

    font_size = min(max(28, min(width, height) * 0.09), max(32, width / max(5, len(text) * 0.55)))
    watermark_canvas.saveState()
    try:
        watermark_canvas.setFillAlpha(0.16)
    except AttributeError:
        pass
    watermark_canvas.setFillColor(colors.Color(0.45, 0.45, 0.45))
    watermark_canvas.translate(width / 2, height / 2)
    watermark_canvas.rotate(35)
    watermark_canvas.setFont(font_name, font_size)
    for offset in (-height * 0.28, 0, height * 0.28):
        watermark_canvas.drawCentredString(0, offset, text)
    watermark_canvas.restoreState()
    watermark_canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def convert_word_to_pdf(source: Path, soffice: Optional[Path], output_dir: Path) -> Path:
    if source.suffix.lower() == ".pdf":
        target = output_dir / source.name
        shutil.copy2(source, target)
        return target

    if soffice is None:
        raise FileNotFoundError("没有找到 LibreOffice 的 soffice 命令。")

    process = subprocess.run(
        [
            str(soffice),
            "--headless",
            "--convert-to",
            "pdf:writer_pdf_Export",
            "--outdir",
            str(output_dir),
            str(source),
        ],
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "LibreOffice 转换失败。")

    output_pdf = output_dir / f"{source.stem}.pdf"
    if not output_pdf.exists():
        raise FileNotFoundError(f"未找到转换后的 PDF：{output_pdf}")
    return output_pdf


def add_watermark(source_pdf: Path, watermark_text: str, output_pdf: Path) -> Path:
    reader = PdfReader(str(source_pdf))
    writer = PdfWriter()

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay = build_watermark_overlay(width, height, watermark_text)
        page.merge_page(overlay)
        writer.add_page(page)

    with output_pdf.open("wb") as handle:
        writer.write(handle)
    return output_pdf


def resolve_inputs(args: argparse.Namespace) -> list[Path]:
    if args.files:
        return [Path(path).expanduser() for path in args.files]
    if getattr(args, "no_ui", False):
        raise ValueError("没有提供要处理的文件。")
    return choose_files()


def validate_inputs(paths: list[Path]) -> list[Path]:
    valid = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{path}")
        if path.suffix.lower() not in SUPPORTED_INPUTS:
            raise ValueError(f"暂不支持该格式：{path.name}")
        valid.append(path)
    if not valid:
        raise ValueError("没有选择任何文件。")
    return valid


def main() -> int:
    parser = argparse.ArgumentParser(description="把 Word 转成 PDF 并加上文字水印。")
    parser.add_argument("files", nargs="*", help="要处理的 Word 或 PDF 文件")
    parser.add_argument("--watermark", help="水印文字")
    parser.add_argument("--no-ui", action="store_true", help="禁用图形界面弹窗，适合由外部启动器调用")
    args = parser.parse_args()

    try:
        sources = validate_inputs(resolve_inputs(args))
        watermark_text = (args.watermark or prompt_watermark(DEFAULT_WATERMARK)).strip()
        if not watermark_text:
            raise ValueError("水印文字不能为空。")

        soffice = None
        if any(source.suffix.lower() != ".pdf" for source in sources):
            soffice = find_soffice()
        generated_files = []

        with tempfile.TemporaryDirectory(prefix="word-pdf-watermark-") as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            for source in sources:
                converted_pdf = convert_word_to_pdf(source, soffice, temp_dir)
                output_pdf = source.with_name(f"{source.stem}_带水印.pdf")
                add_watermark(converted_pdf, watermark_text, output_pdf)
                generated_files.append(output_pdf)

        for generated in generated_files:
            subprocess.run(["open", "-R", str(generated)], check=False)

        summary = "\n".join(str(path) for path in generated_files)
        if not args.no_ui:
            show_message("处理完成", f"已生成以下文件：\n{summary}")
        print(summary)
        return 0
    except subprocess.CalledProcessError:
        print("操作已取消。")
        return 1
    except Exception as error:
        if not args.no_ui:
            show_message("处理失败", str(error).replace('"', "'"))
        print(f"错误：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
