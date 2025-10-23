# backend/routes/api_data.py
# We use this file to handle all data-related API endpoints
# this could have been in app.py, but for better organization we separate it out, to not make the file too big
# The api_auth.py file works similarly, but for authentication-related endpoints.

"""
Contains all data-related API endpoints (appointments, addresses, services).
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
# Sørg for at db-importstien er korrekt
import backend.service.database_logic as db
from database.DB_read import DB_read 

# Opret et Blueprint. Alle ruter her vil starte med /api
api_data_bp = Blueprint('data_api', __name__, url_prefix='/api')


# --- Nødvendig hjælpe-funktion (kopieret fra app.py) ---
def ensure_logged_in():
    """
    Check if user is authenticated in current session
    
    Returns:
        bool: True if user_id exists in session, False otherwise
    """
    return 'user_id' in session

# ============================================================================
# API ROUTES - BOOKING SYSTEM
# RESTful API endpoints for appointment and booking management
# ============================================================================

@api_data_bp.route('/manual_insert', methods=['POST'])
def api_manual_insert():
    """
    Create new appointment via manual form submission
    
    Expected JSON payload:
        - customer information (name, email, phone, address)
        - appointment details (date, time, service type)
        - cleaning preferences
    
    Returns:
        tuple: JSON response with success/error message and HTTP status code
    """
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Den oprindelige app.py gav ikke user_id med her.
        # Vi beholder den oprindelige kode, selvom create_full_appointment
        # i database_logic.py måske forventer det.
        result = db.create_full_appointment(data)
        return jsonify(result), 201
    except db.ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Log the full error for debugging
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred. Please try again."}), 500

# ============================================================================
# API ROUTES - USER DATA MANAGEMENT
# Endpoints for retrieving and managing user-specific data
# ============================================================================

@api_data_bp.route('/user/addresses', methods=['GET'])
def api_get_user_addresses():
    """
    Get all addresses associated with the current user
    
    Returns:
        tuple: JSON array of user addresses or error message with HTTP status
    """
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    from database.DB_read import DB_read
    reader = DB_read()
    user_id = session.get('user_id')
    addresses = reader.get_addresses_by_customer_id(user_id)
    return jsonify(addresses)

@api_data_bp.route('/appointments', methods=['GET'])
def api_get_appointments():
    """
    Get all appointments for the current user
    
    Returns:
        tuple: JSON array of user appointments or error message with HTTP status
    """
    if not ensure_logged_in(): 
        return jsonify({"error": "Authentication required"}), 401
    
    user_id = session.get('user_id')
    # Fetch appointments specific to the logged-in user
    appointments = db.get_appointments_for_customer(user_id) 
    return jsonify(appointments)

@api_data_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def api_delete_appointment(appointment_id):
    """
    Delete a specific appointment by ID
    
    Args:
        appointment_id (int): ID of appointment to delete
        
    Returns:
        tuple: JSON response with success/error message and HTTP status code
    """
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        # Delegate deletion to database logic layer
        db.delete_appointment(appointment_id) # Beholder denne linje som i din fil
        return jsonify({"success": True, "message": "Appointment deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_data_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
def api_update_appointment(appointment_id):
    """
    Update an existing appointment
    
    Args:
        appointment_id (int): ID of appointment to update
        
    Expected JSON payload:
        - Updated appointment details (date, time, service, etc.)
        
    Returns:
        tuple: JSON response with success/error message and HTTP status code
    """
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Get user context for authorization
        user_id = session.get('user_id')
        
        # Delegate update to database logic layer
        db.update_appointment(appointment_id, data, user_id) # Beholder denne linje som i din fil
        return jsonify({"success": True, "message": "Appointment updated"}), 200
    except db.ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update appointment: {str(e)}"}), 500

@api_data_bp.route('/appointments/by-address/<int:address_id>')
def api_get_appointments_by_address(address_id):
    """
    Get all appointments for a specific address
    
    Args:
        address_id (int): ID of the address to get appointments for
        
    Returns:
        tuple: JSON array of appointments for the address or error message with HTTP status
    """
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    # Use database reader class for direct database access
    from database.DB_read import DB_read
    reader = DB_read()
    
    try:
        # Fetch appointments for the specified address
        appointments = reader.get_appointments_by_address_id(address_id)
        return jsonify(appointments)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch appointments: {str(e)}"}), 500

@api_data_bp.route('/user/addresses-with-preferences')
def api_get_user_addresses_with_preferences():
    """
    Get user addresses with their associated cleaning preferences
    Combines address information with preference settings for enhanced booking
    
    Returns:
        tuple: JSON array of addresses with preferences or error message with HTTP status
    """
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    user_id = session.get('user_id')
    # Fetch addresses with associated preferences
    addresses = db.get_addresses_and_preferences_for_customer(user_id)
    return jsonify(addresses)

@api_data_bp.route('/services', methods=['GET'])
def api_get_services():
    """
    Get all available cleaning services
    Public endpoint that returns service catalog for booking forms
    
    Returns:
        dict: JSON array of all cleaning services with details
    """
    services = db.get_all_services()
    return jsonify(services)