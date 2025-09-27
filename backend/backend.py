# backend/backend.py
import mysql.connector as m
from db_config import DB 

def main():
    conn = m.connect(**DB)
    print("Connected:", conn.is_connected())
    cur = conn.cursor()
    cur.execute("SHOW TABLES;")
    print("Tabels in customerdb:")
    for (t,) in cur.fetchall():
        print("-", t)
    cur.close(); conn.close()

if __name__ == "__main__":
    main()

