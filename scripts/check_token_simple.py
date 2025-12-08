#!/usr/bin/env python3
"""
Simple token checker without heavy Google imports.
"""

import sys
import os
import json

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__) + "/..")
sys.path.insert(0, project_root)

try:
    import private_settings
    
    print("=" * 60)
    print("CHECKING OAUTH TOKEN IN private_settings.py")
    print("=" * 60)
    
    if not hasattr(private_settings, 'TOKEN'):
        print("\n❌ No TOKEN attribute found in private_settings.py")
        sys.exit(1)
    
    token = private_settings.TOKEN
    if not token:
        print("\n❌ TOKEN is empty/None in private_settings.py")
        sys.exit(1)
    
    print("\n✅ TOKEN found!")
    print(f"\nToken details:")
    print(f"  - Client ID: {token.get('client_id', 'N/A')[:30]}...")
    print(f"  - Has refresh_token: {'refresh_token' in token and bool(token['refresh_token'])}")
    print(f"  - Has access token: {'token' in token and bool(token['token'])}")
    print(f"  - Expiry: {token.get('expiry', 'N/A')}")
    print(f"  - Scopes: {token.get('scopes', 'N/A')}")
    
    # Check if refresh token exists
    refresh_token = token.get('refresh_token')
    if not refresh_token:
        print("\n⚠️  WARNING: No refresh_token in TOKEN!")
        print("   You MUST re-authorize with Google")
        print("   Steps:")
        print("   1. python app.py")
        print("   2. Visit http://127.0.0.1:5000/calendar/connect")
        print("   3. Complete Google OAuth flow")
        sys.exit(1)
    
    print(f"\n✅ Refresh token exists: {refresh_token[:20]}...")
    print("\n📝 Next step: Start the Flask app and let it auto-refresh the token")
    print("   python app.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
