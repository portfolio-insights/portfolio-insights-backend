-- Creates the `users` table for storing account credentials and metadata.
--
-- This table is intended for use with the Portfolio Insights backend
-- and is referenced by the `alerts` table via a foreign key.

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);