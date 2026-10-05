# Self-Test Report

Run date: 2026-09-30

## Automated tests
- `python -m pytest -q` → **6 passed**
- `python -m compileall -q src run_demo.py app.py` → **PASS**

## End-to-end demo result
- Discovery input: **53** records
- Micro-influencers in range: **53/53**
- Public contact emails: **43/53**
- Technology segment passed: **13**
- Generated email word counts: **85–88** for the 13 shortlisted creators
- Generated DM word counts: **20–23** for the 13 shortlisted creators
- Sending mode tested: **simulation**
- Duplicate prevention tested: **PASS** (second send returns `SKIPPED_DUPLICATE`)
- Missing-email handling tested: **PASS** (`Not Found`, never guessed)

## Manual UI test
The UI is implemented in `app.py`. This environment did not have Streamlit installed, so the Streamlit browser UI itself was not launched here. Install requirements and run `streamlit run app.py` to perform the UI test cases in the README.
