#!/usr/bin/env python3
import os
import time
from typing import Dict, Tuple, Optional, List

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

# Optional: rate limiting
SEARCH_SLEEP_SECONDS = 0.1
ADD_SLEEP_SECONDS = 0.2


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
        print(f"\n❌ {YTMUSIC_AUTH_FILE} not found!")
        print("\nTo set up YouTube Music authentication, run:")
        print("  python setup_ytmusic_browser.py")
        print("\nThis will guide you through copying your browser headers.")
        print("It's much simpler than OAuth and doesn't require Google Cloud setup!\n")
        raise FileNotFoundError(f"{YTMUSIC_AUTH_FILE} not found. Please run setup_ytmusic_browser.py first.")
    
    return YTMusic(YTMUSIC_AUTH_FILE)


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
    max_results: int = 5
) -> Optional[str]:
    """
    Returns YouTube Music videoId for a Spotify track, or None if not found.
    Uses a simple cache to avoid repeated searches.
    """
    key = spotify_track_key(track)
    if key in cache:
        return cache[key]

    query = spotify_track_search_query(track)
    results = yt.search(query, filter="songs", limit=max_results)

    video_id = None
    if results:
        # naive but usually fine: pick first result
        candidate = results[0]
        video_id = candidate.get("videoId") or candidate.get("video_id")

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
                            cache: Dict[Tuple[str, str], Optional[str]]) -> None:
    name = playlist["name"]
    description = (playlist.get("description") or "") + " (imported from Spotify)"
    print(f"\n=== Migrating playlist: {name} ===")

    tracks = get_playlist_tracks(sp, playlist["id"])
    print(f"  Spotify tracks: {len(tracks)}")

    video_ids: List[str] = []
    missing = 0

    for t in tracks:
        vid = find_ytmusic_song(yt, t, cache)
        if not vid:
            missing += 1
            artists = ", ".join(a["name"] for a in t.get("artists", []))
            print(f"  ! Not found on YT Music: {t['name']} – {artists}")
            continue
        video_ids.append(vid)

    if not video_ids:
        print("  No matches found, skipping playlist.")
        return

    yt_playlist_id = create_yt_playlist(yt, name, description)
    add_tracks_to_yt_playlist(yt, yt_playlist_id, video_ids)

    print(f"  -> Created YT Music playlist {yt_playlist_id}")
    print(f"  -> Added {len(video_ids)} tracks (missing {missing}).")


def migrate_liked_songs(
    sp: spotipy.Spotify,
    yt: YTMusic,
    cache: Dict[Tuple[str, str], Optional[str]],
    playlist_name: str = "Spotify Liked Songs"
) -> None:
    print("\n=== Migrating Spotify Liked Songs ===")
    tracks = get_liked_tracks(sp)
    print(f"  Spotify liked tracks: {len(tracks)}")

    video_ids: List[str] = []
    missing = 0

    for t in tracks:
        vid = find_ytmusic_song(yt, t, cache)
        if not vid:
            missing += 1
            artists = ", ".join(a["name"] for a in t.get("artists", []))
            print(f"  ! Not found on YT Music: {t['name']} – {artists}")
            continue
        video_ids.append(vid)

    if not video_ids:
        print("  No liked songs matched, skipping.")
        return

    description = "Auto-imported from Spotify Liked Songs"
    yt_playlist_id = create_yt_playlist(yt, playlist_name, description)
    add_tracks_to_yt_playlist(yt, yt_playlist_id, video_ids)

    print(f"  -> Created YT Music playlist {yt_playlist_id}")
    print(f"  -> Added {len(video_ids)} liked songs (missing {missing}).")


def main():
    print("Authorizing with Spotify...")
    sp = get_spotify_client()

    print("Authorizing with YouTube Music...")
    yt = get_ytmusic_client()

    cache: Dict[Tuple[str, str], Optional[str]] = {}

    # 1. Migrate playlists
    playlists = get_all_spotify_playlists(sp)
    print(f"\nFound {len(playlists)} Spotify playlists.")
    for pl in playlists:
        # You can add filters here if you want to skip some playlists
        migrate_single_playlist(sp, yt, pl, cache)

    # 2. Migrate liked songs
    migrate_liked_songs(sp, yt, cache)

    print("\nDone!")


if __name__ == "__main__":
    main()
