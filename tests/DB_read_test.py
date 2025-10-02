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
        db_reader = DB_reader.DB_read()              # Create an instance of DB_read
        test_customer_id = 1                         # Use a test customer id (make sure this id exists in your test database)
        # Act
        result = db_reader.get_appointments_by_customer_id(test_customer_id)  # Call the method on the instance
        # Assert
        if type(result) == str:
            self.assertEqual(result, "No appointments found for this customer ID.")
        else: self.assertIsInstance(result, list)     # Check if the result is a list

    def test_get_customer_by_id(self):
        """
        Tests if the get_customer_by_id function returns a list of tuples
        """
        # Arrange
        db_reader = DB_reader.DB_read()              # Create an instance of DB_read
        test_customer_id = 1111                       # Use a test customer id (make sure this id exists in your test database)
        # Act
        result_by_id = db_reader.get_customer_by_id(customer_id=test_customer_id)  # Call the method on the instance with id
        # Assert
        if type(result_by_id) == str:
            self.assertEqual(result_by_id, "No customer found with this ID.")
        else: self.assertIsInstance(result_by_id, list)  # Check if the result is a list

# These lines makes it so that the code in this file only runs when the file is run directly, and not when imported
if __name__ == '__main__':
    unittest.main()