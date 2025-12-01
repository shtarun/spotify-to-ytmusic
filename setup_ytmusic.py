#!/usr/bin/env python3
"""
Simple script to set up YouTube Music OAuth authentication.
This will open a browser window for you to authorize the application.
"""

from ytmusicapi.setup import setup_oauth

print("Setting up YouTube Music OAuth authentication...")
print("A browser window will open for Google authentication.")
print("Please sign in with your YouTube Music account and authorize the application.\n")

try:
    setup_oauth(filepath="oauth.json", open_browser=True)
    print("\n✓ Success! Authentication saved to oauth.json")
    print("You can now run the migration script: python spotify_to_ytmusic.py")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nAlternative setup method:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a project and enable YouTube Data API v3")
    print("3. Create OAuth 2.0 credentials (Desktop app)")
    print("4. Download client secrets and use them with this script")
