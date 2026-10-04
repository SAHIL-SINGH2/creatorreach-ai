# Assignment-to-Implementation Mapping

| PDF requirement | Implementation |
|---|---|
| 50+ influencers | 53 bundled public records |
| Micro definition 5k–100k | `src/enrichment.py` |
| Filtering/classification | `src/filtering.py` with pass/fail reasons |
| Niche/platform/followers/ER/content/email | `data/influencers_raw.csv` + enrichment |
| Missing email = Not Found | `normalize_email()` |
| 60–90 word email | enforced in `src/personalization.py` |
| 15–30 word DM | enforced in `src/personalization.py` |
| Dynamic personalization | niche + content theme + creator name |
| Sending layer | simulation + optional SMTP |
| Duplicate prevention | SQLite UNIQUE influencer key |
| Outreach log | `OutreachStore` |
| No ToS bypass for Instagram | DM is generated for manual workflow |
| README/setup/limitations | `README.md` |
| Modular/reusable | discovery/enrichment/filtering/personalization/sending modules |
| Error tolerance | validation + LLM fallback + explicit unavailable data |
| 500+ scalability | pipeline functions operate on arbitrary CSV sizes; YouTube provider paginates queries |
