# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-12-08

### Added

#### Core Features
- **Duplicate Prevention**: Smart detection of existing playlists with exact name matching (case-sensitive)
- **Merge Mode**: Automatically add only new songs to existing playlists, skip songs already present
- **Skip Mode**: Configuration option to skip playlists that already exist entirely
- **Retry Logic**: Exponential backoff for API calls (1s → 2s → 4s) with up to 3 attempts
- **Rate Limit Protection**: Comprehensive error handling for API throttling with specific `JSONDecodeError` handling

#### Project Structure
- **Production Organization**: Organized codebase with `src/`, `tests/`, and `scripts/` directories
- **Test Suite**: Three comprehensive test scripts (`test_ytmusic.py`, `test_duplicate_detection.py`, `test_migration.py`)
- **.env.example**: Template file for environment configuration
- **CHANGELOG.md**: Version history following Keep a Changelog format

#### Documentation
- **Enhanced README**: Comprehensive guide with features, setup, troubleshooting, and examples
- **tests/README.md**: Documentation for all test scripts with usage instructions
- **scripts/README.md**: Documentation for setup and utility scripts
- **Progress Tracking**: Clear user feedback with emoji indicators (ℹ️, 🔄, ✓, ⚠)

### Changed

#### Performance & Reliability
- **Search delay**: Increased from 0.1s to 0.5s (5x safer against rate limiting)
- **Playlist add delay**: Increased from 0.2s to 0.3s for additional safety
- **Error handling**: Specific handling for `JSONDecodeError` vs generic exceptions
- **User feedback**: Enhanced console output with emojis and detailed status messages

#### Project Structure
- **File organization**: Moved main script to `src/spotify_to_ytmusic.py`
- **Setup scripts**: Moved to `scripts/` directory
- **Test files**: Moved to `tests/` directory
- **Run script**: Updated paths to reference new structure

### Fixed

#### Critical Fixes
- **JSONDecodeError**: Fixed rate limiting issue causing "Expecting value: line 1 column 1 (char 0)" errors
- **API Reliability**: Added retry logic to handle transient YouTube Music API failures
- **Helper functions**: Added retry logic to `get_all_ytmusic_playlists()` and `get_ytmusic_playlist_tracks()`

#### Feature Fixes
- **Duplicate playlists**: Prevented creation of duplicate playlists through exact name matching
- **Duplicate songs**: Prevented adding songs that already exist in playlists by comparing `videoId`

### Migration Guide (v1.x → v2.0)

> **Breaking Changes**: File paths have changed due to reorganization.

#### Required Changes

1. **Update execution command**:
   ```bash
   # Before (v1.x)
   python spotify_to_ytmusic.py
   
   # After (v2.0)
   python src/spotify_to_ytmusic.py
   # Or simply: bash run.sh
   ```

2. **Update setup command**:
   ```bash
   # Before (v1.x)
   python setup_ytmusic_browser.py
   
   # After (v2.0)
   python scripts/setup_ytmusic_browser.py
   ```

#### Optional Configuration

3. **Configure duplicate handling** (new feature):
   ```python
   # In src/spotify_to_ytmusic.py, line 34
   DUPLICATE_MODE = "merge"  # or "skip"
   ```

4. **Run tests** to verify:
   ```bash
   python tests/test_ytmusic.py
   python tests/test_duplicate_detection.py
   python tests/test_migration.py
   ```

#### Import Changes (for contributors)

If you modified the script:
```python
# Add Set to imports
from typing import Dict, Tuple, Optional, List, Set
```

---

## [1.0.0] - 2024-12-01

### Added

#### Core Features
- Basic Spotify to YouTube Music migration
- Playlist migration with song matching
- Liked songs migration to dedicated playlist
- Browser-based YouTube Music authentication
- Spotify OAuth authentication
- Basic rate limiting (0.1s delay)
- Song search and matching algorithm
- Progress reporting and missing song tracking

#### Initial Setup
- Requirements file with dependencies
- README with setup instructions
- `.gitignore` for sensitive files
- Virtual environment setup guide

[unreleased]: https://github.com/shtarun/spotify-to-ytmusic/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/shtarun/spotify-to-ytmusic/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/shtarun/spotify-to-ytmusic/releases/tag/v1.0.0
