from datetime import datetime, timedelta, timezone


def _parse_iso(s: str):
    """Parse an ISO datetime or date string into a timezone-aware datetime when possible.

    Accepts 'YYYY-MM-DD' or full ISO datetimes. Replaces trailing 'Z' with '+00:00'.
    """
    if s is None:
        return None
    try:
        if s.endswith('Z'):
            s = s.replace('Z', '+00:00')
        # datetime.fromisoformat handles both date and datetime forms (date -> becomes date at midnight)
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        # Last-resort: try parsing date-only
        try:
            return datetime.fromisoformat(s + 'T00:00:00')
        except Exception:
            return None


def _parse_event_start_end(evt):
    """Return (start_dt, end_dt) for a normalized google event dict."""
    s = evt.get('start')
    e = evt.get('end')
    if s is None:
        return None, None
    # google event start may be date-only (YYYY-MM-DD) or dateTime
    start_dt = _parse_iso(s) if isinstance(s, str) else None
    end_dt = _parse_iso(e) if isinstance(e, str) and e else None
    # If end missing, assume 1 hour duration
    if start_dt and not end_dt:
        end_dt = start_dt + timedelta(hours=1)
    return start_dt, end_dt


def _parse_db_appointment(appt):
    """Return (start_dt, end_dt) for a DB appointment row.

    Expects `date` in ISO YYYY-MM-DD and `time` as HH:MM (string) or None.
    If time missing we treat it as full-day start at 00:00.
    """
    # Primary expected fields
    date = appt.get('date')
    time = appt.get('time') or "00:00"

    if date:
        try:
            start = datetime.fromisoformat(f"{date}T{time}")
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
        except Exception:
            # Fallback: try our ISO helper
            start = _parse_iso(f"{date}T{time}")
    else:
        start = None

    # If we couldn't parse using `date`/`time`, try common alternate fields
    if start is None:
        # try a few commonly-used datetime keys on the DB row
        for key in ('start', 'start_datetime', 'appointment_datetime', 'datetime', 'begins'):
            val = appt.get(key)
            if isinstance(val, str):
                candidate = _parse_iso(val)
                if candidate:
                    start = candidate
                    break

    if start is None:
        return None, None

    # default duration: 1 hour
    end = start + timedelta(hours=1)
    return start, end


def events_overlap(a_start, a_end, b_start, b_end):
    if not all([a_start, a_end, b_start, b_end]):
        return False
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    return latest_start < earliest_end


def merge_events(google_events, db_appointments):
    """Merge lists of normalized google events and DB appointments.

    Returns list of objects: {"google": <event or None>, "appointment": <appt or None>, "matched": bool}
    """
    merged = []
    used_db = set()

    # Pre-parse DB appointments into datetime ranges
    db_ranges = []
    for idx, appt in enumerate(db_appointments):
        start, end = _parse_db_appointment(appt)
        db_ranges.append((idx, appt, start, end))

    for g in google_events:
        g_start, g_end = _parse_event_start_end(g)
        match_idx = None
        for idx, appt, a_start, a_end in db_ranges:
            if idx in used_db:
                continue
            if events_overlap(g_start, g_end, a_start, a_end):
                match_idx = idx
                used_db.add(idx)
                merged.append({"google": g, "appointment": appt, "matched": True})
                break
        if match_idx is None:
            merged.append({"google": g, "appointment": None, "matched": False})

    # Add remaining DB-only appointments
    for idx, appt, a_start, a_end in db_ranges:
        if idx not in used_db:
            merged.append({"google": None, "appointment": appt, "matched": False})

    return merged
