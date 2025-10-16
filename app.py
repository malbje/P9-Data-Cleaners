# app.py
# This single file contains all application logic, routing, and database interaction.

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from database.DB_access import get_connection
import database_logic as db # Import the logic file

# --- Flask App Initialization ---
app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)
app.secret_key = 'your-secret-key-change-this-in-production'

# --- Custom Exception ---
class ValidationError(Exception):
    pass

# --- Helper function to ensure login ---
def ensure_logged_in():
    """Checks if a user_id exists in the current session."""
    return 'user_id' in session

# --- PAGE ROUTES ---
@app.route('/')
def dashboard():
    if not ensure_logged_in(): return redirect(url_for('login_page'))
    return render_template('main_page.html')

@app.route('/manual')
def manual_insert():
    if not ensure_logged_in(): return redirect(url_for('login_page'))
    return render_template('manual_insert.html')

@app.route('/admin')
def admin_page():
    if not ensure_logged_in(): return redirect(url_for('login_page'))
    # Use the new function from database_logic to fetch users
    customer_list = db.get_all_users()
    return render_template('admin.html', customers=customer_list)

@app.route('/login')
def login_page():
    if ensure_logged_in(): return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# --- API ROUTES ---

@app.route('/api/manual_insert', methods=['POST'])
def api_manual_insert():
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


@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    try:
        # Call the function from the database_logic file
        result = db.create_user(request.json)
        return jsonify(result), 201
    except db.ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {e}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    # The password from the form is received but will be ignored.

    user = db.find_user_by_email(email)

    # For development: if a user with the provided email exists, log them in
    # without checking the password.
    if user:
        # Store user info in session
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = f"{user['name']} {user['surname']}"
        # Add the notification preference to the session
        session['notification_preference'] = user.get('notification_preference')
        return jsonify({"success": True, "message": "Login successful"})
    else:
        # If no user is found with that email, return an error.
        return jsonify({"error": "No user found with that email address"}), 401

@app.route('/api/auth/status')
def api_auth_status():
    if ensure_logged_in():
        return jsonify({
            "logged_in": True,
            "user": {
                "name": session.get('user_name'), 
                "email": session.get('user_email'),
                # Add the preference to the user object in the response
                "notification_preference": session.get('notification_preference')
            }
        })
    return jsonify({"logged_in": False})

@app.route('/api/user/addresses', methods=['GET'])
def api_get_user_addresses():
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    from database.DB_read import DB_read
    reader = DB_read()
    user_id = session.get('user_id')
    addresses = reader.get_addresses_by_customer_id(user_id)
    return jsonify(addresses)

@app.route('/api/appointments', methods=['GET'])
def api_get_appointments():
    if not ensure_logged_in(): 
        return jsonify({"error": "Authentication required"}), 401
    
    user_id = session.get('user_id')
    # Call the new function to get appointments for the logged-in user
    appointments = db.get_appointments_for_customer(user_id) 
    return jsonify(appointments)

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def api_delete_appointment(appointment_id):
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        # Call the delete function from the database_logic file
        db.delete_appointment(appointment_id)
        return jsonify({"success": True, "message": "Appointment deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
def api_update_appointment(appointment_id):
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Extract the user_id from the session
        user_id = session.get('user_id')

        # Call the update function from the database_logic file
        db.update_appointment(appointment_id, data, user_id)
        return jsonify({"success": True, "message": "Appointment updated"}), 200
    except db.ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update appointment: {str(e)}"}), 500

@app.route('/api/appointments/by-address/<int:address_id>')
def api_get_appointments_by_address(address_id):
    """Gets all appointments for a specific address ID."""
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    # This is the correct way to use your DB_read class
    from database.DB_read import DB_read
    reader = DB_read()
    
    try:
        # Call the method from the reader object
        appointments = reader.get_appointments_by_address_id(address_id)
        return jsonify(appointments)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch appointments: {str(e)}"}), 500

@app.route('/api/user/addresses-with-preferences')
def api_get_user_addresses_with_preferences():
    """Provides a list of user addresses along with their preferences."""
    if not ensure_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    user_id = session.get('user_id')
    # This calls the existing function from database_logic.py
    addresses = db.get_addresses_and_preferences_for_customer(user_id)
    return jsonify(addresses)

@app.route('/api/services', methods=['GET'])
def api_get_services():
    """Provides a list of all available cleaning services."""
    services = db.get_all_services()
    return jsonify(services)

# --- MAIN ENTRY ---
if __name__ == '__main__':
    app.run(debug=True)

