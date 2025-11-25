from flask import Blueprint, request, jsonify
import backend.service.database_logic as db
from backend.service import calendar as gcal
from backend.service import merge as merge_service

api_calendar_bp = Blueprint('calendar_api', __name__, url_prefix='/api/calendar')


@api_calendar_bp.route('/combined')
def api_calendar_combined():
    """
    Return merged list of Google Calendar events and DB appointments.
    Query params: start, end (ISO datetimes). If omitted, defaults to next 7 days.
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

    try:
        google_events = gcal.fetch_google_events(start_iso, end_iso)
    except Exception as e:
        # If Google fetch fails, still try to return DB appointments
        google_events = []

    # Fetch DB appointments (detailed joint view)
    try:
        db_appts = db.get_all_appointments()
    except Exception as e:
        return jsonify({"error": "Failed to read appointments from DB", "details": str(e)}), 500

    merged = merge_service.merge_events(google_events, db_appts)
    return jsonify(merged)
