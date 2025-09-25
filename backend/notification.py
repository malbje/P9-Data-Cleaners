# -----------------------------
# This page works with creating and sending notifications based on 
# 
# Lige nu bliver der bare printet 3 reminders i terminalen baseret på mock database
# -----------------------------


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

# Mock "database" (laves om senere, når vi har en database) 
appointments = [
    {"name": "Alice", "date": "October 10, 2025", "time": "2:30 PM", "email": "alice@example.com"},
    {"name": "Bob", "date": "October 11, 2025", "time": "11:00 AM", "email": "bob@example.com"},
    {"name": "Charlie", "date": "October 12, 2025", "time": "4:15 PM", "email": "charlie@example.com"}
]

# Function to send notification (Mathias du ændre bare som det passer)
def send_notification(notification, email):
    """
    Send a notification to a given email address.
    
    Currently, this function only prints the message to the terminal.
    Later, it can be updated to send real emails or SMS.

    Args:
        notification (str): The notification message to send.
        email (str): The recipient's email address.
    """
    print(f"Sending to {email}: {notification}")

# Loop through all appointments and create + send message
for appointment in appointments:
    notification = create_notification(
        appointment["name"],
        appointment["date"],
        appointment["time"]
    )
    send_notification(notification, appointment["email"])
