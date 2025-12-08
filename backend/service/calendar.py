# service/gcal.py
import os
import json
import pprint as PrettyPrinter
import re
import pathlib
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
import private_settings 

# Use full calendar scope to allow read/write if needed; tokens previously stored
# in private_settings may include either scope. Adjust as required.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def _credentials_from_private_settings():
    # Build Credentials object from private_settings.TOKEN and ensure valid/refresh
    creds = None
    if hasattr(private_settings, "TOKEN") and private_settings.TOKEN:
        creds = Credentials.from_authorized_user_info(private_settings.TOKEN, SCOPES)
    # If expired and has refresh token, refresh
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _write_token_to_private_settings(creds)
        except Exception:
            # If refresh fails, log and re-raise so callers can handle it
            import logging

            logging.exception("Failed to refresh credentials from private_settings")
            raise
    return creds

def _write_token_to_private_settings(creds):
    token_json = creds.to_json()
    token_dict = json.loads(token_json)
    ps_path = os.path.join(os.path.dirname(__file__), "..", "..", "private_settings.py")
    ps_path = os.path.abspath(ps_path)
    with open(ps_path, "r", encoding="utf-8") as ps_read:
        src = ps_read.read()
    start_marker = "# --- OAUTH_TOKEN START ---"
    end_marker = "# --- OAUTH_TOKEN END ---"
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), flags=re.DOTALL)
    token_literal = PrettyPrinter.pformat(token_dict, width=120)
    new_block = f"{start_marker}\nTOKEN = {token_literal}\n{end_marker}"
    if pattern.search(src):
        new_src = pattern.sub(new_block, src)
    else:
        new_src = src + "\n\n" + new_block
    with open(ps_path, "w", encoding="utf-8") as ps_write:
        ps_write.write(new_src)


def build_flow():
    """Build a google oauth Flow object.

    Preference order:
    - If `private_settings.Credentials` exists (dict like client_secret.json), use
      `Flow.from_client_config()` which avoids needing a file on disk.
    - Otherwise, fall back to `secrets/client_secret.json` located at repo root.
    """
    # Try client config in private_settings first
    client_config = getattr(private_settings, "Credentials", None)
    if client_config:
        try:
            return Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri="http://127.0.0.1:5000/google/oauth2callback",
            )
        except Exception:
            # fall through to file-based approach
            pass

    # Fallback: client secrets JSON in repo `secrets/` directory
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    client_file = repo_root / "secrets" / "client_secret.json"
    if not client_file.exists():
        raise FileNotFoundError(
            f"OAuth client secrets not found at {client_file}. Add a client_secret.json or set private_settings.Credentials"
        )
    return Flow.from_client_secrets_file(str(client_file), scopes=SCOPES, redirect_uri="http://127.0.0.1:5000/google/oauth2callback")


def authorization_url():
    """Return (authorization_url, state) to start the OAuth consent flow."""
    flow = build_flow()
    url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return url, state


def fetch_and_persist_tokens(authorization_response):
    """Exchange authorization response for credentials and persist them.

    Returns the `google.oauth2.credentials.Credentials` instance.
    """
    flow = build_flow()
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    # Persist to private_settings so service-layer can use it later
    _write_token_to_private_settings(creds)
    return creds


def get_service_from_private_settings():
    """Build a Google Calendar service client using stored credentials.

    This wraps `_credentials_from_private_settings()` and builds a `service`.
    """
    creds = _credentials_from_private_settings()
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds)

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
    for any in items:
        start = any.get("start", {}).get("dateTime") or any.get("start", {}).get("date")
        end = any.get("end", {}).get("dateTime") or any.get("end", {}).get("date")
        normalized.append({
            "id": any.get("id"),
            "summary": any.get("summary"),
            "description": any.get("description"),
            "start": start,
            "end": end,
            "location": any.get("location"),
            "raw": any
        })
    return normalized