# Scripts

This directory contains setup and utility scripts for the migration tool.

## Setup Scripts

### `setup_ytmusic_browser.py`

Interactive script to set up YouTube Music authentication using browser headers.

**Usage**:
```bash
python scripts/setup_ytmusic_browser.py
```

**What it does**:
1. Guides you through copying request headers from your browser
2. Validates the headers
3. Creates `headers.json` for authentication
4. Authentication remains valid for ~2 years

**Steps**:
1. Open YouTube Music and log in
2. Open Developer Tools (F12)
3. Go to Network tab
4. Filter by `/browse`
5. Click Library to trigger a request
6. Copy Request Headers
7. Paste into terminal

### `setup_ytmusic.py`

Legacy OAuth-based setup script (not recommended).

Use `setup_ytmusic_browser.py` instead for a simpler setup process.

### `run.sh`

Helper script to activate virtual environment and run the migration.

**Usage**:
```bash
bash scripts/run.sh
```

Equivalent to:
```bash
source venv/bin/activate
python src/spotify_to_ytmusic.py
```

## Notes

- All scripts should be run from the project root directory
- Make sure to activate the virtual environment before running scripts
- `setup_ytmusic_browser.py` is the recommended authentication method
