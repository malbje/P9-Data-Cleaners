# backend/routes/api_auth.py
# We use this file to handle all authentication-related API endpoints
# this could have been in app.py, but for better organization we separate it out, to not make the file too big
# The api_data.py file works similarly, but for data-related endpoints.

"""
Contains all API endpoints for authentication (login, signup, status).
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
import backend.service.database_logic as db 


# create a Blueprint. all routes in this file will start with /api/auth
api_auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')


# ============================================================================
# API ROUTES - AUTHENTICATION SYSTEM
# User registration, login, and session management endpoints
# ============================================================================

@api_auth_bp.route('/signup', methods=['POST'])
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

@api_auth_bp.route('/login', methods=['POST'])
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

@api_auth_bp.route('/status')
def api_auth_status():
    """
    Get current user authentication status
    Used by frontend to check if user is logged in and get user info
    
    Returns:
        dict: JSON response with login status and user information
        - logged_in: Boolean indicating authentication status
        - user: Object containing user details (if logged in)
    """
    if 'user_id' in session: # Brug 'user_id' in session direkte
        return jsonify({
            "logged_in": True,
            "user": {
                "name": session.get('user_name'), 
                "email": session.get('user_email'),
                "notification_preference": session.get('notification_preference')
            }
        })
    return jsonify({"logged_in": False})