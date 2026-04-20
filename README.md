<div align="center">
  <img src="docs/images/hero.png" alt="Word PDF Watermark hero" width="100%" />

  <h1>Word PDF Watermark (macOS)</h1>
  <p><strong>把 Word / PDF 快速处理成带文字水印的 PDF</strong><br /><strong>Turn Word / PDF files into watermarked PDFs on macOS</strong></p>

  <p>
    <img src="https://img.shields.io/badge/macOS-Apple-black?logo=apple" alt="macOS" />
    <img src="https://img.shields.io/badge/Python-3-blue?logo=python" alt="Python 3" />
    <img src="https://img.shields.io/badge/LibreOffice-Optional%20for%20Word%20conversion-18A303?logo=libreoffice" alt="LibreOffice" />
    <img src="https://img.shields.io/github/v/release/491034170/word-pdf-watermark-macos?display_name=tag" alt="GitHub Release" />
  </p>

  <p>
    <a href="#中文">中文</a> ·
    <a href="#english">English</a> ·
    <a href="https://github.com/491034170/word-pdf-watermark-macos/releases">Download Release</a>
  </p>
</div>

## Demo

<p align="center">
  <img src="docs/images/demo.gif" alt="Demo GIF" width="100%" />
</p>

<p align="center">
  <img src="docs/images/workflow.png" alt="Workflow overview" width="100%" />
</p>

---

## 中文

### 简介

这是一个面向 macOS 的轻量工具，用来把 Word / PDF 文件快速处理成带文字水印的 PDF。

它适合这些场景：
- 内部资料分发
- 报价单 / 合同 / 提案输出
- 给 PDF 增加“仅供内部使用”“样稿”“审阅版”等文字水印
- 批量处理多个文档

仓库同时提供三种使用方式：
- 命令行：适合自动化和批量处理
- `.command` 启动器：适合本机双击运行
- 拖拽式 `.app`：适合日常图形化使用

### 功能亮点

- 支持输入格式：`.doc` `.docx` `.dot` `.dotx` `.rtf` `.pdf`
- 输入是 PDF 时，直接叠加文字水印
- 输入是 Word / RTF 时，先调用 LibreOffice 转成 PDF，再叠加水印
- 支持中文和英文水印
- 支持一次处理多个文件
- 输出文件生成在原文件旁边，命名为 `*_带水印.pdf`
- Release 里的 `.app` 已内置 Python 依赖，下载即可直接使用打包好的 App 外壳

### 快速开始

#### 方式 A：直接下载 Release

1. 打开 Releases 页面：
   https://github.com/491034170/word-pdf-watermark-macos/releases
2. 下载最新的 `word-pdf-watermark-macos-<version>.zip`
3. 解压后得到 `Word转PDF加水印.app`
4. 双击打开，或直接把文件拖到 App 上

说明：
- Release `.app` 已随包携带 `pypdf` 和 `reportlab`
- 如果你的 macOS 环境里没有 `python3`，请先安装 Python 3
- 如果你要处理 Word / RTF，请先安装 LibreOffice

#### 方式 B：从源码运行

```bash
python3 -m pip install -r requirements.txt
python3 word_pdf_watermark.py 文件1.docx 文件2.pdf
```

### 命令行使用

基础用法：

```bash
python3 word_pdf_watermark.py 文件1.docx 文件2.pdf
```

指定水印：

```bash
python3 word_pdf_watermark.py --watermark "仅供内部使用" 文件.docx
```

无图形界面模式：

```bash
python3 word_pdf_watermark.py --no-ui --watermark "项目资料" 文件.pdf
```

### `.command` 启动器

仓库内置：

```text
scripts/Word转PDF加水印.command
```

它会自动定位仓库根目录下的 `word_pdf_watermark.py`，适合本机双击运行。

### 构建拖拽式 `.app`

```bash
chmod +x scripts/build_applet.sh
./scripts/build_applet.sh
```

生成产物：

```text
dist/Word转PDF加水印.app
```

这个 `.app` 会把以下内容一起打包到 App 资源目录里：
- `word_pdf_watermark.py`
- `requirements.txt`
- vendored Python dependencies: `pypdf`, `reportlab`

### 构建 Release 发布包

```bash
chmod +x scripts/build_release_bundle.sh
./scripts/build_release_bundle.sh v1.0.0
```

生成内容：

