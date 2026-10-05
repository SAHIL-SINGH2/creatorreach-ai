from __future__ import annotations
import os
import re
from typing import Tuple
import pandas as pd


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text))


def _angle(niche: str) -> Tuple[str, str]:
    from .config import NICHE_ANGLES
    return NICHE_ANGLES.get(niche, ("a creator collaboration", "your audience and content"))


def deterministic_messages(row: pd.Series, brand_name: str = "NovaTech") -> tuple[str, str]:
    name = str(row.get("name", "Creator")).split("(")[0].strip()
    niche = str(row.get("niche", "creator"))
    themes = str(row.get("content_themes", "your recent content"))
    first_theme = themes.split(";")[0].strip() if themes else "your content"
    angle, audience = _angle(niche)
    email = (
        f"Hi {name},\n\n"
        f"I’ve been looking at your {niche.lower()} content, especially your work around {first_theme}. "
        f"The way you make {audience} practical feels aligned with {brand_name}. "
        f"We’d love to explore a {angle} where you can keep your own voice while introducing our product to your audience. "
        f"We can offer a paid collaboration, clear campaign brief, and a performance-based upside. "
        f"If this sounds relevant, I’d be happy to share the product and campaign details.\n\nBest,\n{brand_name} Partnerships"
    )
    dm = f"Hi {name}! Loved your {first_theme} content. Your {niche.lower()} audience looks like a strong fit for our upcoming creator campaign."
    return email, dm


def llm_messages(row: pd.Series, brand_name: str, model: str) -> tuple[str, str]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package is not installed") from exc
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not configured")
    prompt = f"""You write one-to-one creator outreach for {brand_name}. Use only the supplied facts; never invent a recent post, metric, email, location, or audience fact.\nCreator: {row.get('name')}\nNiche: {row.get('niche')}\nThemes: {row.get('content_themes')}\nPlatform: {row.get('platforms')}\nFollowers: {row.get('followers')}\n\nReturn exactly two labeled sections: EMAIL and DM. EMAIL must be 60-90 words. DM must be 15-30 words. Make both natural, specific to the supplied themes, and propose a plausible collaboration."""
    res = client.chat.completions.create(model=model, temperature=0.4, messages=[{"role": "system", "content": "You are a careful creator-marketing copywriter."}, {"role": "user", "content": prompt}])
    text = res.choices[0].message.content or ""
    email = text.split("DM:", 1)[0].replace("EMAIL:", "").strip()
    dm = text.split("DM:", 1)[1].strip() if "DM:" in text else ""
    return email, dm


def generate_messages(row: pd.Series, brand_name: str = "NovaTech", use_llm: bool = True, model: str = "gpt-4o-mini") -> tuple[str, str, str]:
    source = "rule_based"
    if use_llm and os.getenv("OPENAI_API_KEY"):
        try:
            email, dm = llm_messages(row, brand_name, model)
            source = "llm"
        except Exception:
            email, dm = deterministic_messages(row, brand_name)
            source = "rule_based_fallback"
    else:
        email, dm = deterministic_messages(row, brand_name)
    if not (60 <= word_count(email) <= 90):
        raise ValueError(f"Email is {word_count(email)} words; required 60-90")
    if not (15 <= word_count(dm) <= 30):
        raise ValueError(f"DM is {word_count(dm)} words; required 15-30")
    return email, dm, source


def personalize(df: pd.DataFrame, brand_name: str = "NovaTech", use_llm: bool = True, model: str = "gpt-4o-mini") -> pd.DataFrame:
    out = df.copy()
    emails, dms, sources = [], [], []
    for _, row in out.iterrows():
        email, dm, source = generate_messages(row, brand_name, use_llm, model)
        emails.append(email); dms.append(dm); sources.append(source)
    out["email_pitch"] = emails
    out["instagram_dm"] = dms
    out["personalization_source"] = sources
    out["email_word_count"] = out["email_pitch"].apply(word_count)
    out["dm_word_count"] = out["instagram_dm"].apply(word_count)
    return out
