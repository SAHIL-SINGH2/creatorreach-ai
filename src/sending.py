from __future__ import annotations
import sqlite3
import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

class OutreachStore:
    def __init__(self, db_path: str | Path = "output/outreach.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute("""CREATE TABLE IF NOT EXISTS outreach_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                influencer_key TEXT UNIQUE NOT NULL,
                influencer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                sent_at TEXT,
                status TEXT NOT NULL,
                mode TEXT NOT NULL,
                message TEXT NOT NULL,
                error TEXT
            )""")

    def already_contacted(self, influencer_key: str) -> bool:
        with sqlite3.connect(self.db_path) as con:
            return con.execute("SELECT 1 FROM outreach_log WHERE influencer_key=?", (influencer_key,)).fetchone() is not None

    def record(self, key: str, name: str, email: str, message: str, status: str, mode: str, error: str = ""):
        with sqlite3.connect(self.db_path) as con:
            con.execute("INSERT OR REPLACE INTO outreach_log(influencer_key,influencer_name,email,sent_at,status,mode,message,error) VALUES(?,?,?,?,?,?,?,?)",
                        (key, name, email, datetime.now(timezone.utc).isoformat(), status, mode, message, error))

    def log(self) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as con:
            return pd.read_sql_query("SELECT * FROM outreach_log ORDER BY id DESC", con)

class OutreachSender:
    def __init__(self, store: OutreachStore):
        self.store = store

    @staticmethod
    def valid_email(email: str) -> bool:
        return isinstance(email, str) and "@" in email and "." in email.split("@")[-1] and email != "Not Found"

    def simulate(self, row: pd.Series) -> str:
        email = str(row.get("contact_email", "Not Found"))
        key = email.lower().strip()
        if not self.valid_email(email):
            return "SKIPPED_NO_EMAIL"
        if self.store.already_contacted(key):
            return "SKIPPED_DUPLICATE"
        self.store.record(key, str(row.get("name", "")), email, str(row.get("email_pitch", "")), "SIMULATED_SENT", "simulation")
        return "SIMULATED_SENT"

    def send_smtp(self, row: pd.Series, host: str, port: int, username: str, password: str, sender_email: str) -> str:
        email = str(row.get("contact_email", "Not Found")); key = email.lower().strip()
        if not self.valid_email(email): return "SKIPPED_NO_EMAIL"
        if self.store.already_contacted(key): return "SKIPPED_DUPLICATE"
        msg = EmailMessage(); msg["Subject"] = "Creator collaboration opportunity"; msg["From"] = sender_email; msg["To"] = email; msg.set_content(str(row.get("email_pitch", "")))
        try:
            with smtplib.SMTP_SSL(host, port, timeout=20) as smtp:
                smtp.login(username, password); smtp.send_message(msg)
            self.store.record(key, str(row.get("name", "")), email, msg.get_content(), "SENT", "smtp")
            return "SENT"
        except Exception as exc:
            self.store.record(key, str(row.get("name", "")), email, msg.get_content(), "FAILED", "smtp", str(exc))
            return "FAILED"
