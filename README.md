# 🛡️ Fraud Detection System for Online Transactions

> A real-time fraud detection system built with Python and MySQL that automatically detects, scores, and blocks suspicious financial transactions using rule-based logic — featuring a professional GUI dashboard.

---

## 👥 Team Members

| Member   | Role                        |
|----------|-----------------------------|
| Ishra    | Coding & Testing            |
| Basheera | Documentation               |
| Areeba   | GitHUb                      |

---

## 🎯 Objective

The objective of this project is to build an automated, database-driven system that:

- Detects fraudulent online transactions **in real time**
- Evaluates every transaction against **5 fraud detection rules**
- Assigns a **composite risk score** and instantly approves or blocks the transaction
- Maintains a **complete audit trail** of every decision made
- Provides a **GUI dashboard** for monitoring alerts, statistics, and system activity

> This solves the real-world problem of financial fraud in digital payments, which causes billions of rupees in losses every year in India alone.

---

## 🛠️ Tech Used

| Technology              | Purpose                                         |
|-------------------------|-------------------------------------------------|
| Python 3                | Application logic, fraud scoring, GUI           |
| MySQL 8                 | Database — stores all tables, views, procedures |
| mysql-connector-python  | Connects Python to MySQL                        |
| Tkinter                 | GUI dashboard (built into Python)               |
| MySQL Workbench         | Run SQL scripts, view tables                    |
| Git & GitHub            | Version control and collaboration               |

---

## 🗂️ Project Structure

```
fraud-detection-system/
│
├── sql/
│   ├── 01_schema.sql                  → Creates database and 5 tables
│   ├── 02_seed_data.sql               → Inserts 10 users and 5 fraud rules
│   ├── 03_trigger_and_procedure.sql   → Stored procedure for fraud scoring
│   └── 04_views.sql                   → 3 reporting views for dashboard
│
├── python/
│   ├── db_connect.py                  → MySQL connection manager
│   ├── transaction_service.py         → Insert transactions + fraud scoring
│   ├── fraud_engine.py                → Read alerts and generate reports
│   ├── simulate_data.py               → Generate test transactions
│   └── gui_dashboard.py               → Full 8-page Tkinter GUI
│
├── docs/
│   ├── FraudDetection_FinalReport.docx
│   ├── diagram_architecture.png
│   └── diagram_er.png
│
├── requirements.txt
└── README.md
```

---

## 📋 Steps Included

### Step 1 — Install Required Library
```bash
pip install mysql-connector-python
```

### Step 2 — Set Up Database in MySQL Workbench
Run the 4 SQL files **in order**:
```
01_schema.sql                → Creates dbms_project database + 5 tables
02_seed_data.sql             → Inserts users and fraud rules
03_trigger_and_procedure.sql → Creates stored procedure
04_views.sql                 → Creates reporting views
```

### Step 3 — Configure Database Password
Open `python/db_connect.py` and update:
```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "YOUR_PASSWORD",   # ← change this
    "database": "dbms_project"
}
```

### Step 4 — Generate Test Data
```bash
cd python
python simulate_data.py
```

### Step 5 — Launch the GUI Dashboard
```bash
python gui_dashboard.py
```

---

## 🔍 Analysis Done

### 5 Fraud Detection Rules Applied

| Rule                | Condition                                    | Risk Score |
|---------------------|----------------------------------------------|------------|
| `HIGH_AMOUNT`       | Transaction amount exceeds Rs. 50,000        | +40        |
| `VELOCITY`          | More than 3 transactions within 10 minutes   | +35        |
| `LOCATION_MISMATCH` | Transaction from a foreign country           | +30        |
| `RAPID_REPEAT`      | Same amount charged twice within 60 seconds  | +25        |
| `ODD_HOURS`         | Transaction between 1 AM and 5 AM            | +15        |

### Risk Level Classification

| Risk Score   | Risk Level  | Action Taken          |
|--------------|-------------|-----------------------|
| 70 and above | 🔴 HIGH     | Blocked immediately   |
| 40 to 69     | 🟠 MEDIUM   | Blocked, flagged      |
| 1 to 39      | 🟡 LOW      | Blocked, low priority |
| 0            | 🟢 SAFE     | Approved              |

### Database Tables Analysed

