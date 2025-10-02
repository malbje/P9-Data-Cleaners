#------------------------------
#  Collection of methods used for reading data from the database.
#
#  Use this by creating a DB_read object in the file you're working in.
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

    global cursorObject # The object that executes queries on the database
    
    global dataBase     # The object that holds the database connection

    def __init__(self): # Constructor
        """
        Setting up the database connection and cursor object when a new DB_read object is created.

        Args:
            "Self" means that this method is an instance method
        """

        global cursorObject, dataBase        # Gives this method access to these global objects

        dataBase = mysql.connector.connect(  # Creates the database connection
        host = private_settings.host,
        user = private_settings.user,
        passwd = private_settings.passwd,
        database = private_settings.database
        )

        cursorObject = dataBase.cursor()     # Defines the cursor object used for executing queries

    def open_DB_connection(self):
        """
        Method for opening a new database connection and returning the new connection and cursor object.
        Same as in the constructor, but can be called again if needed.
        """
        dataBase = mysql.connector.connect(
        host = private_settings.host,
        user = private_settings.user,
        passwd = private_settings.passwd,
        database = private_settings.database
        )

        cursorObject = dataBase.cursor()

        return dataBase, cursorObject

    def close_DB_connection(self, dataBase):
        dataBase.close()

    def all_customers(self):
        dataBase, cursorObject = self.open_DB_connection()

        query = "SELECT * FROM customers"
        cursorObject.execute(query)

        customors = cursorObject.fetchall()
        self.close_DB_connection(dataBase)

        return customors