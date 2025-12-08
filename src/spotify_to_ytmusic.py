#!/usr/bin/env python3
import os
import time
import json.decoder
from typing import Dict, Tuple, Optional, List, Set

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic

# Load environment variables from .env file
load_dotenv()


# ----- CONFIG -----
# Spotify scopes: read playlists + liked songs
SPOTIFY_SCOPE = (
    "user-library-read "
    "playlist-read-private "
    "playlist-read-collaborative"
)

# Path to your ytmusicapi headers file (created by setup_ytmusic_browser.py)
YTMUSIC_AUTH_FILE = "headers.json"

# Optional: rate limiting (increased to avoid API throttling)
SEARCH_SLEEP_SECONDS = 0.5  # Increased from 0.1 to avoid rate limiting
ADD_SLEEP_SECONDS = 0.3     # Slight increase for safety

# Duplicate handling mode
# 'merge' = Add only new songs to existing playlists (recommended)
# 'skip' = Skip playlists that already exist entirely
DUPLICATE_MODE = "merge"


# ----- SPOTIFY HELPERS -----

def get_spotify_client() -> spotipy.Spotify:
    """
    Uses env vars:
      SPOTIPY_CLIENT_ID
      SPOTIPY_CLIENT_SECRET
      SPOTIPY_REDIRECT_URI
    and handles browser auth automatically.
    """
    auth_manager = SpotifyOAuth(scope=SPOTIFY_SCOPE)
    return spotipy.Spotify(auth_manager=auth_manager)


def get_all_spotify_playlists(sp: spotipy.Spotify) -> List[dict]:
    playlists = []
    results = sp.current_user_playlists(limit=50)
    while results:
        playlists.extend(results["items"])
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return playlists


def get_playlist_tracks(sp: spotipy.Spotify, playlist_id: str) -> List[dict]:
    tracks = []
    results = sp.playlist_items(playlist_id, additional_types=["track"], limit=100)
    while results:
        for item in results["items"]:
            track = item.get("track")
            if track and track.get("id"):
                tracks.append(track)
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return tracks


def get_liked_tracks(sp: spotipy.Spotify) -> List[dict]:
    tracks = []
    results = sp.current_user_saved_tracks(limit=50)
    while results:
        for item in results["items"]:
            track = item.get("track")
            if track and track.get("id"):
                tracks.append(track)
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return tracks


# ----- YOUTUBE MUSIC HELPERS -----

def get_ytmusic_client() -> YTMusic:
    """
    Returns an authenticated YTMusic client using browser headers.
    """
    if not os.path.exists(YTMUSIC_AUTH_FILE):
        print("\n" + "=" * 70)
        print("❌ YouTube Music Authentication Required")
        print("=" * 70)
        print(f"\nThe authentication file '{YTMUSIC_AUTH_FILE}' was not found.")
        print("\n📋 To set up YouTube Music authentication:\n")
        print("  1. Run the setup script:")
        print("     └─ source venv/bin/activate  # Activate virtual environment")
        print(f"     └─ python3 setup_ytmusic_browser.py")
        print()
        print("  2. Follow the interactive instructions to:")
        print("     └─ Open YouTube Music in your browser")
        print("     └─ Copy request headers from Developer Tools")
        print("     └─ Paste them into the terminal")
        print()
        print("  3. The authentication will remain valid for ~2 years")
        print()
        print("💡 This method is simpler than OAuth and doesn't require")
        print("   Google Cloud Console setup!")
        print("=" * 70 + "\n")
        raise FileNotFoundError(f"{YTMUSIC_AUTH_FILE} not found. Please run setup_ytmusic_browser.py first.")
    
    return YTMusic(YTMUSIC_AUTH_FILE)


def get_all_ytmusic_playlists(yt: YTMusic) -> Dict[str, str]:
    """
    Returns a dict of {playlist_name: playlist_id} for all user's playlists.
    Uses exact name matching (case-sensitive).
    Includes retry logic for rate limiting.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(0.5)  # Small delay before fetching
            playlists = yt.get_library_playlists(limit=None)
            return {pl['title']: pl['playlistId'] for pl in playlists}
        except json.decoder.JSONDecodeError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"  ⚠ Rate limit hit while fetching playlists, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Warning: Could not fetch existing playlists after {max_retries} attempts")
                return {}
        except Exception as e:
            print(f"Warning: Could not fetch existing playlists: {e}")
            return {}
    return {}


def get_ytmusic_playlist_tracks(yt: YTMusic, playlist_id: str) -> Set[str]:
    """
    Returns a set of videoIds for all tracks in a YouTube Music playlist.
    Includes retry logic for rate limiting.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(0.5)  # Small delay before fetching
            playlist = yt.get_playlist(playlist_id, limit=None)
            tracks = playlist.get('tracks', [])
            return {track['videoId'] for track in tracks if track.get('videoId')}
        except json.decoder.JSONDecodeError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"  ⚠ Rate limit hit while fetching playlist tracks, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  Warning: Could not fetch playlist tracks after {max_retries} attempts")
                return set()
        except Exception as e:
            print(f"  Warning: Could not fetch playlist tracks: {e}")
            return set()
    return set()

