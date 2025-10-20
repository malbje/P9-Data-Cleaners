"""
================================================================================
DATA CLEANERS - NOTIFICATION SYSTEM
================================================================================
Email notification service for appointment reminders and customer communications

Features:
- SMTP email sending with authentication
- Dry-run mode for testing without sending emails
- Appointment reminder message generation
- Integration with database appointment queries
- Error handling for failed email deliveries

Dependencies:
- private_settings: SMTP configuration (host, port, credentials)
- backend.service.get_upcoming_appt: Database appointment queries
- smtplib: Python standard library for email sending

Author: Data Cleaners Team
Last Modified: [Current Date]
================================================================================
"""

# System path configuration for backend imports
import sys, os
sys.path.insert(0, os.getcwd())

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================

import smtplib
from email.message import EmailMessage
import private_settings

# ============================================================================
# SMTP CONFIGURATION
# ============================================================================

# Email server settings from private configuration
SMTP_HOST = private_settings.SMTP_HOST
SMTP_PORT = private_settings.SMTP_PORT
SMTP_USER = private_settings.SMTP_USER
SMTP_PASS = private_settings.SMTP_PASS

FROM = SMTP_USER

# Development mode switch (True = print to terminal, False = send emails)
DRY_RUN = True


# ============================================================================
# NOTIFICATION MESSAGE GENERATION
# ============================================================================

def create_notification(name, date, time):
    """
    Generate a personalized appointment reminder message
    
    Args:
        name (str): Customer's full name
        date (str): Appointment date (YYYY-MM-DD format)
        time (str): Appointment time (HH:MM format)
        
    Returns:
        str: Formatted reminder message for email/SMS delivery
    """
    return f"Hello {name}, this is a reminder that your cleaning is scheduled for {date} at {time}."

# ============================================================================
# DATABASE INTEGRATION AND APPOINTMENT RETRIEVAL  
# ============================================================================

# Import appointment query functions from database service
from backend.service.get_upcoming_appt import get_appointments_to_notify

# Fetch appointments requiring notifications
appointments = get_appointments_to_notify()

# Debug information about notification queue
print(f"Found {len(appointments)} appointments to notify.")
for appt in appointments:
    print("Appointment data:", appt)


# ============================================================================
# EMAIL SENDING FUNCTIONALITY
# ============================================================================

def send_notification(notification, email):
    """
    Send appointment reminder email to customer
    
    Supports both dry-run mode (terminal output) and live email delivery
    Uses SMTP with TLS encryption for secure email transmission
    
    Args:
        notification (str): Pre-formatted reminder message text
        email (str): Customer's email address for delivery
        
    Returns:
        None: Prints success/failure status to console
        
    Raises:
        Exception: Email delivery failures are caught and logged
    """
    # Development mode - print to terminal instead of sending email
    if DRY_RUN:
        print(f"[DRY_RUN] Would send to {email}: {notification}")
        return

    # Create email message with proper headers
    msg = EmailMessage()
    msg["From"] = FROM
    msg["To"] = email
    msg["Subject"] = "Cleaning Appointment Reminder"
    msg.set_content(notification)

    try:
        # Send email via SMTP with TLS encryption
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls()  # Enable TLS encryption
            s.login(SMTP_USER, SMTP_PASS)  # Authenticate with server
            s.send_message(msg)  # Send the email
        print(f"Sent to {email}")
    except Exception as e:
        print(f"FAILED to send to {email}: {e}")

# ============================================================================
# NOTIFICATION PROCESSING LOOP
# ============================================================================

# Process each appointment and send reminder notifications
for appointment in appointments:
    # Generate personalized reminder message
    notification = create_notification(
        appointment["name"],
        appointment["date"], 
        appointment["time"]
    )
    # Send notification via email (or print in dry-run mode)
    send_notification(notification, appointment["email"])
