# 🎵 Modern Media Player — Full Project Architecture & Android Integration Guide

> **Notice for Future AI Assistants / Developers**:  
> This file contains the complete system architecture, production credentials, live endpoints, and step-by-step Android / Kotlin integration instructions for this project. Read this file first when continuing work in a new terminal session or building the Android frontend.

---

## 🌟 1. Project Summary & Live Production Links

| Resource | Value / URL |
|---|---|
| **Live Swagger Documentation** | [https://media-player-backend-rud4.onrender.com/docs](https://media-player-backend-rud4.onrender.com/docs) |
| **Live Production Base URL** | `https://media-player-backend-rud4.onrender.com` |
| **GitHub Repository** | [https://github.com/SHAW258/media-player-backend](https://github.com/SHAW258/media-player-backend) |
| **Cloud Hosting Provider** | [Render.com](https://render.com) (Web Service: `srv-da51htu417fc73dtn4e0`) |
| **Cloud MySQL Database** | [TiDB Cloud Serverless MySQL](https://tidbcloud.com) (Region: AWS Singapore) |
| **Database Name** | `mediaplayer_db` |
| **Total Song Catalog** | **110 Unique Playable Tracks** across 15 Categories & 20 Artists |

---

## 🔐 2. Production Credentials & Demo Accounts

### 👤 Demo User Accounts (Pre-seeded & Active):
* **Default User (Matches Figma UI)**:
  * **Username**: `john_doe` *(or `john.doe@example.com`)*
  * **Password**: `password123`
  * **Role**: `user` (Pre-configured with playlists, favorites, and history)
* **Administrator**:
  * **Username**: `admin` *(or `admin@mediaplayer.io`)*
  * **Password**: `admin123`
  * **Role**: `admin`

### 🗄️ TiDB Cloud Serverless MySQL Connection:
* **Host**: `gateway01.ap-southeast-1.prod.aws.tidbcloud.com`
* **Port**: `4000`
* **User**: `2msvVqGJ7tDBeDJ.root`
* **Password**: `8wZXtvGkWxSpBwZJ`
* **Database**: `mediaplayer_db`
* **SSL Certificate**: `isrgrootx1.pem` (Included in repository root)

---

## 🛡️ 3. Security & Validation Rules Implemented
1. **Password Confirmation**: Requires matching `password` and `confirm_password` during registration.
2. **Case-Insensitive Unique Usernames**: Duplicate usernames are rejected regardless of casing (`JOHN_DOE` == `john_doe`).
3. **Case-Insensitive Unique Emails**: Duplicate email addresses are strictly blocked.
4. **Password Length**: Minimum 6 characters required.
5. **Username Length**: Minimum 3 characters required.
6. **Device Image Avatar Upload**: Strictly allows image MIME types (`image/jpeg`, `image/png`, `image/webp`, `image/gif`) saved under `/uploads/avatars/`.

---

## 📱 4. Figma Screen-by-Screen API Mapping

```
                      FIGMA MOBILE APP DESIGN
┌───────────────────────┬───────────────────────┬───────────────────────┐
│     1. Home Feed      │    2. Podcast Feed    │    3. Now Playing     │
│ ┌───────────────────┐ │ ┌───────────────────┐ │ ┌───────────────────┐ │
│ │ Morning, John Doe │ │ │ Morning, John Doe │ │ │ <   ♡   ✈   ⋮     │ │
│ │ [All][Music][Pod] │ │ │   [Podcast] (on)  │ │ │ ┌───────────────┐ │ │
│ │ ┌───────────────┐ │ │ ┌─────────────────┐ │ │ │  Album Artwork  │ │ │
│ │ │ Hero Featured │ │ │ │ Host Avatars (O)│ │ │ └───────────────┘ │ │
│ │ └───────────────┘ │ │ └─────────────────┘ │ │ Kesariya - Arijit   │ │
│ │ Trending Now    > │ │ Episode Cards       │ │ ───●──────── 17m left │ │
│ │ Popular Artist  > │ │ ──●── 15 min left   │ │ [Lyrics: Mujhko...]   │ │
│ │ New Releases    > │ │ ──●── 30 min left   │ │   |<<   ▶   >>|     │ │
│ └───────────────────┘ │ └───────────────────┘ │ └───────────────────┘ │
└───────────────────────┴───────────────────────┴───────────────────────┘
```

### 🟢 Screen 1: Home Feed Screen
* **User Profile & Greeting**: `GET /api/v1/auth/me` -> Displays *"Morning, {full_name}"* & user avatar.
* **Filter Pills (All, Music, Podcast)**: `GET /api/v1/explore/home?tab=all` (or `?tab=music`, `?tab=podcast`).
* **Featured Hero Banner**: `response.hero` -> Featured track/artist banner with title and artwork.
* **Trending Now Carousel**: `response.trending_now` -> List of top trending songs with streams.
* **Popular Musicians Carousel**: `response.popular_musicians` -> Circular artist avatars with monthly listeners and verified badges.
* **New Releases Grid**: `response.new_releases` -> Album art grid with album types (`Album` / `Single`).
* **Search Icon Action**: `GET /api/v1/search?q={query}` -> Real-time universal search.

### 🟢 Screen 2: Podcast Screen
* **Podcast Tab Active**: `GET /api/v1/explore/home?tab=podcast`
* **Podcast Host Avatars**: `GET /api/v1/podcasts/shows` -> Host avatars, show descriptions, and ratings.
* **Podcast Episodes List**: `GET /api/v1/podcasts/episodes` -> Titles, durations, publish dates, and seekable audio.
* **Podcast Audio Stream**: `GET /api/v1/podcasts/episodes/{id}/stream` -> HTTP 206 partial range streaming.

### 🟢 Screen 3: "Now Playing" Modal (Song Play Screen)
* **Track Metadata**: `GET /api/v1/tracks/{id}` -> Title, artist name, album name, high-res cover art.
* **Audio Range Streaming**: `GET /api/v1/tracks/{id}/stream` -> Supports instant seekbar dragging, rewind, and fast-forward.
* **Live Lyrics**: `GET /api/v1/tracks/{id}/lyrics` -> Returns song lyrics preview.
* **Favorite Heart Toggle**: `POST /api/v1/favorites/toggle` with body `{"track_id": 1}`.
* **Up Next Play Queue**: `GET /api/v1/queue` & `POST /api/v1/queue/add`.
* **Playback Progress Tracking**: `POST /api/v1/playback/progress` with `{ "track_id": 1, "progress_seconds": 120, "completed": false }`.

---

## 🤖 5. Android Development Guide (Kotlin & Jetpack Compose)

When creating the Android application, use the following recommended architecture:

### A. Tech Stack for Android:
- **Language**: Kotlin 2.0+
- **UI Framework**: Jetpack Compose (Material 3 Dark Theme)
- **Networking**: Retrofit 2 + Kotlinx Serialization / Gson + OkHttp 4
- **Image Loading**: Coil (`io.coil-kt:coil-compose`)
- **Audio Engine**: AndroidX Media3 (ExoPlayer) with HTTP range seeking support

---

### B. Networking Setup & Base URL (Kotlin):

```kotlin
// NetworkClient.kt
object NetworkClient {
    private const val BASE_URL = "https://media-player-backend-rud4.onrender.com/"

    private val authInterceptor = Interceptor { chain ->
        val token = TokenManager.getToken() // Retrieve stored JWT
        val request = if (token != null) {
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else {
            chain.request()
        }
        chain.proceed(request)
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
```

---

### C. Retrofit API Service Interface (Kotlin):

```kotlin
// ApiService.kt
interface ApiService {
    // 1. Authentication
    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<TokenResponse>

    @POST("api/v1/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<TokenResponse>

    @GET("api/v1/auth/me")
    suspend fun getProfile(): Response<UserProfile>

    // 2. Explore & Home Feed
    @GET("api/v1/explore/home")
    suspend fun getHomeFeed(@Query("tab") tab: String = "all"): Response<HomeFeedResponse>

    // 3. Tracks & Streaming
    @GET("api/v1/tracks/{id}")
    suspend fun getTrackDetail(@Path("id") id: Int): Response<TrackDto>

    @GET("api/v1/tracks/{id}/lyrics")
    suspend fun getLyrics(@Path("id") id: Int): Response<LyricsDto>

    // 4. Favorites & Queue
    @POST("api/v1/favorites/toggle")
    suspend fun toggleFavorite(@Body request: FavoriteToggleRequest): Response<FavoriteResponse>

    @GET("api/v1/favorites/my-favorites")
    suspend fun getMyFavorites(): Response<FavoritesListResponse>

    @GET("api/v1/queue")
    suspend fun getQueue(): Response<List<QueueItemDto>>

    // 5. Universal Search
    @GET("api/v1/search")
    suspend fun search(@Query("q") query: String): Response<SearchResultResponse>
}
```

---

### D. Audio Playback with AndroidX Media3 / ExoPlayer:

```kotlin
// MediaPlayerController.kt
class MediaPlayerController(context: Context) {
    private val exoPlayer = ExoPlayer.Builder(context).build()

    fun playTrack(trackId: Int) {
        val streamUrl = "https://media-player-backend-rud4.onrender.com/api/v1/tracks/$trackId/stream"
        val mediaItem = MediaItem.fromUri(Uri.parse(streamUrl))
        exoPlayer.setMediaItem(mediaItem)
        exoPlayer.prepare()
        exoPlayer.play()
    }

    fun pause() = exoPlayer.pause()
    fun resume() = exoPlayer.play()
    fun seekTo(positionMs: Long) = exoPlayer.seekTo(positionMs)
    fun release() = exoPlayer.release()
}
```

---

### E. Jetpack Compose UI Theme & Colors (Matching Figma Design):
- **Background**: `#0F0817` (Deep Dark Purple / Black)
- **Card Background**: `#1C122C` / `#231538`
- **Primary Purple Accent**: `#8A2BE2` / `#7B1FA2`
- **Active Pill / Highlight**: `#D946EF` (Vibrant Neon Pink/Purple)
- **Text Color Primary**: `#FFFFFF`
- **Text Color Secondary**: `#A1A1AA`

---

## 🎯 6. Instructions for Future AI Assistant Sessions:
When asked to develop the Android app or add features:
1. Reference the models and endpoints in this file.
2. The live server is deployed at `https://media-player-backend-rud4.onrender.com`.
3. Use `john_doe` / `password123` to test authenticated user interactions.
4. Audio streaming is fully functional and supports seekbar scrubbing via `GET /api/v1/tracks/{id}/stream`.
