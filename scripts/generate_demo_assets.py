#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs" / "images"
ICON_PATH = ROOT / "assets" / "Word转PDF加水印.icns"

DOCS_DIR.mkdir(parents=True, exist_ok=True)

BG_TOP = (246, 248, 255)
BG_BOTTOM = (224, 232, 255)
NAVY = (20, 28, 48)
SLATE = (78, 91, 118)
ACCENT = (74, 108, 247)
ACCENT_2 = (112, 87, 255)
GREEN = (37, 181, 119)
ORANGE = (255, 164, 55)
BORDER = (224, 228, 241)
CARD = (255, 255, 255)
SOFT = (243, 246, 255)
WHITE = (255, 255, 255)


def load_font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if mono:
        candidates = [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/SFNSMono.ttf",
            "/System/Library/Fonts/Monaco.ttf",
        ]
    elif bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
        ]

    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def vertical_gradient(width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (width, height), top)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, width, y), fill=color)
    return image


def draw_shadow(base: Image.Image, box: tuple[int, int, int, int], radius: int = 28, offset: tuple[int, int] = (0, 18), alpha: int = 70) -> None:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    x0, y0, x1, y1 = box
    ox, oy = offset
    shadow_draw.rounded_rectangle((x0 + ox, y0 + oy, x1 + ox, y1 + oy), radius=radius, fill=(28, 38, 76, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    base.alpha_composite(shadow)


def draw_pill(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill, text_fill=(255, 255, 255), padding=(18, 10), font_size: int = 28) -> tuple[int, int, int, int]:
    font = load_font(font_size, bold=True)
    tw, th = text_size(draw, text, font)
    x, y = xy
    w = tw + padding[0] * 2
    h = th + padding[1] * 2
    draw.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fill)
    draw.text((x + padding[0], y + padding[1] - 2), text, font=font, fill=text_fill)
    return (x, y, x + w, y + h)


def icon_image(size: int) -> Image.Image:
    icon = Image.open(ICON_PATH).convert("RGBA")
    return icon.resize((size, size), Image.LANCZOS)


def create_document_preview(size: tuple[int, int], *, watermarked: bool = False) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, (250, 251, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=28, fill=(255, 255, 255, 255), outline=BORDER, width=2)
    draw.rectangle((0, 0, width, 82), fill=(245, 247, 255, 255))

    title_font = load_font(30, bold=True)
    body_font = load_font(21)
    mono_font = load_font(18, mono=True)

    draw.text((36, 28), "项目资料 / Project Brief", font=title_font, fill=NAVY)
    draw.text((36, 104), "• 客户：天智工坊 Tianmind Studio", font=body_font, fill=SLATE)
    draw.text((36, 148), "• 文件：报价单 / Quote / Proposal", font=body_font, fill=SLATE)
    draw.text((36, 192), "• 输出：PDF + 文字水印", font=body_font, fill=SLATE)

    for y in range(272, height - 90, 40):
        line_width = width - 72 if y < height - 180 else width - 180
        draw.rounded_rectangle((36, y, line_width, y + 10), radius=5, fill=(230, 235, 245, 255))

    if watermarked:
        overlay = Image.new("RGBA", size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        watermark_font = load_font(88, bold=True)
        for offset_y in (-140, 0, 140):
            overlay_draw.text((width // 2 - 260, height // 2 - 80 + offset_y), "仅供内部使用", font=watermark_font, fill=(92, 100, 118, 42))
        overlay = overlay.rotate(33, resample=Image.BICUBIC, center=(width // 2, height // 2))
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((28, 24, 260, 66), radius=18, fill=(236, 248, 241, 255))
        draw.text((42, 32), "已加水印 / Watermarked", font=mono_font, fill=GREEN)
    else:
        draw.rounded_rectangle((28, 24, 204, 66), radius=18, fill=(239, 245, 255, 255))
        draw.text((42, 32), "原始文件 / Source", font=mono_font, fill=ACCENT)

    return image


def draw_traffic_lights(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    colors = [(255, 94, 87), (255, 189, 46), (40, 200, 64)]
    for index, color in enumerate(colors):
        dx = x + index * 24
        draw.ellipse((dx, y, dx + 14, y + 14), fill=color)


def create_window(size: tuple[int, int], title: str) -> Image.Image:
    width, height = size
    window = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(window)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=30, fill=(255, 255, 255, 245), outline=BORDER, width=2)
    draw.rounded_rectangle((0, 0, width - 1, 68), radius=30, fill=(248, 250, 255, 250), outline=None)
    draw.rectangle((0, 40, width - 1, 68), fill=(248, 250, 255, 250))
    draw.line((0, 68, width, 68), fill=BORDER, width=2)
    draw_traffic_lights(draw, 24, 26)
    title_font = load_font(24, bold=True)
    tw, _ = text_size(draw, title, title_font)
    draw.text(((width - tw) // 2, 22), title, font=title_font, fill=SLATE)
    return window


def add_glow(base: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    x, y = center
    glow_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 2))
    base.alpha_composite(glow)


def save_png(image: Image.Image, path: Path) -> None:
    image.save(path, format="PNG")


def build_hero() -> None:
    canvas = vertical_gradient(1600, 900, BG_TOP, BG_BOTTOM).convert("RGBA")
    add_glow(canvas, (1220, 180), 260, ACCENT_2, 55)
    add_glow(canvas, (1320, 700), 220, (51, 191, 156), 42)
    add_glow(canvas, (260, 680), 220, (253, 201, 105), 34)

    draw = ImageDraw.Draw(canvas)
    draw_pill(draw, (88, 74), "macOS utility", fill=ACCENT)
    draw_pill(draw, (305, 74), "Word / PDF → Watermark", fill=(27, 38, 68))

    title_font = load_font(72, bold=True)
    subtitle_font = load_font(33)
    bullet_title_font = load_font(26, bold=True)
    bullet_font = load_font(27)
    small_font = load_font(22)

    draw.text((88, 166), "Word 转 PDF + 加水印", font=title_font, fill=NAVY)
    draw.text((88, 254), "A clean macOS workflow for converting documents to PDF and stamping text watermarks.", font=subtitle_font, fill=SLATE)

    bullets = [
        ("支持 Word / PDF / RTF", "Word、PDF、RTF 文档都能处理"),
        ("中文英文水印", "支持中文和英文水印文字"),
        ("三种入口", "CLI、.command、拖拽式 .app 三种使用方式"),
        ("原目录输出", "结果生成在原文件旁边，命名为 *_带水印.pdf"),
    ]

    start_y = 360
    for index, (heading, desc) in enumerate(bullets):
        y = start_y + index * 108
        draw.rounded_rectangle((88, y, 610, y + 82), radius=28, fill=(255, 255, 255, 180), outline=(230, 235, 246), width=2)
        draw.ellipse((108, y + 23, 144, y + 59), fill=ACCENT)
        draw.text((162, y + 14), heading, font=bullet_title_font, fill=NAVY)
        draw.text((162, y + 44), desc, font=bullet_font, fill=SLATE)

    draw.text((88, 818), "Open source • Python • LibreOffice • AppleScript", font=small_font, fill=(96, 107, 136))

    window_box = (780, 96, 1512, 812)
    draw_shadow(canvas, window_box, radius=36)
    window = create_window((window_box[2] - window_box[0], window_box[3] - window_box[1]), "Word PDF Watermark Demo")
    wdraw = ImageDraw.Draw(window)

    icon = icon_image(132)
    window.alpha_composite(icon, (40, 112))
    wdraw.text((196, 128), "Drop files → Enter watermark → Export PDF", font=load_font(33, bold=True), fill=NAVY)
    wdraw.text((196, 176), "面向 macOS 的轻量文档处理工具", font=load_font(26), fill=SLATE)

    input_doc = create_document_preview((250, 360), watermarked=False)
    output_doc = create_document_preview((250, 360), watermarked=True)
    arrow_font = load_font(62, bold=True)
    tag_font = load_font(21, mono=True)

    window.alpha_composite(input_doc, (52, 280))
    window.alpha_composite(output_doc, (420, 280))
    wdraw.rounded_rectangle((58, 238, 210, 272), radius=17, fill=(239, 245, 255))
    wdraw.text((74, 246), "input.docx / input.pdf", font=tag_font, fill=ACCENT)
    wdraw.rounded_rectangle((428, 238, 662, 272), radius=17, fill=(236, 248, 241))
    wdraw.text((444, 246), "output_带水印.pdf", font=tag_font, fill=GREEN)
    wdraw.text((334, 434), "→", font=arrow_font, fill=ACCENT_2)

    info_card = (52, 664, 680, 706)
    wdraw.rounded_rectangle(info_card, radius=18, fill=SOFT)
    wdraw.text((74, 673), "Supports CLI, .command launcher, and drag-and-drop .app release.", font=load_font(22), fill=SLATE)

    canvas.alpha_composite(window, (window_box[0], window_box[1]))
    save_png(canvas, DOCS_DIR / "hero.png")


def draw_step_card(canvas: Image.Image, box: tuple[int, int, int, int], *, step_no: str, title: str, desc: str, highlight: bool, content: str) -> None:
    draw_shadow(canvas, box, radius=32, offset=(0, 16), alpha=58 if highlight else 42)
    card = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
    fill = (255, 255, 255, 250) if not highlight else (250, 252, 255, 255)
    outline = ACCENT if highlight else BORDER
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=30, fill=fill, outline=outline, width=3 if highlight else 2)
    draw.rounded_rectangle((26, 24, 120, 66), radius=21, fill=(238, 243, 255))
    draw.text((42, 31), step_no, font=load_font(24, bold=True), fill=ACCENT)
    draw.text((28, 98), title, font=load_font(30, bold=True), fill=NAVY)
    draw.text((28, 144), desc, font=load_font(22), fill=SLATE)

    if content == "files":
        icon = icon_image(86)
        card.alpha_composite(icon, (36, 224))
        draw.rounded_rectangle((138, 226, 474, 278), radius=18, fill=SOFT)
        draw.text((158, 240), "报价单.docx", font=load_font(24), fill=NAVY)
        draw.rounded_rectangle((138, 300, 474, 352), radius=18, fill=SOFT)
        draw.text((158, 314), "客户资料.pdf", font=load_font(24), fill=NAVY)
        draw.rounded_rectangle((36, 392, 474, 454), radius=22, fill=(239, 245, 255))
        draw.text((60, 410), "支持拖拽文件到 App，也支持先启动后选择", font=load_font(22), fill=ACCENT)
    elif content == "dialog":
        draw.rounded_rectangle((38, 212, 476, 468), radius=24, fill=(248, 250, 255), outline=BORDER, width=2)
        draw.text((66, 244), "请输入水印文字", font=load_font(26, bold=True), fill=NAVY)
        draw.rounded_rectangle((66, 300, 448, 368), radius=18, fill=WHITE, outline=(210, 217, 232), width=2)
        draw.text((88, 321), "仅供内部使用", font=load_font(30), fill=SLATE)
        draw.rounded_rectangle((166, 404, 282, 454), radius=20, fill=(240, 242, 248))
        draw.text((198, 418), "取消", font=load_font(22), fill=SLATE)
        draw.rounded_rectangle((300, 404, 416, 454), radius=20, fill=ACCENT)
        draw.text((332, 418), "确定", font=load_font(22), fill=WHITE)
    else:
        preview = create_document_preview((280, 386), watermarked=True)
        card.alpha_composite(preview, (116, 172))
        draw.rounded_rectangle((36, 516, 474, 578), radius=22, fill=(236, 248, 241))
        draw.text((58, 534), "输出文件：源文件同目录 / *_带水印.pdf", font=load_font(22), fill=GREEN)

    canvas.alpha_composite(card, (box[0], box[1]))


def build_workflow(highlight_index: int | None = None, *, output_name: str = "workflow.png") -> None:
    canvas = vertical_gradient(1600, 900, (248, 249, 255), (232, 238, 255)).convert("RGBA")
    add_glow(canvas, (260, 170), 200, ORANGE, 30)
    add_glow(canvas, (1370, 160), 200, ACCENT_2, 36)

    draw = ImageDraw.Draw(canvas)
    draw_pill(draw, (80, 68), "3-step workflow", fill=(24, 36, 64))
    draw.text((80, 154), "How it works / 使用流程", font=load_font(60, bold=True), fill=NAVY)
    draw.text((80, 228), "拖入文件，输入水印文字，原目录输出带水印 PDF。", font=load_font(30), fill=SLATE)

    boxes = [
        (76, 310, 548, 862),
        (564, 310, 1036, 862),
        (1052, 310, 1524, 862),
    ]
    draw_step_card(canvas, boxes[0], step_no="01", title="选择文件", desc="Word / PDF / RTF 文件都可以", highlight=highlight_index == 0, content="files")
    draw_step_card(canvas, boxes[1], step_no="02", title="输入水印", desc="支持中文英文水印文本", highlight=highlight_index == 1, content="dialog")
    draw_step_card(canvas, boxes[2], step_no="03", title="导出结果", desc="输出 *_带水印.pdf 到原目录", highlight=highlight_index == 2, content="output")

    arrow_font = load_font(70, bold=True)
    draw.text((516, 548), "→", font=arrow_font, fill=ACCENT)
    draw.text((1004, 548), "→", font=arrow_font, fill=ACCENT)
    save_png(canvas, DOCS_DIR / output_name)


def build_demo_gif() -> None:
    frame_paths = []
    for index, name in enumerate(["demo-frame-1.png", "demo-frame-2.png", "demo-frame-3.png"]):
        build_workflow(index, output_name=name)
        frame_paths.append(DOCS_DIR / name)

    frames = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in frame_paths]
    frames[0].save(
        DOCS_DIR / "demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[1100, 1000, 1400],
        loop=0,
        disposal=2,
    )

    for path in frame_paths:
        path.unlink(missing_ok=True)


def build_supporting_assets() -> None:
    save_png(create_document_preview((640, 900), watermarked=False), DOCS_DIR / "sample-input.png")
    save_png(create_document_preview((640, 900), watermarked=True), DOCS_DIR / "sample-output.png")


def main() -> None:
    build_supporting_assets()
    build_hero()
    build_workflow()
    build_demo_gif()
    print(f"Generated assets in {DOCS_DIR}")


if __name__ == "__main__":
    main()
