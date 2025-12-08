#!/usr/bin/env python3
"""
Diagnostic script to test YTMusic API and identify the exact issue.
"""
import time
from ytmusicapi import YTMusic

def test_basic_search():
    """Test 1: Basic search functionality"""
    print("Test 1: Basic YTMusic Search")
    print("-" * 50)
    try:
        yt = YTMusic('headers.json')
        result = yt.search('test song', filter='songs', limit=5)
        print(f"✓ SUCCESS: Found {len(result)} songs")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rapid_searches():
    """Test 2: Rapid consecutive searches (mimics playlist migration)"""
    print("\nTest 2: Rapid Consecutive Searches")
    print("-" * 50)
    try:
        yt = YTMusic('headers.json')
        queries = [
            "indie rock",
            "pop music",
            "jazz song",
            "classic rock",
            "electronic music"
        ]
        
        for i, query in enumerate(queries, 1):
            result = yt.search(query, filter='songs', limit=5)
            print(f"  Search {i}/5: {query} → {len(result)} results")
            time.sleep(0.1)  # Same as in the main script
        
        print("✓ SUCCESS: All rapid searches completed")
        return True
    except Exception as e:
        print(f"✗ FAILED on search: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_delay_searches():
    """Test 3: No delay between searches (stress test)"""
    print("\nTest 3: No Delay Between Searches (Stress Test)")
    print("-" * 50)
    try:
        yt = YTMusic('headers.json')
        
        for i in range(10):
            result = yt.search(f'test {i}', filter='songs', limit=3)
            print(f"  Search {i+1}/10: {len(result)} results", end='\r')
        
        print("\n✓ SUCCESS: All no-delay searches completed")
        return True
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_create_playlist():
    """Test 4: Create a test playlist"""
    print("\nTest 4: Create Playlist")
    print("-" * 50)
    try:
        yt = YTMusic('headers.json')
        
        # Search for a song first
        result = yt.search('test song', filter='songs', limit=1)
        if not result:
            print("✗ FAILED: No songs found to add")
            return False
        
        video_id = result[0].get('videoId')
        if not video_id:
            print("✗ FAILED: No videoId in search result")
            return False
        
        # Create playlist
        playlist_id = yt.create_playlist(
            title="Test Playlist - Delete Me",
            description="Created by diagnostic script",
            privacy_status="PRIVATE"
        )
        print(f"✓ Created playlist: {playlist_id}")
        
        # Add song to playlist
        yt.add_playlist_items(playlist_id, [video_id])
        print(f"✓ Added song to playlist")
        
        print("✓ SUCCESS: Playlist creation and song addition works")
        print(f"  Note: Please delete playlist '{playlist_id}' manually from YouTube Music")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("YouTube Music API Diagnostic Tests")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(("Basic Search", test_basic_search()))
    results.append(("Rapid Searches", test_rapid_searches()))
    results.append(("Stress Test", test_no_delay_searches()))
    results.append(("Create Playlist", test_create_playlist()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✓ All tests passed! The issue might be elsewhere.")
    else:
        print("\n✗ Some tests failed. Check the errors above.")
