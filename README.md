# 🛡️ Fraud Detection System for Online Transactions

> A real-time fraud detection system built with **Python** and **MySQL** that automatically detects, scores, and blocks suspicious financial transactions using rule-based logic — available as both a **Desktop GUI** and a **Web Application**.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-lightblue)

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
- Provides both a **Desktop GUI** and a **Web Application** dashboard for monitoring

> This solves the real-world problem of financial fraud in digital payments, which causes billions of rupees in losses every year in India alone.

---

## 🛠️ Tech Used

| Technology              | Purpose                                          |
|-------------------------|--------------------------------------------------|
| Python 3                | Application logic, fraud scoring                 |
| MySQL 8                 | Database — tables, views, stored procedure       |
| mysql-connector-python  | Connects Python to MySQL                         |
| Flask 3.1               | Web application framework                        |
| Tkinter                 | Desktop GUI dashboard (built into Python)        |
| HTML + CSS              | Web app frontend pages                           |
| MySQL Workbench         | Run SQL scripts, view tables                     |
| Git & GitHub            | Version control and collaboration                |

---

## 🗂️ Project Structure

```
fraud-detection-system/
│
├── sql/
│   ├── 01_schema.sql                  → Creates dbms_project database + 5 tables
│   ├── 02_seed_data.sql               → Inserts 10 users and 5 fraud rules
│   ├── 03_trigger_and_procedure.sql   → Stored procedure for fraud scoring
│   └── 04_views.sql                   → 3 reporting views for dashboard
│
├── python/                            ← Desktop GUI version
│   ├── db_connect.py                  → MySQL connection manager
│   ├── transaction_service.py         → Insert transactions + fraud scoring
│   ├── fraud_engine.py                → Read alerts and generate reports
│   ├── simulate_data.py               → Generate test transactions
│   └── gui_dashboard.py               → Full 8-page Tkinter desktop GUI
│
├── webapp/                            ← Web Application version
│   ├── app.py                         → Flask web server (main entry point)
│   ├── db_connect.py                  → MySQL connection manager
│   ├── transaction_service.py         → Insert transactions + fraud scoring
│   ├── fraud_engine.py                → Read alerts and generate reports
│   ├── simulate_data.py               → Generate test transactions
│   └── templates/
│       ├── base.html                  → Navigation bar + layout
│       ├── overview.html              → Dashboard with stat cards
│       ├── alerts.html                → All fraud alerts table
│       ├── high_risk.html             → High risk alerts only
│       ├── rules.html                 → Rule effectiveness stats
│       ├── users.html                 → User fraud summary
│       ├── audit.html                 → Audit log table
│       ├── simulate.html              → One-click simulation buttons
│       └── add_transaction.html       → Manual transaction entry form
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

## ⚙️ Steps Included

### Step 1 — Install Required Libraries
```bash
pip install flask mysql-connector-python
```

### Step 2 — Set Up Database in MySQL Workbench
Run the 4 SQL files **in this exact order**:
```
01_schema.sql                → Creates dbms_project database + 5 tables
02_seed_data.sql             → Inserts 10 users and 5 fraud rules
03_trigger_and_procedure.sql → Creates stored procedure for fraud scoring
04_views.sql                 → Creates 3 reporting views
```

### Step 3 — Configure Database Password
Open `db_connect.py` and update:
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

### Step 5A — Run Desktop GUI
```bash
cd python
python gui_dashboard.py
```

### Step 5B — Run Web Application
```bash
cd webapp
python app.py
```
Then open: `http://localhost:5000`

---

## 🖥️ Two Ways to Use This Project

### Option 1 — Desktop GUI (Tkinter)
- Dark-themed desktop window
- 8 interactive pages via sidebar navigation
- Run: `python gui_dashboard.py`

### Option 2 — Web Application (Flask)
- Opens in any browser (Chrome, Edge, Firefox)
- Top navigation bar with live alert badge counter
- Run: `python app.py` → open `http://localhost:5000`

---

