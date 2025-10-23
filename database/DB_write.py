# database/DB_write.py
# This file contains ALL functions that write to the database (Data Access Layer).
# ONLY THIS FILE (and DB_read) MAY IMPORT DB_access.

import sys, os
sys.path.insert(0, os.getcwd()) # This should be removed when using a proper package structure
from database.DB_access import get_connection

class DB_write:

    def __init__(self): # Constructor
        pass

    def __execute_query(self, query, params=None, commit=False):
        """
        A private helper method to execute a query.
        Manages connection opening, execution, committing, and closing.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            # For INSERT queries, we want to return the new ID
            if cursor.lastrowid:
                return cursor.lastrowid
        finally:
            if conn and conn.is_connected():
                conn.close()

    def create_customer(self, name, surname, email):
        """
        Creates a new customer in the database.
        """
        query = "INSERT INTO customers (name, surname, email) VALUES (%s, %s, %s)"
        new_user = (name, surname, email.strip().lower())
        return self.__execute_query(query, new_user, commit=True)

    def create_address(self, street_and_number, postal_code, city_name):
        """Creates a new address in the database."""
        query = "INSERT INTO addresses (street_and_number, postal_code, city_name) VALUES (%s, %s, %s)"
        new_address = (street_and_number, postal_code, city_name)
        return self.__execute_query(query, new_address, commit=True)

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