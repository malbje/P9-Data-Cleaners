#This is the main Flask application file for the Data Cleaners booking system.
# we define the Flask app, configure it, and register Blueprints for API routes.
# we use the routes/ folder to organize our API endpoints into separate files,
# for better maintainability and to avoid making this file too big.
# This means that app.py mainly handles web page routes and application setup.
# but the actual API logic is in backend/routes/api_auth.py and backend/routes/api_data.py


# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from database.DB_access import get_connection
from LLM_main_class import LLM_Conversation # Import LLM_Conversation class
# Sørg for at db-importstien er korrekt
import backend.service.database_logic as db 
from database.DB_write import DB_write
import os # For environment variable access

# ============================================================================
# WEATHER SERVICE IMPORT
# ============================================================================
from backend.service.weather_service import get_precipitation  
# 🟢 Imports the helper function 'get_weather_data()' from our weather_service module.
# This function is responsible for fetching weather information (from DMI or Open-Meteo)
# and returning it in a clean JSON structure that can be sent to the frontend.


# Import Blueprints for API routes
from backend.routes.api_auth import api_auth_bp
from backend.routes.api_data import api_data_bp
from backend.routes.api_customers import api_customers_bp

# Imports for Google Calendars API integration (not directly used in this file, but needed for database_logic functions)
import pathlib #to Google API client libraries
from dotenv import load_dotenv # to load environment variables from .env file
from google.oauth2.credentials import Credentials # to handle OAuth2 credentials
from google_auth_oauthlib.flow import Flow # to manage OAuth2 flow (authorization, code, token exchange)
from googleapiclient.discovery import build # to build Google API service clients

# ---------------------------------------------------------------------------
# FLASK APPLICATION INITIALIZATION
# ---------------------------------------------------------------------------
"""
Flask application instance with custom template and static folders
Configured to serve frontend files from the frontend directory structure
"""
app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# Configure Flask session secret key.
# Order of precedence:
# 1) environment variable SECRET_KEY
# 2) private_settings.SECRET_KEY if present
# 3) developer fallback (persistent string) with a warning (NOT for production)
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    try:
        import private_settings
        secret_key = getattr(private_settings, 'SECRET_KEY', None)
    except Exception:
        secret_key = None

if not secret_key:
    # Persistent dev fallback avoids session invalidation on interpreter restarts.
    secret_key = 'dev-secret-change-me-please-set-SECRET_KEY'
    print("WARNING: Flask SECRET_KEY not set. Set environment variable SECRET_KEY or private_settings.SECRET_KEY for production.")

app.secret_key = secret_key # Set Flask secret key for session management

# =====================================================================================================================================================================================
# GOOGLE CALENDAR / OAUTH CONFIGURATION
# To start Google OAuth2 flow and access Calendar API: http://127.0.0.1:5000/calendar/connect
# To get users calendar events: http://127.0.0.1:5000/calendar/status
# To create a calendar event: http://127.0.0.1:5000/calendar/create-cleaning
# To update or delete events, use Event ID from event creation response
# To check if user is free / busy at a time: Implement route using FreeBusy (@app.route('/calendar/freebusy') xxx), afterwards use: http://127.0.0.1:5000/calendar/freebusy
# To combine with AI assistant, add functionality in e.g: LLM_main.py (from backend.service.calendar import get_calendar_service) + function (def suggest_cleaning_time(): xxx...)
# ======================================================================================================================================================================================

load_dotenv()  # Load environment variables from .env file

BASE_DIR = pathlib.Path(__file__).parent
CLIENT_SECRETS_FILE = BASE_DIR / "secrets" / "client_secret.json" # "secrets" and "client_secret.json" for correct path to client secrets

GOOGLE_SCOPES = [os.getenv("GOOGLE_OAUTH_SCOPE", "https://www.googleapis.com/auth/calendar")] # OAuth2 scopes for Google Calendar access
GOOGLE_REDIRECT_URI = "http://127.0.0.1:5000/google/oauth2callback"  # Redirect URI for OAuth2 flow


def build_flow():
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )

