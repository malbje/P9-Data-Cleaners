# ------------------------------
# This file is for creating the obejct (curserObject) that is used to access the database.
# Don't edit this file, except for connection settings. 
# ------------------------------

import mysql.connector
import DB_connection_settings

dataBase = mysql.connector.connect(

    # Go to database/DB_connection_settings.py to edit these settings to your own
    host = DB_connection_settings.host,
    user = DB_connection_settings.user,
    passwd = DB_connection_settings.passwd,
    database = DB_connection_settings.database)

cursorObject = dataBase.cursor()

# Test qurrie
query = "SELECT * FROM appointments"
cursorObject.execute(query)

for row in cursorObject.fetchall():
    print(row)

dataBase.close()