def spotify_track_key(track: dict) -> Tuple[str, str]:
    title = track["name"].strip().lower()
    artists = ", ".join(a["name"] for a in track.get("artists", [])).strip().lower()
    return title, artists


def spotify_track_search_query(track: dict) -> str:
    name = track["name"]
    artists = ", ".join(a["name"] for a in track.get("artists", []))
    album = track.get("album", {}).get("name", "")
    return f"{name} {artists} {album}".strip()


def find_ytmusic_song(
    yt: YTMusic,
    track: dict,
    cache: Dict[Tuple[str, str], Optional[str]],
    max_results: int = 5,
    max_retries: int = 3
) -> Optional[str]:
    """
    Returns YouTube Music videoId for a Spotify track, or None if not found.
    Uses a simple cache to avoid repeated searches.
    Includes retry logic with exponential backoff to handle rate limiting.
    """
    key = spotify_track_key(track)
    if key in cache:
        return cache[key]

    query = spotify_track_search_query(track)
    video_id = None
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            results = yt.search(query, filter="songs", limit=max_results)
            
            if results:
                # naive but usually fine: pick first result
                candidate = results[0]
                video_id = candidate.get("videoId") or candidate.get("video_id")
            
            # Success - break out of retry loop
            break
            
        except json.decoder.JSONDecodeError as e:
            # Rate limiting detected - retry with exponential backoff
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"  ⚠ Rate limit hit, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                # Final attempt failed
                artists = ", ".join(a["name"] for a in track.get("artists", []))
                print(f"  ✗ API error after {max_retries} attempts: {track['name']} – {artists}")
                video_id = None
                
        except Exception as e:
            # Other unexpected errors
            artists = ", ".join(a["name"] for a in track.get("artists", []))
            print(f"  ✗ Unexpected error searching for {track['name']} – {artists}: {e}")
            video_id = None
            break

    cache[key] = video_id
    time.sleep(SEARCH_SLEEP_SECONDS)
    return video_id


def create_yt_playlist(yt: YTMusic, name: str, description: str) -> str:
    playlist_id = yt.create_playlist(
        title=name,
        description=description,
        privacy_status="PRIVATE",
    )
    return playlist_id


def add_tracks_to_yt_playlist(yt: YTMusic, playlist_id: str, video_ids: List[str]) -> None:
    # ytmusicapi lets you add up to 50 items at a time
    chunk_size = 50
    for i in range(0, len(video_ids), chunk_size):
        chunk = video_ids[i:i + chunk_size]
        yt.add_playlist_items(playlist_id, chunk)
        time.sleep(ADD_SLEEP_SECONDS)


# ----- MIGRATION LOGIC -----

def migrate_single_playlist(sp: spotipy.Spotify, yt: YTMusic, playlist: dict,
                            cache: Dict[Tuple[str, str], Optional[str]],
                            existing_playlists: Dict[str, str]) -> None:
    name = playlist["name"]
    description = (playlist.get("description") or "") + " (imported from Spotify)"
    print(f"\n=== Migrating playlist: {name} ===")

    tracks = get_playlist_tracks(sp, playlist["id"])
    print(f"  Spotify tracks: {len(tracks)}")

    # Check if playlist already exists (exact name match)
    existing_video_ids: Set[str] = set()
    yt_playlist_id: Optional[str] = None
    
    if name in existing_playlists:
        yt_playlist_id = existing_playlists[name]
        print(f"  ℹ️  Playlist already exists: {yt_playlist_id}")
        
        if DUPLICATE_MODE == "skip":
            print(f"  ⏭️  Skipping (duplicate mode: skip)")
            return
        elif DUPLICATE_MODE == "merge":
            print(f"  🔄 Merging new songs into existing playlist")
            existing_video_ids = get_ytmusic_playlist_tracks(yt, yt_playlist_id)
            print(f"  📋 Found {len(existing_video_ids)} existing songs")

    video_ids: List[str] = []
    missing = 0

    for t in tracks:
        vid = find_ytmusic_song(yt, t, cache)
        if not vid:
            missing += 1
            artists = ", ".join(a["name"] for a in t.get("artists", []))
            print(f"  ! Not found on YT Music: {t['name']} – {artists}")
            continue
        
        # Skip if song already exists in playlist (for merge mode)
        if vid in existing_video_ids:
            continue
            
        video_ids.append(vid)

    # Filter summary for merge mode
    if existing_video_ids and DUPLICATE_MODE == "merge":
        skipped = len(tracks) - missing - len(video_ids)
        if skipped > 0:
            print(f"  ℹ️  Skipping {skipped} songs already in playlist")

    if not video_ids:
        if existing_video_ids:
            print(f"  ✓ No new songs to add")
        else:
            print(f"  No matches found, skipping playlist.")
        return

    # Create new playlist or add to existing
    if yt_playlist_id is None:
        yt_playlist_id = create_yt_playlist(yt, name, description)
        print(f"  → Created YT Music playlist {yt_playlist_id}")
    else:
        print(f"  → Adding {len(video_ids)} new songs to existing playlist")
    
    add_tracks_to_yt_playlist(yt, yt_playlist_id, video_ids)
    print(f"  ✓ Added {len(video_ids)} tracks (missing {missing})")



