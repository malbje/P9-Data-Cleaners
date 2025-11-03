# database_logic.py
# This file contains all business logic and validation (Business Logic Layer).
# THIS FILE MUST NEVER CONTAIN SQL OR CALL get_connection().
# It exclusively uses functions from DB_read and DB_write.

from database.DB_read import DB_read
from database.DB_write import DB_write
from flask import session

class ValidationError(Exception):
    pass

db_reader = DB_read()
db_writer = DB_write()

def find_user_by_email(email):
    return db_reader.get_customer_by_email(email)

def create_user(data):
    """
    Creates a new user and optional address, validates and returns created ids.
    Accepts either 'name'|'firstname' and 'surname'|'lastname' for compatibility with frontend.
    """
    name = (data.get("name") or data.get("firstname") or "").strip()
    surname = (data.get("surname") or data.get("lastname") or "").strip()
    email = (data.get("email") or "").strip().lower()

    if not name or not surname:
        raise ValidationError("First and last name are required.")
    if "@" not in email:
        raise ValidationError("Invalid email address.")

    if db_reader.get_customer_by_email(email):
        raise ValidationError("A user with this email already exists.")

    # create customer
    customer_id = db_writer.create_customer(name, surname, email)
    if not customer_id:
        raise Exception("Failed to create or resolve customer id.")

    result = {"success": True, "customer_id": customer_id}

    # optional address creation + link
    addr = data.get("address") or {}
    street = (addr.get("street_and_number") or addr.get("street") or "").strip()
    postal = (addr.get("postal_code") or "").strip()
    city = (addr.get("city_name") or addr.get("city") or "").strip()

    address_id = None
    if street and postal and city:
        existing = db_reader.find_address(street, postal) if hasattr(db_reader, "find_address") else None
        if existing and existing.get("id"):
            address_id = existing["id"]
        else:
            address_id = db_writer.create_address(street, postal, city)
        db_writer.link_customer_to_address(customer_id, address_id)
        result.update({"address_id": address_id})

    return result

def get_all_users():
    """Fetches a list of all users (pass-through to DAL)."""
    return db_reader.get_all_customers()

def get_addresses_and_preferences_for_customer(customer_id):
    """Gets all addresses and preferences for a customer (pass-through to DAL)."""
    return db_reader.get_addresses_and_preferences_for_customer(customer_id)

def get_appointments_by_address_id(address_id):
    """Gets appointments for a specific address (pass-through to DAL)."""
    return db_reader.get_appointments_by_address_id(address_id)

# --- DATABASE LOGIC: APPOINTMENTS ---

def get_appointments_for_customer(customer_id):
    """Gets all appointments for a specific customer (pass-through to DAL)."""
    return db_reader.get_appointments_for_customer(customer_id)

def get_all_appointments():
    """Fetches a detailed list of all appointments (pass-through to DAL)."""
    # Uses the detailed joint function from DB_read
    return db_reader.get_joint_customers_appointments_data() 

def create_full_appointment(data):
    """
    Creates a full appointment record.
    This is a "Business Logic" function:
    1. It validates logic (is user logged in? is address selected?).
    2. It coordinates multiple database calls (create appointment, then link services).
    """
    try:
        # Get user_id from the session and address_id from the form data
        customer_id = session.get('user_id')
        address_id = data.get('address_id')

        # Step 1: Validation
        if not customer_id:
            raise ValidationError("User is not logged in.")
        if not address_id:
            raise ValidationError("Address was not selected.")

        # Step 2: Create the appointment (via DAL)
        appointment_id = db_writer.create_appointment(
            address_id, 
            data['date'], 
            data['time'], 
            data.get('notes', '')
        )

        if not appointment_id:
            raise Exception("Failed to create appointment or get new ID.")

        # Step 3: Link any selected services to the new appointment (via DAL)
        service_ids = data.get('service_ids', [])
        for service_id in service_ids:
            db_writer.link_service_to_appointment(appointment_id, service_id)

        return {"success": True, "appointment_id": appointment_id}

    except Exception as e:
        print(f"An error occurred during appointment creation: {e}")
        raise e

def get_all_services():
    """Fetches all available services from the database (pass-through to DAL)."""
    return db_reader.get_all_services()

def create_appointment(customer_id, data):
    """
    Creates a new appointment in the database (alternate version).
    Coordinates creation of appointment and linking of services.
    """
    try:
        # Step 1: Create the main appointment record (via DAL)
        appointment_id = db_writer.create_appointment(
            data['address_id'],
            data['date'],
            data['time'],
            data.get('notes', '')
            # Note: Your original function had 'notification_preference'.
            # If needed, you must add that field to the DB_write.create_appointment function.
        )
        
        if not appointment_id:
            raise Exception("Failed to create appointment or get new ID.")

        # Step 2: Link services (via DAL)
        service_ids = data.get('service_ids', [])
        for service_id in service_ids:
            db_writer.link_service_to_appointment(appointment_id, service_id)

        return appointment_id
    except Exception as e:
        print(f"Error creating appointment: {e}")
        raise e

def delete_appointment(appointment_id):
    """
    Business-logic wrapper to delete an appointment by ID.
    Delegates to DB_write.delete_appointment_by_id.
    """
    try:
        db_writer.delete_appointment_by_id(appointment_id)
        return {"success": True}
    except Exception as e:
        raise e


def update_appointment(appointment_id, data, user_id=None):
    """
    Update an appointment with basic validation.

    Args:
        appointment_id: ID of the appointment to update
        data: dict with keys address_id, date, time, notes (notes optional)
        user_id: optional, used for authorization checks
    """
    # Basic validation
    address_id = data.get('address_id')
    date = data.get('date')
    time = data.get('time')
    notes = data.get('notes', '')

    if not address_id or not date or not time:
        raise ValidationError('address_id, date and time are required to update an appointment')

    try:
        # Optionally: verify that the appointment belongs to the user (if user_id provided).
        if user_id:
            appts = db_reader.get_appointments_for_customer(user_id)
            if not any(a.get('id') == appointment_id for a in appts):
                raise ValidationError('Not authorized to update this appointment')

        db_writer.update_appointment_by_id(appointment_id, address_id, date, time, notes)
        return {"success": True}
    except Exception as e:
        raise e

