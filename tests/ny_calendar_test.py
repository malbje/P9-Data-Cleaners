import sys, os
sys.path.insert(0, os.getcwd()) # This should be removed when using a proper package structure
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import private_settings as ps

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
if hasattr(ps, 'TOKEN'):
    creds = Credentials.from_authorized_user_info(ps.TOKEN, SCOPES)

print('Has refresh token?', getattr(creds, 'refresh_token', None) is not None)
if creds and creds.expired and creds.refresh_token:
    try:
        creds.refresh(Request())
        print('Refreshed. New token:', creds.token)
        print('Saved JSON:', creds.to_json())
    except Exception as e:
        print('Refresh failed:', repr(e))
else:
    print('No refresh attempted (either creds missing, not expired, or no refresh_token).')