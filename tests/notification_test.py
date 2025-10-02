# -----------------------------
# This page tests exists for testing the different methods in notification.py
# (Only create_notification is tested rn, as send_notification doesn't have any agreeded upon 'return's yet)
# -----------------------------

import unittest # Class with unit test methods

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

from backend import notification

class Test_notification(unittest.TestCase):
    def test_create_notification(self):
        """
        Tests if the create_notification function inputs name, date and time correctly into the message
        """
        # Arrange
        name = "Test User"
        date = "January 1, 2025"
        time = "10:00 AM"
        expected_message = "Hello Test User, this is a reminder that your cleaning is scheduled for January 1, 2025 at 10:00 AM."
        # Act
        text = notification.create_notification(name, date, time)
        #Assert
        self.assertEqual(text, expected_message)

# These lines makes it so that the code in this file only runs when the file is run directly, and not when imported
if __name__ == '__main__':
    unittest.main()