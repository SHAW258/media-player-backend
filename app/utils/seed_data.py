import datetime
import math
import struct
import wave
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.category import Category
from app.models.artist import Artist
from app.models.album import Album
from app.models.track import Track
from app.models.podcast import PodcastShow, PodcastEpisode
from app.models.playlist import Playlist, PlaylistTrack
from app.models.favorite import Favorite
from app.models.history import PlaybackHistory
from app.models.queue import UserQueue
from app.utils.security import get_password_hash
from app.config import settings

def create_sample_tone_audio_file(file_path: Path, duration_seconds: int = 15, freq: float = 440.0):
    """Generates a lightweight audio WAV file quickly so playback and range streaming work immediately."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        return
    
    sample_rate = 22050
    # Generate 1 second of audio cycle
    one_sec_samples = []
    for i in range(sample_rate):
        t = float(i) / sample_rate
        value = 0.5 * math.sin(2.0 * math.pi * freq * t) + 0.3 * math.sin(2.0 * math.pi * (freq * 1.5) * t)
        sample = int(value * 32767.0 * 0.4)
        one_sec_samples.append(struct.pack('<h', max(-32768, min(32767, sample))))
    
    one_sec_bytes = b"".join(one_sec_samples)
    
    with wave.open(str(file_path), 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        # Repeat 1 second chunk
        for _ in range(min(duration_seconds, 15)):
            wav_file.writeframesraw(one_sec_bytes)

def seed_database(db: Session):
    """Seeds the database with Figma Media Player mock data and sample audio files."""
    
    # 1. Create sample audio files
    sample_audio_1 = settings.STATIC_DIR / "audio" / "ghost_axe_ross.wav"
    sample_audio_2 = settings.STATIC_DIR / "audio" / "smoke_and_mirrors.wav"
    sample_audio_3 = settings.STATIC_DIR / "audio" / "podcast_tech_talk.wav"
    sample_audio_4 = settings.STATIC_DIR / "audio" / "the_adam.wav"
    
    create_sample_tone_audio_file(sample_audio_1, duration_seconds=225, freq=440.0)
    create_sample_tone_audio_file(sample_audio_2, duration_seconds=198, freq=523.25)
    create_sample_tone_audio_file(sample_audio_3, duration_seconds=640, freq=349.23)
    create_sample_tone_audio_file(sample_audio_4, duration_seconds=210, freq=392.0)

    # 2. Check if already seeded
    if db.query(User).filter(User.username == "john_doe").first():
        return {"status": "already_seeded", "message": "Database already contains seed data"}

    # 3. Seed Default User (John Doe from Figma UI)
    john_doe = User(
        username="john_doe",
        email="john.doe@example.com",
        password_hash=get_password_hash("password123"),
        full_name="John Doe",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300",
        role="user",
        is_active=True
    )
    admin_user = User(
        username="admin",
        email="admin@mediaplayer.io",
        password_hash=get_password_hash("admin123"),
        full_name="Administrator",
        avatar_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=300",
        role="admin",
        is_active=True
    )
    db.add_all([john_doe, admin_user])
    db.commit()
    db.refresh(john_doe)

    # 4. Seed Categories
    cat_pop = Category(name="Pop", slug="pop", category_type="music", icon="music-note", cover_image="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300")
    cat_rock = Category(name="Rock", slug="rock", category_type="music", icon="guitar", cover_image="https://images.unsplash.com/photo-1498038432885-c6f3f1b912ee?w=300")
    cat_electronic = Category(name="Electronic", slug="electronic", category_type="music", icon="disc", cover_image="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300")
    cat_rnb = Category(name="R&B", slug="rnb", category_type="music", icon="mic", cover_image="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300")
    cat_tech = Category(name="Technology", slug="technology", category_type="podcast", icon="cpu", cover_image="https://images.unsplash.com/photo-1518770660439-4636190af475?w=300")
    cat_talk = Category(name="Talk Shows", slug="talk-shows", category_type="podcast", icon="radio", cover_image="https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=300")
    
    db.add_all([cat_pop, cat_rock, cat_electronic, cat_rnb, cat_tech, cat_talk])
    db.commit()

    # 5. Seed Artists (Featured in Figma Design)
    artist_axe_ross = Artist(
        name="Axe Ross",
        bio="Chart-topping producer and synthwave visionary.",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
        header_url="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=1000",
        monthly_listeners=4520000,
        is_verified=True,
        is_popular=True,
        category_id=cat_electronic.id
    )
    artist_charlie = Artist(
        name="Charlie Puth",
        bio="Grammy-nominated multi-platinum singer-songwriter and producer.",
        avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400",
        monthly_listeners=38400000,
        is_verified=True,
        is_popular=True,
        category_id=cat_pop.id
    )
    artist_the_weeknd = Artist(
        name="The Weeknd",
        bio="Global megastar blending dark R&B, synth-pop, and futuristic disco.",
        avatar_url="https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=400",
        monthly_listeners=92000000,
        is_verified=True,
        is_popular=True,
        category_id=cat_rnb.id
    )
    artist_dua_lipa = Artist(
        name="Dua Lipa",
        bio="Pop powerhouse defining modern dance-pop and disco grooves.",
        avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400",
        monthly_listeners=68000000,
        is_verified=True,
        is_popular=True,
        category_id=cat_pop.id
    )
    db.add_all([artist_axe_ross, artist_charlie, artist_the_weeknd, artist_dua_lipa])
    db.commit()

    # 6. Seed Albums (New Releases from Figma)
    album_ghost = Album(
        title="Ghost Dimension",
        artist_id=artist_axe_ross.id,
        cover_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600",
        release_date=datetime.date(2026, 8, 1),
        album_type="album",
        total_tracks=10,
        is_new_release=True
    )
    album_adam = Album(
        title="The Adam",
        artist_id=artist_charlie.id,
        cover_url="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600",
        release_date=datetime.date(2026, 7, 20),
        album_type="album",
        total_tracks=12,
        is_new_release=True
    )
    album_pure_sat = Album(
        title="Pure Saturday",
        artist_id=artist_the_weeknd.id,
        cover_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=600",
        release_date=datetime.date(2026, 8, 10),
        album_type="single",
        total_tracks=2,
        is_new_release=True
    )
    db.add_all([album_ghost, album_adam, album_pure_sat])
    db.commit()

    # 7. Seed Tracks (From Figma: Ghost - Axe Ross, Smoke..., Love..., Ordinary...)
    track_ghost = Track(
        title="Ghost",
        artist_id=artist_axe_ross.id,
        album_id=album_ghost.id,
        category_id=cat_electronic.id,
        duration_seconds=225,  # 3:45
        audio_url="/static/audio/ghost_axe_ross.wav",
        cover_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600",
        lyrics="Walking through the neon lights\nEchoes calling in the night\nJust a ghost inside the machine\nLiving in a holographic dream...",
        stream_count=1845000,
        is_trending=True,
        is_new_release=True,
        media_type="music"
    )
    track_smoke = Track(
        title="Smoke & Mirrors",
        artist_id=artist_axe_ross.id,
        album_id=album_ghost.id,
        category_id=cat_electronic.id,
        duration_seconds=198,  # 3:18
        audio_url="/static/audio/smoke_and_mirrors.wav",
        cover_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600",
        lyrics="Watching shadows on the wall\nWaiting for the rise and fall\nSmoke and mirrors everywhere...",
        stream_count=1230000,
        is_trending=True,
        is_new_release=True,
        media_type="music"
    )
    track_love = Track(
        title="Love In The Dark",
        artist_id=artist_dua_lipa.id,
        album_id=album_adam.id,
        category_id=cat_pop.id,
        duration_seconds=210,
        audio_url="/static/audio/the_adam.wav",
        cover_url="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600",
        lyrics="Dancing through the midnight glow\nWhere the hidden rivers flow...",
        stream_count=980000,
        is_trending=True,
        is_new_release=False,
        media_type="music"
    )
    track_ordinary = Track(
        title="Ordinary Life",
        artist_id=artist_the_weeknd.id,
        album_id=album_pure_sat.id,
        category_id=cat_rnb.id,
        duration_seconds=240,
        audio_url="/static/audio/ghost_axe_ross.wav",
        cover_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=600",
        lyrics="No more ordinary days\nCaught inside the purple haze...",
        stream_count=1420000,
        is_trending=True,
        is_new_release=True,
        media_type="music"
    )
    db.add_all([track_ghost, track_smoke, track_love, track_ordinary])
    db.commit()

    # 8. Seed Podcast Shows & Episodes
    podcast_tech = PodcastShow(
        title="Deep Tech & Soundscapes",
        host_name="Alex Vance",
        description="Exploring the cutting edge of AI, audio engineering, and music production technology.",
        cover_url="https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600",
        category_id=cat_tech.id,
        total_episodes=2,
        rating=4.9
    )
    db.add(podcast_tech)
    db.commit()

    ep_1 = PodcastEpisode(
        show_id=podcast_tech.id,
        title="The Future of Spatial Audio & Media Players",
        description="How modern streaming backends and progressive range headers deliver instant audio playback.",
        duration_seconds=640,
        audio_url="/static/audio/podcast_tech_talk.wav",
        cover_url="https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600",
        episode_number=1,
        stream_count=45000
    )
    ep_2 = PodcastEpisode(
        show_id=podcast_tech.id,
        title="Designing Fluid Dark Mode Interfaces for Music Apps",
        description="UI/UX breakdown of modern dark glassmorphic media players.",
        duration_seconds=520,
        audio_url="/static/audio/podcast_tech_talk.wav",
        cover_url="https://images.unsplash.com/photo-1518770660439-4636190af475?w=600",
        episode_number=2,
        stream_count=32000
    )
    db.add_all([ep_1, ep_2])
    db.commit()

    # 9. Seed Playlists for John Doe
    playlist_favs = Playlist(
        user_id=john_doe.id,
        name="John's Favorites",
        description="Top handpicked tracks for daily listening.",
        cover_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400",
        is_public=True
    )
    db.add(playlist_favs)
    db.commit()

    pt1 = PlaylistTrack(playlist_id=playlist_favs.id, track_id=track_ghost.id, position=0)
    pt2 = PlaylistTrack(playlist_id=playlist_favs.id, track_id=track_smoke.id, position=1)
    db.add_all([pt1, pt2])
    db.commit()

    # 10. Seed Favorites & History
    fav1 = Favorite(user_id=john_doe.id, track_id=track_ghost.id)
    fav2 = Favorite(user_id=john_doe.id, track_id=track_smoke.id)
    hist1 = PlaybackHistory(user_id=john_doe.id, track_id=track_ghost.id, progress_seconds=154, completed=False)
    q1 = UserQueue(user_id=john_doe.id, track_id=track_smoke.id, position=0)
    q2 = UserQueue(user_id=john_doe.id, track_id=track_ordinary.id, position=1)
    
    db.add_all([fav1, fav2, hist1, q1, q2])
    db.commit()

    return {"status": "success", "message": "Database successfully seeded with Figma Media Player mock data"}
