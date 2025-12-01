#!/usr/bin/env python3
"""
Simple script to set up YouTube Music authentication using browser headers.
This method is simpler than OAuth and doesn't require Google Cloud Console setup.
"""

from ytmusicapi import YTMusic

print("=" * 70)
print("YouTube Music Browser Authentication Setup")
print("=" * 70)
print("\nThis will create a 'headers.json' file for authentication.")
print("The authentication will remain valid for ~2 years.\n")

print("INSTRUCTIONS:")
print("1. Open https://music.youtube.com in your browser")
print("2. Make sure you're logged in")
print("3. Open Developer Tools (F12 or Ctrl+Shift+I)")
print("4. Go to the 'Network' tab")
print("5. Filter by '/browse' in the search bar")
print("6. Scroll down the page or click 'Library' to trigger a request")
print("7. Click on a 'browse' request")
print("8. In the 'Headers' tab, scroll to 'Request Headers'")
print("9. Copy EVERYTHING from 'accept: */*' to the end")
print("10. Paste below and press Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows)\n")
print("=" * 70)

try:
    # This will prompt for headers in the terminal
    auth_string = YTMusic.setup(filepath="headers.json")
    print("\n" + "=" * 70)
    print("✓ SUCCESS! Authentication saved to 'headers.json'")
    print("=" * 70)
    print("\nYou can now run the migration script:")
    print("  bash run.sh")
    print("\nor:")
    print("  python spotify_to_ytmusic.py")
except KeyboardInterrupt:
    print("\n\nSetup cancelled.")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nIf you're having trouble, make sure you:")
    print("- Are logged into YouTube Music in your browser")
    print("- Copied the ENTIRE request headers section")
    print("- Included everything from 'accept:' to the end")
