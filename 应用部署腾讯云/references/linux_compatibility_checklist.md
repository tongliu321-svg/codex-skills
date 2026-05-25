# Linux 兼容改造检查清单

部署前先检查：

- 是否调用 `textutil`
- 是否编译或运行 Swift 二进制
- 是否依赖 `PDFKit` / `Vision` / `AppKit` / `AVFoundation`
- 是否使用本地桌面路径或 `.app`
- 是否硬编码 `127.0.0.1`
- 是否前端依赖 `crypto.subtle`
- 是否只适配 macOS shell 语法

如果命中：

- `textutil` -> `libreoffice --headless` / `antiword`
- `PDFKit` -> `pdftotext`
- `Vision OCR` -> `tesseract`
- `AVFoundation` -> `ffmpeg`
- `zsh` 专用写法 -> `bash`
- `crypto.subtle` -> 降级 hash 方案
