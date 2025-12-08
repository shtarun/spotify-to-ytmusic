# Tests

This directory contains test scripts to verify the migration tool functionality.

## Test Scripts

### `test_ytmusic.py`

Tests YouTube Music API functionality including:
- Basic search
- Rapid consecutive searches (rate limiting test)
- Stress test with no delays
- Playlist creation

**Usage**:
```bash
python tests/test_ytmusic.py
```

**Expected Output**:
```
✓ PASS: Basic Search
✓ PASS: Rapid Searches
✓ PASS: Stress Test
✓ PASS: Create Playlist
```

### `test_duplicate_detection.py`

Tests the duplicate detection feature:
- Fetching existing YouTube Music playlists
- Reading playlist tracks
- Verifying duplicate detection logic

**Usage**:
```bash
python tests/test_duplicate_detection.py
```

**Expected Output**:
```
✓ Found X playlists on YouTube Music
✓ Found Y tracks in playlist
✓ All tests passed!
```

### `test_migration.py`

Quick migration test with a small sample:
- Tests with first 5 tracks from first playlist
- Verifies search functionality
- Quick smoke test before full migration

**Usage**:
```bash
python tests/test_migration.py
```

**Expected Output**:
```
✓ [1/5] Found: Song Name - Artist
✓ [2/5] Found: Song Name - Artist
...
✓ Test completed successfully!
```

## Running All Tests

```bash
# Make sure venv is activated
source venv/bin/activate

# Run all tests
python tests/test_ytmusic.py
python tests/test_duplicate_detection.py  
python tests/test_migration.py
```

## Test Requirements

All tests require:
- Active virtual environment
- Valid `headers.json` for YouTube Music
- Valid `.env` for Spotify (test_migration.py only)

## Notes

- Tests create temporary playlists on YouTube Music (with "Test" in the name)
- Remember to delete test playlists manually from YouTube Music
- Tests respect the same rate limiting as the main script
