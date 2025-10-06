# ------------------------------
# This file is for creating the obejct (curserObject) that is used to access the database.
# Don't edit this file, except for connection settings. 
# ------------------------------

import mysql.connector
import private_settings

def get_connection():
    return mysql.connector.connect(
        host=private_settings.host,
        user=private_settings.user,
        passwd=private_settings.passwd,
        database="datacleaners",
        autocommit=False,
    )