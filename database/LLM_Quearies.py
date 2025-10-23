# DB_read.py - Database access layer with CRUD functions for customers, addresses, and appointments.
# Returns dictionaries for JSON serialization. Includes legacy DB_read class for backwards compatibility.

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

# Imports
import mysql.connector, private_settings  # MySQL connector and database credentials
from database.DB_access import get_connection  # Database connection factory - referenced from database/DB_access.py
from mysql.connector import IntegrityError  # For handling duplicate key and constraint violations



class DB_read:

    def __init__(self): # Constructor
        pass

    def __open_DB_connection(self): # The '__'at in the name means it's a private method
        """
        Method for opening a new database connection and returning the new connection and cursor object.
        The cursor object is used for executing queries.

        Returns:
            The database connection object AND The cursor object for executing queries  
        """
        database = mysql.connector.connect(  # Creates the database connection
        host = private_settings.host,        # Remember to edit private_settings.py with your own connection password
        user = private_settings.user,
        passwd = private_settings.passwd,
        database = private_settings.database
        )

        cursorObject = database.cursor()     # Defines the cursor object used for executing queries

        return database, cursorObject        # dataBase: The object that executes queries on the database
                                             # cursorObject: The object that holds the database connection


    def __close_DB_connection(self, dataBase): # The '__'at in the name means it's a private method
        """
        Remember to close the database connection when done, with this.
        """
        dataBase.close()


#### Standalone Functions Used by OpenAI Integration in main.py ####
# These functions provide database access for the OpenAI language model integration.
# They return dictionaries for easy JSON serialization and include proper error handling.

def list_customers():
    """
    Get all customers ordered by ID.
    
    Returns:
        list: Customer dictionaries with id, name, surname, email, notification_preference
    """
    db = get_connection()
    try: 
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM customers ORDER BY id"
        )
        return cur.fetchall()
    finally:
        db.close()


def list_customers_by_name(name: str, surname: str):
    """
    Find customers using partial name matching (LIKE search).
    
    Args:
        name (str): First name (partial match allowed)
        surname (str): Surname (partial match allowed)
            
    Returns:
        list: Matching customer dictionaries
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT * 
            FROM customers 
            WHERE name LIKE %s 
            AND surname LIKE %s 
            ORDER BY id
            """,
            (f"%{name}%", f"%{surname}%")
        )
        return cur.fetchall()
    finally:
        db.close()

def get_customer_by_email(email: str):
    """
    Get customer by unique email address.
    
    Args:
        email (str): Customer email address
        
    Returns:
        dict: Customer data or None if not found
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT * 
            FROM customers 
            WHERE email = %s
            """,
            (email,)
        )
        return cur.fetchone()
    finally:
        db.close()

def get_customer_by_id(customer_id: int):
    """
    Get customer by ID.
    
    Args:
        customer_id (int): Customer ID
        
    Returns:
        dict: Customer data or None if not found
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT * 
            FROM customers 
            WHERE id = %s
            """,
            (customer_id,)
        )
        return cur.fetchone()
    finally:
        db.close()


def add_customer(name: str, surname: str, email: str, notification_preference: str):
    """
    Create new customer. Fails if email exists.
    
    Args:
        name (str): First name
        surname (str): Last name
        email (str): Unique email address
        notification_preference (str): Notification method
        
    Returns:
        dict: Created customer with id, or error dict if email exists
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            INSERT INTO customers (name, surname, email, notification_preference) 
            VALUES (%s, %s, %s, %s)
            """,
            (name, surname, email, notification_preference)
        )
        db.commit()
        return {"id": cur.lastrowid, "name": name, "surname": surname, "email": email, "notification_preference": notification_preference}
    except IntegrityError as e:
        return {"error": "Email already exists", "details": str(e)}

def add_address(city_name: str, postal_code: str, street_and_number: str):
    """
    Add new address to database.
    
    Args:
        city_name (str): City name
        postal_code (str): Postal code
        street_and_number (str): Street and number
        
    Returns:
        dict: Number of updated rows
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            INSERT INTO addresses (city_name, postal_code, street_and_number) 
            VALUES (%s, %s, %s)
            """,
            (city_name, postal_code, street_and_number)
        )
        db.commit()
        return {"updated_rows": cur.rowcount}
    finally:
        db.close()

