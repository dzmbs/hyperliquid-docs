#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests>=2.32"]
# ///
"""
Hyperliquid documentation fetcher.

Parses Gitbook sitemaps, fetches markdown via the .md endpoint,
and saves files preserving the original directory hierarchy.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

Manifest = dict[str, Any]

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://hyperliquid.gitbook.io/hyperliquid-docs"

# Gitbook exposes a sitemap index that references per-section sitemaps.
SITEMAP_INDEX_URL = f"{BASE_URL}/sitemap.xml"

MANIFEST_FILE = "docs_manifest.json"

HEADERS: dict[str, str] = {
    "User-Agent": "Hyperliquid-Docs-Fetcher/1.0",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}

MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_RETRY_DELAY = 30
RATE_LIMIT_DELAY = 0.5

# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------


def load_manifest(docs_dir: Path) -> Manifest:
    manifest_path = docs_dir / MANIFEST_FILE
    if manifest_path.exists():
        try:
            manifest: Manifest = json.loads(manifest_path.read_text())
            if "files" not in manifest:
                manifest["files"] = {}
            return manifest
        except Exception as e:
            logger.warning(f"Failed to load manifest: {e}")
    return {"files": {}, "last_updated": None}


def save_manifest(docs_dir: Path, manifest: Manifest) -> None:
    manifest_path = docs_dir / MANIFEST_FILE
    manifest["last_updated"] = datetime.now().isoformat()

    github_repo = os.environ.get("GITHUB_REPOSITORY", "")
    github_ref = os.environ.get("GITHUB_REF_NAME", "main")

    if github_repo:
        manifest["base_url"] = (
            f"https://raw.githubusercontent.com/{github_repo}/{github_ref}/docs/"
        )
        manifest["github_repository"] = github_repo
        manifest["github_ref"] = github_ref

    manifest["source"] = BASE_URL
    manifest["description"] = (
        "Hyperliquid documentation manifest. Automatically generated — do not edit by hand."
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


# ---------------------------------------------------------------------------
# URL → file-path conversion
# ---------------------------------------------------------------------------

# The three Gitbook "spaces" and the prefix we strip from each URL path.
SPACE_PREFIXES = [
    "/hyperliquid-docs/builder-tools",
    "/hyperliquid-docs/support",
    "/hyperliquid-docs",
]


def url_to_filepath(url: str) -> str:
    """Convert a full Gitbook URL to a relative file path under docs/.

    Examples
    --------
    https://…/hyperliquid-docs/trading/fees  →  trading/fees.md
    https://…/hyperliquid-docs/builder-tools/hyperevm-tools  →  builder-tools/hyperevm-tools.md
    https://…/hyperliquid-docs/support/faq/connectivity-issues
        →  support/faq/connectivity-issues.md
    https://…/hyperliquid-docs  →  README.md  (root page)
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")

    for prefix in SPACE_PREFIXES:
        if path == prefix:
            remainder = ""
            space = (
                prefix.split("/hyperliquid-docs/")[-1] if "/hyperliquid-docs/" in prefix else ""
            )
            break
        if path.startswith(prefix + "/"):
            remainder = path[len(prefix) + 1 :]
            space = (
                prefix.split("/hyperliquid-docs/")[-1] if "/hyperliquid-docs/" in prefix else ""
            )
            break
    else:
        remainder = path.lstrip("/")
        space = ""

    if not remainder and not space:
        return "README.md"
    if not remainder and space:
        return f"{space}/README.md"

    full = f"{space}/{remainder}" if space else remainder
    return f"{full}.md"


# ---------------------------------------------------------------------------
# Sitemap discovery
# ---------------------------------------------------------------------------


def _parse_xml(content: bytes) -> ET.Element:
    """Parse XML with security protections where available."""
    try:
        parser = ET.XMLParser(  # type: ignore[call-arg]  # security kwargs not in all stubs
            forbid_dtd=True,
            forbid_entities=True,
            forbid_external=True,
        )
        return ET.fromstring(content, parser=parser)
    except TypeError:
        # Older Python versions don't support these kwargs
        return ET.fromstring(content)


