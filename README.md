# CreatorReach AI — Automated Micro-Influencer Outreach

**Campaign identity:** CreatorReach AI / **Tech Creator Connect**

A Python + Streamlit prototype that demonstrates the assignment workflow:

**Discovery → Enrichment → Filtering → AI Personalization → Review → Sending Simulation → Tracking**

## What is included
- 53-influencer demonstration dataset
- Micro-influencer qualification (5,000–100,000 followers)
- Niche filtering with explicit pass/fail reasons
- Contact/email validation without guessing missing addresses
- Profile/content enrichment
- 60–90 word personalized email pitches
- 15–30 word personalized Instagram DMs
- Optional LLM personalization with deterministic fallback
- Safe email sending simulation and duplicate prevention
- SQLite outreach tracker
- Optional YouTube Data API discovery
- Streamlit campaign dashboard
- Automated tests

## Brand/campaign identity
**CreatorReach AI** is the project's product identity. **Tech Creator Connect** is the demonstration campaign. The value proposition is AI-assisted creator partnerships with personalized outreach, transparent review, and measurable campaign tracking.

## Setup
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Optional keys can be placed in `.env` using `.env.example`:
- `OPENAI_API_KEY` — LLM personalization
- `YOUTUBE_API_KEY` — live YouTube discovery

The demo works without either key.

## Run
```bash
python run_demo.py
python -m pytest -q
streamlit run app.py
```

## Safety and data quality
- Missing emails are `Not Found`, never guessed.
- Missing engagement data is not fabricated.
- Instagram automation does not bypass platform restrictions.
- Email sending defaults to simulation to avoid accidental outreach.
<img width="1908" height="912" alt="Screenshot 2026-10-04 235219" src="https://github.com/user-attachments/assets/be280ea2-b6e5-463b-86d8-f2966f4c0faf" />
<img width="1903" height="907" alt="Screenshot 2026-10-04 235244" src="https://github.com/user-attachments/assets/a9984597-df3f-4ee3-9ba3-37bf993ce8c6" />


