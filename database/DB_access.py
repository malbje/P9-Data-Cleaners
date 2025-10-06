# ------------------------------
# This file is for creating the obejct (curserObject) that is used to access the database.
# Don't edit this file, except for connection settings. 
# ------------------------------

import mysql.connector
import private_settings

dataBase = mysql.connector.connect(
        host=private_settings.host,
        user=private_settings.user,
        passwd=private_settings.passwd,
        database=private_settings.database, 
        autocommit=False          # vi committer eksplicit på writes
    )

curserObject = dataBase.cursor()