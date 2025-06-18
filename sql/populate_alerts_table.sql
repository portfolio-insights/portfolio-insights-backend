-- The queries in this file are used to populate the `alerts` table with dummy
-- data, consisting of alerts in various states. Useful for testing.
--
-- Assumes that a user with id = 1 exists in the `users` table. This is
-- the guest user created by `populate_users_table.sql`.

-- Active alerts
INSERT INTO alerts (user_id, ticker, price, direction, creation_time, triggered, expired)
VALUES 
    (1, 'AAPL', 175.00, 'above', NOW() - INTERVAL '1 day', false, false),
    (1, 'MSFT', 380.00, 'below', NOW() - INTERVAL '2 days', false, false),
    (1, 'GOOGL', 140.00, 'above', NOW() - INTERVAL '3 days', false, false);

-- Triggered alerts
INSERT INTO alerts (user_id, ticker, price, direction, creation_time, triggered, triggered_time, expired)
VALUES 
    (1, 'AMZN', 180.00, 'above', NOW() - INTERVAL '5 days', true, NOW() - INTERVAL '1 day', false),
    (1, 'META', 450.00, 'below', NOW() - INTERVAL '4 days', true, NOW() - INTERVAL '2 days', false);

-- Expired alerts
INSERT INTO alerts (user_id, ticker, price, direction, creation_time, triggered, expired, expiration_time)
VALUES 
    (1, 'TSLA', 200.00, 'above', NOW() - INTERVAL '10 days', false, true, NOW() - INTERVAL '3 days'),
    (1, 'NVDA', 800.00, 'below', NOW() - INTERVAL '8 days', false, true, NOW() - INTERVAL '1 day');

-- Mixed state alerts
INSERT INTO alerts (user_id, ticker, price, direction, creation_time, triggered, triggered_time, expired, expiration_time)
VALUES 
    (1, 'AMD', 150.00, 'above', NOW() - INTERVAL '7 days', true, NOW() - INTERVAL '2 days', true, NOW() - INTERVAL '1 day'),
    (1, 'INTC', 40.00, 'below', NOW() - INTERVAL '6 days', true, NOW() - INTERVAL '3 days', true, NOW() - INTERVAL '2 days'); 