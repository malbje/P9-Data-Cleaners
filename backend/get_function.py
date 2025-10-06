import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# imports
from datetime import datetime, timedelta
import database.DB_read as DB_reader #Reference to the database read class

def get_appointments_to_notify():
    """
    Fetches appointments from the database scheduled  within the next 24 hours.

    Uses:
        database.DB_read.get_joint_customers_appointments_data()

    Returns:
        list[dict]: List of dictionaries containing:
                    - name (str): Customer's name
            - date (str): Appointment date (YYYY-MM-DD)
            - time (str): Appointment time (HH:MM:SS)
            - email (str): Customer's email address
    """
    DB = DB_reader.DB_read() # Creates an object for reading the database
    raw_data = DB.get_joint_customers_appointments_data() # Get customer-appointment joined data

    upcoming = [] # will contain all upcoming appointments within 24 hours

    now = datetime.now()
    in_24h = now + timedelta(hours=24)

    for row in raw_data:
        # Extract values from DB row (must match coloumn order from SQL query)
        name, address, email, location_addr, appt_date, appt_time = row

        # combine date and time from database into a single datetime object
        try:
            appt_datetime = datetime.strptime(f"{appt_date} {appt_time}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # skip if datetime format is invalid (e.g. wrong DB formatting)
            continue

        # Only include appointments that are within 24 hours
        if now <= appt_datetime <= in_24h:
            upcoming.append({
                "name": name,
                "date": appt_date,
                "time": appt_time,
                "email": email
            })
    return upcoming