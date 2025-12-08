#!/usr/bin/env python3
"""
Simple script to set up YouTube Music authentication using browser headers.
This method is simpler than OAuth and doesn't require Google Cloud Console setup.
"""

import json
import os
from ytmusicapi import setup

def validate_headers(headers_str):
    """Validate that the pasted headers look reasonable."""
    headers_str = headers_str.strip()
    
    # Check if it's not empty
    if not headers_str:
        return False, "Headers are empty. Please paste the request headers."
    
    # Check if it looks like JSON (sometimes users paste JSON directly)
    if headers_str.startswith('{'):
        try:
            headers_dict = json.loads(headers_str)
            # Check for essential headers
            if not any(key.lower() in ['cookie', 'authorization', 'x-goog-authuser'] for key in headers_dict.keys()):
                return False, "Headers JSON is missing authentication fields (cookie, authorization, etc.)"
            return True, "Valid JSON headers detected"
        except json.JSONDecodeError:
            return False, "Input looks like JSON but is invalid"
    
    # Check if it contains essential headers (plain text format)
    headers_lower = headers_str.lower()
    has_cookie = 'cookie:' in headers_lower
    has_accept = 'accept:' in headers_lower
    
    if not has_accept:
        return False, "Headers don't contain 'accept:' field. Make sure you copied from the beginning."
    
    if not has_cookie:
        return False, "Headers don't contain 'cookie:' field. Authentication may fail without cookies."
    
    # Check for the specific required cookie
    if '__secure-3papisid' not in headers_lower:
        return False, "Cookie is missing '__Secure-3PAPISID'. Make sure you copied the COMPLETE cookie line (it's very long!)."
    
    return True, "Headers look valid"

def print_separator():
    print("\n" + "=" * 70 + "\n")

print_separator()
print("🎵 YouTube Music Browser Authentication Setup 🎵")
print_separator()

print("This will create a 'headers.json' file for authentication.")
print("The authentication will remain valid for ~2 years.")
print_separator()

print("📋 STEP-BY-STEP INSTRUCTIONS:")
print()
print("  1. Open https://music.youtube.com in your browser")
print("     └─ Make sure you're logged in to your YouTube Music account")
print()
print("  2. Open Developer Tools:")
print("     └─ Press F12 (or Ctrl+Shift+I / Cmd+Option+I)")
print()
print("  3. Go to the 'Network' tab")
print("     └─ You should see network requests appearing")
print()
print("  4. Filter by '/browse' in the search/filter bar")
print()
print("  5. Trigger a request:")
print("     └─ Click 'Library' or scroll down the page")
print("     └─ You should see 'browse?...' requests appear")
print()
print("  6. Click on any 'browse' request in the list")
print()
print("  7. Find 'Request Headers' section:")
print("     └─ Look for the 'Headers' tab (not 'Response' or 'Preview')")
print("     └─ Scroll to find 'Request Headers'")
print()
print("  8. Copy EVERYTHING from 'accept: */*' to the very end")
print("     └─ Select all text, right-click → Copy")
print()
print("  9. Paste below and press:")
print("     └─ Linux/Mac: Ctrl+D")
print("     └─ Windows: Ctrl+Z then Enter")

print_separator()
print("Ready to paste headers? (Ctrl+C to cancel)")
print_separator()

try:
    # Read headers input
    print("Paste headers here:")
    import sys
    lines = []
    for line in sys.stdin:
        lines.append(line)
    headers_input = ''.join(lines)
    
    # Validate before attempting setup
    valid, message = validate_headers(headers_input)
    
    if not valid:
        print_separator()
        print(f"❌ VALIDATION FAILED: {message}")
        print_separator()
        print("Please try again and make sure you:")
        print("  • Are logged into YouTube Music")
        print("  • Copied from 'accept:' all the way to the end")
        print("  • Included the entire Request Headers section")
        print("  • Didn't accidentally copy Response Headers")
        print_separator()
        sys.exit(1)
    
    print(f"\n✓ {message}")
    print("Creating headers.json file...")
    
    # This will create the headers.json file
    auth_string = setup(filepath="headers.json", headers_raw=headers_input)
    
    # Verify file was created
    if os.path.exists("headers.json"):
        file_size = os.path.getsize("headers.json")
        print_separator()
        print("✅ SUCCESS! Authentication saved to 'headers.json'")
        print(f"   File size: {file_size} bytes")
        print_separator()
        print("Next steps:")
        print()
        print("  1. Run the migration script:")
        print("     └─ bash run.sh")
        print("        OR")
        print("     └─ python3 spotify_to_ytmusic.py")
        print()
        print("  2. The script will:")
        print("     └─ Fetch your Spotify playlists")
        print("     └─ Create matching playlists on YouTube Music")
        print("     └─ Transfer all your songs")
        print_separator()
    else:
        print_separator()
        print("⚠️  WARNING: headers.json was not created")
        print("Please try running the script again.")
        print_separator()
        
except KeyboardInterrupt:
    print_separator()
    print("Setup cancelled by user.")
    print_separator()
    
except Exception as e:
    print_separator()
    print(f"❌ ERROR: {e}")
    print_separator()
    print("Troubleshooting tips:")
    print()
    print("  • Make sure you're logged into YouTube Music")
    print("  • Verify you copied the ENTIRE Request Headers section")
    print("  • Check that you copied 'Request Headers', not 'Response Headers'")
    print("  • Look for the 'cookie:' field in what you copied")
    print("  • Try refreshing YouTube Music and getting fresh headers")
    print()
    print("If problems persist, you may need to:")
    print("  1. Clear your browser cache")
    print("  2. Log out and log back into YouTube Music")
    print("  3. Try a different browser (Chrome/Firefox/Edge)")
    print_separator()
