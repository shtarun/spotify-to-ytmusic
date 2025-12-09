# 🎵 Spotify to YouTube Music Migration Tool

A robust Python script to migrate your Spotify playlists and liked songs to YouTube Music with smart duplicate detection and rate limiting protection.

## ✨ Features

- 🎵 **Migrate all playlists** - Transfer your entire Spotify library to YouTube Music
- ❤️ **Liked songs support** - Convert your Spotify liked songs into a YouTube Music playlist
- 🔍 **Intelligent matching** - Smart song search with retry logic
- 🚫 **Duplicate prevention** - Automatically detects and skips existing playlists and songs
- 🔄 **Smart merge mode** - Add only new songs to existing playlists
- 💾 **State persistence** - Resumes interrupted migrations and avoids re-searching songs
- 📝 **Detailed logging** - Shows song names and creates readable reports of missing songs
- ⚡ **Rate limit protection** - Exponential backoff and retry logic to prevent API errors
- 📊 **Progress tracking** - Clear feedback with missing song reporting
- 🛡️ **Production-ready** - Robust error handling and comprehensive testing
- 📛 **Smart Naming** - Auto-fallback for playlist names that YouTube rejects

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- A Spotify account with playlists/liked songs
- A YouTube Music account
- Spotify Developer credentials ([Get them here](https://developer.spotify.com/dashboard))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shtarun/spotify-to-ytmusic.git
   cd spotify-to-ytmusic
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

#### 1. Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Note your **Client ID** and **Client Secret**
4. Add `http://localhost:8888/callback` to Redirect URIs
5. Create `.env` file in the project root:
   ```bash
   SPOTIPY_CLIENT_ID=your_client_id_here
   SPOTIPY_CLIENT_SECRET=your_client_secret_here
   SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
   ```

#### 2. YouTube Music Authentication

Run the setup script:

```bash
python scripts/setup_ytmusic_browser.py
```

Follow the interactive instructions:
1. Open [YouTube Music](https://music.youtube.com) and log in
2. Open Developer Tools (F12)
3. Go to **Network** tab
4. Filter by `/browse`
5. Click **Library** to trigger a request
6. Copy **Request Headers** from any `browse` request
7. Paste into terminal and press Ctrl+D (Linux/Mac) or Ctrl+Z + Enter (Windows)

This creates `headers.json` which remains valid for ~2 years.

> **Note**: This method is simpler than OAuth and doesn't require Google Cloud Console setup!

## 📖 Usage

### Basic Migration

```bash
# Activate virtual environment
source venv/bin/activate

# Run migration
python src/spotify_to_ytmusic.py

# Or use the helper script
bash run.sh
```

### What It Does

1. ✅ Fetches all your Spotify playlists and liked songs
2. 🔍 Searches for matching songs on YouTube Music
3. 📋 Checks for existing playlists (duplicate detection)
4. 🎵 Creates new playlists or merges into existing ones
5. ✅ Reports missing songs and statistics

### Duplicate Handling

The script has two modes for handling existing playlists:

**Merge Mode (Default)**
```python
DUPLICATE_MODE = "merge"
```
- Detects existing playlists by exact name match
- Fetches existing songs in the playlist
- Only adds new songs that aren't already there
- Perfect for incremental updates

**Skip Mode**
```python
DUPLICATE_MODE = "skip"
```
- Skips playlists that already exist entirely
- Faster if you just want to add new playlists

Change the mode in `src/spotify_to_ytmusic.py` (line 34).

### State Persistence

The script now saves its progress to `.migration_state.json` (git-ignored).
- **Resumable**: If you stop the script, it picks up where it left off.
- **Efficient**: Successful searches are cached forever, saving API calls on future runs.
- **Reporting**: Failed songs are saved to `failed_songs.txt` for easy review.

### Example Output

```
=== Migrating playlist: Indie Dreams ===
  Spotify tracks: 79
  
  [1/79] 🔍 Searching: Left Hand Free - alt-J
         ✓ Found on YouTube Music
         
  [2/79] 🔍 Searching: back to friends - sombr
         ✓ Found (cached from previous run)
         
  [3/79] 🔍 Searching: unknown song - artist
         ! Not found on YT Music: unknown song - artist

  ℹ️  Playlist already exists: PLk1U1Db6VAVBgDyVghgnKkalefPUgzlRZ
  🔄 Merging new songs into existing playlist
  📋 Found 45 existing songs
  ℹ️  Skipping 45 songs already in playlist
  → Adding 34 new songs to existing playlist
  ✓ Added 34 tracks (missing 1)
```

## ⚙️ Configuration

Edit `src/spotify_to_ytmusic.py` to customize:

```python
# Rate limiting (adjust if experiencing errors)
SEARCH_SLEEP_SECONDS = 0.5  # Delay between song searches
ADD_SLEEP_SECONDS = 0.3     # Delay when adding songs

# Duplicate handling
DUPLICATE_MODE = "merge"  # Options: "merge" or "skip"

# Authentication
YTMUSIC_AUTH_FILE = "headers.json"  # YT Music auth file path
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Test YouTube Music API functionality
python tests/test_ytmusic.py

# Test duplicate detection
python tests/test_duplicate_detection.py

# Quick migration test (first 5 songs)
python tests/test_migration.py
```

## 📁 Project Structure

```
spotify-to-ytmusic/
├── src/
│   └── spotify_to_ytmusic.py    # Main migration script
├── scripts/
│   ├── setup_ytmusic_browser.py # YT Music auth setup
│   ├── setup_ytmusic.py         # Legacy OAuth setup
│   └── run.sh                   # Helper run script
├── tests/
│   ├── test_ytmusic.py          # API tests
│   ├── test_migration.py        # Migration tests
│   └── test_duplicate_detection.py  # Duplicate detection tests
├── .env                         # Spotify credentials (not in repo)
├── headers.json                 # YT Music auth (not in repo)
├── requirements.txt             # Python dependencies
├── run.sh                       # Main entry point
└── README.md                    # This file
```

## 🔧 Troubleshooting

### YouTube Music Authentication Errors

**Symptom**: `JSONDecodeError: Expecting value`

**Solutions**:
1. Re-run `python scripts/setup_ytmusic_browser.py`
2. Make sure you copied the ENTIRE Request Headers section
3. Ensure you're logged into YouTube Music
4. Wait 30 seconds between auth attempts (rate limiting)

### Spotify Authentication Fails

1. Verify `.env` credentials are correct
2. Check redirect URI matches in both `.env` and Spotify Dashboard
3. Delete `.cache` file and try again:
   ```bash
   rm .cache
   ```

### Songs Not Matching

The script uses fuzzy search matching. Some songs may not match due to:
- Different titles/artist names between platforms
- Regional availability
- Songs not available on YouTube Music

These will be reported as "Not found" in the console.

### Rate Limiting

If you see retry warnings:
```
⚠ Rate limit hit, retrying in 2s...
```

This is normal! The script will automatically retry up to 3 times with exponential backoff.

## 📊 Performance

| Scenario | Songs | Time |
|----------|-------|------|
| First migration | 1000 | ~10 minutes |
| Re-run (merge, 100 new) | 100 | ~2 minutes |
| Re-run (skip mode) | 0 | ~30 seconds |

## 🛠️ Technical Details

### Rate Limiting Strategy

- **Base delay**: 0.5s between searches (5x safer than minimum)
- **Retry logic**: Up to 3 attempts per API call
- **Exponential backoff**: 1s → 2s → 4s wait times
- **Protection layers**: Search, playlist fetch, creation, and addition all protected with retry logic

### Robustness Features

- **Smart Fallback Naming**: If YouTube rejects a playlist name (e.g. contains invalid characters or emojis), the script automatically sanitizes it. If that fails, it falls back to a safe default (`Imported Playlist <date>`).
- **Comprehensive Retry Logic**: Handles both 429 (Too Many Requests) and transient 5xx errors across all API operations.

### Duplicate Detection

- **Exact name matching**: Case-sensitive playlist name comparison
- **Track comparison**: Uses YouTube Music `videoId` for precise matching
- **Idempotent**: Safe to run multiple times without creating duplicates

### Error Handling

- Specific handling for `JSONDecodeError` (rate limiting)
- Generic exception handling for unexpected errors
- Graceful degradation (skips problematic songs but continues)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 Notes

- **Privacy**: All created playlists are set to PRIVATE by default
- **Caching**: Song searches are cached during execution for better performance
- **Reliability**: Includes comprehensive error handling and retry logic
- **Idempotency**: Safe to run multiple times

## 📄 License

This project is provided as-is for personal use.

## ⚠️ Disclaimer

This tool is not affiliated with Spotify or YouTube Music. Use responsibly and in accordance with both platforms' Terms of Service.

## 🙏 Acknowledgments

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - YouTube Music API
- [spotipy](https://github.com/plamere/spotipy) - Spotify API wrapper
