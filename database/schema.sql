-- ═══════════════════════════════════════════════════════════════
-- AI Chatbot — SQLite Database Schema
-- Run this manually if needed, or let SQLAlchemy auto-create tables.
-- ═══════════════════════════════════════════════════════════════

PRAGMA foreign_keys = ON;

-- ── Users Table ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ── Chats Table ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chats (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      TEXT    NOT NULL DEFAULT 'New Chat',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);

-- ── Messages Table ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id   INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role      TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
    content   TEXT    NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);

-- ═══════════════════════════════════════════════════════════════
-- Relationships:
--   users 1 ─── ∞ chats    (one user, many chats)
--   chats 1 ─── ∞ messages (one chat, many messages)
--   ON DELETE CASCADE means deleting a user deletes their chats,
--   and deleting a chat deletes its messages automatically.
-- ═══════════════════════════════════════════════════════════════
