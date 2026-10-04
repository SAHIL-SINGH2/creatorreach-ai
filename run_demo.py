from pathlib import Path
from src.pipeline import run_pipeline
from src.sending import OutreachStore, OutreachSender

ROOT = Path(__file__).parent
D, E, F, S = run_pipeline(ROOT/'data/influencers_raw.csv', ROOT/'output', target_niche='Technology', use_llm=False)
print(f'Discovered: {len(D)}')
print(f'Micro-influencers: {int(E.micro_influencer.sum())}')
print(f'Public emails: {int(E.email_available.sum())}')
print(f'Technology segment passed: {len(S)}')
if len(S):
    print(S[['name','contact_email','email_word_count','dm_word_count']].to_string(index=False))
    store = OutreachStore(ROOT/'output/outreach.db')
    sender = OutreachSender(store)
    for _, row in S.head(3).iterrows():
        print(row['name'], sender.simulate(row))
