"""
Phishing email analyzer.

Parses .eml files, extracts headers / routing / auth results / IOCs,
does DNS lookups (nslookup-equivalent via stdlib socket), whois (best-effort),
and scores indicators against the local threat intel feed.

VirusTotal integration is optional: if VIRUSTOTAL_API_KEY is set, real
lookups are used; otherwise the local feed provides scores.
"""
import email
import base64
import re
import socket
import json
import os
from email import policy
from email.header import decode_header
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional


# ---------- Header decoding ----------

def _decode_mime_header(value: Optional[str]) -> str:
    if not value:
        return ""
    parts = []
    for text, charset in decode_header(value):
        if isinstance(text, bytes):
            parts.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(text)
    return " ".join(parts)


def _decode_body_payload(part) -> str:
    payload = part.get_payload(decode=True)
    if payload is None:
        return ""
    charset = part.get_content_charset() or "utf-8"
    # Handle transfer encodings (base64 / quoted-printable are handled by get_payload(decode=True))
    return payload.decode(charset, errors="replace")


# ---------- Main parse ----------

def parse_eml(raw_bytes: bytes) -> Dict[str, Any]:
    """Parse a raw .eml byte string into a structured dict."""
    msg = email.message_from_bytes(raw_bytes, policy=policy.default)

    subject = _decode_mime_header(msg.get("Subject"))
    sender = _decode_mime_header(msg.get("From"))
    to = _decode_mime_header(msg.get("To"))
    cc = _decode_mime_header(msg.get("Cc"))
    date = msg.get("Date", "")
    message_id = msg.get("Message-ID", "")
    return_path = msg.get("Return-Path", "")

    # Detect plain/bodies and URLs
    text_body = ""
    html_body = ""
    urls: List[str] = []
    for part in msg.walk():
        ct = part.get_content_type()
        if ct == "text/plain":
            text_body = _decode_body_payload(part)
        elif ct == "text/html":
            html_body = _decode_body_payload(part)
        # extract URLs from both
        for body in (text_body, html_body):
            if body:
                urls.extend(re.findall(r"https?://[^\s\"'<>]+", body))

    # dedupe, keep order
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    return {
        "subject": subject,
        "sender": sender,
        "to": to,
        "cc": cc if cc else None,
        "date": date,
        "message_id": message_id,
        "return_path": return_path,
        "routing": extract_routing(msg),
        "auth_results": extract_auth_results(msg),
        "text_body": text_body[:4000],
        "html_body": html_body[:4000],
        "urls": unique_urls[:50],
        "attachments": extract_attachments(msg),
    }


def extract_routing(msg) -> List[Dict[str, str]]:
    """Extract the Received: chain (email routing path)."""
    received = msg.get_all("Received", [])
    routing = []
    for r in received:
        # parse "from X by Y" and "(IP)" patterns
        ip = None
        m = re.search(r"\[(\d+\.\d+\.\d+\.\d+)\]", r)
        if m:
            ip = m.group(1)
        from_host = None
        m2 = re.search(r"from\s+(\S+)", r)
        if m2:
            from_host = m2.group(1)
        routing.append({"raw": r.strip()[:300], "ip": ip, "from": from_host})
    return routing


def extract_auth_results(msg) -> Dict[str, Any]:
    """Extract SPF/DKIM/DMARC results from Authentication-Results / ARC headers."""
    results = {"spf": None, "dkim": None, "dmarc": None, "raw": None}

    auth = msg.get("Authentication-Results")
    if not auth:
        auth = msg.get("ARC-Authentication-Results")

    if auth:
        results["raw"] = auth.strip()
        spf = re.search(r"spf=(\w+)", auth, re.IGNORECASE)
        dkim = re.search(r"dkim=(\w+)", auth, re.IGNORECASE)
        dmarc = re.search(r"dmarc=(\w+)", auth, re.IGNORECASE)
        if spf:
            results["spf"] = spf.group(1)
        if dkim:
            results["dkim"] = dkim.group(1)
        if dmarc:
            results["dmarc"] = dmarc.group(1)

    return results


def extract_attachments(msg) -> List[Dict[str, str]]:
    attachments = []
    for part in msg.walk():
        cd = part.get("Content-Disposition")
        if cd and "attachment" in cd.lower():
            filename = part.get_filename() or "unnamed"
            attachments.append({
                "filename": filename,
                "content_type": part.get_content_type(),
            })
    return attachments


# ---------- IOC extraction ----------

