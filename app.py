#This is the main Flask application file for the Data Cleaners booking system.
# we define the Flask app, configure it, and register Blueprints for API routes.
# we use the routes/ folder to organize our API endpoints into separate files,
# for better maintainability and to avoid making this file too big.
# This means that app.py mainly handles web page routes and application setup.
# but the actual API logic is in backend/routes/api_auth.py and backend/routes/api_data.py


# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================

from backend.service.llm_tools import chat_with_tools # Import chat function with tool integration
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from database.DB_access import get_connection
# Sørg for at db-importstien er korrekt
import backend.service.database_logic as db 

# Import Blueprints for API routes
from backend.routes.api_auth import api_auth_bp
from backend.routes.api_data import api_data_bp


# FLASK APPLICATION INITIALIZATION
"""
Flask application instance with custom template and static folders
Configured to serve frontend files from the frontend directory structure
"""
app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

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
# REGISTRER BLUEPRINTS defined in separate route files
# ============================================================================

# API route for AI assistant chat interaction
@app.route('/api/chat', methods=['POST'])
def api_chat():
    if not ensure_logged_in(): # Ensure data privacy
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json() or {}
    user_message = data.get("message", "").strip() # ensures good UX and avoids empty messages
    if not user_message:
        return jsonify({"reply": "Skriv noget, så hjælper jeg dig 😊"})

    # valgfrit: historik for bedre dialogflow
    history = session.get("chat_history", [])

    reply = chat_with_tools(user_message, chat_history=history)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    session["chat_history"] = history[-12:]  # model can follow conversation history for performance

    return jsonify({"reply": reply})



app.register_blueprint(api_auth_bp)
app.register_blueprint(api_data_bp)


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