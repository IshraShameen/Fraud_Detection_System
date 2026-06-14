-- ============================================================
-- FILE: 02_seed_data.sql
-- RUN THIS SECOND
-- ============================================================

USE dbms_project;

INSERT INTO users (name, email, country, phone) VALUES
('Arjun Sharma',    'arjun@example.com',   'India', '9876543210'),
('Priya Reddy',     'priya@example.com',   'India', '9123456780'),
('Ravi Kumar',      'ravi@example.com',    'India', '9988776655'),
('Ananya Singh',    'ananya@example.com',  'India', '9090909090'),
('Karan Mehta',     'karan@example.com',   'India', '9001122334'),
('Sita Nair',       'sita@example.com',    'India', '9812345670'),
('Vikram Das',      'vikram@example.com',  'India', '9700011223'),
('Deepa Pillai',    'deepa@example.com',   'India', '9654321890'),
('Mohan Verma',     'mohan@example.com',   'India', '9111222333'),
('Lakshmi Iyer',    'lakshmi@example.com', 'India', '9445566778');

INSERT INTO fraud_rules (rule_name, description, threshold, risk_weight) VALUES
('HIGH_AMOUNT',       'Single transaction exceeds threshold amount',    50000.00, 40),
('VELOCITY',          'More than 3 transactions within 10 minutes',         3.00, 35),
('LOCATION_MISMATCH', 'Transaction location differs from user country',      NULL, 30),
('ODD_HOURS',         'Transaction between 1 AM and 5 AM',                   NULL, 15),
('RAPID_REPEAT',      'Same amount from same user within 60 seconds',        NULL, 25);

SELECT 'Seed data inserted successfully.' AS message;
