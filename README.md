# Word PDF Watermark (macOS)

一个面向 macOS 的小工具：
- 支持把 Word 文档转换成 PDF
- 支持给 PDF 叠加中文或英文文字水印
- 支持命令行、`.command` 启动器、AppleScript App 三种使用方式
- 处理完成后会在原文件旁边生成 `*_带水印.pdf`

这个仓库保留的是“可维护的源码和构建方式”，不直接提交编译后的 `.app` 成品，方便二次修改、协作和复用。

## 支持格式

输入文件格式：
- `.doc`
- `.docx`
- `.dot`
- `.dotx`
- `.rtf`
- `.pdf`

说明：
- 如果输入本身就是 PDF，会直接加水印
- 如果输入是 Word/RTF，会先调用 LibreOffice 转成 PDF，再叠加水印

## 运行环境

- macOS
- Python 3
- LibreOffice（处理 Word/RTF 转 PDF 时需要）

脚本会自动尝试以下 `soffice` 路径：
- `/opt/homebrew/bin/soffice`
- `/Applications/LibreOffice.app/Contents/MacOS/soffice`

## 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

## 命令行使用

```bash
python3 word_pdf_watermark.py 文件1.docx 文件2.pdf
```

直接指定水印文字：

```bash
python3 word_pdf_watermark.py --watermark "仅供内部使用" 文件.docx
```

无图形界面模式（适合被外部启动器调用）：

```bash
python3 word_pdf_watermark.py --no-ui --watermark "项目资料" 文件.pdf
```

## 双击启动 `.command`

仓库内置了：

```text
scripts/Word转PDF加水印.command
```

它会自动定位仓库根目录下的 `word_pdf_watermark.py`，不再依赖写死的绝对路径。

## 构建拖拽式 `.app`

先执行：

```bash
chmod +x scripts/build_applet.sh
./scripts/build_applet.sh
```

执行后会生成：

```text
dist/Word转PDF加水印.app
```

你可以把文档直接拖到这个 App 上处理，也可以双击打开后选择文件。

## 项目结构

```text
.
├── assets/
│   └── Word转PDF加水印.icns
├── launcher.applescript
├── README.md
├── requirements.txt
├── scripts/
│   ├── build_applet.sh
│   └── Word转PDF加水印.command
└── word_pdf_watermark.py
```

## 实现说明

- `word_pdf_watermark.py`
  - 负责参数解析、文件选择、Word 转 PDF、水印生成和结果输出
- `launcher.applescript`
  - 用于生成可拖拽的 macOS App 启动器
- `scripts/Word转PDF加水印.command`
  - 方便本地双击调用 Python 脚本
- `assets/Word转PDF加水印.icns`
  - App 图标资源

## 依赖库

- `pypdf`
- `reportlab`

## 已验证能力

- PDF 输入直接加水印
- 中文水印正常显示
- 输出文件落在原文件同目录

如果你想继续扩展，这个脚本也很适合再加：
- 自定义水印颜色 / 透明度 / 角度
- 批量输出到指定目录
- GUI 打包成更完整的 macOS 小应用
