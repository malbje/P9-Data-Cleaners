# service/gcal.py
import os
import json
import pprint
import re
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import private_settings as ps

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def _credentials_from_private_settings():
    # Build Credentials object from ps.TOKEN and ensure valid/refresh
    creds = None
    if hasattr(ps, "TOKEN") and ps.TOKEN:
        creds = Credentials.from_authorized_user_info(ps.TOKEN, SCOPES)
    # If expired and has refresh token, refresh
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _write_token_to_private_settings(creds)
    return creds

def _write_token_to_private_settings(creds):
    token_json = creds.to_json()
    token_dict = json.loads(token_json)
    # private_settings.py lives at the repository root, two levels above this file
    ps_path = os.path.join(os.path.dirname(__file__), "..", "..", "private_settings.py")
    ps_path = os.path.abspath(ps_path)
    with open(ps_path, "r", encoding="utf-8") as f:
        src = f.read()
    start_marker = "# --- OAUTH_TOKEN START ---"
    end_marker = "# --- OAUTH_TOKEN END ---"
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), flags=re.DOTALL)
    import pprint as _pp
    token_literal = _pp.pformat(token_dict, width=120)
    new_block = f"{start_marker}\\nTOKEN = {token_literal}\\n{end_marker}"
    if pattern.search(src):
        new_src = pattern.sub(new_block, src)
    else:
        new_src = src + "\\n\\n" + new_block
    with open(ps_path, "w", encoding="utf-8") as f:
        f.write(new_src)

def fetch_google_events(start_iso, end_iso, max_results=250):
    creds = _credentials_from_private_settings()
    if creds is None:
        # If no token present, you must run an authorization flow elsewhere (admin)
        raise RuntimeError("No credentials available. Run auth flow to populate private_settings.TOKEN")
    service = build("calendar", "v3", credentials=creds)
    events_result = service.events().list(
        calendarId="primary", timeMin=start_iso, timeMax=end_iso,
        singleEvents=True, orderBy="startTime", maxResults=max_results
    ).execute()
    items = events_result.get("items", [])
    # normalize fields for downstream use
    normalized = []
    for e in items:
        start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date")
        end = e.get("end", {}).get("dateTime") or e.get("end", {}).get("date")
        normalized.append({
            "id": e.get("id"),
            "summary": e.get("summary"),
            "description": e.get("description"),
            "start": start,
            "end": end,
            "location": e.get("location"),
            "raw": e
        })
    return normalized