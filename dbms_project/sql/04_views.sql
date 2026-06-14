-- ============================================================
-- FILE: 04_views.sql
-- RUN THIS FOURTH
-- ============================================================

USE dbms_project;

CREATE OR REPLACE VIEW vw_fraud_report AS
SELECT
    fa.alert_id,
    fa.flagged_at,
    u.name          AS user_name,
    u.email         AS user_email,
    u.country       AS user_country,
    t.txn_id,
    t.amount,
    t.merchant,
    t.location,
    t.txn_time,
    fa.rule_triggered,
    fa.risk_score,
    CASE
        WHEN fa.risk_score >= 70 THEN 'HIGH'
        WHEN fa.risk_score >= 40 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS risk_level,
    fa.reviewed
FROM fraud_alerts fa
JOIN transactions t ON fa.txn_id = t.txn_id
JOIN users        u ON t.user_id = u.user_id
ORDER BY fa.risk_score DESC;

CREATE OR REPLACE VIEW vw_user_fraud_summary AS
SELECT
    u.user_id,
    u.name,
    u.email,
    COUNT(fa.alert_id)  AS total_flags,
    MAX(fa.risk_score)  AS max_risk_score,
    SUM(t.amount)       AS total_flagged_amount
FROM users u
JOIN transactions t  ON u.user_id = t.user_id
JOIN fraud_alerts fa ON t.txn_id  = fa.txn_id
GROUP BY u.user_id, u.name, u.email
ORDER BY total_flags DESC;

CREATE OR REPLACE VIEW vw_rule_summary AS
SELECT
    rule_triggered,
    COUNT(*)        AS times_triggered,
    AVG(risk_score) AS avg_risk_score,
    MAX(risk_score) AS max_risk_score
FROM fraud_alerts
GROUP BY rule_triggered
ORDER BY times_triggered DESC;

SELECT 'Views created successfully.' AS message;
