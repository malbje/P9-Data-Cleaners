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
import os # For environment variable access

# Import Blueprints for API routes
from backend.routes.api_auth import api_auth_bp
from backend.routes.api_data import api_data_bp

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

# ============================================================================
# GOOGLE CALENDAR ROUTES
# Routes that handle Google Calendar OAuth2 and API interactions
# ============================================================================

@app.route('/google/login') # Initiates Google Calendar OAuth2 flow
def google_login():
    """
    Step 1 of Google Calendar login
    Sends user to Google OAuth2 consent screen for authentication
    """
    if not ensure_logged_in(): 
        return redirect(url_for('login_page'))
    
    flow = build_flow()

    authorization_url, state = flow.authorization_url(
        access_type='offline', # to get refresh token
        include_granted_scopes='true', # to reuse existing permissions
        prompt='consent' # to ensure refresh token is provided
    )

    session['google_auth_state'] = state
    print("DEBUG: redirecting user to Google OAuth consent screen")
    return redirect(authorization_url)



# Store state in session for callback verification
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/google/oauth2callback') # Called by Google after user consents
def google_oauth2callback():
    """
    Step 2 of Google Calendar login
    Google redirects back here after user consents
    Exchange authorization code for access and refresh tokens
    """
    if not ensure_logged_in(): 
        return redirect(url_for('login_page'))
    
    state = session.get('google_auth_state')
    if not state:
        return 'State parameter missing in session. Try /google/login again', 400

    flow = build_flow()
    flow.fetch_token(authorization_response=request.url) # Exchange code for tokens

    Creds = flow.credentials # Get OAuth2 credentials

    # Temporarily: Store credentials in session (for demo purposes)
    # Later: Store in database connected to session['user_id']
    session['google_credentials'] = {
        'token': Creds.token,
        'refresh_token': Creds.refresh_token,
        'token_uri': Creds.token_uri,
        'client_id': Creds.client_id,
        'client_secret': Creds.client_secret,
        'scopes': Creds.scopes
    }

# Directs user to status-page after successful OAuth2 flow
    return redirect(url_for('dashboard'))


@app.route('/calendar/status')
def calendar_status():
    """
    Debug/inspection page:
    - Shows whether user has allowed Google Calendar access
    - Displays upcoming calendar events if access granted
    """
    if not ensure_logged_in(): 
        return redirect(url_for('login_page'))
    
    service = get_calendar_service()
    if service is None:
        # not yet authorized
        return (
            'You have not authorized Google Calendar access yet. '
            'Please <a href="/google/login">login with Google</a> to enable calendar features.'
        )
    
    events_result = service.events().list( # Fetch upcoming events
        calendarId='primary', # user's primary calendar
        maxResults=10, # fetch next 10 events
        singleEvents=True, # expand recurring events
        orderBy='startTime' # order by start time
    ).execute()

    items = events_result.get('items', []) # Get list of events
    if not items:
        return 'Connected, but no upcoming events found in your Google Calendar.'
    
    lines = [] # Prepare event display lines
    for ev in items: # Iterate over events
        start = ev['start'].get('dateTime', ev['start'].get('date')) # event start time
        title = ev.get('summary', 'No Title') # event title
        lines.append(f"{start} - {title}") # format event line

        return '<br>'.join(lines) # Return formatted event list
    

@app.route('/calendar/create-cleaning')
def create_cleaning_event():
    """
    Creates cleaning appointment event in user's Google Calendar
    (Hardcoded example for demonstration purposes - AI-suggestions can be integrated later)
    """
    if not ensure_logged_in():
        return redirect(url_for('login_page'))
    
    service = get_calendar_service()
    if service is None:
        return redirect(url_for('google_login')) # Prompt user to authorize if not done
    
    event_body = {
        'Summary': 'House Cleaning Appointment',
        'Description': 'Vacuuming, floor mopping, kitchen, bathroom',
        'Start': {
            'dateTime': '2024-07-01T10:00:00',
            'timeZone': 'Europe/Copenhagen',
        },
        'End': {
            'dateTime': '2024-07-01T12:00:00',
            'timeZone': 'Europe/Copenhagen'
        }
    }

    create = service.events().insert( # Create event in calendar
        calendarId='primary',
        body=event_body,
        sendUpdates='none' # No notifications
    ).execute()

    return f'Event created ✔ Event ID: {create.get("id")}'


@app.route('/calendar/connect')
def calendar_connect():
    # Midlertidigt: ikke kræv login, så vi kan teste OAuth-flowet nemt.
    # Når I er færdige med at teste, kan I slå det her til igen:
    # if not ensure_logged_in():
    #     return redirect(url_for('login_page'))

    print("DEBUG: /calendar/connect route was hit!")

    flow = build_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",          # vi vil gerne have refresh_token
        include_granted_scopes="true",  # genbrug eksisterende tilladelser
        prompt="consent"                # tving dialogen så vi får refresh_token i dev
    )

    # gem state i session, så vi kan validere callbacket
    session["google_auth_state"] = state

    print("DEBUG: redirecting user to Google OAuth consent:", authorization_url)
    return redirect(authorization_url)

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