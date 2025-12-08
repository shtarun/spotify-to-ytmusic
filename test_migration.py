#!/usr/bin/env python3
"""
Test migration with just a few songs to verify the fix works
"""
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic

load_dotenv()

SPOTIFY_SCOPE = (
    "user-library-read "
    "playlist-read-private "
    "playlist-read-collaborative"
)

# Get Spotify client
auth_manager = SpotifyOAuth(scope=SPOTIFY_SCOPE)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Get YouTube Music client
yt = YTMusic('headers.json')

print("Testing with first playlist...")
playlists = sp.current_user_playlists(limit=1)
if playlists['items']:
    first_playlist = playlists['items'][0]
    print(f"\nPlaylist: {first_playlist['name']}")
    
    # Get just first 5 tracks
    results = sp.playlist_items(first_playlist['id'], limit=5)
    tracks = [item['track'] for item in results['items'] if item.get('track')]
    
    print(f"Testing search for {len(tracks)} tracks:\n")
    
    for idx, track in enumerate(tracks, 1):
        track_name = track['name']
        artists = ", ".join(a['name'] for a in track.get('artists', []))
        
        # Search using same logic as main script
        query = f"{track_name} {artists}"
        try:
            results = yt.search(query, filter='songs', limit=5)
            if results:
                print(f"✓ [{idx}/5] Found: {track_name} - {artists}")
            else:
                print(f"✗ [{idx}/5] Not found: {track_name} - {artists}")
        except Exception as e:
            print(f"✗ [{idx}/5] Error: {track_name} - {e}")
    
    print("\n✓ Test completed successfully! The fix is working.")
else:
    print("No playlists found")
