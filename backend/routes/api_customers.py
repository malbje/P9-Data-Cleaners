from flask import Blueprint, request, jsonify
from database.DB_read import DB_read
from database.DB_write import DB_write

api_customers_bp = Blueprint('api_customers', __name__)

@api_customers_bp.route('/api/customers', methods=['POST'])
def create_customer_with_address():
    """Create customer + address (if missing) and link them."""
    # DEBUG: log incoming payload to help diagnose why frontend may be falling back to GET
    data = request.get_json() or {}
    try:
        api_customers_bp.logger.info(f"Incoming signup payload: {data}")
        # print as well to ensure it appears in the console regardless of logger level
        print(f"Incoming signup payload: {data}")
    except Exception:
        # ensure debugging doesn't break the endpoint
        pass
    name = (data.get('name') or '').strip()
    surname = (data.get('surname') or '').strip()
    email = (data.get('email') or '').strip().lower()

    addr = data.get('address') or {}
    street = (addr.get('street_and_number') or '').strip()
    postal = (addr.get('postal_code') or '').strip()
    city = (addr.get('city_name') or '').strip()

    if not (name and surname and email and street and postal and city):
        return jsonify({"error": "Missing required customer or address fields"}), 400

    reader = DB_read()
    writer = DB_write()
    try:
        # Check existing customer
        if reader.get_customer_by_email(email):
            return jsonify({"error": "Email already registered"}), 409

        # Find or create address
        existing_addr = reader.find_address(street, postal)
        if existing_addr and existing_addr.get('id'):
            address_id = existing_addr['id']
        else:
            address_id = writer.create_address(street, postal, city)
        # Defensive: ensure address_id was created
        if not address_id:
            api_customers_bp.logger.error(f"Failed to create/find address for: {street}, {postal}, {city}")
            return jsonify({"error": "Failed to create address"}), 500
        # DEBUG: report address id
        try:
            print(f"DEBUG: address_id = {address_id}")
        except Exception:
            pass

        # Create customer
        customer_id = writer.create_customer(name, surname, email)
        if not customer_id:
            api_customers_bp.logger.error(f"Failed to create customer for email={email}")
            return jsonify({"error": "Failed to create customer"}), 500
        # DEBUG: report customer id
        try:
            print(f"DEBUG: customer_id = {customer_id}")
        except Exception:
            pass

        # Link customer <-> address (lives_in)
        linked = writer.link_customer_to_address(customer_id, address_id)
        if not linked:
            api_customers_bp.logger.error(f"Failed to link customer {customer_id} to address {address_id}")
            return jsonify({"error": "Failed to link customer and address"}), 500
        try:
            print(f"DEBUG: linked customer {customer_id} to address {address_id}")
        except Exception:
            pass

        return jsonify({
            "success": True,
            "customer_id": customer_id,
            "address_id": address_id
        }), 201

    except Exception as e:
        api_customers_bp.logger.exception("Failed to create customer with address")
        return jsonify({"error": "Internal server error"}), 500