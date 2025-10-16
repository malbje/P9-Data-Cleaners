# Flask application to serve a simple frontend and provide a RESTful API
# to the run this, make sure you have Flask installed in your Python environment.
# You can install it using pip:
# pip install Flask 

#to run: python app.py

# app.py

from flask import Flask, request, jsonify, render_template
from datetime import date, datetime

# Initialize the Flask application
app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# This acts as our in-memory database, replacing st.session_state.rows
CUSTOMERS = []

# Custom exception for validation errors
class ValidationError(Exception):
    """Custom exception for handling validation errors."""
    pass

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

# --- API Endpoints ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/customers', methods=['GET', 'POST'])
def handle_customers():
    """Endpoint for getting all customers or creating a new one."""
    if request.method == 'POST':
        try:
            new_customer = create_customer_logic(request.json)
            return jsonify(new_customer), 201 # 201 Created
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400 # 400 Bad Request
    else: # GET
        return jsonify(CUSTOMERS)

@app.route('/api/customers/<string:email>', methods=['PUT', 'DELETE'])
def handle_customer(email):
    """Endpoint for updating or deleting a specific customer."""
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
    app.run(debug=True) # Runs the development server