```text
dist/Word转PDF加水印.app
dist/word-pdf-watermark-macos-1.0.0.zip
dist/SHA256SUMS.txt
```

### 运行环境

- macOS
- Python 3
- LibreOffice（仅在 Word / RTF 转 PDF 时需要）

脚本会自动尝试以下 `soffice` 路径：
- `/opt/homebrew/bin/soffice`
- `/Applications/LibreOffice.app/Contents/MacOS/soffice`

### 仓库结构

```text
.
├── assets/
│   └── Word转PDF加水印.icns
├── docs/
│   └── images/
│       ├── demo.gif
│       ├── hero.png
│       ├── sample-input.png
│       ├── sample-output.png
│       └── workflow.png
├── launcher.applescript
├── README.md
├── requirements.txt
├── scripts/
│   ├── Word转PDF加水印.command
│   ├── build_applet.sh
│   ├── build_release_bundle.sh
│   └── generate_demo_assets.py
└── word_pdf_watermark.py
```

### 实现说明

- `word_pdf_watermark.py`
  - 负责参数解析、文件选择、Word 转 PDF、水印叠加和结果输出
- `launcher.applescript`
  - 负责拖拽式 macOS App 的图形入口
- `scripts/build_applet.sh`
  - 编译 `.app` 并把脚本与 Python 依赖复制进 App bundle
- `scripts/build_release_bundle.sh`
  - 生成 `.zip` 发布包和 SHA256 校验文件
- `scripts/generate_demo_assets.py`
  - 生成 README 所用的封面图、流程图和 GIF 演示素材

### 已验证能力

- PDF 输入直接加水印
- 中文水印正常显示
- 输出文件落在原文件同目录
- 打包后的 App bundle 可调用随包依赖执行 Python 脚本

---

## English

### Overview

Word PDF Watermark is a lightweight macOS utility for turning Word / PDF files into watermarked PDFs.

It supports three entry points:
- CLI for automation and batch processing
- `.command` launcher for double-click local usage
- drag-and-drop `.app` for a friendlier macOS workflow

### Features

- Supported inputs: `.doc`, `.docx`, `.dot`, `.dotx`, `.rtf`, `.pdf`
- PDF inputs are watermarked directly
- Word / RTF inputs are converted through LibreOffice before watermarking
- Chinese and English watermark text are both supported
- Multiple files can be processed in one run
- Output files are written next to the source file as `*_带水印.pdf`
- Release `.app` bundles the required Python libraries (`pypdf`, `reportlab`)

### Quick start

#### Option A: Download the Release

1. Open Releases:
   https://github.com/491034170/word-pdf-watermark-macos/releases
2. Download the latest `word-pdf-watermark-macos-<version>.zip`
3. Unzip it to get `Word转PDF加水印.app`
4. Launch it directly or drag files onto the app icon

Notes:
- The release `.app` vendors Python package dependencies
- You still need `python3` available on your Mac
- LibreOffice is required only when converting Word / RTF files to PDF

#### Option B: Run from source

```bash
python3 -m pip install -r requirements.txt
python3 word_pdf_watermark.py file1.docx file2.pdf
```

### CLI usage

```bash
python3 word_pdf_watermark.py --watermark "Internal Use Only" file.docx
```

```bash
python3 word_pdf_watermark.py --no-ui --watermark "Review Copy" file.pdf
```

### Build the drag-and-drop app

```bash
chmod +x scripts/build_applet.sh
./scripts/build_applet.sh
```

Output:

```text
dist/Word转PDF加水印.app
```

### Build the release bundle

```bash
chmod +x scripts/build_release_bundle.sh
./scripts/build_release_bundle.sh v1.0.0
```

Outputs:

```text
dist/Word转PDF加水印.app
dist/word-pdf-watermark-macos-1.0.0.zip
dist/SHA256SUMS.txt
```

### Requirements

- macOS
- Python 3
- LibreOffice for Word / RTF to PDF conversion

### Project structure

```text
assets/                app icon
docs/images/           README visuals and demo GIF
launcher.applescript   app launcher source
scripts/               build and helper scripts
word_pdf_watermark.py  main conversion + watermark logic
```

### Verified

- Direct watermarking for PDF input
- Chinese watermark rendering works correctly
- Outputs are written next to the source file
- Bundled app resources can execute with vendored Python dependencies