def get_calendar_service(): # builds authorized Google Calendar API client
    creds_data = session.get('google_credentials')
    if not creds_data:
        return None
    
    creds = Credentials(
        token=creds_data['token'],
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=creds_data['scopes']
    )
    service = build('calendar', 'v3', credentials=creds) # Build Google Calendar API service client
    return service # Return the service client

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


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    """
    Render signup form (GET) and handle signup submissions (GET with query params, POST form or JSON).
    On successful creation, redirect to signup_confirmed with the new customer id.
    """
    # If this is a simple page load -> render the template
    if request.method == 'GET' and not any(k in request.args for k in ('firstname', 'lastname', 'email', 'street', 'city', 'postal_code')):
        return render_template('signup.html')

    # Accept data from multiple sources (GET query, POST form, or JSON)
    source = request.args if request.method == 'GET' else (request.form if request.form else request.get_json(silent=True) or {})
    name = source.get('firstname') or source.get('name')
    surname = source.get('lastname') or source.get('surname')
    email = source.get('email')
    street = source.get('street')
    city = source.get('city')
    postal_code = source.get('postal_code') or source.get('postalcode') or source.get('postal')

    # Basic validation
    if not (name and surname and email):
        # Render the form again with an error message (frontend can show it)
        return render_template('signup.html', error="Missing required fields: firstname, lastname, email", form=source), 400

    # Build payload for DB_write.create_customer_with_address
    payload = {
        "name": name,
        "surname": surname,
        "email": email,
    }
    if street and city and postal_code:
        payload["address"] = {
            "street_and_number": street,
            "postal_code": postal_code,
            "city_name": city
        }

    try:
        writer = DB_write()
        result = writer.create_customer_with_address(payload)
        customer_id = result.get("customer_id")
        if customer_id:
            # signup confirmation page removed — redirect user to login instead
            return redirect(url_for('login_page'))
        # fallback if creation didn't return id
        return render_template('signup.html', error="Failed to create account, please try again."), 500
    except ValueError as ve:
        return render_template('signup.html', error=str(ve), form=source), 400
    except Exception:
        app.logger.exception("Signup failed")
        return render_template('signup.html', error="Internal server error"), 500

# ============================================================================
# REGISTERED BLUEPRINTS defined in separate route files
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

    # Asking chat_gpt for a reply
    reply = chatbot.ask_llm(user_message)

    return jsonify({"reply": reply})

# New route: create customer (+ optional address) from frontend JSON
@app.route('/api/customers', methods=['POST'])
def api_create_customer():
     payload = request.get_json()
     if not payload:
         return jsonify({"error": "Invalid or missing JSON body"}), 400

     try:
         writer = DB_write()
         result = writer.create_customer_with_address(payload)
         return jsonify(result), 201
     except ValueError as ve:
         return jsonify({"error": str(ve)}), 400
     except Exception:
         app.logger.exception("Failed to create customer")
         return jsonify({"error": "Internal server error"}), 500
# ============================================================================
# WEATHER SERVICE ROUTE
# ============================================================================
@app.route("/api/weather", methods=["GET"])
def api_weather():
    """
    API route: Provides live weather data to the frontend and other modules.
    
    Why:
        This endpoint allows the main dashboard and AI logic to access
        up-to-date weather information for contextual suggestions and
        user-facing widgets.
    
    How:
        Calls get_weather_data() from backend/service/weather_service.py,
        which handles both DMI and fallback APIs (Open-Meteo).
        Returns the structured JSON data to the frontend for rendering.
    """
    # 🟢 Fetch latest weather data using helper function
    data = get_precipitation()
    
    # 🟢 Convert the Python dict to JSON and send it back to the browser
    return jsonify(data)


app.register_blueprint(api_auth_bp)
app.register_blueprint(api_data_bp)
app.register_blueprint(api_customers_bp)


# This means that the app is run, if this file is run
if __name__ == '__main__':
    """
    Development server entry point
    Runs Flask application in debug mode for development
    
    Note: Change debug=False for production deployment
    """
    chatbot = LLM_Conversation()  # Initialize chatbot instance

    app.run(debug=True)