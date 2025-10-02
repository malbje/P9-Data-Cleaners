# app/service.py
from datetime import datetime, date

# Gør mappen til en Python-pakke: husk også en tom fil app/__init__.py

class ValidationError(Exception):
    """Fejl som UI viser som rød besked."""
    pass

# Enkel "in-memory" storage til demo.
# Skift dette ud med rigtig database senere.
_CUSTOMERS = {}  # key = email, value = dict(name, address, cleaning_date)

def _require(value: str, field: str) -> str:
    if not value or not value.strip():
        raise ValidationError(f"{field} er påkrævet.")
    return value.strip()

def _parse_date(iso: str) -> date:
    try:
        d = datetime.strptime(iso.strip(), "%Y-%m-%d").date()
    except Exception:
        raise ValidationError("Dato skal være i formatet YYYY-MM-DD.")
    if d < date.today():
        raise ValidationError("Dato må ikke ligge i fortiden.")
    return d

def create_customer_logic(name: str, email: str, address: str, cleaning_date_str: str):
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
    return {"status": "ok", "customer_id": email}  # email som ID i denne simple version

def update_date_logic(email: str, new_date_str: str):
    email = _require(email, "Email")
    _parse_date(new_date_str)
    if email not in _CUSTOMERS:
        raise ValidationError("Ingen kunde fundet med den email.")
    _CUSTOMERS[email]["cleaning_date"] = new_date_str
    return {"status": "ok", "updated": 1}

def delete_customer_logic(email: str):
    email = _require(email, "Email")
    if email not in _CUSTOMERS:
        raise ValidationError("Ingen kunde fundet med den email.")
    del _CUSTOMERS[email]
    return {"status": "ok", "deleted": 1}
