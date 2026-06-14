# 🛡️ Fraud Detection System for Online Transactions

A real-time fraud detection system built with **Python 3** and **MySQL 8**,
featuring a dark-themed Tkinter GUI dashboard.

## 👥 Team
| Member   | Role                    |
|----------|-------------------------|
| Ishra    | Coding & GitHub         |
| Basheera | Documentation           |
| Areeba   | Testing & Presentation  |

## 🗂️ Project Structure
fraud-detection-system/

├── sql/

│   ├── 01_schema.sql

│   ├── 02_seed_data.sql

│   ├── 03_trigger_and_procedure.sql

│   └── 04_views.sql

├── python/

│   ├── db_connect.py

│   ├── transaction_service.py

│   ├── fraud_engine.py

│   ├── simulate_data.py

│   └── gui_dashboard.py

└── docs/

└── FraudDetection_FinalReport.docx

## ⚙️ How to Run
1. `pip install mysql-connector-python`
2. Run SQL files 01 to 04 in MySQL Workbench
3. Update password in `python/db_connect.py`
4. `python simulate_data.py`
5. `python gui_dashboard.py`

## 🔍 Fraud Detection Rules
| Rule | Condition | Risk Score |
|------|-----------|------------|
| HIGH_AMOUNT | Amount > Rs.50,000 | +40 |
| VELOCITY | >3 txns in 10 mins | +35 |
| LOCATION_MISMATCH | Foreign country | +30 |
| RAPID_REPEAT | Same amount < 60 secs | +25 |
| ODD_HOURS | 1 AM – 5 AM | +15 |

## 🎯 SDG Goals
- **SDG 16** — Peace, Justice and Strong Institutions
- **SDG 9** — Industry, Innovation and Infrastructure
- **SDG 10** — Reduced Inequalities
