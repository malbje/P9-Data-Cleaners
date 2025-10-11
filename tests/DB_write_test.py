import unittest

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

import mysql.connector
import database.DB_read as DB_reader
import database.DB_write as DB_writer
import private_settings

class Test_DB_write(unittest.TestCase):

    import database.DB_write as DB_writer
    db_writer = DB_writer.DB_write()
    db_reader= DB_reader.DB_read()

    def setUp(self):

        test_customer = self.db_reader.get_customer_by_id(-1)
        if type(test_customer) == str: # If the test customer doesn't exist, create it
            self.db_writer.create_customer_including_id(-1, "Test User", "Test Address", "Test Email")

        test_appointment = self.db_reader.get_appointment_by_id(-1)
        if type(test_appointment) == str: # If the test appointment doesn't exist, create
            self.db_writer.create_appointment_including_id(-1, -1, "Test Location", "2000-01-01", "12:00:00")

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

    def test_create_customer(self):
        try:

            self.db_writer.create_customer(name="Test User 2", address="Test Address 2", email="Test Email 2")

            customers = self.db_reader.get_all_customers()
            customer: tuple
            for item in customers:
                _, name, address, email = item
                if name == "Test User 2" and address == "Test Address 2" and email == "Test Email 2":
                    customer = item # type: ignore
                
            assert isinstance(customer, tuple)
            assert customer[1] == "Test User 2"
            assert customer[2] == "Test Address 2"
            assert customer[3] == "Test Email 2"

        finally:
            self.db_writer.delete_customers_by_name("Test User 2") # Delete the test user

    def test_create_customer_including_id(self):
        if self.db_reader.get_customer_by_id(-1) != str:
            self.db_writer.delete_customer_by_id(-1) # Delete the test user if it already exists

        self.db_writer.create_customer_including_id(id = -1, name="Test User 1", address="Test Address 1", email="Test Email 1")

        customer = self.db_reader.get_customer_by_id(-1)[0]
        assert isinstance(customer, tuple)
        id, name, address, email = customer
        assert id == -1
        assert name == "Test User 1"
        assert address == "Test Address 1"
        assert email == "Test Email 1"

    def test_create_appointment(self):
        
        if self.db_reader.get_appointment_by_id(-1) != str:
            self.db_writer.delete_appointment_by_id(-1) # Delete the test appointment if it already exists

        self.db_writer.create_appointment(customer_id = -1, location_addr = "Test Location 1", appt_date = "2001-01-01", appt_time = "13:00:00")

        appointment: tuple
        appointments = self.db_reader.get_all_appointments()
        for item in appointments:
            _, customer_id, location_addr, appt_date, appt_time = item
            if customer_id == -1 and location_addr == "Test Location 1" and str(appt_date) == "2001-01-01" and str(appt_time) == "13:00:00":
                appointment = item # type: ignore
                break

        assert isinstance(appointment, tuple)
        _, customer_id, location_addr, appt_date, appt_time = appointment
        assert customer_id == -1
        assert location_addr == "Test Location 1"
        assert str(appt_date) == "2001-01-01"
        assert str(appt_time) == "13:00:00"

    def test_uppdate_customer_by_id(self):

        self.db_writer.update_customer_by_id(id = -1, name="Updated Test User", address="Updated Test Address", email="Updated Test Email")

        customer = self.db_reader.get_customer_by_id(-1)[0]
        assert isinstance(customer, tuple)
        id, name, address, email = customer
        assert name == "Updated Test User"
        assert address == "Updated Test Address"
        assert email == "Updated Test Email"

    def test_update_appointment_by_id(self):

        try:
            oldAppointment = self.db_reader.get_appointment_by_id(-1)[0]

            self.db_writer.update_appointment_by_id(-1, -1, "Updated Test Location", "2002-02-02", "14:00:00")

            newAppointment = self.db_reader.get_appointment_by_id(-1)[0]

            assert isinstance(newAppointment, tuple)
            assert isinstance(oldAppointment, tuple)
            assert newAppointment != oldAppointment

        finally:
            self.db_writer.delete_appointment_by_id(-1) # Delete the test appointment

    def test_update_customer_name_by_id(self):

        try:
            _, name, *_ = self.db_reader.get_customer_by_id(-1)[0]

            self.db_writer.update_customer_name_by_id(-1, "Updated Test User Name Only")

            customer = self.db_reader.get_customer_by_id(-1)[0]
            _, newName, *_ = customer

            assert newName != name
            assert newName == "Updated Test User Name Only"

        finally:
            self.db_writer.delete_customer_by_id(-1)

    def test_update_customer_address_by_id(self):

        try:
            _, _, address, *_ = self.db_reader.get_customer_by_id(-1)[0]

            self.db_writer.update_customer_address_by_id(-1, "Updated Test User Address Only")

            customer = self.db_reader.get_customer_by_id(-1)[0]
            _, _, newAddress, *_ = customer

            assert newAddress != address
            assert newAddress == "Updated Test User Address Only"

        finally:
            self.db_writer.delete_customer_by_id(-1)

    def test_update_customer_email_by_id(self):

        try:
            _, _, _, email = self.db_reader.get_customer_by_id(-1)[0]

            self.db_writer.update_customer_email_by_id(-1, "Updated Test User Email Only")

            customer = self.db_reader.get_customer_by_id(-1)[0]
            _, _, _, newEmail = customer

            assert newEmail != email
            assert newEmail == "Updated Test User Email Only"

        finally:
            self.db_writer.delete_customer_by_id(-1)

    def test_update_appointment_location_by_id(self):

        try:
            #Arrange
            _, _, location_addr, *_ = self.db_reader.get_appointment_by_id(-1)[0]

            #Act
            self.db_writer.update_appointment_location_by_id(-1, "Updated Test Location Only")

            appointment = self.db_reader.get_appointment_by_id(-1)[0]
            _, _, newLocation_addr, *_ = appointment

            #Assert
            assert newLocation_addr != location_addr
            assert newLocation_addr == "Updated Test Location Only"

        finally:
            self.db_writer.delete_appointment_by_id(-1)

    def test_update_appointment_date_by_id(self):

        try:
            #Arrange
            _, _, _, appt_date, *_ = self.db_reader.get_appointment_by_id(-1)[0]

            #Act
            self.db_writer.update_appointment_date_by_id(-1, "2003-03-03")

            appointment = self.db_reader.get_appointment_by_id(-1)[0]
            _, _, _, newAppt_date, *_ = appointment

            #Assert
            assert str(newAppt_date) != str(appt_date)
            assert str(newAppt_date) == "2003-03-03"

        finally:
            self.db_writer.delete_appointment_by_id(-1)

    def test_update_appointment_time_by_id(self):

        try:
            #Arrange
            *_, appt_time = self.db_reader.get_appointment_by_id(-1)[0]

            #Act
            self.db_writer.update_appointment_time_by_id(-1, "15:00:00")

            appointment = self.db_reader.get_appointment_by_id(-1)[0]
            *_, newAppt_time = appointment

            #Assert
            assert str(newAppt_time) != str(appt_time)
            assert str(newAppt_time) == "15:00:00"

        finally:
            self.db_writer.delete_appointment_by_id(-1)

# These lines makes it so that the code in this file only runs when the file is run directly, and not when imported
if __name__ == '__main__':
    unittest.main()
        
        