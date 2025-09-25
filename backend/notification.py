
# Notification message

def create_notification(name, date, time):
    message = f"Hello {name}, this is a reminder that your cleaning is scheduled for {date} at {time}."
    return message


# Example usage (mock database values for now)
name = "Alice"
date = "October 10, 2025"
time = "2:30 PM"


# "notification" can be used for sending message later
notification = create_notification(name, date, time)
# temporary used for showing notification(delete later)
print(notification)


#Send notification