"""
Service module responsible for selecting upcoming appointments that require
notification reminders. This file acts as a service layer between the business
logic (database_logic.py) and the notification delivery system (notification.py).

The main responsibility is:
- Retrieve simplified appointment data from the Business Logic Layer
- Filter appointments based on notification rules (e.g., 1 day before)
- Return data in the exact structure required by notification.py
"""

from datetime import datetime, timedelta
from backend.service import database_logic as db


def get_appointments_to_notify():
    """Return a filtered list of appointments that should receive reminders.

    This function fetches relevant appointment data from the Business Logic Layer
    and applies notification rules (currently: notify customers exactly one day
    before their scheduled cleaning appointment).

    The output is formatted specifically for use by notification.py:
        {
            "name": "Full Name",
            "email": "customer@example.com",
            "date": "YYYY-MM-DD",
            "time": "HH:MM"
        }

    Returns:
        list[dict]: A list of appointment dictionaries ready for notification.
        Each dict contains:
            - name: Customer's full name (str)
            - email: Customer email (str)
            - date: Appointment date as string (YYYY-MM-DD)
            - time: Appointment time as string (HH:MM)
    """
    try:
        # Retrieve simplified appointment data via Business Logic Layer
        appts = db.get_all_appointments_for_notification()
    except Exception as e:
        print("ERROR: could not load appointments:", e)
        return []

    results = []
    today = datetime.now().date()
    notify_date = today + timedelta(days=1)  # Rule: notify 1 day before appointment

    for appt in appts:
        try:
            # Convert DB date string into a Python date object
            appt_date = datetime.strptime(str(appt["date"]), "%Y-%m-%d").date()

            # Only notify appointments scheduled for the next day
            if appt_date == notify_date:
                full_name = f"{appt.get('name', '')} {appt.get('surname', '')}".strip()

                results.append(
                    {
                        "name": full_name,
                        "email": appt["email"],
                        "date": appt["date"],
                        "time": appt["time"],
                    }
                )

        except Exception as e:
            # Skip malformed appointment rows but keep system running
            print("Skipping invalid appointment:", appt, e)

    return results
