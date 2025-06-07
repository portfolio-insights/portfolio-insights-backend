-- Test users for development
-- Note: In production, passwords should be properly hashed

INSERT INTO users (username, password, created_at)
VALUES 
    ('test_user', 'test123', NOW() - INTERVAL '30 days'),
    ('demo_user', 'demo456', NOW() - INTERVAL '15 days');
