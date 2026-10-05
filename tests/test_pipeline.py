from pathlib import Path
import pandas as pd
from src.discovery import discover_from_csv
from src.enrichment import enrich, normalize_email
from src.filtering import classify
from src.personalization import generate_messages, word_count
from src.sending import OutreachStore, OutreachSender

ROOT = Path(__file__).parents[1]
CSV = ROOT / "data" / "influencers_raw.csv"

def test_discovery_has_at_least_50_real_records():
    df = discover_from_csv(CSV, 100)
    assert len(df) >= 50
    assert df["followers"].between(5000, 100000).all()

def test_missing_email_is_never_guessed():
    assert normalize_email("") == "Not Found"
    assert normalize_email("Not Found") == "Not Found"
    assert normalize_email("bad-email") == "Not Found"

def test_enrichment_normalizes_platform_field():
    df = enrich(discover_from_csv(CSV, 53))
    assert "platform" in df.columns
    assert df["platform"].notna().all()
    assert df["platform"].astype(str).str.len().gt(0).all()


def test_enrichment_preserves_missing_engagement_as_unknown():
    df = enrich(discover_from_csv(CSV, 53))
    assert (df.loc[df["engagement_rate_pct"].isna(), "engagement_quality"] == "Not Found").all()

def test_filter_explains_pass_fail():
    df = classify(enrich(discover_from_csv(CSV, 53)), target_niche="Technology")
    assert set(df["filter_status"]) <= {"Passed", "Failed"}
    assert df["filter_reason"].notna().all()

def test_message_word_limits_and_personalization():
    df = enrich(discover_from_csv(CSV, 53))
    row = df.iloc[21]
    email, dm, source = generate_messages(row, "NovaTech", use_llm=False)
    assert 60 <= word_count(email) <= 90
    assert 15 <= word_count(dm) <= 30
    assert str(row["content_themes"].split(";")[0]) in email
    assert source == "rule_based"

def test_sending_dedup_and_log(tmp_path):
    df = enrich(discover_from_csv(CSV, 53))
    row = df[df["email_available"]].iloc[0].copy()
    row["email_pitch"] = "Test outreach message"
    store = OutreachStore(tmp_path / "outreach.db")
    sender = OutreachSender(store)
    assert sender.simulate(row) == "SIMULATED_SENT"
    assert sender.simulate(row) == "SKIPPED_DUPLICATE"
    assert len(store.log()) == 1
