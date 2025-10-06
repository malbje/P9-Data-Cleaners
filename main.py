#------------------------------
# main.py right now only tests the DB_read class
#------------------------------

import mcp
import database.DB_read as DB_reader # Importing the file (module) containing the DB_read class
import asyncio
from fastmcp import FastMCP
from database.DB_access import dataBase
from mysql.connector import IntegrityError

mcp = FastMCP("DataCleaners")

def _query_all(sql, params=None):
    db = dataBase()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        db.close()

def _execute(sql, params=None):
    db = dataBase()
    try:
        cur = db.cursor()
        cur.execute(sql, params or ())
        db.commit()
        return cur.lastrowid
    except:
        db.rollback()
        raise
    finally:
        db.close()

@mcp.tool
async def list_customers():
    """Returnér alle kunder."""
    return _query_all("SELECT id, name, address, email FROM customers ORDER BY id")

@mcp.tool
async def get_customer_by_email(email: str):
    """Hent én kunde via email."""
    rows = _query_all("SELECT id, name, address, email FROM customers WHERE email = %s", (email,))
    return rows[0] if rows else None

@mcp.tool
async def add_customer(name: str, address: str, email: str):
    """Opret kunde. Fejler hvis email allerede findes (UNIQUE)."""
    try:
        new_id = _execute(
            "INSERT INTO customers (name, address, email) VALUES (%s, %s, %s)",
            (name, address, email)
        )
        return {"id": new_id, "name": name, "address": address, "email": email}
    except IntegrityError as e:
        return {"error": "Email already exists", "details": str(e)}

@mcp.tool
async def update_customer_address(customer_id: int, new_address: str):
    """Opdater adresse på kunde-id."""
    db = dataBase()
    try:
        cur = db.cursor()
        cur.execute("UPDATE customers SET address = %s WHERE id = %s", (new_address, customer_id))
        db.commit()
        return {"updated_rows": cur.rowcount}
    except:
        db.rollback()
        raise
    finally:
        db.close()

@mcp.tool
async def delete_customer(customer_id: int):
    """Slet kunde."""
    db = dataBase()
    try:
        cur = db.cursor()
        cur.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
        db.commit()
        return {"deleted_rows": cur.rowcount}
    except:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()   # FastMCP.run() er synkron – drop asyncio her