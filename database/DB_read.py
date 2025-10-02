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

    def open_DB_connection(self):
        """
        Method for opening a new database connection and returning the new connection and cursor object.
        The cursor object is used for executing queries.

        Returns:
            The database connection object AND The cursor object for executing queries  
        """
        dataBase = mysql.connector.connect(  # Creates the database connection
        host = private_settings.host,        # Remember to edit private_settings.py with your own connection password
        user = private_settings.user,
        passwd = private_settings.passwd,
        database = private_settings.database
        )

        cursorObject = dataBase.cursor()     # Defines the cursor object used for executing queries

        return dataBase, cursorObject        # dataBase: The object that executes queries on the database
                                             # cursorObject: The object that holds the database connection


    def close_DB_connection(self, dataBase):
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
            dataBase, cursorObject = self.open_DB_connection() # Always start with opening a new connection

            query = "SELECT * FROM customers"                  # The SQL query to be executed
            cursorObject.execute(query)                        # Executing the query

            customers = cursorObject.fetchall()                # Getting all results from the executed query

        # ...But if the qurry fails for some reason, we always close the connection
        finally:
            self.close_DB_connection(dataBase)                 # Always remember to close the database connection when done

        return customers