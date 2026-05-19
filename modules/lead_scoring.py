"""
lead_scoring.py
---------------
Computes a numeric quality score (0–100) for a captured lead and
classifies it as Hot / Warm / Cold.

Scoring breakdown (total possible = 100):
  ┌──────────────────────────────────────┬────────┐
  │ Signal                               │ Points │
  ├──────────────────────────────────────┼────────┤
  │ Phone number provided                │  +15   │
  │ Message / details provided           │  +15   │
  │ Interest: AI/ML Course               │  +20   │
  │ Interest: Internship Program         │  +15   │
  │ Interest: Consultation               │  +25   │
  │ Interest: Other                      │  +10   │
  │ Professional email domain            │  +15   │
  │ Long message (>80 chars)             │  +10   │
  └──────────────────────────────────────┴────────┘
"""

# ── Domain blocklist (free / disposable providers) ────────────────────────────
_FREE_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "live.com", "icloud.com", "aol.com", "protonmail.com",
    "temp-mail.org", "guerrillamail.com", "mailinator.com",
}

# ── Points per interest ───────────────────────────────────────────────────────
_INTEREST_POINTS: dict[str, int] = {
    "Consultation":       25,
    "AI/ML Course":       20,
    "Internship Program": 15,
    "Other":              10,
}


def compute_score(lead_data: dict) -> int:
    """
    Calculate a lead quality score (0–100).

    Args:
        lead_data: Dict with keys: name, email, phone, interest, message.

    Returns:
        Integer score clamped to [0, 100].
    """
    score = 0

    # Phone provided (+15)
    phone = (lead_data.get("phone") or "").strip()
    if phone:
        score += 15

    # Message provided (+15, bonus +10 if long)
    message = (lead_data.get("message") or "").strip()
    if message:
        score += 15
        if len(message) > 80:
            score += 10

    # Interest bucket (+10 to +25)
    interest = (lead_data.get("interest") or "").strip()
    score += _INTEREST_POINTS.get(interest, 0)

    # Professional email domain (+15 if NOT a free provider)
    email = (lead_data.get("email") or "").strip().lower()
    domain = email.split("@")[-1] if "@" in email else ""
    if domain and domain not in _FREE_DOMAINS:
        score += 15

    return min(score, 100)


def classify_lead(score: int) -> str:
    """
    Map a numeric score to a human-readable category.

    Args:
        score: Integer 0–100.

    Returns:
        One of 'Hot 🔥', 'Warm 🌤️', or 'Cold ❄️'.
    """
    if score >= 70:
        return "Hot 🔥"
    elif score >= 40:
        return "Warm 🌤️"
    return "Cold ❄️"
