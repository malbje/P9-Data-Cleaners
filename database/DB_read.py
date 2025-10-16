#------------------------------
#  Collection of methods used for reading data from the database.
#
#  Use this by creating a DB_read object in the file you're working on.
#  Example: import database.DB_read as DB_reader
#          DB_read_object = DB_reader.DB_read()
#          data = DB_read_object.get_all_customers()
#------------------------------

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

# Imports
from database.DB_access import get_connection

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
        database = get_connection()
        cursorObject = database.cursor(dictionary=True) # Use dictionary cursor for easier data handling
        return database, cursorObject

    def __close_DB_connection(self, dataBase): # The '__'at in the name means it's a private method
        """
        Remember to close the database connection when done, with this.
        """
        if dataBase and dataBase.is_connected():
            dataBase.close()

    def get_all_customers(self):
        """
        Method for getting a list of all customers from the database.

        Returns:
            List of dictionaries, each containing customer data.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM customers"
            cursorObject.execute(query)
            customers = cursorObject.fetchall()
            return customers
        finally:
            self.__close_DB_connection(database)
    
    def get_all_appointments(self):
        """
        Method for getting a list of all cleaning appointments from the database.
        This is a basic query; for detailed info, use get_joint_customers_appointments_data.

        Returns:
            List of dictionaries, each containing appointment data.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM appointments"
            cursorObject.execute(query)
            appointments = cursorObject.fetchall()
            return appointments
        finally:
            self.__close_DB_connection(database)
    
    def get_appointments_by_customer_id(self, customer_id):
        """
        Method for getting a list of all cleaning appointments for a specific customer.

        Args:
            customer_id (int): The ID of the customer.
        
        Returns:
            List of dictionaries, each containing appointment data for the specified customer.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            # This query now joins through the necessary tables to link customers to appointments
            query = """
                SELECT apt.* 
                FROM appointments apt
                JOIN addresses addr ON apt.address_id = addr.id
                JOIN lives_in li ON addr.id = li.address_id
                WHERE li.customer_id = %s
            """
            cursorObject.execute(query, (customer_id,))
            appointments = cursorObject.fetchall()
            return appointments
        finally:
            self.__close_DB_connection(database)

    def get_appointments_by_address_id(self, address_id):
        """
        Gets all appointments for a specific address, including service details.
        """
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
                if appt.get('time'):
                    total_seconds = appt['time'].total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    appt['time'] = f"{hours:02}:{minutes:02}"
            return appointments
        finally:
            self.__close_DB_connection(database)

    def get_customer_by_id(self, customer_id):
        """
        A method for getting the customer with given ID number
        
        Args:
            customer_id (int): The ID (primary key) of the customer.

        Resturns:
            A dictionary containing customer data matching the ID, or None if not found.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM customers WHERE id = %s"
            cursorObject.execute(query, (customer_id,))
            customer = cursorObject.fetchone() # fetchone is better for single results
            return customer
        finally:
            self.__close_DB_connection(database)

    def get_customer_by_email(self, email):
        """Finds a user in the database by their email."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM customers WHERE email = %s"
            cursorObject.execute(query, (email.lower().strip(),))
            user = cursorObject.fetchone()
            return user
        finally:
            self.__close_DB_connection(database)

    def find_address(self, street_and_number, postal_code):
        """Finds an address by street and postal code to avoid duplicates."""
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM addresses WHERE street_and_number = %s AND postal_code = %s"
            cursorObject.execute(query, (street_and_number, postal_code))
            address = cursorObject.fetchone()
            return address
        finally:
            self.__close_DB_connection(database)

    def get_appointment_by_id(self, appointment_id):
        """
        Method for getting a specific appointment by its ID.

        Args:
            appointment_id (int): The ID of the appointment.

        Returns:
            A dictionary containing appointment data matching the ID, or None if not found.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            query = "SELECT * FROM appointments WHERE id = %s"
            cursorObject.execute(query, (appointment_id,))
            appointment = cursorObject.fetchone() # fetchone is better for single results
            return appointment
        finally:
            self.__close_DB_connection(database)

    def get_joint_customers_appointments_data(self):
        """
        Creates a detailed list of all appointments with customer, address, and service info.

        Returns:
            List of dictionaries, each containing detailed data on an appointment.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            # This query is updated to correctly join all the new tables
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
            cursorObject.execute(query)
            result = cursorObject.fetchall()
            return result
        finally:
            self.__close_DB_connection(database)

    def get_appointments_by_customer_email(self, customer_email):
        """
        Gets all appointments for a customer based on their email address.
        
        Args:
            customer_email (str): The email of the customer.

        Returns:
            List of dictionaries, each representing an appointment.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            # This is a more efficient query that doesn't require multiple DB calls.
            query = """
                SELECT apt.* 
                FROM appointments apt
                JOIN addresses addr ON apt.address_id = addr.id
                JOIN lives_in li ON addr.id = li.address_id
                JOIN customers c ON li.customer_id = c.id
                WHERE c.email = %s
            """
            cursorObject.execute(query, (customer_email,))
            appointments = cursorObject.fetchall()
            return appointments
        finally:
            self.__close_DB_connection(database)

    def get_addresses_by_customer_id(self, customer_id):
        """
        Gets all addresses and their associated preferences for a specific customer.
        """
        database, cursorObject = self.__open_DB_connection()
        try:
            # LEFT JOIN to include addresses even if they don't have preferences.
            # Alias pref.notes to avoid conflicts.
            query = """
                SELECT 
                    addr.*, 
                    pref.allergies, 
                    pref.pets, 
                    pref.kids, 
                    pref.square_footage, 
                    pref.notes AS preference_notes
                FROM addresses addr
                JOIN lives_in li ON addr.id = li.address_id
                LEFT JOIN preferences pref ON addr.id = pref.address_id
                WHERE li.customer_id = %s
            """
            cursorObject.execute(query, (customer_id,))
            addresses = cursorObject.fetchall()
            return addresses
        finally:
            self.__close_DB_connection(database)