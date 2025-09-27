# backend/db_config.py
DB = {
    "host": "localhost",
    "user": "root",
    "password": "26Aalb0rgUni26@",# den her skal I rette til jeres egen login til workbenc/mysql
    "database": "customerdb",
}

ADDRESS_COL = "address"

#start
# HURTIG GUIDE (til teamet)
#
# 1) Installer Python-pakker
#    pip install -r requirements.txt
#
# 2) Lokal DB-konfiguration
#    Kopiér backend/db_config.example.py → backend/db_config.py
#    Ret værdierne:
#      DB = {"host":"localhost","user":"root","password":"<DIT_PASSWORD>","database":"customerdb"}
#      ADDRESS_COL = "address"
#
# 3) Opret database + tabeller (MySQL Workbench)
#    Åbn backend/setup.sql og kør hele scriptet.
#    (CLI alternativ: mysql -u root -p -e "SOURCE backend/setup.sql;")
#
# 4) CSV-filer (læg dem i backend/data/)
#      - customerdata.csv       (id;full_name;email;street;city;postal_code)
#      - appointmentdata.csv    (id;customer_id;appointment_date;appointment_time;address)
#    Datoformater der accepteres: dd-mm-YYYY, YYYY-mm-dd eller dd/mm/YYYY
#
# 5) Importér data + test
#    python backend/import_csv.py
#    python backend/backend.py     # burde vise "Connected: True" og liste tabeller
#
# FEJLSØGNING (kort)
#  - "Access denied": Tjek password i db_config.py
#  - "Unknown database": Kør setup.sql
#  - Dato-fejl: Ret datoer til ét af de accepterede formater
#slut

#hvis alt held er ude, så kan ChatGPT være til en stor hjælp