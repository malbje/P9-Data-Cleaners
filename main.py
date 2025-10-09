# ------------------------------
# main.py – MCP server for DataCleaners
# ------------------------------

from mcp.server.fastmcp import FastMCP
from mysql.connector import IntegrityError
from database.DB_access import get_connection

# Opret MCP-server
mcp = FastMCP("DataCleaners")

# ---------- Helper functions ----------
def _query_all(sql, params=None):
    db = get_connection()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        db.close()

def _execute(sql, params=None):
    db = get_connection()
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

# ---------- MCP tools ----------
@mcp.tool()
def ping() -> str:
    """Bruges til at teste at serveren kører."""
    return "pong"

<<<<<<< HEAD
for item in all:
    print(item)
=======
@mcp.tool()
def list_customers():
    """Alle kunder (ingen input)."""
    return _query_all("SELECT id, name, address, email FROM customers ORDER BY id")

@mcp.tool()
def list_customers_by_name(customer_name: str):
    """Find kunder via navn (LIKE-søgning)."""
    return _query_all(
        "SELECT id, name, address, email FROM customers WHERE name LIKE %s ORDER BY id",
        (f"%{customer_name}%",),
    )

@mcp.tool()
def get_customer_by_email(email: str):
    """Hent en kunde via email."""
    rows = _query_all(
        "SELECT id, name, address, email FROM customers WHERE email = %s",
        (email,),
    )
    return rows[0] if rows else None

@mcp.tool()
def add_customer(name: str, address: str, email: str):
    """Opret en kunde. Fejler hvis email allerede findes."""
    try:
        new_id = _execute(
            "INSERT INTO customers (name, address, email) VALUES (%s, %s, %s)",
            (name, address, email),
        )
        return {"id": new_id, "name": name, "address": address, "email": email}
    except IntegrityError as e:
        return {"error": "Email already exists", "details": str(e)}

@mcp.tool()
def update_customer_address(customer_id: int, new_address: str):
    """Opdater kundeadresse."""
    db = get_connection()
    try:
        cur = db.cursor()
        cur.execute(
            "UPDATE customers SET address = %s WHERE id = %s",
            (new_address, customer_id),
        )
        db.commit()
        return {"updated_rows": cur.rowcount}
    except:
        db.rollback()
        raise
    finally:
        db.close()

@mcp.tool()
def delete_customer(customer_id: int):
    """Slet kunde."""
    db = get_connection()
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

# ---------- Run ----------
if __name__ == "__main__":
    mcp.run(transport="stdio")
>>>>>>> LLM
