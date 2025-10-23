"""
@fileoverview Main Flask application for Data Cleaners booking system
Contains all routing, authentication, and API endpoints for the cleaning service application
Handles both web pages and RESTful API endpoints with session-based authentication
@author Data Cleaners Team
@version 1.0.0
"""

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from database.DB_access import get_connection
import backend.service.database_logic as db  # Import the database logic layer

# ============================================================================
# FLASK APPLICATION INITIALIZATION
# ============================================================================

"""
Flask application instance with custom template and static folders
Configured to serve frontend files from the frontend directory structure
"""
app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# TODO: Change this secret key in production environment
app.secret_key = 'your-secret-key-change-this-in-production'

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class ValidationError(Exception):
    """
    Custom exception for data validation errors
    Used to provide specific error messages for invalid input data
    """
    pass

# ============================================================================
# AUTHENTICATION UTILITIES
# ============================================================================

def ensure_logged_in():
    """
    Check if user is authenticated in current session
    
    Returns:
        bool: True if user_id exists in session, False otherwise
    """
    return 'user_id' in session

# ============================================================================
# WEB PAGE ROUTES
# Routes that serve HTML templates to users
# ============================================================================

@app.route('/')
def dashboard():
    """
    Main dashboard page route
    Displays the AI assistant interface with widgets for weather, appointments, etc.
    
    Returns:
        str: Rendered main_page.html template or redirect to login
    """
    if not ensure_logged_in(): 
        return redirect(url_for('login_page'))
    return render_template('main_page.html')

@app.route('/manual')
def manual_insert():
    """
    Manual booking interface page route
    Provides form-based booking system for direct appointment creation
    
    Returns:
        str: Rendered manual_insert.html template or redirect to login
    """
    if not ensure_logged_in(): 
        return redirect(url_for('login_page'))
    return render_template('manual_insert.html')

@app.route('/admin')
def admin_page():
    """
    Administrator dashboard page route
    Displays customer management interface with user list
    
    Returns:
        str: Rendered admin.html template with customer data or redirect to login
    """
    if not ensure_logged_in(): 
        return redirect(url_for('login_page'))
    # Fetch all users for admin management interface
    customer_list = db.get_all_users()
    return render_template('admin.html', customers=customer_list)

@app.route('/login')
def login_page():
    """
    User authentication page route
    Displays login form for user authentication
    
    Returns:
        str: Rendered login.html template or redirect to dashboard if already logged in
    """
    if ensure_logged_in(): 
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    User logout route
    Clears session data and redirects to login page
    
    Returns:
        Response: Redirect to login page
    """
    session.clear()
    return redirect(url_for('login_page'))

# ============================================================================
# API ROUTES - BOOKING SYSTEM
# RESTful API endpoints for appointment and booking management
# ============================================================================

@app.route('/api/manual_insert', methods=['POST'])
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
        result = db.create_full_appointment(data)
        return jsonify(result), 201
    except db.ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Log the full error for debugging
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred. Please try again."}), 500

# ============================================================================
# API ROUTES - AUTHENTICATION SYSTEM
# User registration, login, and session management endpoints
# ============================================================================

@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    """
    User registration endpoint
    Creates new user account with validation
    
    Expected JSON payload:
        - firstname: User's first name
        - lastname: User's last name  
        - email: Valid email address
        - phone: Phone number
        - password: User password
    
    Returns:
        tuple: JSON response with success/error message and HTTP status code
    """
    try:
        # Delegate user creation to database logic layer
        result = db.create_user(request.json)
        return jsonify(result), 201
    except db.ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {e}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """
    User authentication endpoint
    Validates user credentials and creates session
    
    Note: Currently uses email-only authentication for development
    Password validation is disabled but field is accepted
    
    Expected JSON payload:
        - email: User's email address
        - password: User password (currently ignored)
        - rememberMe: Optional boolean for session persistence
    
    Returns:
        tuple: JSON response with success/error message and HTTP status code
    """
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    # Password is received but ignored for development authentication
    
    user = db.find_user_by_email(email)

    # Development authentication: login with email only
    if user:
        # Create user session with relevant information
        session['user_id'] = user['id']
        session['user_email'] = user['email'] 
        session['user_name'] = f"{user['name']} {user['surname']}"
        session['notification_preference'] = user.get('notification_preference')
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"error": "No user found with that email address"}), 401

@app.route('/api/auth/status')
def api_auth_status():
    """
    Get current user authentication status
    Used by frontend to check if user is logged in and get user info
    
    Returns:
        dict: JSON response with login status and user information
        - logged_in: Boolean indicating authentication status
        - user: Object containing user details (if logged in)
    """
    if ensure_logged_in():
        return jsonify({
            "logged_in": True,
            "user": {
                "name": session.get('user_name'), 
                "email": session.get('user_email'),
                "notification_preference": session.get('notification_preference')
            }
        })
    return jsonify({"logged_in": False})

# ============================================================================
# API ROUTES - USER DATA MANAGEMENT
# Endpoints for retrieving and managing user-specific data
# ============================================================================

@app.route('/api/user/addresses', methods=['GET'])
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

@app.route('/api/appointments', methods=['GET'])
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

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
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
        db.delete_appointment(appointment_id)
        return jsonify({"success": True, "message": "Appointment deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
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
        db.update_appointment(appointment_id, data, user_id)
        return jsonify({"success": True, "message": "Appointment updated"}), 200
    except db.ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update appointment: {str(e)}"}), 500

@app.route('/api/appointments/by-address/<int:address_id>')
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

@app.route('/api/user/addresses-with-preferences')
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

@app.route('/api/services', methods=['GET'])
def api_get_services():
    """
    Get all available cleaning services
    Public endpoint that returns service catalog for booking forms
    
    Returns:
        dict: JSON array of all cleaning services with details
    """
    services = db.get_all_services()
    return jsonify(services)

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    """
    Development server entry point
    Runs Flask application in debug mode for development
    
    Note: Change debug=False for production deployment
    """
    app.run(debug=True)

