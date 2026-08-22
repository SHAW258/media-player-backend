# 🎵 Media Player Backend & Database

A production-grade, asynchronous **FastAPI** backend with **MySQL Database** and automated **Interactive Swagger UI / OpenAPI** documentation, custom-tailored for the **Figma Media Player App Design**.

---

## 📱 Figma Design Mapping

The backend is architected to power every screen, component, and user interaction in the Figma Media Player design:

| Figma UI Element / Screen | Description | Backend Route(s) |
|---|---|---|
| **Top Header & Greeting** | User profile avatar, notifications, John Doe greeting | `GET /api/v1/auth/me`, `GET /api/v1/users/profile` |
| **Category Filter Pills** | Navigation tabs (`All`, `Music`, `Podcast`) | `GET /api/v1/explore/home?tab={all\|music\|podcast}` |
| **Hero / Featured Banner** | Featured track/podcast banner with play button | `GET /api/v1/explore/home` (`hero` field) |
| **Trending Now** | List of trending tracks (*Ghost - Axe Ross*, *Smoke & Mirrors*, etc.) | `GET /api/v1/explore/trending`, `GET /api/v1/tracks` |
| **Popular Musicians** | Carousel of popular artists with monthly listeners | `GET /api/v1/artists/popular` |
| **New Releases** | Album grid (*The Adam*, *Pure Saturday*, *Ghost Dimension*) | `GET /api/v1/albums/new-releases` |
| **Podcasts Section** | Podcast shows and episode cards with progress bars | `GET /api/v1/podcasts/shows`, `GET /api/v1/podcasts/episodes` |
| **Now Playing Screen** | Full player modal with album art, scrubber, lyrics, controls | `GET /api/v1/tracks/{id}`, `GET /api/v1/tracks/{id}/lyrics` |
| **Audio Streaming** | HTTP 206 Partial Content Range streaming (seeking/scrubbing) | `GET /api/v1/tracks/{id}/stream`, `GET /api/v1/podcasts/episodes/{id}/stream` |
| **Favorites / Like Button** | Heart button toggle on tracks, albums, podcast episodes | `POST /api/v1/favorites/toggle`, `GET /api/v1/favorites/my-favorites` |
| **Playback State & History** | Save progress timestamp (e.g. 2:34 / 3:45) & history | `POST /api/v1/playback/progress`, `GET /api/v1/playback/history` |
| **Play Queue (Up Next)** | Up next queue management (add, play next, reorder) | `GET /api/v1/queue`, `POST /api/v1/queue/add`, `DELETE /api/v1/queue` |
| **Playlists Library** | User custom playlists with track ordering | `GET /api/v1/playlists`, `POST /api/v1/playlists`, `POST /api/v1/playlists/{id}/tracks` |
| **Universal Search** | Real-time search across tracks, artists, albums, podcasts | `GET /api/v1/search?q={query}` |

---

## 🗄️ MySQL Database Architecture

The schema contains 12 normalized relational tables with indexing, foreign key cascades, and unique constraints:

```mermaid
erDiagram
    USERS ||--o{ PLAYLISTS : creates
    USERS ||--o{ FAVORITES : likes
    USERS ||--o{ PLAYBACK_HISTORY : listens
    USERS ||--o{ USER_QUEUE : queues
    
    CATEGORIES ||--o{ ARTISTS : classifies
    CATEGORIES ||--o{ TRACKS : classifies
    CATEGORIES ||--o{ PODCAST_SHOWS : categorizes
    
    ARTISTS ||--o{ ALBUMS : releases
    ARTISTS ||--o{ TRACKS : performs
    
    ALBUMS ||--o{ TRACKS : contains
    
    PODCAST_SHOWS ||--o{ PODCAST_EPISODES : broadcasts
    
    PLAYLISTS ||--o{ PLAYLIST_TRACKS : includes
    TRACKS ||--o{ PLAYLIST_TRACKS : placed_in
    
    TRACKS ||--o{ FAVORITES : favorited
    TRACKS ||--o{ PLAYBACK_HISTORY : recorded
    TRACKS ||--o{ USER_QUEUE : queued
```

### Table Breakdown:
1. `users` — User credentials, roles, avatar, and account status.
2. `categories` — Genre and topic classifications (Pop, Rock, Tech, etc.).
3. `artists` — Musician profiles, bio, avatar, monthly listeners, and verified badges.
4. `albums` — Album collections, cover art, release dates, and new-release tags.
5. `tracks` — Song metadata, audio URL, duration, stream count, and lyrics.
6. `podcast_shows` — Podcast series with host names, ratings, and covers.
7. `podcast_episodes` — Individual podcast episodes with audio files and duration.
8. `playlists` — User-created playlists (public/private).
9. `playlist_tracks` — Ordered junction table linking playlists to tracks.
10. `favorites` — User liked items (polymorphic relation to tracks, albums, episodes).
11. `playback_history` — User playback progress timestamp and listening history.
12. `user_queue` — Active "Up Next" audio playback queue.

The complete standalone SQL DDL script is located in [`schema.sql`](./schema.sql).

---

## 📖 Swagger UI & API Documentation

FastAPI auto-generates interactive API documentation:

* **Interactive Swagger UI**: `http://localhost:8000/docs`
* **ReDoc Interactive UI**: `http://localhost:8000/redoc`
* **Raw OpenAPI 3.1 JSON**: `http://localhost:8000/openapi.json`

### Authentication in Swagger UI:
Click the **Authorize** 🔓 button on `/docs` and enter:
* **Username**: `john_doe`
* **Password**: `password123`

---

## 🚀 Quick Start Guide

### 1. Configure Environment (`.env`)
The database connection string is configured in `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=mediaplayer_db
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/mediaplayer_db
```
> **Note**: If MySQL server is offline during initial startup, the backend automatically activates SQLite development fallback mode (`mediaplayer_fallback.db`) so you can explore APIs and Swagger UI immediately without configuration friction!

### 2. Initialize and Seed Database
Run the initialization script to create tables and load realistic Figma mockup data:
```bash
python init_db.py
```

### 3. Start Backend Server
```bash
python run.py
```
Or with Uvicorn CLI:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run Automated Test Suite
```bash
python test_api.py
```

---

## 🧪 Default Seed Accounts & Mock Data

### Demo Users:
| Username | Email | Password | Role |
|---|---|---|---|
| `john_doe` | `john.doe@example.com` | `password123` | User (Figma Avatar) |
| `admin` | `admin@mediaplayer.io` | `admin123` | Administrator |

### Seeded Artists & Songs:
* **Axe Ross** — *Ghost* (Hero / Trending), *Smoke & Mirrors*
* **Charlie Puth** — *The Adam* (Album & Singles)
* **The Weeknd** — *Ordinary Life*, *Pure Saturday*
* **Dua Lipa** — *Love In The Dark*
* **Alex Vance** — *Deep Tech & Soundscapes Podcast* (Episodes 1 & 2)

---

## 🎧 Audio Streaming & Range Header Support

The audio streaming endpoint (`GET /api/v1/tracks/{id}/stream`) implements HTTP 206 Partial Content:
```http
GET /api/v1/tracks/1/stream HTTP/1.1
Range: bytes=0-1024
```
**Response:**
```http
HTTP/1.1 206 Partial Content
Content-Range: bytes 0-1024/19845044
Content-Length: 1025
Content-Type: audio/mpeg
Accept-Ranges: bytes
```
This enables audio seek bars, smooth buffering, and low-latency playback in mobile and web frontend applications.
