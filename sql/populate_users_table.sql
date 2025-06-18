-- The query in this file is used to populate the `users` table with a
-- guest user, which can be used for testing and also allows users to
-- log in with the guest account rather than registering a new account.

INSERT INTO users (id, username, password, created_at)
VALUES 
    (1, 'Guest', 'GuestPassword', NOW() - INTERVAL '30 days');
