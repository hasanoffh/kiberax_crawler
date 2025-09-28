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

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Interactive](#interactive)
- [Contact / Author](#contact--author)

---

## Installation

Clone the repository and enter the project folder:

```bash
git clone https://github.com/hasanoffh/kiberax_crawler.git
cd kiberax_crawler
```

Create and activate a Python virtual environment, then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

---

## Usage

### Interactive

Run the crawler in interactive mode (it will prompt for the target URL):

```bash
python3 crawler.py
# When prompted, enter the target URL, e.g. https://example.com
```

---

## Contact / Author

Project maintained by: **KiberAx / Ilgar Hasanof**

If you have questions or feature requests, please open an issue in this repository.
