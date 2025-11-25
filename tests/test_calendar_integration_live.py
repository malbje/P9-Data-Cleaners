import os
import unittest
import datetime

from backend.service import calendar as gcal
from database.DB_read import DB_read
import private_settings as ps


class LiveCalendarIntegrationTest(unittest.TestCase):
    def test_live_google_and_db_fetch(self):
        """
        Live integration test: fetch events from Google Calendar and appointments from DB.
        This test will only run when the environment variable `RUN_LIVE_CALENDAR_TEST` is set to '1'.
        Make sure `private_settings.TOKEN` is populated and your DB is reachable.
        """
        if os.getenv('RUN_LIVE_CALENDAR_TEST') != '1':
            self.skipTest('Live integration test disabled. Set RUN_LIVE_CALENDAR_TEST=1 to enable.')

        # Validate presence of token in private_settings
        if not hasattr(ps, 'TOKEN') or not ps.TOKEN:
            self.fail('private_settings.TOKEN is missing or empty. Run the OAuth flow first.')

        now = datetime.datetime.now(datetime.timezone.utc)
        start_iso = now.isoformat()
        end_iso = (now + datetime.timedelta(days=7)).isoformat()

        # Fetch from Google
        events = gcal.fetch_google_events(start_iso, end_iso)
        self.assertIsInstance(events, list, 'Google fetch did not return a list')

        # Fetch from DB using simple appointments reader to avoid complex GROUP BY SQL
        reader = DB_read()
        appts = reader.get_all_appointments()
        self.assertIsInstance(appts, list, 'DB fetch did not return a list')

        # Basic sanity checks (no exceptions thrown and we got lists)
        print(f"Live test: fetched {len(events)} google events and {len(appts)} db appointments")


if __name__ == '__main__':
    unittest.main()
