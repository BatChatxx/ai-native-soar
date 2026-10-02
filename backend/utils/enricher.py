"""
Observable enrichment.

Looks up observables against a local threat-intel feed to assign a
malicious score and reputation. In production this would call external
APIs (VirusTotal, AbuseIPDB, etc.).
"""
import json
import os
from typing import Optional, Dict, Any

_INTEL = None


def _load_intel() -> Dict[str, Any]:
    global _INTEL
    if _INTEL is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "threat_intel.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                _INTEL = json.load(f)
        except Exception:
            _INTEL = {"ips": {}, "domains": {}, "hashes": {}, "urls": {}}
    return _INTEL


def _section_for_type(observable_type: str) -> str:
    if observable_type == "ip":
        return "ips"
    if observable_type == "domain":
        return "domains"
    if observable_type == "url":
        return "urls"
    if observable_type in ("hash_md5", "hash_sha1", "hash_sha256"):
        return "hashes"
    return observable_type


def enrich_value(observable_type: str, value: str) -> Optional[Dict[str, Any]]:
    """Return enrichment result for a single observable value, or None if unknown."""
    intel = _load_intel()
    section = _section_for_type(observable_type)
    lookup = intel.get(section, {})

    # normalize case for domains/urls, lowercase for hashes
    key = value.lower() if observable_type in ("domain", "url", "hash_md5", "hash_sha1", "hash_sha256") else value

    entry = lookup.get(key)
    if entry:
        return {
            "score": entry.get("score", 0),
            "reputation": entry.get("reputation", "unknown"),
            "tags": entry.get("tags", []),
            "source": entry.get("source", "local-feed"),
        }

    # Not in feed → unknown reputation
    return {
        "score": 0,
        "reputation": "unknown",
        "tags": [],
        "source": "local-feed",
    }
