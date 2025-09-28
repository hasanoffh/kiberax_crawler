#!/usr/bin/env python3
"""
kiberax_crawler - Simple async web crawler to discover exposed admin panels, backups, .git/ and .env

Usage:
    python3 crawler.py

It will ask for a target base URL (e.g. https://example.com) and scan using a compact built-in wordlist
or the file `wordlists/common.txt` if present.

Ethics: Use only on domains you own or have permission to test.
"""

import asyncio
import aiohttp
from aiohttp import ClientSession
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
import sys
import shutil
from tqdm import tqdm
import time

# -----------------------------
# KIBERAX banner (clearly reads "KIBERAX")
# -----------------------------
BANNER = r"""
K   K  I  BBBB  EEEEE RRRR  AAAAA  X   X
K  K   I  B   B E     R   R A   A   X X 
KKK    I  BBBB  EEE   RRRR  AAAAA    X  
K  K   I  B   B E     R  R  A   A   X X 
K   K  I  BBBB  EEEEE R   R A   A  X   X
"""

def center_print(s):
    cols = shutil.get_terminal_size((80, 20)).columns
    for line in s.splitlines():
        print(line.center(cols))

# Print banner centered
try:
    print("\033[36m", end="")  # cyan
    center_print(BANNER)
finally:
    print("\033[0m", end="")

# -----------------------------
# Config
# -----------------------------
DEFAULT_WORDLIST = [
    "admin/",
    "administrator/",
    "login/",
    "dashboard/",
    "admin.php",
    "login.php",
    "backup.zip",
    "backup.bak",
    ".git/",
    ".env",
    "config.php",
]

WORDLIST_PATH = os.path.join("wordlists", "common.txt")
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.txt")
MAX_CONCURRENT = 12
TIMEOUT = 10
USER_AGENT = "kiberax_crawler/1.0 (+https://kiberax.local)"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Helpers
# -----------------------------

def load_wordlist():
    if os.path.isfile(WORDLIST_PATH):
        with open(WORDLIST_PATH, "r", encoding="utf-8", errors="ignore") as f:
            entries = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            if entries:
                return entries
    return DEFAULT_WORDLIST

async def fetch_robots(base_url, session):
    try:
        robots_url = urljoin(base_url, "/robots.txt")
        async with session.get(robots_url, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                text = await resp.text()
                return parse_robots(text)
    except Exception:
        pass
    return set()

def parse_robots(text):
    """Return a set of disallowed paths from robots.txt (basic parsing)."""
    disallowed = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(":", 1)
        if len(parts) != 2:
            continue
        key, val = parts[0].strip().lower(), parts[1].strip()
        if key == "disallow" and val:
            # normalize
            if not val.startswith("/"):
                val = "/" + val
            disallowed.add(val)
    return disallowed

def is_path_allowed(path, disallowed_paths):
    # Very simple check: if any disallowed path is a prefix of the path, treat as disallowed
    for dp in disallowed_paths:
        if path.startswith(dp):
            return False
    return True

# -----------------------------
# Core scanning
# -----------------------------
async def head_or_get(session, url):
    try:
        # prefer HEAD to save bandwidth, fallback to GET if HEAD not allowed
        headers = {"User-Agent": USER_AGENT}
        async with session.head(url, timeout=TIMEOUT, allow_redirects=True) as resp:
            return resp.status, resp.headers
    except Exception:
        try:
            async with session.get(url, timeout=TIMEOUT, allow_redirects=True) as resp:
                return resp.status, resp.headers
        except Exception:
            return None, None

async def check_target(base_url, paths, disallowed_paths):
    connector = aiohttp.TCPConnector(limit_per_host=MAX_CONCURRENT)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT + 5)
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async with ClientSession(connector=connector, timeout=timeout, headers={"User-Agent": USER_AGENT}) as session:
        tasks = []
        results = []

        async def worker(path):
            # skip if robots disallowed
            parsed = urlparse(path)
            rel = parsed.path if parsed.path else "/"
            if not is_path_allowed(rel, disallowed_paths):
                return None

            target = urljoin(base_url, path)
            async with sem:
                status, headers = await head_or_get(session, target)
                if status and status < 400:
                    # small heuristics to filter trivial hits
                    content_type = headers.get("Content-Type", "") if headers else ""
                    results.append((target, status, content_type))
            return None

        for p in paths:
            tasks.append(asyncio.ensure_future(worker(p)))

        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scanning", unit="req"):
            try:
                await f
            except Exception:
                pass

        return results

# -----------------------------
# Sitemap discovery helper
# -----------------------------
async def fetch_sitemap(base_url, session):
    try:
        sitemap_url = urljoin(base_url, "/sitemap.xml")
        async with session.get(sitemap_url, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                text = await resp.text()
                return extract_urls_from_sitemap(text)
    except Exception:
        pass
    return []

def extract_urls_from_sitemap(xml_text):
    urls = []
    try:
        soup = BeautifulSoup(xml_text, "xml")
        for url in soup.find_all("loc"):
            if url and url.text:
                parsed = urlparse(url.text)
                urls.append(parsed.path)
    except Exception:
        pass
    return urls

# -----------------------------
# Main
# -----------------------------

def normalize_base(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    if not url.endswith("/"):
        url = url + "/"
    return url

async def main():
    base = input("Target URL (e.g. https://example.com): ").strip()
    if not base:
        print("No target provided, exiting.")
        return
    base = normalize_base(base)

    # prepare wordlist
    words = load_wordlist()

    # also try to fetch sitemap and add discovered paths
    timeout = aiohttp.ClientTimeout(total=TIMEOUT + 5)
    async with ClientSession(timeout=timeout, headers={"User-Agent": USER_AGENT}) as session:
        disallowed = await fetch_robots(base, session)
        sitemap_paths = await fetch_sitemap(base, session)

    # combine and dedupe
    combined = []
    for w in sitemap_paths + words:
        # ensure entries are relative paths or filenames
        w = w.strip()
        if not w:
            continue
        if w.startswith("http://") or w.startswith("https://"):
            # convert to relative path
            p = urlparse(w).path
            if p:
                w = p
        combined.append(w)
    # dedupe while preserving order
    seen = set()
    final_paths = []
    for c in combined:
        if c not in seen:
            seen.add(c)
            final_paths.append(c)

    print(f"Scanning {len(final_paths)} paths (robots disallowed: {len(disallowed)})...")

    results = await check_target(base, final_paths, disallowed)

    if results:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
            for target, status, ctype in results:
                line = f"{target}\t{status}\t{ctype}\n"
                fout.write(line)
        print(f"Found {len(results)} items. Results saved to {OUTPUT_FILE}")
    else:
        print("No interesting items found.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled by user.")
