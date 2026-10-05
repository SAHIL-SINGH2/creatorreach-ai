from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    brand_name: str = os.getenv("BRAND_NAME", "CreatorReach AI")
    brand_value_prop: str = os.getenv("BRAND_VALUE_PROP", "AI-assisted creator partnerships with personalized outreach, transparent review, and measurable campaign tracking")
    min_followers: int = int(os.getenv("MIN_FOLLOWERS", "5000"))
    max_followers: int = int(os.getenv("MAX_FOLLOWERS", "100000"))
    min_engagement: float = float(os.getenv("MIN_ENGAGEMENT", "2.0"))
    target_niche: str = os.getenv("TARGET_NICHE", "Technology")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

SETTINGS = Settings()

NICHE_ANGLES = {
    "Technology": ("paid product review or UGC demo", "hands-on tech reviews and buying guidance"),
    "Fitness": ("UGC workout/product integration", "practical fitness and wellness content"),
    "Food": ("sponsored tasting or product feature", "food discovery, reviews and recommendations"),
    "Travel": ("destination/content partnership", "travel storytelling, guides and trip inspiration"),
    "Lifestyle": ("UGC or sponsored lifestyle integration", "lifestyle, fashion, beauty and everyday recommendations"),
    "Beauty": ("UGC beauty tutorial or product placement", "beauty-focused tutorials and product discovery"),
    "Fashion": ("UGC styling campaign", "style inspiration and fashion discovery"),
    "Gaming": ("sponsored gameplay or UGC integration", "gaming content and community engagement"),
    "Fintech": ("educational product integration", "personal-finance and fintech education"),
    "Crypto": ("educational product collaboration", "crypto and Web3 education"),
    "Parenting": ("family-focused UGC campaign", "parenting recommendations and family lifestyle"),
}
