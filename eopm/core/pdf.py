from __future__ import annotations

import io
import os

import httpx


def fetch_pdf_text(url: str, *, timeout_s: float = 30.0, max_bytes: int = 8_000_000) -> str:
    """Fetch a PDF and extract plain text.

    Uses PyMuPDF (fitz). Kept in a separate module so the dependency is explicit.
    """

    import fitz  # PyMuPDF

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
        data = resp.content[:max_bytes]

    doc = fitz.open(stream=io.BytesIO(data), filetype="pdf")
    parts: list[str] = []
    for page in doc:
        parts.append(page.get_text("text"))
    return "\n".join(parts).strip()
