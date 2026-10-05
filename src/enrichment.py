from __future__ import annotations
import re
import pandas as pd
from .config import SETTINGS

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_email(value) -> str:
    if pd.isna(value) or not str(value).strip() or str(value).strip().lower() in {"nan", "none", "not found", "not_found"}:
        return "Not Found"
    value = str(value).strip()
    return value if EMAIL_RE.match(value) else "Not Found"


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["followers"] = pd.to_numeric(out["followers"], errors="coerce")
    out["engagement_rate_pct"] = pd.to_numeric(out["engagement_rate_pct"], errors="coerce")
    # Normalize the source schema to the canonical singular field used by the UI and outputs.
    # The input dataset uses `platforms`, while the assignment output calls for `platform`.
    if "platform" not in out.columns:
        out["platform"] = out.get("platforms", "Not Found").fillna("Not Found").astype(str)
    out["contact_email"] = out["contact_email"].apply(normalize_email)
    out["email_available"] = out["contact_email"].ne("Not Found")
    out["content_themes"] = out["content_themes"].fillna("Not Found").astype(str)
    out["niche"] = out["niche"].fillna("Unclassified").astype(str)
    out["content_context"] = out["niche"] + " | " + out["content_themes"]
    out["micro_influencer"] = out["followers"].between(SETTINGS.min_followers, SETTINGS.max_followers, inclusive="both")
    out["engagement_quality"] = out["engagement_rate_pct"].apply(lambda x: "measured" if pd.notna(x) else "Not Found")
    out["data_quality_flag"] = out.apply(lambda r: "complete" if r.email_available and r.micro_influencer else "needs_review", axis=1)
    return out
