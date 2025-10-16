# database_logic.py
# This file contains all functions that interact with the database.

from database.DB_access import get_connection
from database.DB_read import DB_read
from database.DB_write import DB_write
from flask import session # Make sure session is imported

# --- Custom Exception ---
class ValidationError(Exception):
    """Custom exception for handling validation errors."""
    pass

# --- DATABASE LOGIC: USER AUTHENTICATION ---

def find_user_by_email(email):
    """Finds a single user by their email address, including their preferences."""
    conn = get_connection()
    if not conn:
        return None
    # Using dictionary=True is crucial. It makes cursor.fetchone() return a dictionary.
    cursor = conn.cursor(dictionary=True)
    try:
        # This query MUST include `notification_preference`.
        query = "SELECT id, name, surname, email, notification_preference FROM customers WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"Error finding user by email: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_user(data):
    """Creates a new user in the database."""
    # Validation
    firstname = data.get("firstname", "").strip()
    lastname = data.get("lastname", "").strip()
    email = data.get("email", "").strip()
    # Password is no longer stored, so validation is removed.

    if not firstname or not lastname: raise ValidationError("First and last name are required.")
    if "@" not in email: raise ValidationError("Invalid email address.")
    if find_user_by_email(email): raise ValidationError("A user with this email already exists.")

    # Database Insertion
    conn = get_connection()
    if not conn: raise Exception("Database connection failed.")
    cursor = conn.cursor()
    try:
        # The password column has been removed from the customers table.
        query = "INSERT INTO customers (name, surname, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (firstname, lastname, email))
        conn.commit()
        return {"success": True, "message": "User created successfully"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_all_users():
    """Fetches a list of all users from the customers table."""
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, name, surname, email FROM customers ORDER BY name"
        cursor.execute(query)
        users = cursor.fetchall()
        return users
    finally:
        cursor.close()
        conn.close()

def get_addresses_and_preferences_for_customer(customer_id):
    """
    Gets all addresses for a customer, including any associated preferences.
    """
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        # This query joins addresses with preferences for a given customer ID
        query = """
            SELECT 
                addr.id,
                addr.street_and_number,
                addr.postal_code,
                addr.city_name,
                p.allergies,
                p.pets,
                p.kids,
                p.square_footage,
                p.notes AS preference_notes
            FROM addresses addr
            JOIN lives_in li ON addr.id = li.address_id
            LEFT JOIN preferences p ON addr.id = p.address_id
            WHERE li.customer_id = %s
            ORDER BY addr.id;
        """
        cursor.execute(query, (customer_id,))
        addresses = cursor.fetchall()
        return addresses
    except Exception as e:
        print(f"Error getting addresses and preferences: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- DATABASE LOGIC: APPOINTMENTS ---

def get_appointments_for_customer(customer_id):
    """
    Gets all appointments for a specific customer.
    This version uses the correct table name 'has_ordered' from your new schema.
    """
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        # This query now uses the correct table name 'has_ordered'
        query = """
            SELECT 
                appt.id,
                appt.date,
                appt.time,
                appt.notes,
                CONCAT(addr.street_and_number, ', ', addr.postal_code, ' ', addr.city_name) AS address,
                (SELECT GROUP_CONCAT(s.name SEPARATOR ', ') 
                 FROM has_ordered ho 
                 JOIN services s ON ho.service_id = s.id 
                 WHERE ho.appointment_id = appt.id) AS service_names
            FROM appointments appt
            JOIN addresses addr ON appt.address_id = addr.id
            WHERE appt.address_id IN (
                SELECT address_id FROM lives_in WHERE customer_id = %s
            )
            ORDER BY appt.date, appt.time;
        """
        cursor.execute(query, (customer_id,))
        appointments = cursor.fetchall()
        
        # Convert data types for JSON
        for appt in appointments:
            if appt.get('date'):
                appt['date'] = appt['date'].isoformat()
            if appt.get('time'):
                total_seconds = appt['time'].total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                appt['time'] = f"{hours:02}:{minutes:02}"
        
        return appointments
    except Exception as e:
        print(f"--- CRITICAL ERROR in get_appointments_for_customer: {e} ---")
        return []
    finally:
        cursor.close()
        conn.close()

def get_all_appointments():
    """Fetches a detailed list of all appointments for the table view."""
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    # Updated query to use the correct table name 'has_ordered'.
    query = """
        SELECT 
            apt.id, apt.date, apt.time, apt.notes,
            GROUP_CONCAT(s.name SEPARATOR ', ') AS service_names,
            CONCAT(addr.street_and_number, ', ', addr.postal_code, ' ', addr.city_name) as address,
            c.name, c.surname, c.email
        FROM appointments apt
        JOIN addresses addr ON apt.address_id = addr.id
        LEFT JOIN lives_in li ON addr.id = li.address_id
        LEFT JOIN customers c ON li.customer_id = c.id
        LEFT JOIN has_ordered ho ON apt.id = ho.appointment_id
        LEFT JOIN services s ON ho.service_id = s.id
        GROUP BY apt.id
        ORDER BY apt.date, apt.time
    """
    cursor.execute(query)
    appointments = cursor.fetchall()
    for appt in appointments: # Format for JSON
        if appt.get('date'): appt['date'] = appt['date'].isoformat()
        if appt.get('time'): 
            # Convert datetime.timedelta to a string like 'HH:MM:SS'
            appt['time'] = str(appt['time'])
    cursor.close()
    conn.close()
    return appointments

def create_full_appointment(data):
    """
    Creates a full appointment using the logged-in user's session
    and a selected address_id from the form.
    """
    writer = DB_write()

    try:
        # Get user_id from the session and address_id from the form data
        customer_id = session.get('user_id')
        address_id = data.get('address_id')

        if not customer_id:
            raise ValidationError("User is not logged in.")
        if not address_id:
            raise ValidationError("Address was not selected.")

        # Step 1: Create the appointment record
        # The writer class handles the database interaction.
        appointment_id = writer.create_appointment(
            address_id, 
            data['date'], 
            data['time'], 
            data.get('notes', '')
        )

        # Step 2: Link any selected services to the new appointment
        service_ids = data.get('service_ids', [])
        for service_id in service_ids:
            writer.link_service_to_appointment(appointment_id, service_id)

        return {"success": True, "appointment_id": appointment_id}

    except Exception as e:
        # It's good practice to log the actual error on the server
        print(f"An error occurred during appointment creation: {e}")
        # Re-raise the exception so the API layer can handle it
        raise e

