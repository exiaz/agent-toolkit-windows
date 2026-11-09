# Tools untuk pengembangan aplikasi dan desain

Tools berikut digunakan sebagai bagian dari lingkungan kerja toolkit. Pilih sesuai kebutuhan dan ikuti petunjuk penyedia untuk pemasangan, akun, dan izin akses. Inventaris snapshot tersedia di [manifest.json](manifest.json).

## Agent dan harness

| Tool | Kegunaan | Sumber resmi |
|---|---|---|
| Codex Desktop / CLI | Pengembangan aplikasi, pemahaman codebase, debugging, dan review | [OpenAI Codex](https://developers.openai.com/codex/) |
| Claude Code | Pengembangan aplikasi, review, UI/UX, dan teks | [Claude Code](https://code.claude.com/docs/en/overview) |
| Google Antigravity | Lingkungan pengembangan berbasis agent | [Antigravity](https://antigravity.google/) |
| TasteCode | Workspace desktop untuk provider agent dengan Design Mode | [TasteCode](https://tastecode.dev/), [source](https://github.com/Leonxlnx/tastecode) |

## Skills, desain, dan workflow

| Sumber | Fokus | Tautan |
|---|---|---|
| Awesome DESIGN.md | Referensi sistem desain dengan skill pengarah lintas agent | [VoltAgent/awesome-design-md](https://github.com/voltagent/awesome-design-md) |
| Emil Kowalski skills | Antarmuka, animasi, interaksi, dan review motion | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| Taste Skill | Arahan visual dan desain frontend | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) |
| Impeccable | Desain, audit, polish, dan aksesibilitas | [pbakaus/impeccable](https://github.com/pbakaus/impeccable), [website](https://impeccable.style/) |
| Hallmark | Desain halaman dengan arahan visual dan referensi | [Nutlope/hallmark](https://github.com/Nutlope/hallmark) |
| Hue | Sistem desain berdasarkan referensi | [dominikmartn/hue](https://github.com/dominikmartn/hue) |
| Skills / find-skills | Penemuan dan pengelolaan skills | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| Ponytail | Workflow coding, review, dan audit | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| Andrej Karpathy Skills | Panduan kerja coding agent dari proyek forrestchang | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) |

Skills kustom seperti `modern-ui-ux`, `semantic-compressor`, `shared-conversation-history` tersedia dalam payload. Pertahankan referensi dan atribusi yang tercantum pada masing-masing berkas.

## MCP, plugin, dan connector

| Tool | Kegunaan | Sumber resmi |
|---|---|---|
| Codebase Memory MCP | Analisis struktur dan hubungan dalam codebase | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) |
| REA | Inspeksi dan analisis aplikasi, binary, serta perilaku runtime | [morluto/rea](https://github.com/morluto/rea) |
| Figma Console MCP | Menghubungkan agent dengan Figma | [southleft/figma-console-mcp](https://github.com/southleft/figma-console-mcp) |
| Codex plugin for Claude Code | Integrasi Codex melalui plugin Claude Code | [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) |

Plugin dan connector penyedia dipasang lewat pengelolaan plugin native. Manifest mencakup layanan seperti Google, GitHub, Figma, Adobe, Canva, Spotify, dan tools dokumen/visual lainnya. Hak akses mengikuti akun serta izin pengguna.

- **Claude Code:** gunakan `claude plugin marketplace add OWNER/REPO`, lalu `claude plugin install NAME@MARKETPLACE --scope user`. [Dokumentasi resmi](https://code.claude.com/docs/en/discover-plugins).
- **Codex:** gunakan pengelolaan Plugins aplikasi, atau perintah `codex plugin marketplace add` dan `codex plugin add NAME@MARKETPLACE` yang tersedia pada CLI. [Dokumentasi plugin](https://developers.openai.com/plugins/build/plugins).
- **Antigravity:** gunakan halaman Plugins / Installed customizations pada aplikasi.

Untuk Figma Console, sediakan `FIGMA_ACCESS_TOKEN` melalui environment atau pengelolaan secrets native. Token dan kredensial layanan tidak disimpan dalam repo.

## Runtime dan tools pendukung

| Tool | Kegunaan | Unduhan / panduan |
|---|---|---|
| Node.js 24+ | Runtime hooks dan koordinasi | [Node.js](https://nodejs.org/en/download) |
| Python 3.11+ | Installer paket | [Python Windows](https://www.python.org/downloads/windows/) |
| Git | Pengelolaan versi source | [Git for Windows](https://gitforwindows.org/) |
| GitHub CLI | Akses dan clone repo GitHub | [GitHub CLI](https://cli.github.com/) |
| Poppler | Pembacaan dan rendering PDF | [Poppler Windows](https://github.com/oschwartz10612/poppler-windows) |
| FFmpeg | Pemrosesan audio dan video | [FFmpeg](https://ffmpeg.org/download.html) |
| Tesseract | OCR gambar dan dokumen | [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) |
| LibreOffice | Pengolahan dan konversi dokumen | [LibreOffice](https://www.libreoffice.org/download/download-libreoffice/) |
| Pandoc | Konversi format dokumen | [Pandoc](https://pandoc.org/installing.html) |
| Espanso | Ekspansi teks dan snippet | [Espanso](https://espanso.org/install/) |

Aplikasi penyedia, binary tool MCP, dan tools sistem dipasang melalui sumber masing-masing. Payload berisi customizations dan berkas pendukung terpilih; binary pemeriksa Impeccable yang menyertai skill tetap mengikuti lisensi upstream.
