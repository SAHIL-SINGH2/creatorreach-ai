from __future__ import annotations
from pathlib import Path
import pandas as pd
from .discovery import discover_from_csv
from .enrichment import enrich
from .filtering import classify
from .personalization import personalize
from .config import SETTINGS


def run_pipeline(input_csv: str | Path, output_dir: str | Path = "output", target_niche: str = SETTINGS.target_niche, use_llm: bool = False):
    outdir = Path(output_dir); outdir.mkdir(parents=True, exist_ok=True)
    discovered = discover_from_csv(input_csv, limit=1000)
    enriched = enrich(discovered)
    classified = classify(enriched, target_niche=target_niche)
    shortlisted = classified[classified["filter_status"] == "Passed"].copy()
    if not shortlisted.empty:
        shortlisted = personalize(shortlisted, SETTINGS.brand_name, use_llm=use_llm, model=SETTINGS.llm_model)
    else:
        shortlisted["email_pitch"] = []
        shortlisted["instagram_dm"] = []
        shortlisted["personalization_source"] = []
        shortlisted["email_word_count"] = []
        shortlisted["dm_word_count"] = []
    enriched.to_csv(outdir / "influencers_enriched.csv", index=False)
    classified.to_csv(outdir / "filter_results.csv", index=False)
    shortlisted.to_csv(outdir / "shortlisted_outreach.csv", index=False)
    return discovered, enriched, classified, shortlisted