| Table           | Records Stored                   |
|-----------------|----------------------------------|
| `users`         | 10 registered users              |
| `transactions`  | All inserted transactions        |
| `fraud_rules`   | 5 configurable fraud rules       |
| `fraud_alerts`  | Every flagged transaction        |
| `audit_log`     | Every approve / block decision   |

### Views Used for Reporting

| View                    | Purpose                           |
|-------------------------|-----------------------------------|
| `vw_fraud_report`       | Full fraud details with user info |
| `vw_user_fraud_summary` | Most flagged users ranked         |
| `vw_rule_summary`       | How often each rule fires         |

---

## 💡 Key Insights

- **VELOCITY** rule triggered most frequently — rapid successive transactions are the most common fraud pattern
- **HIGH_AMOUNT + LOCATION_MISMATCH** together produce the highest risk score (70 = HIGH risk), meaning large foreign transactions are the most dangerous combination
- **40.5% fraud rate** observed in simulation — matching real-world studies where 30–50% of fraud scenarios are caught by rule-based systems
- Fraud rules stored in the **`fraud_rules` table** make thresholds configurable without touching any Python code — a key engineering advantage
- The **audit_log** proves that every single transaction decision is recorded, providing full transparency and accountability
- **LOCATION_MISMATCH** alone (score 30) does not block a transaction — it requires a second rule to breach the threshold, reducing false positives for legitimate travellers

---

## 🗃️ Database Concepts Demonstrated

| Concept                 | Where Used                                       |
|-------------------------|--------------------------------------------------|
| Stored Procedure        | `score_transaction()` in MySQL                  |
| Views                   | `vw_fraud_report`, `vw_rule_summary`            |
| Foreign Key Constraints | transactions→users, fraud_alerts→transactions   |
| ENUM Type               | `transactions.status` (pending/approved/blocked) |
| Composite Index         | `idx_user_time` on transactions                 |
| SELECT FOR UPDATE       | Row-level locking in transaction updates        |
| AUTO_INCREMENT          | All primary keys                                |
| DECIMAL Precision       | `transactions.amount` — exact currency storage  |

---

## 🌍 SDG Goals Achieved

| SDG Goal | Title                                 | How This Project Contributes                          |
|----------|---------------------------------------|-------------------------------------------------------|
| Goal 16  | Peace, Justice & Strong Institutions  | Transparent audit trail, automated fraud prevention   |
| Goal 9   | Industry, Innovation & Infrastructure | Innovative DB engineering for real fintech problem    |
| Goal 10  | Reduced Inequalities                  | Accessible fraud protection for all users             |

---

## 🖥️ GUI Dashboard Pages

| Page            | What It Shows                                                      |
|-----------------|--------------------------------------------------------------------|
| Overview        | Total transactions, approved, blocked, fraud rate, flagged amount  |
| Fraud Alerts    | All flagged transactions with color-coded risk levels              |
| High Risk       | Only transactions with score ≥ 70                                  |
| Rule Stats      | How many times each fraud rule was triggered                       |
| Users           | Most flagged users ranked by total flags                           |
| Audit Log       | Every system action recorded with timestamp                        |
| Simulate        | One-click buttons to test each fraud scenario                      |
| Add Transaction | Manual transaction entry with instant approve/block result         |

---

## ✅ Conclusion

The **Fraud Detection System for Online Transactions** successfully demonstrates how Python and MySQL can be combined to solve a real-world, complex engineering problem. The system:

- ✅ Detects fraud **in real time** at the point of transaction insert
- ✅ Applies **5 configurable rules** with composite risk scoring
- ✅ Maintains a **complete audit trail** — every decision is logged
- ✅ Uses advanced MySQL concepts — stored procedures, views, row-level locking, ENUM, indexes
- ✅ Provides a **professional GUI dashboard** with 8 interactive pages
- ✅ Rules are **configurable from the database** — no code changes needed to update thresholds
- ✅ Contributes to **SDG 16, SDG 9, and SDG 10**

This project mirrors real-world fraud detection systems used by banks and fintech companies, and demonstrates the practical value of Database Management Systems in solving problems of significant social and economic importance.

---

## 📦 Requirements

```
mysql-connector-python==9.7.0
```

Install with:
```bash
pip install mysql-connector-python
```

> Tkinter is built into Python — no separate installation needed.
