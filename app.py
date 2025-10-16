# Flask application to serve a simple frontend and provide a RESTful API
# to the run this, make sure you have Flask installed in your Python environment.
# You can install it using pip:
# pip install Flask 

#to run: python app.py

# app.py

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from datetime import date, datetime
import hashlib

# Initialize the Flask application
app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# Secret key for session management (in production, use a more secure key)
app.secret_key = 'your-secret-key-change-this-in-production'

# --- Helper Functions ---

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

# This acts as our in-memory database, replacing st.session_state.rows
CUSTOMERS = []
USERS = []  # In-memory user storage

# Add a default admin user for testing
default_admin = {
    "id": 1,
    "firstname": "Admin",
    "lastname": "User",
    "email": "admin@datacleaner.com",
    "phone": "+45 12345678",
    "password": hash_password("password123"),
    "created_at": datetime.now().isoformat()
}

def initialize_default_data():
    """Initialize default data if not already present."""
    if not USERS:
        USERS.append(default_admin)

# Custom exception for validation errors
class ValidationError(Exception):
    """Custom exception for handling validation errors."""
    pass

# --- Helper Functions ---

def check_password(stored_password, provided_password):
    """Check if provided password matches stored password."""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def find_user_by_email(email):
    """Find a user by email address."""
    for user in USERS:
        if user["email"].lower().strip() == email.lower().strip():
            return user
    return None

def is_logged_in():
    """Check if user is logged in."""
    return 'user_id' in session

def require_login():
    """Decorator to require login for routes."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not is_logged_in():
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# --- Helper Functions (adapted from your Streamlit code) ---

def find_customer_by_email(email):
    """Finds a customer and their index by email."""
    for i, customer in enumerate(CUSTOMERS):
        if customer["email"].lower().strip() == email.lower().strip():
            return i, customer
    return -1, None

# --- API Logic Functions ---

def create_customer_logic(data):
    """Validates and creates a new customer."""
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    address = data.get("address", "").strip()
    cleaning_date_str = data.get("cleaning_date", "").strip()

    if not name:
        raise ValidationError("Name is required.")
    if "@" not in email:
        raise ValidationError("Not a valid email address.")
    if not address:
        raise ValidationError("Address is required.")

    try:
        cleaning_date = datetime.strptime(cleaning_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Date MUST be in the format YYYY-MM-DD.")

    if cleaning_date < date.today():
        raise ValidationError("Cleaning date cannot be in the past.")
    
    index, _ = find_customer_by_email(email)
    if index != -1:
        raise ValidationError("A customer with this email already exists.")

    new_customer = {
        "name": name,
        "email": email,
        "address": address,
        "cleaning_date": cleaning_date.isoformat()
    }
    CUSTOMERS.append(new_customer)
    return new_customer

def update_date_logic(email, data):
    """Updates the cleaning date for an existing customer."""
    new_date_str = data.get("new_date", "").strip()
    
    try:
        new_cleaning_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("New date must be in the format YYYY-MM-DD.")

    if new_cleaning_date < date.today():
        raise ValidationError("New date cannot be in the past.")
    
    index, customer = find_customer_by_email(email)
    if index == -1:
        raise ValidationError("No customer found with that email.")
    
    CUSTOMERS[index]["cleaning_date"] = new_cleaning_date.isoformat()
    return CUSTOMERS[index]

# --- User Authentication Logic ---

def create_user_logic(data):
    """Create a new user account."""
    firstname = data.get("firstname", "").strip()
    lastname = data.get("lastname", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")

    # Validation
    if not firstname or not lastname:
        raise ValidationError("First name and last name are required.")
    if "@" not in email:
        raise ValidationError("Invalid email address.")
    if not phone:
        raise ValidationError("Phone number is required.")
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    # Check if user already exists
    if find_user_by_email(email):
        raise ValidationError("A user with this email already exists.")

    # Create new user
    new_user = {
        "id": len(USERS) + 1,
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "phone": phone,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    
    USERS.append(new_user)
    return {"success": True, "message": "User created successfully"}

def login_user_logic(data):
    """Authenticate user login."""
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        raise ValidationError("Email and password are required.")

    user = find_user_by_email(email)
    if not user:
        raise ValidationError("Invalid email or password.")

    if not check_password(user["password"], password):
        raise ValidationError("Invalid email or password.")

    # Set session
    session['user_id'] = user["id"]
    session['user_email'] = user["email"]
    session['user_name'] = f"{user['firstname']} {user['lastname']}"

    return {"success": True, "message": "Login successful"}

# --- API Endpoints ---
@app.route('/')
def dashboard():
    """Serves the main dashboard page (requires login)."""
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('main_page.html')

@app.route('/manual')
def manual_insert():
    """Serves the manual insert HTML page (requires login)."""
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('manual_insert.html')

@app.route('/login')
def login():
    """Serves the authentication (login/signup) page."""
    # Redirect to dashboard if already logged in
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/customers', methods=['GET', 'POST'])
def handle_customers():
    """Endpoint for getting all customers or creating a new one (requires login)."""
    if not is_logged_in():
        return jsonify({"error": "Authentication required"}), 401
        
    if request.method == 'POST':
        try:
            new_customer = create_customer_logic(request.json)
            return jsonify(new_customer), 201 # 201 Created
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400 # 400 Bad Request
    else: # GET
        return jsonify(CUSTOMERS)

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login."""
    try:
        result = login_user_logic(request.json)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "Login failed"}), 500

@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    """API endpoint for user registration."""
    try:
        result = create_user_logic(request.json)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "Registration failed"}), 500

@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    """Check if user is logged in."""
    if is_logged_in():
        return jsonify({
            "logged_in": True,
            "user": {
                "id": session.get('user_id'),
                "email": session.get('user_email'),
                "name": session.get('user_name')
            }
        })
    else:
        return jsonify({"logged_in": False})

@app.route('/api/customers/<string:email>', methods=['PUT', 'DELETE'])
def handle_customer(email):
    """Endpoint for updating or deleting a specific customer (requires login)."""
    if not is_logged_in():
        return jsonify({"error": "Authentication required"}), 401
        
    if request.method == 'PUT':
        try:
            updated_customer = update_date_logic(email, request.json)
            return jsonify(updated_customer)
        except ValidationError as e:
            # Check for "not found" error to return a 404
            if "No customer found" in str(e):
                 return jsonify({"error": str(e)}), 404 # 404 Not Found
            return jsonify({"error": str(e)}), 400 # 400 Bad Request

    elif request.method == 'DELETE':
        index, _ = find_customer_by_email(email)
        if index == -1:
            return jsonify({"error": "No customer found with that email."}), 404 # 404 Not Found
        
        CUSTOMERS.pop(index)
        return '', 204 # 204 No Content

# --- Main entry point ---
if __name__ == '__main__':
    initialize_default_data()  # Initialize default users
    app.run(debug=True) # Runs the development server