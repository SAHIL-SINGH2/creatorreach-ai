from __future__ import annotations
import pandas as pd
from .config import SETTINGS


def classify(df: pd.DataFrame, target_niche: str | None = None, require_email: bool = True,
             min_engagement: float | None = None) -> pd.DataFrame:
    target_niche = target_niche or SETTINGS.target_niche
    min_engagement = SETTINGS.min_engagement if min_engagement is None else min_engagement
    out = df.copy()
    reasons = []
    passed = []
    for _, r in out.iterrows():
        checks = []
        if not bool(r.get("micro_influencer", False)):
            checks.append(f"followers outside {SETTINGS.min_followers:,}-{SETTINGS.max_followers:,}")
        if target_niche and str(r.get("niche", "")).lower() != target_niche.lower():
            checks.append(f"niche is {r.get('niche', 'Unknown')}, target is {target_niche}")
        if require_email and not bool(r.get("email_available", False)):
            checks.append("contact email not found")
        er = r.get("engagement_rate_pct")
        if pd.notna(er) and float(er) < min_engagement:
            checks.append(f"measured engagement {float(er):.2f}% < {min_engagement:.2f}%")
        # Missing ER is explicitly treated as unknown, never fabricated or silently converted.
        passed.append(len(checks) == 0)
        reasons.append("PASS" if not checks else "; ".join(checks))
    out["filter_status"] = ["Passed" if x else "Failed" for x in passed]
    out["filter_reason"] = reasons
    return out
