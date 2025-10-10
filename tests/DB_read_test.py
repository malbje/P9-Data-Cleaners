# -----------------------------
# This page exists for testing the different methods in DB_read.py
# Not all methods are nessecarily tested yet
# -----------------------------

import unittest # Class with unit test methods

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

import database.DB_read as DB_reader

class Test_DB_read(unittest.TestCase):

    def setUp(self):
        import database.DB_write as DB_writer
        db_writer = DB_writer.DB_write()
        db_reader= DB_reader.DB_read()

        test_customer = db_reader.get_customer_by_id(-1)
        if type(test_customer) == str: # If the test customer doesn't exist, create it
            db_writer.create_user(name="Test User", address="Test Address", email="Test Email")
            db_writer.update_user_id_by_name("Test User", -1) # Set the new user's id to -1

        test_appointment = db_reader.get_appointment_by_id(-1)
        if type(test_appointment) == str: # If the test appointment doesn't exist, create
            db_writer.create_appointment(customer_id = -1, location_addr = "Test Location", appt_date = "2000-01-01", appt_time = "12:00:00")
            db_writer.update_appointment_id_by_customer_id(-1) # Set the new appointment's id to -1

    def test_get_all_customers(self):
        """
        Tests if the get_all_customers function returns a list of tuples
        """
        # Arrange
        db_reader = DB_reader.DB_read()              # Create an instance of DB_read
        # Act
        result = db_reader.get_all_customers()       # Call the method on the instance
        
        # Assert
        self.assertIsInstance(result, list)          # Check if the result is a list
        if result:                                   # If the list is not empty, check the type of the first element
            self.assertIsInstance(result[0], tuple)  # Check if the first element is a tuple
            self.assertIsInstance(result[0][0], int) # type: ignore
                                                     # Check if the first element of the tuple is an int (id)

    def test_get_all_appointments(self):
        """
        Tests if the get_all_appointments function returns a list of tuples
        """
        # Arrange
        db_reader = DB_reader.DB_read()              # Create an instance of DB_read
        # Act
        result = db_reader.get_all_appointments()    # Call the method on the instance
        # Assert
        self.assertIsInstance(result, list)          # Check if the result is a list
        if result:                                   # If the list is not empty, check the type of the first element
            self.assertIsInstance(result[0], tuple)  # Check if the first element is a tuple
            self.assertIsInstance(result[0][0], int) # type: ignore
                                                     # Check if the first element of the tuple is an int (id)

    def test_get_appointments_by_customer_id(self):
        """
        Tests if the get_appointments_by_customer_id function returns a list of tuples
        """
        # Arrange
        db_reader = DB_reader.DB_read()              
        test_customer_id = -1                         
        # Act
        result = db_reader.get_appointments_by_customer_id(test_customer_id)  
        # Assert
        if type(result) == str:
            self.assertEqual(result, "No appointments found for this customer ID.")
        else: self.assertIsInstance(result, list) 

    def test_get_customer_by_id(self):
        """
        Tests if the get_customer_by_id function returns a list of tuples
        """
        # Arrange
        db_reader = DB_reader.DB_read()              
        test_customer_id = -1                      
        # Act
        result_by_id = db_reader.get_customer_by_id(customer_id=test_customer_id)  
        # Assert
        if type(result_by_id) == str:
            self.assertEqual(result_by_id, "No customer found with this ID.")
        else: self.assertIsInstance(result_by_id, list)  

    def test_get_appointment_by_id(self):
        """
        Tests if the get_appointment_by_id function returns a list of tuples
        """
        # Arrange
        db_reader = DB_reader.DB_read()             
        test_appointment_id = -1                      
        # Act
        result_by_id = db_reader.get_appointment_by_id(appointment_id=test_appointment_id)
        # Assert
        if type(result_by_id) == str:
            self.assertEqual(result_by_id, "No appointment found with this ID.")
        else: self.assertIsInstance(result_by_id, list)  

    def test_get_joint_customers_appointments_data(self):
        db_reader = DB_reader.DB_read()

        table = db_reader.get_joint_customers_appointments_data()

        assert isinstance(table, list)
        assert isinstance(table[0], tuple)

        assert len(table[0]) == 7  # Assuming there are 7 columns

    def test_get_appointment_id_by_customer_email(self):
        db_reader = DB_reader.DB_read()
        test_email = "Test Email"

        appointment_id = db_reader.get_appointment_id_by_customer_email(test_email)

        assert isinstance(appointment_id, list)
        assert isinstance(appointment_id[0], tuple)
        id, *_ = appointment_id[0]
        assert isinstance(id, int)

# These lines makes it so that the code in this file only runs when the file is run directly, and not when imported
if __name__ == '__main__':
    unittest.main()