def add_appointment(address_id: int, date: str, time: str, notes: str = "", notification_preference: str = "email"):
    """
    Create new appointment with error handling and rollback.
    
    Args:
        address_id (int): Address ID where appointment takes place
        date (str): Date in YYYY-MM-DD format
        time (str): Time in HH:MM format
        notes (str, optional): Appointment notes. Default empty string
        notification_preference (str, optional): Notification method. Default "email"
            
    Returns:
        dict: Created appointment with id, or error dict on failure
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            INSERT INTO appointments (address_id, date, time, notes, notification_preference) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (address_id, date, time, notes, notification_preference)
        )
        db.commit()
        return {"id": cur.lastrowid, "address_id": address_id, "date": date, "time": time, "notes": notes, "notification_preference": notification_preference}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create appointment: {str(e)}"}
    finally:
        db.close()

def update_customer_address(customer_id: int, address_id: int , city_name: str, postal_code: str, street_and_number: str):
    """
    Update customer address via JOIN with lives_in table.
    
    Args:
        customer_id (int): Customer ID
        address_id (int): Address ID
        city_name (str): New city name
        postal_code (str): New postal code
        street_and_number (str): New street and number
        
    Returns:
        dict: Number of updated rows
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            UPDATE addresses 
            INNER JOIN lives_in 
                ON lives_in.address_id = addresses.id 
            SET addresses.city_name = %s, 
                addresses.postal_code = %s, 
                addresses.street_and_number = %s 
            WHERE addresses.id = %s 
                AND lives_in.customer_id = %s
            """,
            (city_name, postal_code, street_and_number, address_id, customer_id)
        )
        db.commit()
        return {"updated_rows": cur.rowcount}
    finally:
        db.close()

def get_appointment_by_id(appointment_id: int):
    """
    Get appointment by ID.
    
    Args:
        appointment_id (int): Appointment ID
        
    Returns:
        dict: Appointment data or None
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT * 
            FROM appointments 
            WHERE id = %s
            """,
            (appointment_id,)
        )
        return cur.fetchone()
    finally:
        db.close()

def get_customers_by_address_id(address_id: int):
    """
    Get all customers at address via lives_in JOIN.
    
    Args:
        address_id (int): Address ID
        
    Returns:
        list: Customer dictionaries
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT customers.* 
            FROM customers 
            INNER JOIN lives_in 
                ON customers.id = lives_in.customer_id 
            WHERE lives_in.address_id = %s
            """,
            (address_id,)
        )
        return cur.fetchall()
    finally:
        db.close()

def get_customers_by_appointment_id(appointment_id: int):
    """
    Get customers by appointment via lives_in and appointments JOIN.
    
    Args:
        appointment_id (int): Appointment ID
        
    Returns:
        list: Customer dictionaries
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT customers.* 
            FROM customers 
            INNER JOIN lives_in 
                ON lives_in.customer_id = customers.id 
            INNER JOIN appointments 
                ON appointments.address_id = lives_in.address_id 
            WHERE appointments.id = %s
            """,
            (appointment_id,)
        )
        return cur.fetchall()
    finally:
        db.close()

def get_appointments_by_address_id(address_id: int):
    """
    Get all appointments at address ordered by date and time.
    
    Args:
        address_id (int): Address ID
        
    Returns:
        list: Appointment dictionaries
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT * 
            FROM appointments 
            WHERE address_id = %s 
            ORDER BY date, time
            """,
            (address_id,)
        )
        return cur.fetchall()
    finally:
        db.close()

def delete_customer(customer_id: int):
    """
    Delete customer by ID.
    
    Args:
        customer_id (int): Customer ID
        
    Returns:
        dict: Number of deleted rows
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            DELETE FROM customers 
            WHERE id = %s
            """,
            (customer_id,)
        )
        db.commit()
        return {"deleted_rows": cur.rowcount}
    finally:
        db.close()

def find_address_by_text(search_text: str):
    """
    Search addresses across street, postal code, and city using partial matching.
    Converts natural language addresses to address_id.
    
    Args:
        search_text (str): Text to search (case-insensitive LIKE)
            
    Returns:
        list: Matching address dictionaries with id, street_and_number, postal_code, city_name
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT id, street_and_number, postal_code, city_name 
            FROM addresses 
            WHERE street_and_number LIKE %s 
            OR postal_code LIKE %s 
            OR city_name LIKE %s 
            OR CONCAT(street_and_number, ' ', postal_code, ' ', city_name) LIKE %s
            ORDER BY id
            """,
            (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", f"%{search_text}%")
        )
        return cur.fetchall()
    finally:
        db.close()

def get_address_by_id(address_id: int):
    """
    Get address by ID.
    
    Args:
        address_id (int): Address ID
        
    Returns:
        dict: Address data or None
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT * 
            FROM addresses 
            WHERE id = %s
            """,
            (address_id,)
        )
        return cur.fetchone()
    finally:
        db.close()
