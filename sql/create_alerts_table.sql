-- Creates the `alerts` table for storing user-specific stock price alerts.
-- Alerts are linked to a `users` table via a foreign key.
--
-- This table is intended for use with the Portfolio Insights backend
-- and supports multi-user alert tracking with cascading deletes on user removal.

CREATE TABLE alerts(
    alert_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    ticker VARCHAR(10) CHECK (char_length(ticker) >= 1) NOT NULL,
    price DECIMAL(10, 2) CHECK (price > 0) NOT NULL,
    direction TEXT CHECK (direction IN ('above', 'below')) NOT NULL,
    creation_time TIMESTAMPTZ DEFAULT NOW() NOT NULL, 
    update_time TIMESTAMPTZ,
    triggered BOOLEAN DEFAULT false,
    triggered_time TIMESTAMPTZ,
    expired BOOLEAN,
    expiration_time TIMESTAMPTZ,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);