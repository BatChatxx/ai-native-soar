"""
LLM client for the local Qwen 3.5 model (OpenAI-compatible API).

Handles the reasoning-model response format (content + reasoning_content).
"""
import json
import os
import urllib.request
from typing import Optional, Dict, Any


# In-memory cache of the active LLM profile (refreshed on settings changes).
_active_profile_cache: Optional[Dict[str, Any]] = None


def _load_active_profile() -> Optional[Dict[str, Any]]:
    """Load the active LLM profile from the database (lazy import to avoid cycles)."""
    try:
        from models.models import LLMProfile
        from models.database import get_session_local

        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            p = db.query(LLMProfile).filter(LLMProfile.is_active == True).first()  # noqa: E712
            if p:
                return {
                    "api_key": p.api_key or "",
                    "base_url": p.base_url,
                    "model": p.model,
                    "context_window": p.context_window,
                }
            return None
        finally:
            db.close()
    except Exception:
        return None


def get_active_profile_id(db=None) -> Optional[int]:
    """Return the id of the active LLM profile, or None."""
    try:
        from models.models import LLMProfile
        if db is not None:
            p = db.query(LLMProfile).filter(LLMProfile.is_active == True).first()  # noqa: E712
            return p.id if p else None
        SessionLocal = __import__("models.database", fromlist=["get_session_local"]).get_session_local()
        d = SessionLocal()
        try:
            p = d.query(LLMProfile).filter(LLMProfile.is_active == True).first()  # noqa: E712
            return p.id if p else None
        finally:
            d.close()
    except Exception:
        return None


def _config() -> Dict[str, str]:
    """Resolve LLM config: active DB profile first, then env vars fallback."""
    global _active_profile_cache
    if _active_profile_cache is None:
        _active_profile_cache = _load_active_profile()

    profile = _active_profile_cache
    if profile:
        return {
            "api_key": profile.get("api_key") or os.getenv("LLM_API_KEY", ""),
            "base_url": profile.get("base_url") or os.getenv("LLM_BASE_URL", "http://host.docker.internal:56987"),
            "model": profile.get("model") or os.getenv("LLM_MODEL", "qwen/qwen3.5-9b"),
        }

    return {
        "api_key": os.getenv("LLM_API_KEY", ""),
        "base_url": os.getenv("LLM_BASE_URL", "http://host.docker.internal:56987"),
        "model": os.getenv("LLM_MODEL", "qwen/qwen3.5-9b"),
    }


def reset_profile_cache():
    """Clear the cached profile (called after settings change)."""
    global _active_profile_cache
    _active_profile_cache = None


def _api_url(base_url: str, path: str) -> str:
    """Build an API URL, normalizing a base_url that may or may not include /v1."""
    base = base_url.rstrip('/')
    if base.endswith('/v1'):
        return f"{base}{path}"
    return f"{base}/v1{path}"


def test_llm_connection() -> tuple:
    """Test LLM connectivity. Returns (ok: bool, message: str)."""
    cfg = _config()
    url = _api_url(cfg['base_url'], '/models')
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {cfg['api_key']}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        ids = [m.get("id", "") for m in data.get("data", [])]
        return True, f"Connected, {len(ids)} model(s): {', '.join(ids[:3])}"
    except Exception as e:
        return False, str(e)