def extract_indicators(parsed: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract domains, IPs, and URLs from a parsed email."""
    domains = set()
    ips = set()

    # From sender / return path / routing
    for field in (parsed.get("sender") or "", parsed.get("return_path") or ""):
        for d in re.findall(r"@([A-Za-z0-9.-]+\.[A-Za-z]{2,})", field):
            domains.add(d.lower())

    for r in parsed.get("routing", []):
        if r.get("ip"):
            ips.add(r["ip"])

    # URLs
    for u in parsed.get("urls", []):
        try:
            netloc = urlparse(u).netloc
            if netloc:
                domains.add(netloc.lower())
        except Exception:
            pass

    return {
        "domains": sorted(domains),
        "ips": sorted(ips),
        "urls": parsed.get("urls", []),
    }


# ---------- DNS lookup (nslookup-equivalent) ----------

def dns_lookup(domain: str) -> Dict[str, Any]:
    """Resolve a domain's A records and MX records using stdlib socket."""
    result = {"domain": domain, "a_records": [], "mx_records": [], "error": None}
    try:
        infos = socket.getaddrinfo(domain, None)
        a_records = sorted({info[4][0] for info in infos})
        result["a_records"] = a_records
    except Exception as e:
        result["error"] = str(e)

    # MX lookup requires raw DNS; try a basic heuristic via getaddrinfo on the domain
    # (std socket doesn't expose MX; we do a best-effort by querying a public resolver is out of scope)
    result["mx_records"] = []  # no raw MX without dnspython; noted as limitation

    return result


# ---------- WhoIs (best-effort) ----------

def whois_lookup(domain: str) -> Dict[str, Any]:
    """Best-effort whois via TCP 43 (IANA -> registrar). Returns raw text snippet."""
    # Strip subdomains to a registrable-ish domain (last two labels)
    labels = domain.split(".")
    if len(labels) >= 2:
        registrable = labels[-2] + "." + labels[-1]
    else:
        registrable = domain

    result = {"domain": domain, "registrable": registrable, "raw": None, "error": None}
    try:
        # Query IANA first to find the whois server
        s = socket.create_connection(("whois.iana.org", 43), timeout=8)
        s.sendall((registrable + "\r\n").encode())
        data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.close()
        result["raw"] = data.decode(errors="replace")[:800]
    except Exception as e:
        result["error"] = str(e)

    return result


# ---------- Local threat intel scoring ----------

def score_indicator(indicator_type: str, value: str) -> Dict[str, Any]:
    """Score an indicator against the local threat intel feed."""
    from utils.enricher import enrich_value
    return enrich_value(indicator_type, value) or {"score": 0, "reputation": "unknown"}


# ---------- Full analysis ----------

def analyze_eml(raw_bytes: bytes) -> Dict[str, Any]:
    """Run the full phishing analysis pipeline on a raw .eml file."""
    parsed = parse_eml(raw_bytes)
    indicators = extract_indicators(parsed)

    # DNS lookups on domains
    dns_results = {}
    for d in indicators["domains"][:10]:
        dns_results[d] = dns_lookup(d)

    # Score domains/IPs against local intel
    scored = []
    for d in indicators["domains"]:
        scored.append({"type": "domain", "value": d, **score_indicator("domain", d)})
    for ip in indicators["ips"]:
        scored.append({"type": "ip", "value": ip, **score_indicator("ip", ip)})

    return {
        "parsed": parsed,
        "indicators": indicators,
        "dns": dns_results,
        "scored": scored,
        "verdict": {
            "is_likely_phishing": _is_likely_phishing(parsed, scored),
        },
    }


def _is_likely_phishing(parsed: Dict, scored: List[Dict]) -> bool:
    """Heuristic: flag as likely phishing if sender domain is suspicious or auth fails."""
    sender = parsed.get("sender") or ""
    m = re.search(r"@([A-Za-z0-9.-]+)", sender)
    if m:
        sender_domain = m.group(1).lower()
        # suspicious TLDs / domains
        suspicious = [".shop", ".us", ".my.id", ".xyz", ".top", ".store", ".online"]
        if any(sender_domain.endswith(s) for s in suspicious):
            return True
    # auth failures
    auth = parsed.get("auth_results") or {}
    if auth.get("spf") == "fail" or auth.get("dkim") == "fail" or auth.get("dmarc") == "fail":
        return True
    # any malicious-scored indicator
    if any(s.get("reputation") == "malicious" for s in scored):
        return True
    return False
