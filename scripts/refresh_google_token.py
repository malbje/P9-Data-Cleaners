#!/usr/bin/env python3
"""
Quick script to manually test and refresh Google OAuth token.
Run this if your Google Calendar integration stops working.

Usage:
    python refresh_google_token.py
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from backend.service import calendar as gcal
from google.auth.transport.requests import Request
import private_settings

def test_and_refresh_token():
    """Test current token and try to refresh if expired."""
    print("=" * 60)
    print("GOOGLE OAUTH TOKEN TESTER & REFRESHER")
    print("=" * 60)
    
    # Check if token exists
    if not hasattr(private_settings, 'TOKEN') or not private_settings.TOKEN:
        print("❌ No TOKEN found in private_settings.py")
        print("\nYou need to authorize first. Run:")
        print("  1. Start the Flask app: python app.py")
        print("  2. Visit: http://127.0.0.1:5000/calendar/connect")
        print("  3. Complete the Google OAuth flow")
        return False
    
    token = private_settings.TOKEN
    print(f"\n✅ Token found in private_settings.py")
    print(f"   Client ID: {token.get('client_id', 'N/A')[:20]}...")
    print(f"   Expires: {token.get('expiry', 'N/A')}")
    
    # Try to build credentials
    try:
        creds = gcal._credentials_from_private_settings()
        print(f"\n✅ Credentials loaded successfully")
        
        if creds.expired:
            print(f"⚠️  Token is EXPIRED - refreshing...")
            try:
                creds.refresh(Request())
                gcal._write_token_to_private_settings(creds)
                print(f"✅ Token refreshed and saved to private_settings.py")
                print(f"   New expiry: {creds.expiry}")
                return True
            except Exception as e:
                print(f"❌ Refresh failed: {e}")
                print("\nRefresh token is likely invalid or revoked.")
                print("You need to authorize again:")
                print("  1. Start the Flask app: python app.py")
                print("  2. Visit: http://127.0.0.1:5000/calendar/connect")
                print("  3. Complete the Google OAuth flow")
                return False
        else:
            print(f"✅ Token is VALID (not expired)")
            print(f"   Expires: {creds.expiry}")
            return True
            
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False


def test_calendar_access():
    """Test if we can actually fetch Google Calendar events."""
    print("\n" + "=" * 60)
    print("TESTING GOOGLE CALENDAR ACCESS")
    print("=" * 60)
    
    try:
        service = gcal.get_service_from_private_settings()
        if not service:
            print("❌ Could not create service")
            return False
        
        print("✅ Service created successfully")
        
        # Try to list events
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        start_iso = now.isoformat()
        end_iso = now.replace(day=now.day + 7).isoformat()
        
        events = gcal.fetch_google_events(start_iso, end_iso)
        print(f"✅ Successfully fetched {len(events)} upcoming events from Google Calendar")
        
        if events:
            print("\nUpcoming events:")
            for event in events[:3]:
                print(f"  - {event.get('summary', 'No title')} ({event.get('start', 'N/A')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_and_refresh_token()
    
    if success:
        test_calendar_access()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Everything looks good!")
    else:
        print("❌ Please re-authorize with Google to fix the issue")
    print("=" * 60)
