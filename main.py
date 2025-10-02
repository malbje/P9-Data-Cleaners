#------------------------------
# main.py right now only tests the DB_read class
#------------------------------

import database.DB_read as DB_reader # Importing the file (module) containing the DB_read class

readDB = DB_reader.DB_read()      # Creating an object (instance) of the DB_read class

text = readDB.get_all_customers() # Calling the all_customers() method from the DB_read object

print(text)

customer = readDB.get_customer_by_id(1) # Calling the get_customer_by_id() method from the DB_read object

print(customer)