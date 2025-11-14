import datetime
import os.path
import json
import pprint
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Optional: use `private_settings.py` to store client secrets and token.
try:
  import private_settings as ps
except Exception:
  ps = None

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # First try: token in private_settings module (TOKEN dict)
  if ps and hasattr(ps, "TOKEN") and ps.TOKEN:
    try:
      creds = Credentials.from_authorized_user_info(ps.TOKEN, SCOPES)
    except Exception:
      creds = None

  # Fallback: token.json file (legacy)
  if not creds and os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run.
    # By default we update `private_settings.TOKEN` if available, otherwise
    # we write the legacy `token.json` file.
    token_json = creds.to_json()
    if ps is not None:
      # update the TOKEN block inside private_settings.py
      try:
        token_dict = json.loads(token_json)
        ps_path = os.path.join(os.path.dirname(__file__), "private_settings.py")
        with open(ps_path, "r", encoding="utf-8") as f:
          src = f.read()

        start_marker = "# --- OAUTH_TOKEN START ---"
        end_marker = "# --- OAUTH_TOKEN END ---"
        pattern = re.compile(
          re.escape(start_marker) + r".*?" + re.escape(end_marker),
          flags=re.DOTALL,
        )

        token_literal = pprint.pformat(token_dict, width=120)
        new_block = f"{start_marker}\nTOKEN = {token_literal}\n{end_marker}"

        if pattern.search(src):
          new_src = pattern.sub(new_block, src)
        else:
          # Append block if not present
          new_src = src + "\n\n" + new_block

        with open(ps_path, "w", encoding="utf-8") as f:
          f.write(new_src)
      except Exception:
        # Fallback: write token.json file
        with open("token.json", "w") as token:
          token.write(token_json)
    else:
      with open("token.json", "w") as token:
        token.write(token_json)

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()