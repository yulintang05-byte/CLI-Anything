"""
User Profile — stores investor name, LLC, financing preferences.
Used by the Auto Offer system to personalize all offer emails.
Saved at ~/.wholesale-ai/profile.json
"""
import json
from pathlib import Path
from typing import Optional

PROFILE_DIR = Path.home() / ".wholesale-ai"
PROFILE_FILE = PROFILE_DIR / "profile.json"

DEFAULTS = {
    "name": "",
    "company": "",
    "email": "",
    "phone": "",
    "preferred_financing": "DSCR Loan",
    "purchasing_entity": "",
    "portfolio_size": 0,
    "years_experience": 1,
    "emd_amount": 1000,
    "closing_days": 30,
    "seller_credit_pct": 3,
    "bio_line": "",
    # Investor financial position — drives personalized strategy recommendations
    "credit_score": 730,
    "available_cash": 12000,
    "monthly_income": 0,       # for conventional loan qualification
    "target_markets": "Detroit MI, Birmingham AL, Memphis TN",
    "exit_strategy": "BRRRR",  # Wholesale / Flip / BRRRR / Buy & Hold
}


def load_profile() -> dict:
    PROFILE_DIR.mkdir(exist_ok=True)
    if not PROFILE_FILE.exists():
        return dict(DEFAULTS)
    try:
        saved = json.loads(PROFILE_FILE.read_text())
        return {**DEFAULTS, **saved}
    except Exception:
        return dict(DEFAULTS)


def save_profile(profile: dict):
    PROFILE_DIR.mkdir(exist_ok=True)
    PROFILE_FILE.write_text(json.dumps(profile, indent=2))


def is_profile_complete(profile: dict) -> bool:
    return bool(profile.get("name") and profile.get("company"))
