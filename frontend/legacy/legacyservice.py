# -----------------------------
# This page works as the 'rule book' for the business logic. (a custom set of rules, algorithms that defines how data is defined, processed, etc.).
# It contains:
    # ValidationError class for handling validation errors.
    # Helper functions for input validation and date parsing.
    # In-memory storage for customer data.
    # Functions for creating, updating, and deleting customers.
    # Each function includes validation checks and raises ValidationError for any issues.
# Currently it is printing 3 reminders in the terminal based on the mock data
# -----------------------------

from datetime import datetime, date

# Gør mappen til en Python-pakke: husk også en tom fil __init__.py

class ValidationError(Exception):
    """Fejl som UI viser som rød besked."""
    pass

# Simple "in-memory" storage.
_CUSTOMERS = {}  # key = email, value = dict(name, address, cleaning_date)

def _require(value: str, field: str) -> str:
    """
    Ensure that a required field is provided and not empty.
    Args:
        value (str): The value to check.
        field (str): The name of the field (for error messages).
    Returns:
        str: The stripped value if valid.
    Raises:
        ValidationError: If the value is missing or empty.
    """
    if not value or not value.strip():
        raise ValidationError(f"{field} er påkrævet.")
    return value.strip()

def _parse_date(iso: str) -> date:
    """
    Parse and validate a date string in ISO format (YYYY-MM-DD).
    Args:
        iso (str): The date string to parse.
    Returns:
        date: The parsed date object.
    Raises:
        ValidationError: If the date is invalid or in the past.
    """
    try:
        d = datetime.strptime(iso.strip(), "%Y-%m-%d").date()
    except Exception:
        raise ValidationError("Dato skal være i formatet YYYY-MM-DD.")
    if d < date.today():
        raise ValidationError("Dato må ikke ligge i fortiden.")
    return d

def create_customer_logic(name: str, email: str, address: str, cleaning_date_str: str):
    """
    Create a new customer with validation and add to in-memory storage.
    Args:
        name (str): Customer's name.
        email (str): Customer's email (must be unique).
        address (str): Customer's address.
        cleaning_date_str (str): Cleaning date in YYYY-MM-DD format.
    Returns:
        dict: Status and customer ID if successful.
    Raises:
        ValidationError: If any validation fails or customer already exists.
    """
    name = _require(name, "Navn")
    email = _require(email, "Email")
    if "@" not in email:
        raise ValidationError("Email ser forkert ud (mangler @).")
    address = _require(address, "Adresse")
    _parse_date(cleaning_date_str)

    if email in _CUSTOMERS:
        raise ValidationError("Der findes allerede en kunde med denne email.")

    _CUSTOMERS[email] = {
        "name": name,
        "email": email,
        "address": address,
        "cleaning_date": cleaning_date_str,
    }
    return {"status": "ok", "customer_id": email}  # email as ID in this simple version

def update_date_logic(email: str, new_date_str: str):
    """
    Update the cleaning date for an existing customer.
    Args:
        email (str): Customer's email to identify the record.
        new_date_str (str): New cleaning date in YYYY-MM-DD format.
    Returns:
        dict: Status and update count if successful.
    Raises:
        ValidationError: If customer not found or date is invalid.
    """
    email = _require(email, "Email")
    _parse_date(new_date_str)
    if email not in _CUSTOMERS:
        raise ValidationError("Ingen kunde fundet med den email.")
    _CUSTOMERS[email]["cleaning_date"] = new_date_str
    return {"status": "ok", "updated": 1}

def delete_customer_logic(email: str):
    """
    Delete a customer from in-memory storage by email.
    Args:
        email (str): Customer's email to identify the record.
    Returns:
        dict: Status and delete count if successful.
    Raises:
        ValidationError: If customer not found.
    """
    email = _require(email, "Email")
    if email not in _CUSTOMERS:
        raise ValidationError("Ingen kunde fundet med den email.")
    del _CUSTOMERS[email]
    return {"status": "ok", "deleted": 1}
