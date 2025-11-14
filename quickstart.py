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

# Storing private settings in a separate module
import private_settings as ps

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  credentials = None
  # First try: token in private_settings module (TOKEN dict)
  if hasattr(ps, "TOKEN") and ps.TOKEN:
    try:
      credentials = Credentials.from_authorized_user_info(ps.TOKEN, SCOPES)
    except Exception:
      credentials = None

  # If there are no (valid) credentials available, let the user log in.
  if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
      credentials.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      credentials = flow.run_local_server(port=0)
    # Save the credentials for the next run. We persist only to
    # `private_settings.TOKEN`.
    token_json = credentials.to_json()
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
    except Exception as exc:
      raise RuntimeError("Failed to write OAuth token into private_settings.py") from exc

  try:
    service = build("calendar", "v3", credentials=credentials)

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