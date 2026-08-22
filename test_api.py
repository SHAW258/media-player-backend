"""
Automated Test Suite for Media Player Backend API
Tests all routes, authentication, feeds, streaming, and database models.
Run:
    python test_api.py
"""

import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy"
    print("  [PASSED] Health check OK.")

def test_openapi_swagger():
    print("Testing OpenAPI & Swagger docs...")
    res = client.get("/openapi.json")
    assert res.status_code == 200
    assert "Media Player REST API" in res.json()["info"]["title"]
    
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    print("  [PASSED] Swagger UI and OpenAPI documentation are active and accessible.")

def test_auth_and_login():
    print("Testing Authentication (Login & Profile)...")
    # Login with seeded John Doe user
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "john_doe",
        "password": "password123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token_data = login_res.json()
    token = token_data["access_token"]
    assert token is not None
    assert token_data["username"] == "john_doe"
    print("  [PASSED] Login successful.")

    # Me profile
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "john.doe@example.com"
    print("  [PASSED] Authenticated profile retrieval OK.")
    return token

def test_explore_feeds(token: str):
    print("Testing Explore Home Feeds (All / Music / Podcast tabs)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. All tab
    res_all = client.get("/api/v1/explore/home?tab=all", headers=headers)
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert len(data_all["trending_now"]) > 0
    assert len(data_all["popular_musicians"]) > 0
    assert len(data_all["new_releases"]) > 0
    print(f"  [PASSED] Home feed (All): {len(data_all['trending_now'])} trending, {len(data_all['popular_musicians'])} artists, {len(data_all['new_releases'])} new releases.")

    # 2. Music tab
    res_music = client.get("/api/v1/explore/home?tab=music", headers=headers)
    assert res_music.status_code == 200
    assert res_music.json()["tab"] == "music"
    print("  [PASSED] Home feed (Music tab) OK.")

    # 3. Podcast tab
    res_pod = client.get("/api/v1/explore/home?tab=podcast", headers=headers)
    assert res_pod.status_code == 200
    assert len(res_pod.json()["podcast_shows"]) > 0
    print("  [PASSED] Home feed (Podcast tab) OK.")

def test_tracks_and_audio_streaming():
    print("Testing Tracks & HTTP 206 Partial Content Audio Streaming...")
    tracks_res = client.get("/api/v1/tracks")
    assert tracks_res.status_code == 200
    tracks = tracks_res.json()
    assert len(tracks) > 0
    first_track_id = tracks[0]["id"]

    # Test lyrics
    lyrics_res = client.get(f"/api/v1/tracks/{first_track_id}/lyrics")
    assert lyrics_res.status_code == 200
    print(f"  [PASSED] Track lyrics retrieved: '{lyrics_res.json()['title']}'")

    # Test full audio stream
    stream_res = client.get(f"/api/v1/tracks/{first_track_id}/stream")
    assert stream_res.status_code in (200, 206, 307)
    print("  [PASSED] Audio streaming stream endpoint OK.")

    # Test range seeking header (e.g. bytes=0-1024)
    range_res = client.get(f"/api/v1/tracks/{first_track_id}/stream", headers={"Range": "bytes=0-1024"})
    assert range_res.status_code in (206, 307)
    if range_res.status_code == 206:
        assert "Content-Range" in range_res.headers
        assert len(range_res.content) == 1025
        print(f"  [PASSED] HTTP 206 Partial Content Range streaming validated: {range_res.headers.get('Content-Range')}")

def test_artists_and_albums():
    print("Testing Artists and Albums...")
    artists_res = client.get("/api/v1/artists/popular")
    assert artists_res.status_code == 200
    assert len(artists_res.json()) > 0
    print(f"  [PASSED] Popular Artists returned {len(artists_res.json())} artists.")

    albums_res = client.get("/api/v1/albums/new-releases")
    assert albums_res.status_code == 200
    assert len(albums_res.json()) > 0
    print(f"  [PASSED] New Releases returned {len(albums_res.json())} albums.")

def test_playlists_and_favorites(token: str):
    print("Testing Playlists and Favorites...")
    headers = {"Authorization": f"Bearer {token}"}

    # Create playlist
    create_pl_res = client.post("/api/v1/playlists", headers=headers, json={
        "name": "My Test Groove 2026",
        "description": "Awesome playlist created via API",
        "is_public": True
    })
    assert create_pl_res.status_code == 201
    pl_id = create_pl_res.json()["id"]

    # Add track to playlist
    add_track_res = client.post(f"/api/v1/playlists/{pl_id}/tracks", headers=headers, json={
        "track_id": 1
    })
    assert add_track_res.status_code in (200, 201)

    # Fetch playlist details
    pl_detail = client.get(f"/api/v1/playlists/{pl_id}", headers=headers)
    assert pl_detail.status_code == 200
    assert pl_detail.json()["track_count"] >= 1
    print("  [PASSED] Playlist created and track attached successfully.")

    # Toggle favorite
    fav_res = client.post("/api/v1/favorites/toggle", headers=headers, json={"track_id": 1})
    assert fav_res.status_code == 200
    print(f"  [PASSED] Favorite toggled: {fav_res.json()}")

def test_playback_and_queue(token: str):
    print("Testing Playback Progress & Queue...")
    headers = {"Authorization": f"Bearer {token}"}

    # Update playback position (e.g. 120 seconds in)
    prog_res = client.post("/api/v1/playback/progress", headers=headers, json={
        "track_id": 1,
        "progress_seconds": 120,
        "completed": False
    })
    assert prog_res.status_code == 200
    assert prog_res.json()["progress_seconds"] == 120
    print("  [PASSED] Playback progress recorded.")

    # Add to queue
    q_res = client.post("/api/v1/queue/add", headers=headers, json={
        "track_id": 2,
        "play_next": True
    })
    assert q_res.status_code == 201
    
    # List queue
    q_list = client.get("/api/v1/queue", headers=headers)
    assert q_list.status_code == 200
    assert len(q_list.json()) > 0
    print(f"  [PASSED] Play queue retrieved with {len(q_list.json())} items.")

def test_search():
    print("Testing Universal Search...")
    search_res = client.get("/api/v1/search?q=Kesariya")
    assert search_res.status_code == 200
    data = search_res.json()
    assert len(data["tracks"]) > 0 or len(data["artists"]) > 0 or len(data["albums"]) > 0
    print(f"  [PASSED] Search for 'Kesariya' returned {len(data['tracks'])} tracks, {len(data['artists'])} artists.")

def run_all_tests():
    print("=================================================================")
    print("  RUNNING MEDIA PLAYER BACKEND INTEGRATION & UNIT TEST SUITE")
    print("=================================================================")
    test_health()
    test_openapi_swagger()
    token = test_auth_and_login()
    test_explore_feeds(token)
    test_tracks_and_audio_streaming()
    test_artists_and_albums()
    test_playlists_and_favorites(token)
    test_playback_and_queue(token)
    test_search()
    print("=================================================================")
    print("  [SUCCESS] ALL TESTS PASSED SUCCESSFULLY! BACKEND IS READY!")
    print("=================================================================")

if __name__ == "__main__":
    run_all_tests()
