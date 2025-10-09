# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

# Imports
import mysql.connector, private_settings
import database.DB_read as DB_reader

class DB_write:

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

    def create_user(self, name, address, email):
        """
        Creates a new user in the database.
        """
        try:
            dataBase, cursorObject = self.__open_DB_connection() # Opens a new database connection

            query = "INSERT INTO customers (name, address, email) VALUES (%s, %s, %s)" # The query to be executed
            new_user = (name, address, email)                                          # The new user to be added, as a tuple

            cursorObject.execute(query, new_user)               # Executes the query
            dataBase.commit()                                    # Commits the changes to the database
        finally:
            self.__close_DB_connection(dataBase)                 # Closes the database connection

    def create_appointment(self, customer_id, location_addr, appt_date, appt_time):
        """
        Creates a new appointment in the database.
        """
        try:
            database, cursorObject = self.__open_DB_connection() # Opens a new database connection

            query = "INSERT INTO appointments (customer_id, location_addr, appt_date, appt_time) VALUES (%s, %s, %s, %s)" # The query to be executed
            new_appointment = (customer_id, location_addr, appt_date, appt_time)                                          # The new appointment to be added, as a tuple

            cursorObject.execute(query, new_appointment)               # Executes the query
            database.commit()                                    # Commits the changes to the database
        finally:
            self.__close_DB_connection(database)                 # Closes the database connection

    def update_user_by_id(self, id, name, address, email):
        """
        Updates a user in the database by its id.
        """
        try:
            dataBase, cursorObject = self.__open_DB_connection() # Opens a new database connection

            query = "UPDATE customers SET name = %s, address = %s, email = %s WHERE id = %s" # The query to be executed
            updated_user = (name, address, email, id)                                          # The updated user data, as a tuple

            cursorObject.execute(query, updated_user)               # Executes the query
            dataBase.commit()                                    # Commits the changes to the database
        finally:
            self.__close_DB_connection(dataBase)                 # Closes the database connection

    def update_appointment_by_id(self, id, customer_id, location_addr, appt_date, appt_time):

        try:
            database, cursorObject = self.__open_DB_connection() # Opens a new database connection

            query = "UPDATE appointments SET customer_id = %s, location_addr = %s, appt_date = %s, appt_time = %s WHERE id = %s" # The query to be executed
            updated_appointment = (customer_id, location_addr, appt_date, appt_time, id)                                          # The updated appointment data, as a tuple

            cursorObject.execute(query, updated_appointment)               # Executes the query
            database.commit()                                    # Commits the changes to the database
        
        finally:
            self.__close_DB_connection(database)                 # Closes the database connection

    def delete_user_by_id(self, id):
        """
        Deletes a user from the database by its id.
        """
        try:
            dataBase, cursorObject = self.__open_DB_connection() # Opens a new database connection

            query = "DELETE FROM customers WHERE id = %s"            # The query to be executed
            customer_id = (id,)                                           # The id to be deleted, as a tuple

            cursorObject.execute(query, customer_id)                 # Executes the query
            dataBase.commit()      
                                          # Commits the changes to the database
        finally:
            self.__close_DB_connection(dataBase)                 # Closes the database connection

    def delete_appointment_by_id(self, id):
        """
        Deletes an appointment from the database by its id.
        """
        try:
            dataBase, cursorObject = self.__open_DB_connection() # Opens a new database connection

            query = "DELETE FROM appointments WHERE id = %s"     # The query to be executed
            appointment_id = (id,)                               # The id to be deleted, as a tuple

            cursorObject.execute(query, appointment_id)          # Executes the query
            dataBase.commit()                                    # Commits the changes to the database
        finally:
            self.__close_DB_connection(dataBase)                 # Closes the database connection

    def update_user_name_by_id(self, id, name):

        db_reader = DB_reader.DB_read()
        customer = db_reader.get_customer_by_id(id)

        id, _, address, email = customer[0]
        self.update_user_by_id(id, name, address, email)

    def update_user_address_by_id(self, id, address):

        db_reader = DB_reader.DB_read()
        customer = db_reader.get_customer_by_id(id)

        id, name, _, email = customer[0]
        self.update_user_by_id(id, name, address, email)

    def update_user_email_by_id(self, id, email):

        db_reader = DB_reader.DB_read()
        customer = db_reader.get_customer_by_id(id)

        id, name, address, _ = customer[0]
        self.update_user_by_id(id, name, address, email)

    def update_appointment_location_by_id(self, id, location_addr):

        db_reader = DB_reader.DB_read()
        appointment = db_reader.get_appointment_by_id(id)

        id, customer_id, _, appt_date, appt_time = appointment[0]
        self.update_appointment_by_id(id, customer_id, location_addr, appt_date, appt_time)

    def update_appointment_date_by_id(self, id, appt_date):

        db_reader = DB_reader.DB_read()
        appointment = db_reader.get_appointment_by_id(id)

        id, customer_id, location_addr, _, appt_time = appointment[0]
        self.update_appointment_by_id(id, customer_id, location_addr, appt_date, appt_time)

    def update_appointment_time_by_id(self, id, appt_time):

        db_reader = DB_reader.DB_read()
        appointment = db_reader.get_appointment_by_id(id)

        id, customer_id, location_addr, appt_date, _ = appointment[0]
        self.update_appointment_by_id(id, customer_id, location_addr, appt_date, appt_time)


db_writer = DB_write()

# db_writer.create_user("mig", "min adresse", "min email")

# db_writer.update_user_by_id(16, "dig", "din adresse", "din email")

db_writer.update_user_name_by_id(15, "Henrik")