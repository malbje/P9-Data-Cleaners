# -----------------------------
# This page works with creating and sending notifications based on 
# 
# Lige nu bliver der bare printet 3 reminders i terminalen baseret på mock database
# -----------------------------
import os
import smtplib
from email.message import EmailMessage

# Notification system
# ----- SMTP KONFIGURATION (skift disse to linjer) -----
SMTP_HOST = "smtp.gmail.com"   # standadard for gmail
SMTP_PORT = 587                # Typisk 587 (TLS)
SMTP_USER = "data.cleaners2@gmail.com"   # vores fælles test-mail (BØR IKKE INKLUDERES I GIT, VI FINDER EN BEDRE LØSNING SENERE)
SMTP_PASS = "ogypbjdvvfkihrua"        # vores app-password (BØR IKKE INKLUDERES I GIT, VI FINDER EN BEDRE LØSNING SENERE)

FROM = SMTP_USER

# Slå til/fra for test (True = print kun til terminalen, False = send mails)
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

# Mock "database" (laves om senere, når vi har en database) *rettet til kommentare for afprøvning*
appointments = [
    {"name": "Alice", "date": "October 10, 2025", "time": "2:30 PM", "email": "data.cleaners2@gmail.com"},
    #{"name": "Bob", "date": "October 11, 2025", "time": "11:00 AM", "email": "bob@example.com"},
    #{"name": "Charlie", "date": "October 12, 2025", "time": "4:15 PM", "email": "charlie@example.com"}
]

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