def migrate_liked_songs(
    sp: spotipy.Spotify,
    yt: YTMusic,
    cache: Dict[Tuple[str, str], Optional[str]],
    existing_playlists: Dict[str, str],
    playlist_name: str = "Spotify Liked Songs"
) -> None:
    print("\n=== Migrating Spotify Liked Songs ===")
    tracks = get_liked_tracks(sp)
    print(f"  Spotify liked tracks: {len(tracks)}")

    # Check if playlist already exists
    existing_video_ids: Set[str] = set()
    yt_playlist_id: Optional[str] = None
    
    if playlist_name in existing_playlists:
        yt_playlist_id = existing_playlists[playlist_name]
        print(f"  ℹ️  Playlist already exists: {yt_playlist_id}")
        
        if DUPLICATE_MODE == "skip":
            print(f"  ⏭️  Skipping (duplicate mode: skip)")
            return
        elif DUPLICATE_MODE == "merge":
            print(f"  🔄 Merging new songs into existing playlist")
            existing_video_ids = get_ytmusic_playlist_tracks(yt, yt_playlist_id)
            print(f"  📋 Found {len(existing_video_ids)} existing songs")

    video_ids: List[str] = []
    missing = 0

    for t in tracks:
        vid = find_ytmusic_song(yt, t, cache)
        if not vid:
            missing += 1
            artists = ", ".join(a["name"] for a in t.get("artists", []))
            print(f"  ! Not found on YT Music: {t['name']} – {artists}")
            continue
        
        # Skip if song already exists in playlist
        if vid in existing_video_ids:
            continue
            
        video_ids.append(vid)

    # Filter summary
    if existing_video_ids and DUPLICATE_MODE == "merge":
        skipped = len(tracks) - missing - len(video_ids)
        if skipped > 0:
            print(f"  ℹ️  Skipping {skipped} songs already in playlist")

    if not video_ids:
        if existing_video_ids:
            print(f"  ✓ No new songs to add")
        else:
            print(f"  No liked songs matched, skipping.")
        return

    # Create or update playlist
    description = "Auto-imported from Spotify Liked Songs"
    if yt_playlist_id is None:
        yt_playlist_id = create_yt_playlist(yt, playlist_name, description)
        print(f"  → Created YT Music playlist {yt_playlist_id}")
    else:
        print(f"  → Adding {len(video_ids)} new songs to existing playlist")
    
    add_tracks_to_yt_playlist(yt, yt_playlist_id, video_ids)
    print(f"  ✓ Added {len(video_ids)} liked songs (missing {missing})")


def main():
    print("Authorizing with Spotify...")
    sp = get_spotify_client()

    print("Authorizing with YouTube Music...")
    yt = get_ytmusic_client()
    
    # Fetch existing YouTube Music playlists for duplicate detection
    print("Fetching existing YouTube Music playlists...")
    existing_playlists = get_all_ytmusic_playlists(yt)
    print(f"Found {len(existing_playlists)} existing playlists on YouTube Music")
    print(f"Duplicate mode: {DUPLICATE_MODE}")

    cache: Dict[Tuple[str, str], Optional[str]] = {}

    # 1. Migrate playlists
    playlists = get_all_spotify_playlists(sp)
    print(f"\nFound {len(playlists)} Spotify playlists.")
    for pl in playlists:
        # You can add filters here if you want to skip some playlists
        migrate_single_playlist(sp, yt, pl, cache, existing_playlists)

    # 2. Migrate liked songs
    migrate_liked_songs(sp, yt, cache, existing_playlists)

    print("\nDone!")


if __name__ == "__main__":
    main()
