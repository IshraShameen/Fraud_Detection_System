-- ============================================================
-- FILE: 01_schema.sql
-- RUN THIS FIRST
-- ============================================================

CREATE DATABASE IF NOT EXISTS dbms_project;
USE dbms_project;

CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    country     VARCHAR(50)  NOT NULL,
    phone       VARCHAR(20),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    txn_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    amount      DECIMAL(12, 2) NOT NULL,
    merchant    VARCHAR(100) NOT NULL,
    location    VARCHAR(100) NOT NULL,
    txn_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status      ENUM('pending', 'approved', 'blocked') DEFAULT 'pending',
    ip_address  VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_time (user_id, txn_time),
    INDEX idx_status    (status)
);

CREATE TABLE IF NOT EXISTS fraud_rules (
    rule_id     INT AUTO_INCREMENT PRIMARY KEY,
    rule_name   VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    threshold   DECIMAL(12, 2),
    risk_weight INT NOT NULL DEFAULT 20,
    is_active   TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS fraud_alerts (
    alert_id        INT AUTO_INCREMENT PRIMARY KEY,
    txn_id          INT NOT NULL,
    rule_triggered  VARCHAR(100) NOT NULL,
    risk_score      INT NOT NULL DEFAULT 0,
    flagged_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed        TINYINT(1) DEFAULT 0,
    FOREIGN KEY (txn_id) REFERENCES transactions(txn_id) ON DELETE CASCADE,
    INDEX idx_txn   (txn_id),
    INDEX idx_score (risk_score)
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id         INT AUTO_INCREMENT PRIMARY KEY,
    action         VARCHAR(100) NOT NULL,
    table_affected VARCHAR(50),
    record_id      INT,
    performed_by   VARCHAR(100) DEFAULT 'system',
    details        TEXT,
    log_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT 'Schema created successfully in dbms_project.' AS message;
