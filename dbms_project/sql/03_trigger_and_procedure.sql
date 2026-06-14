-- ============================================================
-- FILE: 03_trigger_and_procedure.sql
-- RUN THIS THIRD
-- ============================================================

USE dbms_project;

DELIMITER $$

DROP PROCEDURE IF EXISTS score_transaction$$

CREATE PROCEDURE score_transaction(IN p_txn_id INT)
BEGIN
    DECLARE v_user_id      INT;
    DECLARE v_amount       DECIMAL(12,2);
    DECLARE v_location     VARCHAR(100);
    DECLARE v_txn_time     TIMESTAMP;
    DECLARE v_user_country VARCHAR(50);
    DECLARE v_txn_hour     INT;
    DECLARE v_recent_count INT;
    DECLARE v_repeat_count INT;
    DECLARE v_risk_score   INT DEFAULT 0;
    DECLARE v_rules_fired  VARCHAR(500) DEFAULT '';
    DECLARE v_high_amount_threshold DECIMAL(12,2);
    DECLARE v_velocity_limit        INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        INSERT INTO audit_log (action, table_affected, details)
        VALUES ('PROCEDURE_ERROR', 'fraud_alerts', CONCAT('Error scoring txn_id=', p_txn_id));
    END;

    START TRANSACTION;

    SELECT t.user_id, t.amount, t.location, t.txn_time, u.country
    INTO   v_user_id, v_amount, v_location, v_txn_time, v_user_country
    FROM   transactions t
    JOIN   users u ON t.user_id = u.user_id
    WHERE  t.txn_id = p_txn_id
    FOR UPDATE;

    SELECT threshold INTO v_high_amount_threshold
    FROM fraud_rules WHERE rule_name = 'HIGH_AMOUNT' AND is_active = 1;

    SELECT threshold INTO v_velocity_limit
    FROM fraud_rules WHERE rule_name = 'VELOCITY' AND is_active = 1;

    SET v_txn_hour = HOUR(v_txn_time);

    -- RULE 1: HIGH AMOUNT
    IF v_amount > v_high_amount_threshold THEN
        SET v_risk_score = v_risk_score + 40;
        SET v_rules_fired = CONCAT(v_rules_fired, 'HIGH_AMOUNT ');
    END IF;

    -- RULE 2: VELOCITY
    SELECT COUNT(*) INTO v_recent_count
    FROM transactions
    WHERE user_id = v_user_id
      AND txn_time BETWEEN DATE_SUB(v_txn_time, INTERVAL 10 MINUTE) AND v_txn_time
      AND txn_id != p_txn_id;

    IF v_recent_count >= v_velocity_limit THEN
        SET v_risk_score = v_risk_score + 35;
        SET v_rules_fired = CONCAT(v_rules_fired, 'VELOCITY ');
    END IF;

    -- RULE 3: LOCATION MISMATCH
    IF v_location NOT LIKE CONCAT('%', v_user_country, '%') THEN
        SET v_risk_score = v_risk_score + 30;
        SET v_rules_fired = CONCAT(v_rules_fired, 'LOCATION_MISMATCH ');
    END IF;

    -- RULE 4: ODD HOURS
    IF v_txn_hour BETWEEN 1 AND 5 THEN
        SET v_risk_score = v_risk_score + 15;
        SET v_rules_fired = CONCAT(v_rules_fired, 'ODD_HOURS ');
    END IF;

    -- RULE 5: RAPID REPEAT
    SELECT COUNT(*) INTO v_repeat_count
    FROM transactions
    WHERE user_id = v_user_id
      AND amount  = v_amount
      AND txn_time BETWEEN DATE_SUB(v_txn_time, INTERVAL 60 SECOND) AND v_txn_time
      AND txn_id != p_txn_id;

    IF v_repeat_count >= 1 THEN
        SET v_risk_score = v_risk_score + 25;
        SET v_rules_fired = CONCAT(v_rules_fired, 'RAPID_REPEAT ');
    END IF;

    -- FINAL DECISION
    IF v_risk_score > 0 THEN
        INSERT INTO fraud_alerts (txn_id, rule_triggered, risk_score)
        VALUES (p_txn_id, TRIM(v_rules_fired), v_risk_score);

        UPDATE transactions SET status = 'blocked' WHERE txn_id = p_txn_id;

        INSERT INTO audit_log (action, table_affected, record_id, details)
        VALUES ('FRAUD_FLAGGED', 'transactions', p_txn_id,
                CONCAT('Risk score: ', v_risk_score, ' | Rules: ', v_rules_fired));
    ELSE
        UPDATE transactions SET status = 'approved' WHERE txn_id = p_txn_id;

        INSERT INTO audit_log (action, table_affected, record_id, details)
        VALUES ('TXN_APPROVED', 'transactions', p_txn_id, 'No fraud rules triggered');
    END IF;

    COMMIT;
END$$

DROP TRIGGER IF EXISTS after_txn_insert$$

CREATE TRIGGER after_txn_insert
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    CALL score_transaction(NEW.txn_id);
END$$

DELIMITER ;

SELECT 'Trigger and stored procedure created successfully.' AS message;
