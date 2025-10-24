"""
Utility: Print the first customer email found in the application's database.

This script is intended for local development only. It imports the project's
database access layer and prints the email address of the first customer row.

Usage:
    python scripts/get_first_user_email.py

It prints the email to stdout (or exits with non-zero status if none found).
"""
import sys
import os

# Make sure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

try:
    from database.DB_read import DB_read
except Exception as e:
    print(f"ERROR: failed to import DB_read: {e}", file=sys.stderr)
    sys.exit(2)

def main():
    db = DB_read()
    try:
        customers = db.get_all_customers()
    except Exception as e:
        print(f"ERROR: could not read customers from DB: {e}", file=sys.stderr)
        sys.exit(3)

    if not customers:
        print("", end="")
        sys.exit(1)

    # customers is expected to be a list of dict rows with an 'email' key
    first = customers[0]
    email = first.get('email') if isinstance(first, dict) else None
    if not email:
        print("", end="")
        sys.exit(1)

    print(email)

if __name__ == '__main__':
    main()
