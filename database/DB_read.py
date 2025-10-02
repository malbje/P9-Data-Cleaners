#------------------------------
#  Collection of methods used for reading data from the database.
#
#  Use this by creating a DB_read object in the file you're working on.
#  Example: import database.DB_read as DB_reader
#          DB_read_object = DB_reader.DB_read()
#          data = DB_read_object.all_customers()
#------------------------------

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

# Imports
import mysql.connector, private_settings

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

    def get_all_customers(self):
        """
        Method for getting a list of all customers from the database.

        Returns:
            List of tuples, each containing customer data.
        """
        # We try to qurry successfully...
        try:
            database, cursorObject = self.__open_DB_connection() # Always start with opening a new connection

            query = "SELECT * FROM customers"                  # The SQL query to be executed

            cursorObject.execute(query)                        # Executing the query
            customers = cursorObject.fetchall()                # Getting all results from the executed query

        # ...But if the qurry fails for some reason, we always close the connection
        finally:
            self.__close_DB_connection(database)               # Always remember to close the database connection when done

        return customers
    
    def get_all_appointments(self):
        """
        Method for getting a list of all cleaning appointments from the database.

        Returns:
            List of tuples, each containing appointment data.
        """
        # We try to qurry successfully...
        try:
            database, cursorObject = self.__open_DB_connection() # Always start with opening a new connection

            query = "SELECT * FROM appointments"               # The SQL query to be executed

            cursorObject.execute(query)                        # Executing the query
            appointments = cursorObject.fetchall()             # Getting all results from the executed query

        # ...But if the qurry fails for some reason, we always close the connection
        finally:
            self.__close_DB_connection(database)               # Always remember to close the database connection when done

        return appointments
    
    def get_appointments_by_customer_id(self, customer_id):
        """
        Method for getting a list of all cleaning appointments for a specific customer from the database.

        Args:
            customer_id (int): The ID of the customer.
        
        Returns:
            List of tuples, each containing appointment data for the specified customer.
            If no appointments are found, returns a message saying so.
        """
        try:
            database, curserObject = self.__open_DB_connection()

            query = "SELECT * FROM appointments WHERE customer_id = %s"

            curserObject.execute(query, (customer_id,))
            appointments = curserObject.fetchall()

            if appointments:
                return appointments
            else:
                return "No appointments found for this customer ID."
            
        finally:
            self.__close_DB_connection(database)

    def get_customer_by_id(self, customer_id):
        """
        A method for getting the customer with given ID number
        
        Args:
            customer_id (int): The ID (primary key) of the customer.

        Resturns:
            List of tuples, each containing customer data matching the ID.
            If no customer is found, returns a message saying so.
        """
        try:
            database, cursorObject = self.__open_DB_connection()

            query = "SELECT * FROM customers WHERE id = %s"

            cursorObject.execute(query, (customer_id,))
            customer = cursorObject.fetchall()

            if customer:
                return customer
            else:
                return "No customer found with this ID."
            
        finally:
            self.__close_DB_connection(database)

    def get_appointment_by_id(self, appointment_id):
        """
        Method for getting a specific appointment by its ID.

        Args:
            appointment_id (int): The ID of the appointment.

        Returns:
            List of tuples, each containing appointment data matching the ID.
            If no appointment is found, returns a message saying so.
        """
        try:
            database, cursorObject = self.__open_DB_connection()

            query = "SELECT * FROM appointments WHERE id = %s"

            cursorObject.execute(query, (appointment_id,))
            appointment = cursorObject.fetchall()

            if appointment:
                return appointment
            else:
                return "No appointment found with this ID."
        finally:
            self.__close_DB_connection(database)

    def get_joint_customers_appointments_data(self):
        """
        Creates a joint table of customers with their appointments.

        Returns:
            List of tuples, each containing data on a customer and their appointments.
        """
        try:
            database, cursorObject = self.__open_DB_connection()

            query = "SELECT name, address, email, location_addr, appt_date, appt_time " \
                    "FROM customers INNER JOIN appointments ON customers.id = appointments.customer_id"

            cursorObject.execute(query)
            result = cursorObject.fetchall()

            return result
        
        finally:
            self.__close_DB_connection(database)