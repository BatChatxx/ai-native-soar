"""
Observable (IOC) extraction utilities.

Extract indicators of compromise (IPs, domains, URLs, file hashes) from text.
"""
import re
from typing import List, Dict

# IPv4 (simple, reasonable)
IPV4_RE = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)

# Domain (e.g. malware.example.com, but avoid matching file names like foo.txt)
DOMAIN_RE = re.compile(
    r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"(?:com|net|org|io|info|biz|co|ru|cn|xyz|top|online|site|me|dev|app)\b",
    re.IGNORECASE,
)

# URL (http/https)
URL_RE = re.compile(r"\bhttps?://[^\s\"'<>]+", re.IGNORECASE)

# MD5 (32 hex)
MD5_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")
# SHA1 (40 hex)
SHA1_RE = re.compile(r"\b[a-fA-F0-9]{40}\b")
# SHA256 (64 hex)
SHA256_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")


def extract_ip(text: str) -> List[str]:
    return list(dict.fromkeys(m.group(0) for m in IPV4_RE.finditer(text)))


def extract_domains(text: str) -> List[str]:
    # exclude domains that are part of a URL (handled separately)
    urls = URL_RE.findall(text)
    domains = []
    for m in DOMAIN_RE.finditer(text):
        d = m.group(0).lower()
        if not any(d in u for u in urls):
            domains.append(d)
    return list(dict.fromkeys(domains))


def extract_urls(text: str) -> List[str]:
    return list(dict.fromkeys(URL_RE.findall(text)))


def extract_hashes(text: str) -> List[Dict[str, str]]:
    """Return list of {type, value} for md5/sha1/sha256, longest first to dedupe."""
    result = []
    seen = set()

    for m in SHA256_RE.finditer(text):
        v = m.group(0).lower()
        if v not in seen:
            seen.add(v)
            result.append({"type": "hash_sha256", "value": v})

    for m in SHA1_RE.finditer(text):
        v = m.group(0).lower()
        if v not in seen and not any(v in s["value"] for s in result):
            seen.add(v)
            result.append({"type": "hash_sha1", "value": v})

    for m in MD5_RE.finditer(text):
        v = m.group(0).lower()
        if v not in seen and not any(v in s["value"] for s in result):
            seen.add(v)
            result.append({"type": "hash_md5", "value": v})

    return result


def extract_observables(text: str) -> List[Dict[str, str]]:
    """Extract all observable types. Returns list of {type, value}."""
    if not text:
        return []

    observables: List[Dict[str, str]] = []

    for ip in extract_ip(text):
        observables.append({"type": "ip", "value": ip})
    for domain in extract_domains(text):
        observables.append({"type": "domain", "value": domain})
    for url in extract_urls(text):
        observables.append({"type": "url", "value": url})
    for h in extract_hashes(text):
        observables.append({"type": h["type"], "value": h["value"]})

    return observables
