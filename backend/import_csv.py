import csv
from pathlib import Path
from datetime import datetime
import mysql.connector

DB = {"host": "localhost", "user": "root", "password": "26AalborgUni26@", "database": "customerdb"}

ADDRESS_COL = "address"

def _read_csv(path: Path):
    """Åbn CSV med semikolon-delimiter. Prøv UTF-8 først, falder tilbage til cp1252."""
    try:
        f = open(path, newline="", encoding="utf-8-sig")
        r = csv.DictReader(f, delimiter=";")
        # fjern evt. BOM fra headernavne
        r.fieldnames = [h.lstrip("\ufeff").strip() for h in r.fieldnames]
        return f, r
    except UnicodeDecodeError:
        f = open(path, newline="", encoding="cp1252")
        r = csv.DictReader(f, delimiter=";")
        r.fieldnames = [h.lstrip("\ufeff").strip() for h in r.fieldnames]
        return f, r

def import_customers(csv_path: Path):
    db = mysql.connector.connect(**DB)
    cur = db.cursor()

    f, reader = _read_csv(csv_path)
    with f:
        for idx, row in enumerate(reader, start=2):
            try:
                cust_id = int(row["id"])
                name    = row["full_name"].strip()
                email   = row["email"].strip()
                address = f'{row["street"].strip()}, {row["postal_code"].strip()} {row["city"].strip()}'

                sql = (
                    f"INSERT INTO customers (id, name, {ADDRESS_COL}, email) "
                    f"VALUES (%s, %s, %s, %s) "
                    f"ON DUPLICATE KEY UPDATE "
                    f"name=VALUES(name), {ADDRESS_COL}=VALUES({ADDRESS_COL}), email=VALUES(email)"
                )
                cur.execute(sql, (cust_id, name, address, email))
            except Exception as e:
                print(f" Skips row {idx} in customers: {e}")

    db.commit()
    cur.close(); db.close()
    print("Customers importet")

def import_appointments(csv_path: Path):
    db = mysql.connector.connect(**DB)
    cur = db.cursor()

    f, reader = _read_csv(csv_path)
    with f:
        for idx, row in enumerate(reader, start=2):
            try:
                appt_id     = int(row["id"])
                customer_id = int(row["customer"])  # refers to customers.id
                # CSV is dd-mm-YYYY → makes to YYYY-mm-dd (MySQL DATE)
                appt_date   = datetime.strptime(row["appointment_date"].strip(), "%d-%m-%Y").date().isoformat()
                t           = row["appointment_time"].strip()   # "HH:MM" eller "HH:MM:SS"
                appt_time   = t if len(t) >= 8 else (t + ":00")
                location    = row["address"].strip()

                cur.execute(
                    "INSERT INTO appointments (id, customer_id, location_addr, appt_date, appt_time) "
                    "VALUES (%s, %s, %s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE "
                    "customer_id=VALUES(customer_id), "
                    "location_addr=VALUES(location_addr), "
                    "appt_date=VALUES(appt_date), "
                    "appt_time=VALUES(appt_time)",
                    (appt_id, customer_id, location, appt_date, appt_time)
                )
            except Exception as e:
                print(f"Skips row {idx} in appointments: {e}")

    db.commit()
    cur.close(); db.close()
    print("Appointments importet")

if __name__ == "__main__":
    BASE = Path(__file__).resolve().parent / "data"   # backend/data
    import_customers(BASE / "customerdata.csv")
    import_appointments(BASE / "appointmentdata.csv")
    print("Done!")
