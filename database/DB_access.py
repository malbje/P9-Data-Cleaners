# ------------------------------
# This file is for creating the obejct (curserObject) that is used to access the database.
# Don't edit this file, except for connection settings. 
# ------------------------------

import mysql.connector
import DB_connection_settings

dataBase = mysql.connector.connect(

    # Create a file called "database/DB_connection_settings.py" in the "database"-folder 
    # and edit password to the same as you have for your MySQL Workbench
    host = DB_connection_settings.host,
    user = DB_connection_settings.user,
    passwd = DB_connection_settings.passwd,
    database = DB_connection_settings.database)

cursorObject = dataBase.cursor()

# Test query
query = "SELECT * FROM appointments"
cursorObject.execute(query)

for row in cursorObject.fetchall():
    print(row)

dataBase.close()

