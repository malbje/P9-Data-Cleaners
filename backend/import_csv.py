# backend/import_csv.py
import csv
from pathlib import Path
from datetime import datetime
import mysql.connector as m

# Get DB config from db_config.py (what a process...)
import db_config
DB = db_config.DB
ADDRESS_COL = getattr(db_config, "ADDRESS_COL", "address")

def _read_csv(path: Path):
    """Open a semicolon-separated CSV. Try UTF-8 first, fall back to cp1252 (Excel)."""
    try:
        f = open(path, newline="", encoding="utf-8-sig")
        r = csv.DictReader(f, delimiter=";")
        # Strip a possible BOM from headers and trim whitespace
        r.fieldnames = [h.lstrip("\ufeff").strip() for h in r.fieldnames]
        return f, r
    except UnicodeDecodeError:
        f = open(path, newline="", encoding="cp1252")
        r = csv.DictReader(f, delimiter=";")
        r.fieldnames = [h.lstrip("\ufeff").strip() for h in r.fieldnames]
        return f, r

# Helper: accept multiple date formats (DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY) and return ISO 'YYYY-MM-DD'
def _parse_date(s: str) -> str:
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s.strip(), fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {s!r}")

def import_customers(csv_path: Path):
    """Upsert customers from CSV into the customers table."""
    db = m.connect(**DB)
    cur = db.cursor()

    f, reader = _read_csv(csv_path)
    with f:
        for idx, row in enumerate(reader, start=2):   # start=2 to reflect CSV line numbers incl. header
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
                print(f"Skip row {idx} in customers: {e}")

    db.commit()
    cur.close(); db.close()
    print("Customers imported")

def import_appointments(csv_path: Path):
    """Upsert appointments from CSV into the appointments table."""
    db = m.connect(**DB)
    cur = db.cursor()

    f, reader = _read_csv(csv_path)
    with f:
        for idx, row in enumerate(reader, start=2):
            try:
                appt_id     = int(row["id"])
                customer_id = int(row.get("customer") or row["customer_id"])
                # CSV is dd-mm-YYYY → convert to YYYY-mm-dd for MySQL DATE så det bliver sat korrekt op
                appt_date   = _parse_date(row["appointment_date"])
                t           = row["appointment_time"].strip()   # "HH:MM" or "HH:MM:SS"
                appt_time   = t if len(t) >= 8 else (t + ":00") #defines hour:minute
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
                print(f"Skip row {idx} in appointments: {e}")

    db.commit()
    cur.close(); db.close()
    print("Appointments imported")

if __name__ == "__main__":
    BASE = Path(__file__).resolve().parent / "data"
    import_appointments(BASE / "appointmentdata.csv")
    print("Done!")
    #What a rollercoaster of a process for a db
