from flask import Blueprint, request, jsonify, session, redirect, url_for
import backend.service.database_logic as db
from backend.service import calendar as gcal
from backend.service import merge as merge_service
import logging
from google.auth.exceptions import RefreshError

logger = logging.getLogger(__name__)
api_calendar_bp = Blueprint('calendar_api', __name__, url_prefix='')


@api_calendar_bp.route('/api/calendar/combined')
def api_calendar_combined():
    """Return merged list of Google Calendar events and DB appointments.

    Query params: start, end (ISO datetimes). If omitted, defaults to next 7 days.
    
    Special response when token is invalid:
    {
        "error": "google_auth_required",
        "message": "Google Calendar authorization required",
        "auth_url": "/calendar/connect"
    }
    """
    start = request.args.get('start')
    end = request.args.get('end')
    # Default range: now -> now + 7 days
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    if not start:
        start_iso = now.isoformat()
    else:
        start_iso = start
    if not end:
        end_iso = (now + timedelta(days=7)).isoformat()
    else:
        end_iso = end

    google_events = []
    try:
        google_events = gcal.fetch_google_events(start_iso, end_iso)
    except RefreshError as e:
        # Token is invalid/expired - return special error code
        logger.warning("Google token refresh failed: %s", str(e))
        return jsonify({
            "error": "google_auth_required",
            "message": "Google Calendar authorization required",
            "auth_url": "/calendar/connect"
        }), 401
    except Exception as e:
        # If Google fetch fails for other reasons, still try to return DB appointments
        logger.exception("Google fetch failed: %s", str(e))
        google_events = []

    # Fetch DB appointments (detailed joint view)
    try:
        db_appts = db.get_all_appointments()
    except Exception as e:
        return jsonify({"error": "Failed to read appointments from DB", "details": str(e)}), 500

    merged = merge_service.merge_events(google_events, db_appts)
    return jsonify(merged)


# ----------------- Web-facing calendar routes (moved from app.py) -----------------
@api_calendar_bp.route('/signup', methods=['GET', 'POST'])
def signup_page():
    """Start OAuth flow (consent screen)"""
    # require login in real app; kept permissive for dev
    authorization_url, state = gcal.authorization_url()
    session['google_auth_state'] = state
    logger.debug("redirecting user to Google OAuth consent screen")
    return redirect(authorization_url)


@api_calendar_bp.route('/google/oauth2callback')
def google_oauth2callback():
    """OAuth2 callback: exchange code for tokens and persist them."""
    state = session.get('google_auth_state')
    if not state:
        return 'State parameter missing in session. Try /signup again', 400

    # Exchange and persist tokens
    creds = gcal.fetch_and_persist_tokens(request.url)

    # store in session for immediate use
    session['google_credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
    }
    return redirect(url_for('dashboard'))


@api_calendar_bp.route('/calendar/connect')
def calendar_connect():
    logger.debug("/calendar/connect route hit")
    authorization_url, state = gcal.authorization_url()
    session['google_auth_state'] = state
    logger.debug("redirecting user to Google OAuth consent: %s", authorization_url)
    return redirect(authorization_url)


@api_calendar_bp.route('/calendar/status')
def calendar_status():
    """Show upcoming Google events (debug view)."""
    service = gcal.get_service_from_private_settings()
    if service is None:
        return (
            'You have not authorized Google Calendar access yet. '
            'Please <a href="http://127.0.0.1:5000/google/oauth2callback">login with Google</a> to enable calendar features.'
        )

    events_result = service.events().list(
        calendarId='primary', maxResults=10, singleEvents=True, orderBy='startTime'
    ).execute()
    items = events_result.get('items', [])
    if not items:
        return 'Connected, but no upcoming events found in your Google Calendar.'
    lines = []
    for ev in items:
        start = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date'))
        title = ev.get('summary', 'No Title')
        lines.append(f"{start} - {title}")
    return '<br>'.join(lines)


