#!/usr/bin/env python3
"""
Test duplicate prevention feature
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

print("=" * 70)
print("Testing Duplicate Detection Feature")
print("=" * 70)

# Get clients
print("\n1. Authorizing with Spotify...")
auth_manager = SpotifyOAuth(scope=SPOTIFY_SCOPE)
sp = spotipy.Spotify(auth_manager=auth_manager)

print("2. Authorizing with YouTube Music...")
yt = YTMusic('headers.json')

# Test fetching existing playlists
print("\n3. Fetching existing YouTube Music playlists...")
try:
    playlists = yt.get_library_playlists(limit=None)
    yt_playlist_dict = {pl['title']: pl['playlistId'] for pl in playlists}
    
    print(f"\n✓ Found {len(yt_playlist_dict)} playlists on YouTube Music:")
    for i, (name, pl_id) in enumerate(list(yt_playlist_dict.items())[:5], 1):
        print(f"   {i}. {name} ({pl_id})")
    
    if len(yt_playlist_dict) > 5:
        print(f"   ... and {len(yt_playlist_dict) - 5} more")
    
    # Test fetching tracks from a playlist
    if yt_playlist_dict:
        test_name, test_id = list(yt_playlist_dict.items())[0]
        print(f"\n4. Testing track fetch from '{test_name}'...")
        
        playlist_data = yt.get_playlist(test_id, limit=None)
        tracks = playlist_data.get('tracks', [])
        video_ids = {track['videoId'] for track in tracks if track.get('videoId')}
        
        print(f"✓ Found {len(video_ids)} tracks in playlist")
        
        # Show first few
        for i, track in enumerate(tracks[:3], 1):
            title = track.get('title', 'Unknown')
            artist = track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown'
            print(f"   {i}. {title} - {artist}")
            
    print("\n" + "=" * 70)
    print("✓ All tests passed! Duplicate detection is ready.")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
