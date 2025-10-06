# ------------------------------
# This file is for creating the obejct (curserObject) that is used to access the database.
# Don't edit this file, except for connection settings. 
# ------------------------------

import mysql.connector
import private_settings

dataBase = mysql.connector.connect(

    # Create a file called "database/DB_connection_settings.py" in the "database"-folder 
    # and edit password to the same as you have for your MySQL Workbench
    host = private_settings.host,
    user = private_settings.user,
    passwd = private_settings.passwd,
    database = private_settings.database)

cursorObject = dataBase.cursor()

# Test query
query = "SELECT * FROM appointments"
cursorObject.execute(query)

for row in cursorObject.fetchall():
    print(row)

dataBase.close()

