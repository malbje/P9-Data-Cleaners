# -----------------------------
# This page works with creating and sending notifications
#
# Currently it is printing 3 reminders in the terminal based on the mock data
# -----------------------------

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

import smtplib
from email.message import EmailMessage
import private_settings

# Notification system
# ----- SMTP CONFIGURATION (change these two lines) -----
SMTP_HOST = private_settings.SMTP_HOST
SMTP_PORT = private_settings.SMTP_PORT
SMTP_USER = private_settings.SMTP_USER
SMTP_PASS = private_settings.SMTP_PASS

FROM = SMTP_USER

# Turn on/off for testing (True = print to terminal, False = send mails)
DRY_RUN = True


# Notification message
def create_notification(name, date, time):
    """
    Create a notification message for a cleaning appointment.

    Args:
        name (str): The name of the person.
        date (str): The date of the cleaning appointment.
        time (str): The time of the cleaning appointment.

    Returns:
        str: A notification message.
    """
   
    return f"Hello {name}, this is a reminder that your cleaning is scheduled for {date} at {time}."

# Reference:
# Using get_appointments_to_notify() from get_function.py to fetch real data from DB
from backend.get_function import get_appointments_to_notify

appointments = get_appointments_to_notify()

print(f"Found {len(appointments)} appointments to notify.")
for appt in appointments:
    print("Appointment data:", appt)


# Function to send notification
def send_notification(notification, email):
    """
    Send a notification to a given email address.
    
    Currently, this function only prints the message to the terminal.
    Later, it can be updated to send real emails or SMS.

    If dryrun=true: prints to terminal
    If dryrun=false: sends email

    Args:
        notification (str): The notification message to send.
        email (str): The recipient's email address.
    """
    if DRY_RUN:
        print(f"[DRY_RUN] Would send to {email}: {notification}")
        return

    msg = EmailMessage()
    msg["From"] = FROM
    msg["To"] = email
    msg["Subject"] = "Cleaning Appointment Reminder"
    msg.set_content(notification)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        print(f"Sent to {email}")
    except Exception as e:
        print(f"FAILED to send to {email}: {e}")

# Loop through all appointments and create + send message
for appointment in appointments:
    notification = create_notification(
        appointment["name"],
        appointment["date"],
        appointment["time"]
    )
    send_notification(notification, appointment["email"])
