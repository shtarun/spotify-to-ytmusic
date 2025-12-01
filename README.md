# Spotify to YouTube Music Migration Tool

A Python script to migrate your Spotify playlists and liked songs to YouTube Music.

## Features

- 🎵 Migrate all your Spotify playlists to YouTube Music
- ❤️ Transfer your Spotify liked songs to a YouTube Music playlist
- 🔍 Intelligent song matching using search
- 📊 Progress tracking and missing song reporting
- ⚡ Rate limiting to avoid API throttling

## Prerequisites

- Python 3.7 or higher
- A Spotify account with playlists/liked songs
- A YouTube Music account
- Spotify Developer credentials (Client ID and Secret)

## Setup

### 1. Clone or Download

Download this project to your local machine.

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Note your **Client ID** and **Client Secret**
4. Add `http://localhost:8888/callback` to the Redirect URIs in your app settings
5. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
6. Edit `.env` and add your credentials:
   ```
   SPOTIPY_CLIENT_ID=your_actual_client_id
   SPOTIPY_CLIENT_SECRET=your_actual_client_secret
   SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
   ```

### 5. Configure YouTube Music Authentication

Run the browser-based authentication setup:

```bash
python setup_ytmusic_browser.py
```

This will guide you through the process:
1. Open [YouTube Music](https://music.youtube.com) in your browser and log in
2. Open Developer Tools (F12 or Ctrl+Shift+I)
3. Go to the **Network** tab
4. Filter by `/browse` in the search bar
5. Scroll down or click **Library** to trigger a request
6. Click on a `browse` request
7. In the **Headers** tab, find **Request Headers**
8. Copy EVERYTHING from `accept: */*` to the end
9. Paste into the terminal and press Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows)

This creates a `headers.json` file that remains valid for ~2 years.

> **Note**: This method is much simpler than OAuth and doesn't require Google Cloud Console setup!

## Usage

Make sure your virtual environment is activated and your `.env` file is configured:

```bash
source venv/bin/activate  # Activate virtual environment
python spotify_to_ytmusic.py
```

Or use the helper script:

```bash
bash run.sh
```

The script will:
1. Authenticate with Spotify (browser window will open on first run)
2. Fetch all your Spotify playlists and liked songs
3. Search for matching songs on YouTube Music
4. Create new playlists on YouTube Music
5. Add matched songs to the playlists

## Configuration

You can adjust the following settings in `spotify_to_ytmusic.py`:

- `SEARCH_SLEEP_SECONDS`: Delay between song searches (default: 0.1s)
- `ADD_SLEEP_SECONDS`: Delay between adding songs to playlists (default: 0.2s)
- `YTMUSIC_AUTH_FILE`: Path to YouTube Music auth file (default: `headers.json`)

## Notes

- **Private Playlists**: All created YouTube Music playlists are set to PRIVATE by default
- **Missing Songs**: Songs not found on YouTube Music will be reported in the console
- **Rate Limiting**: The script includes delays to avoid hitting API rate limits
- **Caching**: Song searches are cached during execution to improve performance

## Troubleshooting

### "headers.json not found" or YouTube Music authentication fails
- Run `python setup_ytmusic_browser.py` to set up authentication
- Make sure you're logged into YouTube Music in your browser
- Copy the ENTIRE request headers section (from `accept:` to the end)
- If headers expire (~2 years), just run the setup script again

### Spotify authentication fails
- Verify your credentials in `.env`
- Make sure the redirect URI matches exactly in both `.env` and Spotify Developer Dashboard
- Delete `.cache` file and try again

### Songs not matching correctly
The script uses a simple search-based matching. Some songs may not match perfectly due to:
- Different song titles or artist names
- Regional availability differences
- Songs not available on YouTube Music

## License

This project is provided as-is for personal use.

## Disclaimer

This tool is not affiliated with Spotify or YouTube Music. Use responsibly and in accordance with both platforms' Terms of Service.
