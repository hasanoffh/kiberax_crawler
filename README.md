# kiberax_crawler

**Simple async web crawler** — a lightweight tool designed to detect exposed/admin panels, backup files, and other common sensitive files.  
The tool is written in Python and performs parallel scanning using asynchronous requests (aiohttp).

> **Warning — Ethics:** This tool should only be used on domains you own or have explicit written permission for. Unauthorized scanning is illegal and unethical.

---

## Features

- Asynchronous requests (aiohttp) for fast parallel scanning.
- Wordlist-based scanning (wordlists/common.txt).
- Respects robots.txt.
- Extracts paths from sitemap.xml.
- Special heuristics for .env, .git/, and backup files.
- Results are saved in the output/ folder.

---

## Requirements

- Python 3.8 or higher
- Recommended: virtual environment
- Required packages (listed in requirements.txt):
  - aiohttp
  - beautifulsoup4
  - tqdm
  - requests

To install packages on Linux:
\`\`\`bash
python3 -m pip install -r requirements.txt
\`\`\`

---
## English (short overview)

# kiberax_crawler

**Simple async web crawler** — a lightweight tool designed to detect exposed/admin panels, backup files, and other common sensitive files.  
The tool is written in Python and performs parallel scanning using asynchronous requests (aiohttp).

> **Warning — Ethics:** This tool should only be used on domains you own or have explicit written permission for. Unauthorized scanning is illegal and unethical.

---

## Features

- Asynchronous requests (aiohttp) for fast parallel scanning.
- Wordlist-based scanning (wordlists/common.txt).
- Respects robots.txt.
- Extracts paths from sitemap.xml.
- Special heuristics for .env, .git/, and backup files.
- Results are saved in the output/ folder.

---

## Requirements

- Python 3.8 or higher
- Recommended: virtual environment
- Required packages (listed in requirements.txt):
  - aiohttp
  - beautifulsoup4
  - tqdm
  - requests

To install packages on Linux:
\`\`\`bash
python3 -m pip install -r requirements.txt
\`\`\`
