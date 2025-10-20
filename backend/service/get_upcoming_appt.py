"""
================================================================================
DATA CLEANERS - UPCOMING APPOINTMENTS SERVICE
================================================================================
Database query service for retrieving appointments requiring notifications

Features:
- Fetches appointments within 24-hour notification window
- Joins customer and appointment data from database
- Filters appointments by time proximity
- Returns structured data for notification system
- Error handling for invalid datetime formats

Dependencies:
- database.DB_read: Database access layer for customer/appointment queries
- datetime: Python standard library for date/time calculations

Author: Data Cleaners Team  
Last Modified: [Current Date]
================================================================================
"""

# ============================================================================
# IMPORTS AND PATH CONFIGURATION
# ============================================================================

import sys
import os

# Add project root to Python path for database imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from database import DB_read as DB_reader  # Database read operations
from datetime import datetime, timedelta   # Date/time calculations

# ============================================================================
# APPOINTMENT NOTIFICATION QUERY FUNCTIONS
# ============================================================================

def get_appointments_to_notify():
    """
    Retrieve appointments scheduled within the next 24 hours for notification
    
    Queries the database for customer-appointment data and filters by time proximity
    Used by the notification system to identify appointments requiring reminders
    
    Database Dependencies:
        - database.DB_read.get_joint_customers_appointments_data(): Joined customer/appointment query
        
    Returns:
        list[dict]: Appointments requiring notification, each containing:
            - name (str): Customer's full name
            - date (str): Appointment date (YYYY-MM-DD format)  
            - time (str): Appointment time (HH:MM:SS format)
            - email (str): Customer's email address for notification delivery
            
    Raises:
        ValueError: Invalid datetime formats are silently skipped with continue
    """
    # Initialize database reader and fetch joined customer-appointment data
    DB = DB_reader.DB_read()
    raw_data = DB.get_joint_customers_appointments_data()

    upcoming = []  # Collection for appointments within notification window

    # Define 24-hour notification window from current time
    now = datetime.now()
    in_24h = now + timedelta(hours=24)

    # Process each database row and filter by time criteria
    for row in raw_data:
        # Extract columns (order must match SQL query structure)
        name, addresses, email, appt_addr, appt_date, appt_time = row

        # Convert separate date/time strings to datetime object for comparison
        try:
            appt_datetime = datetime.strptime(f"{appt_date} {appt_time}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Skip appointments with invalid datetime formatting
            continue

        # Include only appointments within the 24-hour notification window
        if now <= appt_datetime <= in_24h:
            upcoming.append({
                "name": name,
                "date": appt_date, 
                "time": appt_time,
                "email": email
            })
            
    return upcoming