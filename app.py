import os
from pathlib import Path
import streamlit as st
from src.pipeline import run_pipeline
from src.sending import OutreachStore, OutreachSender
from src.config import SETTINGS

st.set_page_config(page_title="CreatorReach AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.block-container{padding-top:2rem;max-width:1400px}.hero{padding:28px 30px;border:1px solid rgba(128,128,128,.2);border-radius:18px;margin-bottom:22px;background:linear-gradient(135deg,rgba(99,102,241,.13),rgba(14,165,233,.08))}.hero h1{margin:0;font-size:2.3rem;letter-spacing:-.04em}.hero p{margin:8px 0 0;color:#64748b}.badge{display:inline-block;padding:5px 10px;border-radius:999px;background:rgba(99,102,241,.13);color:#6366f1;font-size:.78rem;font-weight:700;margin-bottom:10px}.section-title{font-size:1.15rem;font-weight:700;margin:22px 0 10px}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="badge">AI-POWERED CREATOR OUTREACH</div><h1>CreatorReach AI</h1><p>Discover → qualify → enrich → personalize → review → track creator partnerships.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ✨ CreatorReach AI")
    st.caption("Micro-influencer campaign workspace")
    st.divider()
    niche = st.selectbox("Target niche", ["Technology","Travel","Food","Fitness","Lifestyle","Beauty","Fashion","Gaming","Fintech"])
    use_llm = st.checkbox("Use LLM personalization", value=bool(os.getenv("OPENAI_API_KEY")), help="Uses the configured LLM when available and falls back to deterministic personalization.")
    run = st.button("Run campaign pipeline", type="primary", use_container_width=True)
    st.divider()
    st.caption("Campaign: Tech Creator Connect")
    st.caption("Mode: Safe simulation by default")

if run or "results" not in st.session_state:
    data_path = Path(__file__).parent / "data" / "influencers_raw.csv"
    with st.spinner("Running discovery, enrichment, filtering and personalization..."):
        st.session_state.results = run_pipeline(data_path, Path(__file__).parent / "output", target_niche=niche, use_llm=use_llm)

discovered, enriched, classified, shortlisted = st.session_state.results
st.markdown('<div class="section-title">Campaign overview</div>', unsafe_allow_html=True)
c1,c2,c3,c4=st.columns(4); c1.metric("Profiles discovered",len(discovered)); c2.metric("Micro-influencers",int(enriched["micro_influencer"].sum())); c3.metric("Qualified",len(shortlisted)); c4.metric("Public emails",int(enriched["email_available"].sum()))
st.markdown('<div class="section-title">Qualification results</div>', unsafe_allow_html=True)
st.caption(f"Target: {niche} · {SETTINGS.min_followers:,}–{SETTINGS.max_followers:,} followers · engagement threshold: {SETTINGS.min_engagement:.1f}%")
display_cols = ["name", "platform", "niche", "followers", "engagement_rate_pct", "contact_email", "filter_status", "filter_reason"]
# Defensive UI guard: keep the dashboard usable if an older/custom dataset omits a column.
for col in display_cols:
    if col not in classified.columns:
        classified[col] = "Not Found"
st.dataframe(classified[display_cols],use_container_width=True,hide_index=True)

if not shortlisted.empty:
    st.markdown('<div class="section-title">Personalized outreach</div>', unsafe_allow_html=True)
    st.caption("Each qualified creator receives a campaign-specific email pitch and Instagram DM. Review before sending.")
    st.dataframe(shortlisted[["name","contact_email","email_pitch","instagram_dm","email_word_count","dm_word_count"]],use_container_width=True,hide_index=True)
    st.download_button("Download qualified outreach CSV",shortlisted.to_csv(index=False),"creatorreach_shortlisted_outreach.csv","text/csv")
else: st.info("No creators passed this segment. Missing emails and unavailable metrics are never guessed.")

st.markdown('<div class="section-title">Sending & outreach tracker</div>', unsafe_allow_html=True)
store=OutreachStore(Path(__file__).parent/"output"/"outreach.db"); sender=OutreachSender(store)
if not shortlisted.empty:
    selected=st.multiselect("Select recipients for safe simulation",shortlisted["name"].tolist())
    if st.button("Simulate sending"):
        statuses=[sender.simulate(row) for _,row in shortlisted[shortlisted.name.isin(selected)].iterrows()]
        st.success(f"Processed {len(statuses)} recipient(s): {', '.join(statuses) if statuses else 'none selected'}")
st.dataframe(store.log(),use_container_width=True,hide_index=True)
with st.expander("Methodology, provenance & limitations"):
    st.write("Seed dataset: public, hand-verified July 2026 research dataset used as demonstration input. The system does not invent unavailable emails or engagement metrics. Optional live YouTube discovery uses the official YouTube Data API when YOUTUBE_API_KEY is configured. Instagram DMs remain a review/manual workflow where direct automated sending is unavailable or restricted.")
st.caption("CreatorReach AI · Tech Creator Connect · Review-first creator outreach prototype")
