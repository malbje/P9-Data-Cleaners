import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="26Aalb0rgUni26@",   # husk at sætte dit eget password
        database="customerdb"
    )

    print("Connected to MySQL!")

    cursor = db.cursor()
    cursor.execute("SHOW TABLES;")

    print("Tabeller i customerdb:")
    for (table,) in cursor.fetchall():
        print("-", table)

except mysql.connector.Error as err:
    print("Error to connect:", err)