def chat(prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> Optional[str]:
    """
    Call the local LLM with a single user prompt.
    Returns the assistant's final content (not reasoning).
    """
    # Final safety net: ensure prompt + answer fits the context window.
    # (The ask_* functions already trim, but this guards unexpected callers.)
    available = _context_window() - max_tokens
    if estimate_tokens(prompt) > available:
        prompt = truncate_text(prompt, available, suffix="\n…[context truncated to fit window]")
    cfg = _config()
    url = _api_url(cfg['base_url'], '/chat/completions')

    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return f"[LLM error: {e}]"

    try:
        message = data["choices"][0]["message"]
        content = message.get("content") or ""
        reasoning = message.get("reasoning_content") or ""
        finish = data["choices"][0].get("finish_reason")

        if content.strip():
            return content.strip()

        # Reasoning model produced no final content (thinking consumed max_tokens).
        # Retry once with a larger budget, capped by the context window.
        if finish == "length":
            prompt_tokens = estimate_tokens(prompt)
            max_allowed = max(1, _context_window() - prompt_tokens - 256)
            if max_tokens < max_allowed:
                return chat(prompt, max_tokens=max_allowed, temperature=temperature)

        # Still empty: return the tail of the reasoning (closest to a conclusion).
        if reasoning.strip():
            return reasoning[-2000:].strip() or "[Answer was consumed by reasoning; reasoning truncated]"

        return "[No answer produced]"
    except (KeyError, IndexError):
        return "[LLM returned unexpected format]"


def analyze_incident(incident: Dict[str, Any]) -> str:
    """Generate an AI analysis summary for an incident."""
    observables = incident.get("observables") or []
    obs_str = ", ".join(
        f"{o.get('observable_type')}={o.get('observable_value')}"
        + (f" (score {o.get('malicious_score')}, {o.get('reputation')})" if o.get('reputation') else "")
        for o in observables
    ) or "none"

    prompt = f"""You are a cybersecurity analyst assistant. Analyze the following security incident and provide a concise summary with:
1. What happened (1-2 sentences)
2. Severity assessment
3. Recommended immediate actions (bullet points, max 3)
4. Key indicators of compromise (IOCs) to focus on

INCIDENT:
- Number: {incident.get('number')}
- Title: {incident.get('title')}
- Severity: {incident.get('severity')}
- Status: {incident.get('status')}
- Source: {incident.get('source_type')}
- Description: {incident.get('description') or 'N/A'}
- Observables: {obs_str}

Keep the total response under 200 words."""

    return chat(prompt) or "[No analysis available]"


def analyze_alert(alert: Dict[str, Any]) -> str:
    """Generate an AI analysis summary for an alert."""
    observables = alert.get("observables") or []
    obs_str = ", ".join(
        f"{o.get('observable_type')}={o.get('observable_value')}"
        + (f" (score {o.get('malicious_score')}, {o.get('reputation')})" if o.get('reputation') else "")
        for o in observables
    ) or "none"

    prompt = f"""You are a cybersecurity analyst assistant. Analyze the following security alert and provide a concise triage summary with:
1. What triggered the alert (1-2 sentences)
2. Likelihood this is a true positive (high/medium/low)
3. Recommended triage steps (bullet points, max 3)
4. Whether it should be promoted to an incident

ALERT:
- Number: {alert.get('number')}
- Title: {alert.get('title')}
- Severity: {alert.get('severity')}
- Status: {alert.get('status')}
- Source: {alert.get('source_type')}
- Description: {alert.get('description') or 'N/A'}
- Observables: {obs_str}

Keep the total response under 200 words."""

    return chat(prompt) or "[No analysis available]"


def _render_observables(observables: list) -> str:
    if not observables:
        return "(none)"
    parts = []
    for o in observables:
        base = f"{o.get('observable_type')}={o.get('observable_value')}"
        if o.get('reputation'):
            base += f" [score {o.get('malicious_score')}, {o.get('reputation')}]"
        if o.get('file_name'):
            base += f" (file: {o.get('file_name')})"
        parts.append(base)
    return "\n".join(f"- {p}" for p in parts)


def _render_events(events: list) -> str:
    if not events:
        return "(none)"
    parts = []
    for e in events:
        line = e.get("title") or ""
        if e.get("description"):
            line += f": {e.get('description')}"
        parts.append(line)
    return "\n".join(f"- {p}" for p in parts)


def _render_comments(comments: list) -> str:
    if not comments:
        return "(none)"
    return "\n".join(f"- {c.get('content')}" for c in comments)


# ============= Token budget management =============
# The local model has a ~40k context window. We reserve headroom for the
# answer (max_tokens) and the prompt template, then fit the evidence within
# the remaining budget by progressively truncating lower-priority sections.

# Default context window (characters-based rough estimate). Can be overridden
# via LLM_CONTEXT_WINDOW env var.
def _context_window() -> int:
    # Prefer the active profile's context window, fallback to env var / default.
    profile = _load_active_profile()
    if profile and profile.get("context_window"):
        return int(profile["context_window"])
    return int(os.getenv("LLM_CONTEXT_WINDOW", "40000"))

# Reserve this many tokens for the model's answer.
# Qwen 3.5 9B is a reasoning model that spends many tokens on internal
# 'thinking' before emitting content, so reserve generously.
ANSWER_RESERVE = 16000


def estimate_tokens(text: str) -> int:
    """Rough token estimate without an external tokenizer.

    Heuristic: CJK characters ≈ 1 token each; other text ≈ 4 chars/token.
    Good enough for budget gating (we only need to avoid blowing the window).
    """
    if not text:
        return 0
    cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other = len(text) - cjk
    return cjk + (other + 3) // 4


def truncate_text(text: str, max_tokens: int, suffix: str = "\n…[truncated]") -> str:
    """Truncate text to fit within max_tokens (rough estimate)."""
    if estimate_tokens(text) <= max_tokens:
        return text
    # Binary-search-ish: cut by character ratio
    ratio = max_tokens / max(1, estimate_tokens(text))
    cut = int(len(text) * ratio * 0.9)
    if cut <= 0:
        return ""
    return text[:cut] + suffix


def _budget_context_window() -> int:
    """Context tokens available for the prompt (window minus answer reserve)."""
    return _context_window() - ANSWER_RESERVE


def ask_incident(incident: Dict[str, Any], question: str) -> str:
    """Deep-dive analysis with token-budget-aware context trimming."""
    budget = _budget_context_window()

    description = incident.get('description') or 'N/A'
    observables = _render_observables(incident.get("observables") or [])
    events = _render_events(incident.get("events") or [])
    comments = _render_comments(incident.get("comments") or [])

    prompt = f"""You are an expert cybersecurity analyst assistant. Answer the analyst's question based on the FULL context of the incident below. Be specific, reference concrete IOCs and techniques, and provide actionable reasoning.

=== INCIDENT CONTEXT ===
Number: {incident.get('number')}
Title: {incident.get('title')}
Severity: {incident.get('severity')}
Status: {incident.get('status')}
Priority: {incident.get('priority')}
Source: {incident.get('source_type')}

Description:
{truncate_text(description, budget)}

Observables (IOCs):
{truncate_text(observables, budget)}

Attack chain / timeline:
{truncate_text(events, budget)}

Analyst comments:
{truncate_text(comments, budget // 2)}

=== ANALYST QUESTION ===
{question}

Provide a detailed, well-structured answer. Use bullet points where appropriate. Output ONLY the final answer directly — do not include step-by-step thinking."""

    return chat(prompt, max_tokens=ANSWER_RESERVE) or "[No answer available]"


def ask_alert(alert: Dict[str, Any], question: str) -> str:
    """Deep-dive analysis with token-budget-aware context trimming."""
    budget = _budget_context_window()

    description = alert.get('description') or 'N/A'
    observables = _render_observables(alert.get("observables") or [])

    prompt = f"""You are an expert cybersecurity analyst assistant. Answer the analyst's question based on the FULL context of the alert below. Be specific, reference concrete IOCs, and provide actionable reasoning.

=== ALERT CONTEXT ===
Number: {alert.get('number')}
Title: {alert.get('title')}
Severity: {alert.get('severity')}
Status: {alert.get('status')}
Source: {alert.get('source_type')}

Description:
{truncate_text(description, budget)}

Observables (IOCs):
{truncate_text(observables, budget)}

=== ANALYST QUESTION ===
{question}

Provide a detailed, well-structured answer. Use bullet points where appropriate. Output ONLY the final answer directly — do not include step-by-step thinking."""

    return chat(prompt, max_tokens=ANSWER_RESERVE) or "[No answer available]"
