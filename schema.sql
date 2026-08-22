-- ==============================================================================
-- Media Player Database Schema (MySQL)
-- Designed for Figma Media Player App Design
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS mediaplayer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mediaplayer_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(255) DEFAULT NULL,
    role ENUM('user', 'admin', 'artist') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Categories / Genres Table (Supports both Music & Podcast)
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    category_type ENUM('music', 'podcast', 'both') DEFAULT 'both',
    icon VARCHAR(100) DEFAULT NULL,
    cover_image VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Artists / Musicians Table
CREATE TABLE IF NOT EXISTS artists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    bio TEXT DEFAULT NULL,
    avatar_url VARCHAR(255) DEFAULT NULL,
    header_url VARCHAR(255) DEFAULT NULL,
    monthly_listeners INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_popular BOOLEAN DEFAULT FALSE,
    category_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_artists_name (name),
    INDEX idx_artists_popular (is_popular)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Albums Table
CREATE TABLE IF NOT EXISTS albums (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    artist_id INT NOT NULL,
    cover_url VARCHAR(255) DEFAULT NULL,
    release_date DATE DEFAULT NULL,
    album_type ENUM('album', 'single', 'ep') DEFAULT 'album',
    total_tracks INT DEFAULT 1,
    is_new_release BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
    INDEX idx_albums_artist (artist_id),
    INDEX idx_albums_new_release (is_new_release)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Tracks / Songs Table
CREATE TABLE IF NOT EXISTS tracks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    artist_id INT NOT NULL,
    album_id INT DEFAULT NULL,
    category_id INT DEFAULT NULL,
    duration_seconds INT NOT NULL DEFAULT 0,
    audio_url VARCHAR(255) NOT NULL,
    cover_url VARCHAR(255) DEFAULT NULL,
    lyrics TEXT DEFAULT NULL,
    stream_count INT DEFAULT 0,
    is_trending BOOLEAN DEFAULT FALSE,
    is_new_release BOOLEAN DEFAULT FALSE,
    media_type ENUM('music', 'podcast') DEFAULT 'music',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_tracks_trending (is_trending),
    INDEX idx_tracks_media_type (media_type),
    INDEX idx_tracks_stream_count (stream_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Podcast Shows Table
CREATE TABLE IF NOT EXISTS podcast_shows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    host_name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    cover_url VARCHAR(255) DEFAULT NULL,
    category_id INT DEFAULT NULL,
    total_episodes INT DEFAULT 0,
    rating DECIMAL(2,1) DEFAULT 5.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Podcast Episodes Table
CREATE TABLE IF NOT EXISTS podcast_episodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    show_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT DEFAULT NULL,
    duration_seconds INT NOT NULL DEFAULT 0,
    audio_url VARCHAR(255) NOT NULL,
    cover_url VARCHAR(255) DEFAULT NULL,
    episode_number INT DEFAULT 1,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stream_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (show_id) REFERENCES podcast_shows(id) ON DELETE CASCADE,
    INDEX idx_episodes_show (show_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Playlists Table
CREATE TABLE IF NOT EXISTS playlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    cover_url VARCHAR(255) DEFAULT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_playlists_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Playlist Tracks Table (Junction)
CREATE TABLE IF NOT EXISTS playlist_tracks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id INT NOT NULL,
    track_id INT NOT NULL,
    position INT DEFAULT 0,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
    UNIQUE KEY uk_playlist_track (playlist_id, track_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Favorites / Likes Table
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    track_id INT DEFAULT NULL,
    podcast_episode_id INT DEFAULT NULL,
    album_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
    FOREIGN KEY (podcast_episode_id) REFERENCES podcast_episodes(id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
    INDEX idx_favorites_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Playback History & Progress Table
CREATE TABLE IF NOT EXISTS playback_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    track_id INT DEFAULT NULL,
    podcast_episode_id INT DEFAULT NULL,
    progress_seconds INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE SET NULL,
    FOREIGN KEY (podcast_episode_id) REFERENCES podcast_episodes(id) ON DELETE SET NULL,
    INDEX idx_history_user (user_id),
    INDEX idx_history_played (played_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Playback Queue Table
CREATE TABLE IF NOT EXISTS user_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    track_id INT DEFAULT NULL,
    podcast_episode_id INT DEFAULT NULL,
    position INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
    FOREIGN KEY (podcast_episode_id) REFERENCES podcast_episodes(id) ON DELETE CASCADE,
    INDEX idx_queue_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