## 🗃️ Database Design

### 5 Tables

| Table           | Key Columns                                          | Purpose                      |
|-----------------|------------------------------------------------------|------------------------------|
| `users`         | user_id (PK), name, email, country, phone            | Registered user profiles     |
| `transactions`  | txn_id (PK), user_id (FK), amount, location, status  | All transaction records      |
| `fraud_rules`   | rule_id (PK), rule_name, threshold, risk_weight       | Configurable detection rules |
| `fraud_alerts`  | alert_id (PK), txn_id (FK), rule_triggered, risk_score | Fraud detection events     |
| `audit_log`     | log_id (PK), action, record_id, details, log_time    | Complete system activity log |

### Advanced MySQL Concepts Used

| Concept                 | Where Used                                        |
|-------------------------|---------------------------------------------------|
| Stored Procedure        | `score_transaction()` — encapsulated fraud logic  |
| Views                   | `vw_fraud_report`, `vw_rule_summary`              |
| Foreign Key Constraints | transactions → users, fraud_alerts → transactions |
| ENUM Type               | `transactions.status` (pending/approved/blocked)  |
| Composite Index         | `idx_user_time` on transactions table             |
| SELECT FOR UPDATE       | Row-level locking in concurrent updates           |
| AUTO_INCREMENT          | All primary keys                                  |
| DECIMAL Precision       | `transactions.amount` — exact currency storage    |

---

## 🔍 Analysis Done

### 5 Fraud Detection Rules

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

---

## 💡 Key Insights

- **VELOCITY** rule triggered most frequently (76.5% of all alerts) — rapid successive transactions are the most common fraud pattern
- **HIGH_AMOUNT + LOCATION_MISMATCH** together produce the highest risk score (70 = HIGH risk)
- **40.5% fraud rate** observed in simulation — matching real-world studies
- Fraud rules in **`fraud_rules` table** are configurable without touching any Python code
- **audit_log** ensures every transaction decision is permanently recorded with timestamp
- **LOCATION_MISMATCH** alone (score 30) does not block — requires a second rule, reducing false positives
- All **5 fraud scenarios** successfully detected in testing

---

## 🌍 SDG Goals Achieved

| SDG Goal | Title                                  | How This Project Contributes                          |
|----------|----------------------------------------|-------------------------------------------------------|
| Goal 16  | Peace, Justice & Strong Institutions   | Transparent audit trail, automated fraud prevention   |
| Goal 9   | Industry, Innovation & Infrastructure  | Innovative DB engineering for real fintech problem    |
| Goal 10  | Reduced Inequalities                   | Accessible automated fraud protection for all users   |

---

## ✅ Conclusion

The **Fraud Detection System for Online Transactions** successfully demonstrates how Python and MySQL can be combined to solve a real-world, complex engineering problem. The system:

- ✅ Detects fraud **in real time** at the point of transaction insert
- ✅ Applies **5 configurable rules** with composite risk scoring (0–100)
- ✅ Maintains a **complete audit trail** — every decision permanently logged
- ✅ Uses advanced MySQL — stored procedures, views, row-level locking, ENUM, indexes
- ✅ Provides **two interfaces** — Tkinter desktop GUI and Flask web application
- ✅ Rules are **configurable from the database** — no code changes needed
- ✅ Successfully tested all **5 fraud scenarios** with correct detection
- ✅ Contributes to **SDG 16, SDG 9, and SDG 10**

---

## 📦 Requirements

```
flask==3.1.3
mysql-connector-python==9.7.0
```

```bash
pip install flask mysql-connector-python
```

> Tkinter is built into Python — no installation needed.

---

## 📁 References

- [MySQL 8.0 Documentation](https://dev.mysql.com/doc/refman/8.0/en/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python mysql-connector Docs](https://dev.mysql.com/doc/connector-python/en/)
- [UN Sustainable Development Goals](https://sdgs.un.org/goals)
- [RBI Payment Fraud Report 2023](https://www.rbi.org.in)
