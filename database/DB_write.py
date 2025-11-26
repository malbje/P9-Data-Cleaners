# database/DB_write.py
# This file contains ALL functions that write to the database (Data Access Layer).
# ONLY THIS FILE (and DB_read) MAY IMPORT DB_access.

import sys, os
sys.path.insert(0, os.getcwd()) # This should be removed when using a proper package structure
from database.DB_access import get_connection
import logging

class DB_write:

    def __init__(self): # Constructor
        pass

    def __execute_query(self, query, params=None, commit=False):
        """
        A private helper method to execute a query.
        Manages connection opening, execution, committing, and closing.
        Returns lastrowid if available, otherwise rowcount. Raises on error.
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            # Prefer lastrowid when available (INSERT), otherwise rowcount
            lastid = getattr(cursor, 'lastrowid', None)
            if lastid:
                return lastid
            return getattr(cursor, 'rowcount', None)
        except Exception as e:
            logging.exception("Database query failed: %s", e)
            # Attempt rollback if a transaction is in progress
            try:
                if conn:
                    conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
            try:
                if conn and getattr(conn, "is_connected", lambda: True)():
                    conn.close()
            except Exception:
                pass

    def create_customer(self, name, surname, email, notification_preference=None):
        """
        Creates a new customer in the database.
        notification_preference is optional (e.g. 'none', '24h', '2h').
        """
        # store notification_preference in the customers table (nullable)
        query = "INSERT INTO customers (name, surname, email, notification_preference) VALUES (%s, %s, %s, %s)"
        new_user = (name, surname, email.strip().lower(), notification_preference)

        return self.__execute_query(query, new_user, commit=True)

    def create_address(self, street_and_number, postal_code, city_name):
        """Creates a new address in the database."""
        query = "INSERT INTO addresses (street_and_number, postal_code, city_name) VALUES (%s, %s, %s)"
        new_address = (street_and_number, postal_code, city_name)
        return self.__execute_query(query, new_address, commit=True)

    def add_prefrences_for_address_id(self, address_id, allergies = None, pets = None, kids = None, square_footage = None, notes = None):
        query = "INSERT INTO preferences (address_id, allergies, pets, kids, square_footage, notes) VALUES (%s, %s, %s, %s, %s, %s)"
        new_preferences = (address_id, allergies, pets, kids, square_footage, notes)
        return self.__execute_query(query, new_preferences, commit=True)

    def link_customer_to_address(self, customer_id, address_id):
        """Links a customer and an address in the lives_in table."""
        # First, check if the link already exists to avoid errors
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lives_in WHERE customer_id = %s AND address_id = %s", (customer_id, address_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            query = "INSERT INTO lives_in (customer_id, address_id) VALUES (%s, %s)"
            self.__execute_query(query, (customer_id, address_id), commit=True)
        else:
            cursor.close()
            conn.close()

    def link_service_to_appointment(self, appointment_id, service_id):
        """Links a service to an appointment in the has_ordered table."""
        query = "INSERT INTO has_ordered (appointment_id, service_id) VALUES (%s, %s)"
        self.__execute_query(query, (appointment_id, service_id), commit=True)

    def create_appointment(self, address_id, date, time, notes=""):
        """
        Creates a new appointment in the database.
        Note: You must provide a valid address_id.
        Returns the ID of the newly created appointment.
        """
        query = "INSERT INTO appointments (address_id, date, time, notes) VALUES (%s, %s, %s, %s)"
        new_appointment = (address_id, date, time, notes)
        return self.__execute_query(query, new_appointment, commit=True)

    def update_customer_by_id(self, id, name, surname, email):
        """
        Updates a customer in the database by their id.
        """
        query = "UPDATE customers SET name = %s, surname = %s, email = %s WHERE id = %s"
        updated_user = (name, surname, email, id)
        self.__execute_query(query, updated_user, commit=True)

    def update_appointment_by_id(self, id, address_id, date, time, notes):
        """
        Updates an appointment in the database by its id.
        """
        query = "UPDATE appointments SET address_id = %s, date = %s, time = %s, notes = %s WHERE id = %s"
        updated_appointment = (address_id, date, time, notes, id)
        self.__execute_query(query, updated_appointment, commit=True)

    # --- More efficient single-field updates ---

    def update_customer_name_by_id(self, id, name, surname):
        """Updates a customer's name and surname by their ID."""
        query = "UPDATE customers SET name = %s, surname = %s WHERE id = %s"
        self.__execute_query(query, (name, surname, id), commit=True)

    def update_customer_email_by_id(self, id, email):
        """Updates a customer's email by their ID."""
        query = "UPDATE customers SET email = %s WHERE id = %s"
        self.__execute_query(query, (email, id), commit=True)

    def update_customer_address(self, customer_id, address_id, city_name, postal_code, street_and_number):
        """
        Update the address record for a given customer/address pair.
        This uses an UPDATE with JOIN to ensure the address belongs to the customer (via lives_in).
        """
        query = """
            UPDATE addresses
            INNER JOIN lives_in ON lives_in.address_id = addresses.id
            SET addresses.city_name = %s, addresses.postal_code = %s, addresses.street_and_number = %s
            WHERE addresses.id = %s AND lives_in.customer_id = %s
        """
        self.__execute_query(query, (city_name, postal_code, street_and_number, address_id, customer_id), commit=True)

    def update_appointment_date_by_id(self, id, date):
        """Updates an appointment's date by its ID."""
        query = "UPDATE appointments SET date = %s WHERE id = %s"
        self.__execute_query(query, (date, id), commit=True)

    def update_appointment_time_by_id(self, id, time):
        """Updates an appointment's time by its ID."""
        query = "UPDATE appointments SET time = %s WHERE id = %s"
        self.__execute_query(query, (time, id), commit=True)

    # --- Deletion Methods ---

    def delete_customer_by_id(self, id):
        """
        Deletes a customer from the database by their id.
        Note: ON DELETE CASCADE will also delete related 'lives_in' entries.
        """
        query = "DELETE FROM customers WHERE id = %s"
        self.__execute_query(query, (id,), commit=True)

    def delete_appointment_by_id(self, id):
        """
        Deletes an appointment from the database by its id.
        Note: ON DELETE CASCADE will also delete related 'has_ordered' entries.
        """
        query = "DELETE FROM appointments WHERE id = %s"
        self.__execute_query(query, (id,), commit=True)

    def create_customer_with_address(self, payload):
        """
        Orchestrator to accept frontend payload (dict) and create a customer
        and optional address, linking them. Returns {'customer_id': ..., 'address_id': ...?}.
        Expected payload example:
          {
            "name": "Jane",
            "surname": "Doe",
            "email": "jane@example.com",
            "address": {
              "street_and_number": "Main 1",
              "postal_code": "12345",
              "city_name": "Town"
            }
          }
        """
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dict")

        name = payload.get("name")
        surname = payload.get("surname")
        email = payload.get("email")
        # Accept either key 'notifications' or 'notification_preference'
        notification_pref = payload.get("notifications") or payload.get("notification_preference")
        if not (name and surname and email):
            raise ValueError("Missing required customer fields: name, surname, email")

        # create customer
        customer_id = self.create_customer(name, surname, email, notification_preference=notification_pref)
        result = {"customer_id": customer_id}

        # optional address
        address = payload.get("address")
        if isinstance(address, dict):
            street = address.get("street_and_number")
            postal = address.get("postal_code")
            city = address.get("city_name")
            if street and postal and city:
                address_id = self.create_address(street, postal, city)
                # link them
                self.link_customer_to_address(customer_id, address_id)
                result["address_id"] = address_id

        return result
    
    def delete_preference_by_address_id(self, address_id):
        query = "DELETE FROM preferences WHERE address_id = %s"
        self.__execute_query(query, (address_id,), commit=True)

    def delete_orders_by_appointment_id(self, appointment_id):
        query = "DELETE FROM has_ordered WHERE appointment_id = %s"
        self.__execute_query(query, (appointment_id,), commit=True)