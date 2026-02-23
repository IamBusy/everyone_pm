from __future__ import annotations

import os
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class WebPage:
    url: str
    content_type: str | None
    text: str


_URL_RE = re.compile(r"https?://[^\s)\]]+")


def extract_urls(text: str) -> list[str]:
    """Extract http/https URLs from a free-form user prompt."""
    return _URL_RE.findall(text)


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Drop non-content tags.
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    # Prefer <main> if present.
    main = soup.find("main")
    root = main if main is not None else soup.body if soup.body is not None else soup

    text = root.get_text("\n", strip=True)
    # Compact excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def fetch_url(url: str, *, timeout_s: float = 20.0, max_bytes: int = 2_000_000) -> WebPage:
    """Fetch a public URL and extract readable text.

    - Supports HTML pages.
    - For PDFs, returns a short placeholder message (PDF parsing is handled elsewhere).
    """

    verify = True
    ca_bundle = os.getenv("EOPM_CA_BUNDLE")
    if ca_bundle:
        verify = ca_bundle

    with httpx.Client(
        follow_redirects=True,
        timeout=httpx.Timeout(timeout_s),
        headers={"User-Agent": "EveryonePM/0.2 (+https://local)"},
        verify=verify,
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type")
        body = resp.content[:max_bytes]

    if content_type and "pdf" in content_type.lower():
        return WebPage(url=url, content_type=content_type, text="(PDF detected; extracting text...)\n")

    # Default to HTML/text.
    encoding = resp.encoding or "utf-8"
    html = body.decode(encoding, errors="replace")
    return WebPage(url=url, content_type=content_type, text=_html_to_text(html))
