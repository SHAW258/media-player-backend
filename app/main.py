import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.utils.seed_data import seed_database
from app.routers import (
    auth_router,
    users_router,
    explore_router,
    tracks_router,
    artists_router,
    albums_router,
    podcasts_router,
    playlists_router,
    favorites_router,
    playback_router,
    queue_router,
    search_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event: create tables on startup and seed initial database."""
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[Warning] Database initialization error during startup: {e}")
    yield

app = FastAPI(
    title="Media Player REST API",
    description="""
# 🎵 Media Player Backend API & Database

Comprehensive backend built for the **Figma Media Player App Design** using **FastAPI** and **MySQL Database**.

### 🌟 Key Capabilities:
* **Audio Streaming & Seeking**: Full HTTP 206 Partial Content (Range header) audio playback streaming.
* **Explore Feeds**: Tabs for *All*, *Music*, and *Podcasts*, with *Hero Banner*, *Trending Now*, *Popular Musicians*, and *New Releases*.
* **Track & Album Management**: Metadata, cover art, stream count stats, and lyrics.
* **Podcast Shows & Episodes**: Episode streaming, podcast categories, and host info.
* **User Library & Playlists**: Custom playlists, add/remove tracks, reordering, and public/private toggles.
* **Player State & Queue**: Progress sync (e.g. 2:34 / 3:45), recently played history, and 'Up Next' queue.
* **Favorites & Likes**: Instant toggle likes for tracks, albums, and podcast episodes.
* **Authentication**: JWT Bearer token authentication + OAuth2 Password Flow.

### 🔑 Demo Credentials:
* **Username**: `john_doe` | **Password**: `password123`
* **Admin**: `admin` | **Password**: `admin123`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Uploads Mount
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# Include Routers under /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(explore_router, prefix="/api/v1")
app.include_router(tracks_router, prefix="/api/v1")
app.include_router(artists_router, prefix="/api/v1")
app.include_router(albums_router, prefix="/api/v1")
app.include_router(podcasts_router, prefix="/api/v1")
app.include_router(playlists_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(playback_router, prefix="/api/v1")
app.include_router(queue_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def root():
    """Redirect root path to interactive Swagger Documentation."""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health & Status"], summary="Health check endpoint")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": settings.DB_NAME,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
