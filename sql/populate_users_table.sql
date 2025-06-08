-- The queries in this file are used to populate the `users` table with test
-- data, consisting of two users. Useful for testing.

INSERT INTO users (username, password, created_at)
VALUES 
    ('test_user', 'test123', NOW() - INTERVAL '30 days'),
    ('demo_user', 'demo456', NOW() - INTERVAL '15 days');
