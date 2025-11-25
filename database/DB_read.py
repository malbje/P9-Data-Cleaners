# database/DB_read.py
# This file contains ALL functions that read from the database (Data Access Layer).
# ONLY THIS FILE (and DB_write) MAY IMPORT DB_access.

import sys, os
sys.path.insert(0, os.getcwd()) # This should be removed when using a proper package structure
from database.DB_access import get_connection
from datetime import timedelta # Required for time conversion
from typing import List, Dict, Optional, Any
from mysql.connector import Error # This may be used for error handling

class DB_read:

    def __init__(self): # Constructor
        pass

    def __open_DB_connection(self):
        """Opens a new DB connection with a dictionary cursor."""
        database = get_connection()
        cursorObject = database.cursor(dictionary=True) # Use dictionary cursor
        return database, cursorObject

    def __close_DB_connection(self, dataBase):
        """Closes the DB connection."""
        if dataBase and dataBase.is_connected():
            dataBase.close()

    def get_all_customers(self):
        """Fetches all customers."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM customers"
            cursorObject.execute(query)
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def search_customers(self, query: str = "", limit: int = 20):
        """
        Flexible search across customers (name, surname, email).
        Returns up to `limit` rows.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            like = f"%{query}%"
            sql = """
                SELECT *
                FROM customers
                WHERE name LIKE %s OR surname LIKE %s OR email LIKE %s
                ORDER BY id
                LIMIT %s
            """
            cursorObject.execute(sql, (like, like, like, limit))
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)
    
    def get_all_appointments(self):
        """Fetches all appointments (simple query)."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM appointments"
            cursorObject.execute(query)
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)
    
    def get_appointments_by_customer_id(self, customer_id):
        """Fetches all appointments for a specific customer."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = """
                SELECT apt.* FROM appointments apt
                JOIN addresses addr ON apt.address_id = addr.id
                JOIN lives_in li ON addr.id = li.address_id
                WHERE li.customer_id = %s
            """
            cursorObject.execute(query, (customer_id,))
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def get_appointments_by_address_id(self, address_id):
        """Fetches all appointments for a specific address, including service names."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = """
                SELECT 
                    apt.id, 
                    apt.date, 
                    apt.time, 
                    apt.notes,
                    apt.address_id,
                    GROUP_CONCAT(s.name SEPARATOR ', ') AS service_names
                FROM appointments apt
                LEFT JOIN has_ordered ho ON apt.id = ho.appointment_id
                LEFT JOIN services s ON ho.service_id = s.id
                WHERE apt.address_id = %s
                GROUP BY apt.id
                ORDER BY apt.date, apt.time;
            """
            cursorObject.execute(query, (address_id,))
            appointments = cursorObject.fetchall()
            # Convert date/time objects to strings for JSON serialization
            for appt in appointments:
                if appt.get('date'):
                    appt['date'] = appt['date'].isoformat()
                if appt.get('time') and isinstance(appt['time'], timedelta):
                    total_seconds = appt['time'].total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    appt['time'] = f"{hours:02}:{minutes:02}"
            return appointments
        finally:
            self.__close_DB_connection(database)

    def get_customer_by_id(self, customer_id):
        """Fetches a specific customer by ID."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM customers WHERE id = %s"
            cursorObject.execute(query, (customer_id,))
            return cursorObject.fetchone()
        finally:
            self.__close_DB_connection(database)

    def get_addresses_by_customer_id(self, customer_id: int):
        """
        Return basic addresses (no preferences) for a given customer id.
        Used by API routes that only need the address list.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            cursorObject.execute(
                """
                SELECT a.id, a.street_and_number, a.postal_code, a.city_name
                FROM addresses a
                JOIN lives_in li ON li.address_id = a.id
                WHERE li.customer_id = %s
                ORDER BY a.id
                """,
                (customer_id,)
            )
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def get_customer_by_email(self, email):
        """
        Finds a customer by email. 
        This was moved from database_logic.py.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            # Query from database_logic.py, as it was more specific
            query = "SELECT id, name, surname, email, notification_preference FROM customers WHERE email = %s"
            cursorObject.execute(query, (email.lower().strip(),))
            return cursorObject.fetchone()
        finally:
            self.__close_DB_connection(database)

    def find_address_by_text(self, search_text: str): #værd opmærksom på denne metode - kan være en der laver fejl i AI logik
        """
        Search addresses across street, postal code and city using partial matching.
        Returns list of matching addresses.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            like = f"%{search_text}%"
            cursorObject.execute(
                """
                SELECT id, street_and_number, postal_code, city_name
                FROM addresses
                WHERE street_and_number LIKE %s
                OR postal_code LIKE %s
                OR city_name LIKE %s
                OR CONCAT(street_and_number, ' ', postal_code, ' ', city_name) LIKE %s
                ORDER BY id
                """,
                (like, like, like, like)
            )
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def find_address(self, street_and_number, postal_code):
        """Finds an address by street and postal code to avoid duplicates."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM addresses WHERE street_and_number = %s AND postal_code = %s"
            cursorObject.execute(query, (street_and_number, postal_code))
            return cursorObject.fetchone()
        finally:
            self.__close_DB_connection(database)

    def get_address_by_id(self, address_id: int):
        """
        Get address by ID.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            cursorObject.execute(
                "SELECT * FROM addresses WHERE id = %s",
                (address_id,)
            )
            return cursorObject.fetchone()
        finally:
            self.__close_DB_connection(database)

    def get_appointment_by_id(self, appointment_id):
        """Fetches a specific appointment by ID."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM appointments WHERE id = %s"
            cursorObject.execute(query, (appointment_id,))
            return cursorObject.fetchone()
        finally:
            self.__close_DB_connection(database)

    def get_customers_by_appointment_id(self, appointment_id: int):
        """
        Retrieve all customers linked to an appointment via the appointment's address and lives_in table.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            query = """
                SELECT customers.*
                FROM customers
                INNER JOIN lives_in ON customers.id = lives_in.customer_id
                INNER JOIN appointments ON appointments.address_id = lives_in.address_id
                WHERE appointments.id = %s
            """
            cursorObject.execute(query, (appointment_id,))
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def get_customers_by_address_id(self, address_id: int):
        """
        Return all customers for a specific address_id (via lives_in join).
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            query = """
                SELECT customers.*
                FROM customers
                JOIN lives_in ON customers.id = lives_in.customer_id
                WHERE lives_in.address_id = %s
            """
            cursorObject.execute(query, (address_id,))
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def get_joint_customers_appointments_data(self):
        """
        Creates a detailed list of all appointments with customer, address, and service info.
        (This replaces `get_all_appointments` from `database_logic.py`)
        """
        database, cursorObject = self.__open_DB_connection()
        try:
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
                GROUP BY apt.id, apt.date, apt.time, apt.notes,
                         addr.street_and_number, addr.postal_code, addr.city_name,
                         c.name, c.surname, c.email
                ORDER BY apt.date, apt.time
            """
            cursorObject.execute(query)
            appointments = cursorObject.fetchall()
            for appt in appointments: # Format for JSON
                if appt.get('date'): appt['date'] = appt['date'].isoformat()
                if appt.get('time') and isinstance(appt['time'], timedelta): 
                    appt['time'] = str(appt['time']) # Simple string conversion for timedelta
            return appointments
        finally:
            self.__close_DB_connection(database)

    def get_appointments_by_customer_email(self, customer_email):
        """Gets all appointments for a customer based on their email address."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = """
                SELECT apt.* FROM appointments apt
                JOIN addresses addr ON apt.address_id = addr.id
                JOIN lives_in li ON addr.id = li.address_id
                JOIN customers c ON li.customer_id = c.id
                WHERE c.email = %s
            """
            cursorObject.execute(query, (customer_email,))
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def get_addresses_and_preferences_for_customer(self, customer_id):
        """
        Gets all addresses and their associated preferences for a specific customer.
        Moved from database_logic.py
        """
        database, cursorObject = self.__open_DB_connection()
        try:
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
            cursorObject.execute(query, (customer_id,))
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def get_all_services(self):
        """
        Fetches all available services from the database.
        Moved from database_logic.py
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            cursorObject.execute("SELECT id, name, length FROM services ORDER BY name")
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def get_appointments_for_customer(self, customer_id):
        """
        Gets all appointments for a specific customer, including address and services.
        Moved from database_logic.py
        """
        database, cursorObject = self.__open_DB_connection()
        try:
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
            cursorObject.execute(query, (customer_id,))
            appointments = cursorObject.fetchall()
            
            # Convert data types for JSON
            for appt in appointments:
                if appt.get('date'):
                    appt['date'] = appt['date'].isoformat()
                if appt.get('time') and isinstance(appt['time'], timedelta):
                    total_seconds = appt['time'].total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    appt['time'] = f"{hours:02}:{minutes:02}"
            
            return appointments
        except Exception as e:
            print(f"--- CRITICAL ERROR in get_appointments_for_customer: {e} ---")
            return []
        finally:
            self.__close_DB_connection(database)

    
    def search_customers_by_name(self, query: Optional[str] = None, limit: int = 100):
        """
        Searches for customers whose names contain the given substring (name, surname, email).
        If `query` is None or empty, returns up to `limit` customers ordered by name and surname.
        """
        database, cursorObject = self.__open_DB_connection()  # Open DB connection
        try:
            if not query:
                sql = "SELECT id, name, surname, email FROM customers ORDER BY name, surname LIMIT %s"
                cursorObject.execute(sql, (limit,))
            else:
                sql = """
                    SELECT id, name, surname, email
                    FROM customers
                    WHERE CONCAT(name, ' ', surname, ' ', email) LIKE %s
                    OR name LIKE %s
                    OR surname LIKE %s
                    OR email LIKE %s
                    ORDER BY name, surname
                    LIMIT %s
                    """
                like_query = f"%{query}%"
                cursorObject.execute(sql, (like_query, like_query, like_query, like_query, limit))
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    def get_customer_by_name_or_email(self, name_or_email: str) -> Optional[Dict[str, any]]:
        """
        Finds first match on name/surname or email.
        Good for questions like: 'Who is Anne Madsen?' Or 'find customer with anne@...' .
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            sql = """
                SELECT id, name, surname, email
                FROM customers
                WHERE email = %s
                OR CONCAT(name, ' ', surname) LIKE %s
                OR name LIKE %s
                OR surname LIKE %s
                LIMIT 1
            """
            like = f"%{name_or_email}%"
            cursorObject.execute(sql, (name_or_email, like, like, like))
            return cursorObject.fetchone()
        finally:
            self.__close_DB_connection(database)

    def get_addresses_for_customer_name_or_email(self, name_or_email: str) -> List[Dict[str, Any]]:
        """
        Returns all addresses for a customer when only the name or email is known.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            sql = """
                SELECT 
                    a.id AS address_id,
                    a.street_and_number,
                    a.postal_code,
                    a.city_name,
                    c.id AS customer_id,
                    c.name,
                    c.surname,
                    c.email
                FROM customers c
                JOIN lives_in li ON li.customer_id = c.id
                JOIN addresses a ON a.id = li.address_id
                WHERE c.email = %s
                OR CONCAT(c.name, ' ', c.surname) LIKE %s
                OR c.name LIKE %s
                OR c.surname LIKE %s
                ORDER BY a.id
            """
            like = f"%{name_or_email}%"
            cursorObject.execute(sql, (name_or_email, like, like, like))
            rows = cursorObject.fetchall()
            return rows
        finally:
            self.__close_DB_connection(database)

    # NEW: Notification-safe appointment fetcher
    def get_appointments_for_notifications(self):
        """
        A simple appointment query that avoids GROUP BY issues.
        Returns customer name, email, date, time for all upcoming appointments.
        Safe to use for the notification service.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            query = """
                SELECT 
                    a.id AS appointment_id,
                    c.name AS name,
                    c.surname AS surname,
                    c.email AS email,
                    a.date AS date,
                    a.time AS time
                FROM appointments a
                JOIN addresses ad ON ad.id = a.address_id
                JOIN lives_in li ON li.address_id = ad.id
                JOIN customers c ON c.id = li.customer_id
                ORDER BY a.date ASC, a.time ASC;
            """
            cursorObject.execute(query)
            return cursorObject.fetchall()
        finally:
            self.__close_DB_connection(database)

    # ----------------------------------------------------------------
    # New methods for chatbot integration can be added here as needed.
    # ----------------------------------------------------------------