def fetch_sitemap_urls(session: requests.Session, sitemap_url: str) -> list[str]:
    """Fetch a sitemap (or sitemap index) and return all page URLs."""
    resp = session.get(sitemap_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    root = _parse_xml(resp.content)
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # Check if this is a sitemap index (contains <sitemap> elements)
    sub_sitemaps = [loc.text for loc in root.findall(".//ns:sitemap/ns:loc", ns) if loc.text]

    if sub_sitemaps:
        all_urls: list[str] = []
        for sub_url in sub_sitemaps:
            logger.info(f"  Fetching sub-sitemap: {sub_url}")
            try:
                all_urls.extend(fetch_sitemap_urls(session, sub_url))
                time.sleep(RATE_LIMIT_DELAY)
            except Exception as e:
                logger.warning(f"  Failed to fetch sub-sitemap {sub_url}: {e}")
        return all_urls

    # Regular sitemap — extract <url><loc> entries
    urls = [loc.text for loc in root.findall(".//ns:url/ns:loc", ns) if loc.text]

    # Fallback without namespace
    if not urls:
        urls = [loc.text for loc in root.findall(".//loc") if loc.text]

    return urls


# Gitbook space root pages have their .md at a different slug than the page URL.
SPACE_ROOT_MD_OVERRIDES: dict[str, str] = {
    "/hyperliquid-docs": f"{BASE_URL}/about-hyperliquid.md",
    "/hyperliquid-docs/builder-tools": f"{BASE_URL}/builder-tools/read-me-builder-tools.md",
    "/hyperliquid-docs/support": f"{BASE_URL}/support/read-me-support-guide.md",
}


def discover_pages(session: requests.Session) -> list[str]:
    """Return all Hyperliquid doc page URLs from the sitemap index."""
    logger.info(f"Discovering pages from {SITEMAP_INDEX_URL}")
    urls = fetch_sitemap_urls(session, SITEMAP_INDEX_URL)
    logger.info(f"Discovered {len(urls)} pages")
    return sorted(set(urls))


# ---------------------------------------------------------------------------
# Markdown fetching
# ---------------------------------------------------------------------------


def fetch_markdown(url: str, session: requests.Session) -> str:
    """Fetch markdown content by appending .md to the page URL."""
    parsed_path = urlparse(url).path.rstrip("/")
    md_url = SPACE_ROOT_MD_OVERRIDES.get(parsed_path, url.rstrip("/") + ".md")

    for attempt in range(MAX_RETRIES):
        try:
            resp = session.get(md_url, headers=HEADERS, timeout=30, allow_redirects=True)

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 60))
                logger.warning(f"Rate-limited, waiting {wait}s …")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            content = resp.text

            if content.startswith("<!DOCTYPE") or "<html" in content[:200]:
                raise ValueError("Received HTML instead of markdown")
            if len(content.strip()) < 20:
                raise ValueError(f"Content too short ({len(content)} bytes)")

            return content

        except requests.exceptions.RequestException as e:
            logger.warning(f"  Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                delay = min(RETRY_DELAY * (2**attempt), MAX_RETRY_DELAY)
                time.sleep(delay * random.uniform(0.5, 1.0))
            else:
                raise
        except ValueError:
            raise

    msg = f"Failed to fetch {md_url} after {MAX_RETRIES} attempts"
    raise RuntimeError(msg)


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def save_file(docs_dir: Path, rel_path: str, content: str) -> str:
    """Write content to docs_dir/rel_path and return its sha256."""
    dest = docs_dir / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return hashlib.sha256(content.encode()).hexdigest()


def cleanup_old_files(
    docs_dir: Path,
    current_files: set[str],
    manifest: Manifest,
) -> None:
    """Remove files that were previously fetched but no longer exist in the sitemap."""
    previous = set(manifest.get("files", {}).keys())
    for rel_path in previous - current_files:
        fp = docs_dir / rel_path
        if fp.exists():
            logger.info(f"  Removing obsolete: {rel_path}")
            fp.unlink()
            for parent in fp.parents:
                if parent == docs_dir:
                    break
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    start = datetime.now()
    logger.info("Starting Hyperliquid documentation fetch")

    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)

    manifest = load_manifest(docs_dir)
    new_manifest: Manifest = {"files": {}}

    successful = 0
    failed = 0
    failed_pages: list[str] = []
    fetched_files: set[str] = set()

    with requests.Session() as session:
        pages = discover_pages(session)
        if not pages:
            logger.error("No pages discovered!")
            sys.exit(1)

        for i, url in enumerate(pages, 1):
            rel_path = url_to_filepath(url)
            logger.info(f"[{i}/{len(pages)}] {url}  →  {rel_path}")

            try:
                content = fetch_markdown(url, session)
                old_hash: str = manifest.get("files", {}).get(rel_path, {}).get("hash", "")
                new_hash = hashlib.sha256(content.encode()).hexdigest()

                if new_hash != old_hash:
                    save_file(docs_dir, rel_path, content)
                    logger.info(f"  Updated: {rel_path}")
                    last_updated = datetime.now().isoformat()
                else:
                    logger.info(f"  Unchanged: {rel_path}")
                    last_updated = str(
                        manifest.get("files", {})
                        .get(rel_path, {})
                        .get("last_updated", datetime.now().isoformat())
                    )

                new_manifest["files"][rel_path] = {
                    "source_url": url,
                    "md_url": url.rstrip("/") + ".md",
                    "hash": new_hash,
                    "last_updated": last_updated,
                }
                fetched_files.add(rel_path)
                successful += 1

                if i < len(pages):
                    time.sleep(RATE_LIMIT_DELAY)

            except Exception as e:
                logger.error(f"  Failed: {e}")
                failed += 1
                failed_pages.append(url)

    cleanup_old_files(docs_dir, fetched_files, manifest)

    new_manifest["fetch_metadata"] = {
        "completed_at": datetime.now().isoformat(),
        "duration_seconds": (datetime.now() - start).total_seconds(),
        "pages_discovered": len(pages),
        "pages_fetched": successful,
        "pages_failed": failed,
        "failed_pages": failed_pages,
    }

    save_manifest(docs_dir, new_manifest)

    logger.info("=" * 50)
    logger.info(f"Done in {datetime.now() - start}")
    logger.info(f"Fetched: {successful}/{len(pages)}  |  Failed: {failed}")

    if failed_pages:
        logger.warning("Failed pages:")
        for p in failed_pages:
            logger.warning(f"  - {p}")
        if successful == 0:
            sys.exit(1)
    else:
        logger.info("All pages fetched successfully!")


if __name__ == "__main__":
    main()
