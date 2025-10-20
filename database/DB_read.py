#------------------------------
#  Collection of methods used for reading data from the database.
#
#  Use this by creating a DB_read object in the file you're working on.
#  Example: import database.DB_read as DB_reader
#          DB_read_object = DB_reader.DB_read()
#          data = DB_read_object.all_customers()
#------------------------------

# This defines the current working directory as the root directory, so we can import from backend
# Otherwise notification.py and its methods won't be found
import sys, os
sys.path.insert(0, os.getcwd())
# ------------------------------

# Imports
import mysql.connector, private_settings
from database.DB_access import get_connection
from mysql.connector import IntegrityError



class DB_read:

    def __init__(self): # Constructor
        pass

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


#### Functions from Main.py ####

def list_customers():
    """
    Hent alle kunder fra databasen.
    """
    db = get_connection()
    try: 
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM customers ORDER BY id")
        return cur.fetchall()
    finally:
        db.close()


def list_customers_by_name(name: str, surname: str):
    """
    Find kunder via navn og efternavn (LIKE-søgning).
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM customers WHERE name LIKE %s AND surname LIKE %s ORDER BY id",
            (f"%{name}%", f"%{surname}%")
        )
        return cur.fetchall()
    finally:
        db.close()

def get_customer_by_email(email: str):
    """
    Hent en kunde via email.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM customers WHERE email = %s",
            (email,),
        )
        return cur.fetchone()  # Antager email er unik, så vi forventer kun én række
    finally:
        db.close()

def get_customer_by_id(customer_id: int):
    """
    Hent en kunde via dens ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM customers WHERE id = %s",
            (customer_id,),
        )
        return cur.fetchone()  # Antager ID er unik, så vi forventer kun én række
    finally:
        db.close()


def add_customer(name: str, surname: str, email: str, notification_preference: str):
    """
    Opret en kunde. Fejler hvis email allerede findes.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO customers (name, surname, email, notification_preference) VALUES (%s, %s, %s, %s)",
            (name, surname, email, notification_preference),
        )
        db.commit()
        return {"id": cur.lastrowid, "name": name, "surname": surname, "email": email, "notification_preference": notification_preference}
    except IntegrityError as e:
        return {"error": "Email already exists", "details": str(e)}

def add_address(city_name: str, postal_code: str, street_and_number: str):
    """
    Tilføjer en adresse til en kunde baseret på deres ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO addresses (city_name, postal_code, street_and_number) VALUES (%s, %s, %s)",
            (city_name, postal_code, street_and_number),
        )
        db.commit()
        return {"updated_rows": cur.rowcount}
    finally:
        db.close()

def add_appointment(address_id: int, date: str, time: str, notes: str, notification_preference: str):
    """
    Tilføjer en appointment til en given adresse.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO appointments (address_id, date, time, notes, notification_preference) VALUES (%s, %s, %s, %s, %s)",
            (address_id, date, time, notes, notification_preference),
        )
        db.commit()
        return {"id": cur.lastrowid, "address_id": address_id, "date": date, "time": time, "notes": notes, "notification_preference": notification_preference}
    finally:
        db.close()

def update_customer_address(customer_id: int, address_id: int , city_name: str, postal_code: str, street_and_number: str):
    """
    Opdaterer en kundes adresse baseret på deres ID.
    UPDATE addresses → vi vil ændre data i tabellen addresses.

    JOIN lives_in ON lives_in.address_id = addresses.id → vi kobler addresses sammen med lives_in.
    Det betyder: “Kun de adresser, som faktisk optræder i lives_in, kan ændres.”

    SET addresses.city_name = %s, ... → sætter de nye værdier for felterne.

    WHERE addresses.id = %s AND lives_in.customer_id = %s → betyder:
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "UPDATE addresses JOIN lives_in ON lives_in.address_id = addresses.id SET addresses.city_name = %s, addresses.postal_code = %s, addresses.street_and_number = %s WHERE addresses.id = %s AND lives_in.customer_id = %s",
            (city_name, postal_code, street_and_number, address_id, customer_id),
        )
        db.commit()
        return {"updated_rows": cur.rowcount}
    finally:
        db.close()

def get_appointment_by_id(appointment_id: int):
    """
    Hent en specifik aftale via dens ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM appointments WHERE id = %s",
            (appointment_id,),
        )
        return cur.fetchone()  # Antager ID er unik, så vi forventer kun én række
    finally:
        db.close()

def get_customers_by_address_id(address_id: int):
    """
    Hent alle kunder via adresse ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT customers.* FROM customers JOIN lives_in ON customers.id = lives_in.customer_id WHERE lives_in.address_id = %s",
            (address_id,),
        )
        return cur.fetchall()  # Returnerer alle kunder på adressen
    finally:
        db.close()

def get_customers_by_appointment_id(appointment_id: int):
    """
    Hent alle kunder via aftale ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT customers.* FROM customers JOIN appointments ON customers.id = appointments.customer_id WHERE appointments.id = %s",
            (appointment_id,),
        )
        return cur.fetchall()  # Returnerer alle kunder med den pågældende aftale
    finally:
        db.close()

def get_appointments_by_address_id(address_id: int):
    """
    Hent alle aftaler for en specifik kunde via addressens ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM appointments WHERE address_id = %s ORDER BY date, time",
            (address_id,),
        )
        return cur.fetchall()
    finally:
        db.close()

def delete_customer(customer_id: int):
    """
    Slet en kunde baseret på deres ID.
    """
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(
            "DELETE FROM customers WHERE id = %s",
            (customer_id,),
        )
        db.commit()
        return {"deleted_rows": cur.rowcount}
    finally:
        db.close()
