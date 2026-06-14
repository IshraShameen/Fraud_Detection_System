# ============================================================
# FILE: python/gui_dashboard.py
# RUN: python gui_dashboard.py
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from db_connect import get_connection, close_connection
from fraud_engine import (
    get_all_alerts, get_high_risk_alerts,
    get_rule_summary, get_user_fraud_summary,
    mark_alert_reviewed
)
from transaction_service import insert_transaction, get_transaction_status
from simulate_data import (
    simulate_normal_transactions, simulate_high_amount,
    simulate_velocity, simulate_location_mismatch,
    simulate_rapid_repeat, simulate_multi_rule
)

BG      = "#0f1117"
PANEL   = "#1a1d27"
CARD    = "#22263a"
ACCENT  = "#4f8ef7"
DANGER  = "#e05252"
SUCCESS = "#4caf7d"
WARNING = "#f0a732"
TEXT    = "#e8eaf0"
MUTED   = "#7a7f9a"
WHITE   = "#ffffff"

FONT_H1   = ("Segoe UI", 20, "bold")
FONT_H2   = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 10)
FONT_SMALL= ("Segoe UI", 9)


class FraudDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fraud Detection System — dbms_project")
        self.geometry("1200x720")
        self.minsize(1000, 600)
        self.configure(bg=BG)
        self._build_layout()
        self.show_page("overview")
        self.after(300, self.refresh_overview)

    def _build_layout(self):
        # Sidebar
        sidebar = tk.Frame(self, bg=PANEL, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="FraudGuard", font=("Segoe UI", 15, "bold"),
                 bg=PANEL, fg=ACCENT).pack(pady=(24, 2))
        tk.Label(sidebar, text="dbms_project", font=FONT_SMALL,
                 bg=PANEL, fg=MUTED).pack(pady=(0, 24))

        self.nav_buttons = {}
        nav_items = [
            ("overview",  "  Overview"),
            ("alerts",    "  Fraud Alerts"),
            ("high_risk", "  High Risk"),
            ("rules",     "  Rule Stats"),
            ("users",     "  Users"),
            ("audit",     "  Audit Log"),
            ("simulate",  "  Simulate"),
            ("insert",    "  Add Transaction"),
        ]
        for key, label in nav_items:
            btn = tk.Button(
                sidebar, text=label, font=FONT_BODY,
                bg=PANEL, fg=TEXT, bd=0, padx=20, pady=10,
                anchor="w", cursor="hand2",
                activebackground=CARD, activeforeground=ACCENT,
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(sidebar, textvariable=self.status_var, font=FONT_SMALL,
                 bg=PANEL, fg=MUTED, wraplength=190).pack(side="bottom", pady=12)

        # Main area
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        self.pages = {}
        for key, _ in nav_items:
            f = tk.Frame(self.main, bg=BG)
            f.place(relwidth=1, relheight=1)
            self.pages[key] = f

        self._build_overview()
        self._build_alerts_page()
        self._build_high_risk_page()
        self._build_rules_page()
        self._build_users_page()
        self._build_audit_page()
        self._build_simulate_page()
        self._build_insert_page()

    def show_page(self, key):
        for k, btn in self.nav_buttons.items():
            btn.configure(bg=CARD if k == key else PANEL,
                          fg=ACCENT if k == key else TEXT)
        self.pages[key].lift()
        refresh_map = {
            "overview":  self.refresh_overview,
            "alerts":    self.refresh_alerts,
            "high_risk": self.refresh_high_risk,
            "rules":     self.refresh_rules,
            "users":     self.refresh_users,
            "audit":     self.refresh_audit,
        }
        if key in refresh_map:
            refresh_map[key]()

    def _page_header(self, parent, title, subtitle=""):
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(20, 4))
        tk.Label(hdr, text=title, font=FONT_H1, bg=BG, fg=TEXT).pack(side="left")
        if subtitle:
            tk.Label(hdr, text=subtitle, font=FONT_SMALL,
                     bg=BG, fg=MUTED).pack(side="left", padx=12, pady=6)

    def _make_table(self, parent, columns, col_widths=None):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=CARD, foreground=TEXT,
                        fieldbackground=CARD, rowheight=30,
                        font=FONT_BODY, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                        background=PANEL, foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", WHITE)])

        frame = tk.Frame(parent, bg=BG)
        tree  = ttk.Treeview(frame, columns=columns, show="headings",
                              style="Custom.Treeview")
        vsb   = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for i, col in enumerate(columns):
            w = col_widths[i] if col_widths else 120
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")

        return frame, tree

    # ── OVERVIEW ─────────────────────────────────────────────
    def _build_overview(self):
        p = self.pages["overview"]
        self._page_header(p, "Overview", "System summary")

        self.stat_cards_frame = tk.Frame(p, bg=BG)
        self.stat_cards_frame.pack(fill="x", padx=28, pady=10)

        self.stat_vars = {k: tk.StringVar(value="—") for k in
                         ["total", "approved", "blocked", "alerts", "rate", "amount"]}
        card_defs = [
            ("Total Transactions", "total",    ACCENT),
            ("Approved",           "approved", SUCCESS),
            ("Blocked / Fraud",    "blocked",  DANGER),
            ("Fraud Alerts",       "alerts",   WARNING),
            ("Fraud Rate",         "rate",     DANGER),
            ("Flagged Amount",     "amount",   WARNING),
        ]
        for i, (lbl, key, color) in enumerate(card_defs):
            f = tk.Frame(self.stat_cards_frame, bg=CARD, padx=20, pady=14)
            f.grid(row=0, column=i, padx=6, pady=4, sticky="ew")
            self.stat_cards_frame.columnconfigure(i, weight=1)
            tk.Label(f, textvariable=self.stat_vars[key],
                     font=("Segoe UI", 20, "bold"), bg=CARD, fg=color).pack(anchor="w")
            tk.Label(f, text=lbl, font=FONT_SMALL, bg=CARD, fg=MUTED).pack(anchor="w")

        tk.Label(p, text="Recent Fraud Alerts", font=FONT_H2,
                 bg=BG, fg=TEXT).pack(anchor="w", padx=28, pady=(14, 4))

        cols   = ["Alert ID", "User", "Amount", "Rules Triggered", "Score", "Level", "Time"]
        widths = [70, 140, 110, 230, 60, 70, 170]
        tf, self.overview_tree = self._make_table(p, cols, widths)
        tf.pack(fill="both", expand=True, padx=28, pady=(0, 8))

        tk.Button(p, text="  Refresh", font=FONT_BODY, bg=ACCENT, fg=WHITE,
                  bd=0, padx=14, pady=6, cursor="hand2",
                  command=self.refresh_overview).pack(anchor="e", padx=28, pady=(0, 12))

    def refresh_overview(self):
        self.status_var.set("Loading...")
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT COUNT(*) AS c FROM transactions")
            total = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) AS c FROM transactions WHERE status='blocked'")
            blocked = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) AS c FROM transactions WHERE status='approved'")
            approved = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) AS c FROM fraud_alerts")
            alerts = cursor.fetchone()["c"]
            cursor.execute("""
                SELECT COALESCE(SUM(t.amount),0) AS s
                FROM transactions t JOIN fraud_alerts fa ON t.txn_id=fa.txn_id
            """)
            amount = cursor.fetchone()["s"]
            close_connection(conn, cursor)

            rate = f"{(blocked/total*100):.1f}%" if total else "0%"
            self.stat_vars["total"].set(total)
            self.stat_vars["approved"].set(approved)
            self.stat_vars["blocked"].set(blocked)
            self.stat_vars["alerts"].set(alerts)
            self.stat_vars["rate"].set(rate)
            self.stat_vars["amount"].set(f"Rs.{float(amount):,.0f}")

            for row in self.overview_tree.get_children():
                self.overview_tree.delete(row)
            for a in get_all_alerts()[:20]:
                tag = "high" if a["risk_score"] >= 70 else ("med" if a["risk_score"] >= 40 else "low")
                self.overview_tree.insert("", "end", values=(
                    a["alert_id"], a["user_name"],
                    f"Rs.{float(a['amount']):,.2f}",
                    a["rule_triggered"], a["risk_score"],
                    a["risk_level"], str(a["flagged_at"])
                ), tags=(tag,))
            self.overview_tree.tag_configure("high", foreground=DANGER)
            self.overview_tree.tag_configure("med",  foreground=WARNING)
            self.overview_tree.tag_configure("low",  foreground=SUCCESS)
            self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set(f"Error: {e}")

    # ── ALERTS ───────────────────────────────────────────────
    def _build_alerts_page(self):
        p = self.pages["alerts"]
        self._page_header(p, "Fraud Alerts", "All flagged transactions")
        cols   = ["Alert ID", "User", "Country", "Amount", "Merchant",
                  "Location", "Rules", "Score", "Level", "Reviewed"]
        widths = [70, 120, 80, 110, 130, 130, 180, 60, 70, 75]
        tf, self.alerts_tree = self._make_table(p, cols, widths)
        tf.pack(fill="both", expand=True, padx=28, pady=(8, 4))

        row = tk.Frame(p, bg=BG)
        row.pack(fill="x", padx=28, pady=8)
        tk.Button(row, text="  Refresh", font=FONT_BODY, bg=ACCENT, fg=WHITE,
                  bd=0, padx=14, pady=6, cursor="hand2",
                  command=self.refresh_alerts).pack(side="left", padx=(0, 8))
        tk.Button(row, text="  Mark Reviewed", font=FONT_BODY, bg=SUCCESS, fg=WHITE,
                  bd=0, padx=14, pady=6, cursor="hand2",
                  command=self._mark_reviewed).pack(side="left")

    def refresh_alerts(self):
        for row in self.alerts_tree.get_children():
            self.alerts_tree.delete(row)
        for a in get_all_alerts():
            tag = "high" if a["risk_score"] >= 70 else ("med" if a["risk_score"] >= 40 else "low")
            self.alerts_tree.insert("", "end", values=(
                a["alert_id"], a["user_name"], a["user_country"],
                f"Rs.{float(a['amount']):,.2f}", a["merchant"],
                a["location"], a["rule_triggered"],
                a["risk_score"], a["risk_level"],
                "Yes" if a["reviewed"] else "No"
            ), tags=(tag,))
        self.alerts_tree.tag_configure("high", foreground=DANGER)
        self.alerts_tree.tag_configure("med",  foreground=WARNING)
        self.alerts_tree.tag_configure("low",  foreground=SUCCESS)

    def _mark_reviewed(self):
        selected = self.alerts_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an alert first.")
            return
        alert_id = self.alerts_tree.item(selected[0])["values"][0]
        mark_alert_reviewed(alert_id)
        self.refresh_alerts()
        messagebox.showinfo("Done", f"Alert {alert_id} marked as reviewed.")

    # ── HIGH RISK ────────────────────────────────────────────
    def _build_high_risk_page(self):
        p = self.pages["high_risk"]
        self._page_header(p, "High Risk Alerts", "Risk score >= 70")
        cols   = ["Alert ID", "User", "Amount", "Merchant", "Location", "Rules", "Score", "Time"]
        widths = [70, 130, 110, 150, 150, 200, 60, 160]
        tf, self.hr_tree = self._make_table(p, cols, widths)
        tf.pack(fill="both", expand=True, padx=28, pady=(8, 8))
        tk.Button(p, text="  Refresh", font=FONT_BODY, bg=DANGER, fg=WHITE,
                  bd=0, padx=14, pady=6, cursor="hand2",
                  command=self.refresh_high_risk).pack(anchor="e", padx=28, pady=(0, 12))

    def refresh_high_risk(self):
        for row in self.hr_tree.get_children():
            self.hr_tree.delete(row)
        for a in get_high_risk_alerts(70):
            self.hr_tree.insert("", "end", values=(
                a["alert_id"], a["user_name"],
                f"Rs.{float(a['amount']):,.2f}", a["merchant"],
                a["location"], a["rule_triggered"],
                a["risk_score"], str(a["flagged_at"])
            ), tags=("high",))
        self.hr_tree.tag_configure("high", foreground=DANGER)

    # ── RULES ────────────────────────────────────────────────
    def _build_rules_page(self):
        p = self.pages["rules"]
        self._page_header(p, "Rule Statistics", "How often each rule fires")
        cols   = ["Rule Name", "Times Triggered", "Avg Risk Score", "Max Risk Score"]
        widths = [220, 160, 160, 160]
        tf, self.rules_tree = self._make_table(p, cols, widths)
        tf.pack(fill="both", expand=True, padx=28, pady=(8, 8))
        tk.Button(p, text="  Refresh", font=FONT_BODY, bg=ACCENT, fg=WHITE,
                  bd=0, padx=14, pady=6, cursor="hand2",
                  command=self.refresh_rules).pack(anchor="e", padx=28, pady=(0, 12))

    def refresh_rules(self):
        for row in self.rules_tree.get_children():
            self.rules_tree.delete(row)
        for r in get_rule_summary():
            self.rules_tree.insert("", "end", values=(
                r["rule_triggered"], r["times_triggered"],
                f"{float(r['avg_risk_score']):.1f}", r["max_risk_score"]
            ))

    # ── USERS ────────────────────────────────────────────────
    def _build_users_page(self):
        p = self.pages["users"]
        self._page_header(p, "User Fraud Summary", "Most flagged users")
        cols   = ["User ID", "Name", "Email", "Total Flags", "Max Score", "Total Flagged"]
        widths = [70, 150, 210, 110, 110, 160]
        tf, self.users_tree = self._make_table(p, cols, widths)
        tf.pack(fill="both", expand=True, padx=28, pady=(8, 8))
        tk.Button(p, text="  Refresh", font=FONT_BODY, bg=ACCENT, fg=WHITE,
                  bd=0, padx=14, pady=6, cursor="hand2",
                  command=self.refresh_users).pack(anchor="e", padx=28, pady=(0, 12))

    def refresh_users(self):
        for row in self.users_tree.get_children():
            self.users_tree.delete(row)
        for u in get_user_fraud_summary():
            self.users_tree.insert("", "end", values=(
                u["user_id"], u["name"], u["email"],
                u["total_flags"], u["max_risk_score"],
                f"Rs.{float(u['total_flagged_amount']):,.2f}"
            ))

    # ── AUDIT LOG ────────────────────────────────────────────
    def _build_audit_page(self):
        p = self.pages["audit"]
        self._page_header(p, "Audit Log", "Every system action recorded")
        cols   = ["Log ID", "Action", "Table", "Record ID", "Details", "Time"]
        widths = [70, 150, 120, 90, 300, 160]
        tf, self.audit_tree = self._make_table(p, cols, widths)
        tf.pack(fill="both", expand=True, padx=28, pady=(8, 8))
        tk.Button(p, text="  Refresh", font=FONT_BODY, bg=ACCENT, fg=WHITE,
                  bd=0, padx=14, pady=6, cursor="hand2",
                  command=self.refresh_audit).pack(anchor="e", padx=28, pady=(0, 12))

    def refresh_audit(self):
        for row in self.audit_tree.get_children():
            self.audit_tree.delete(row)
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM audit_log ORDER BY log_time DESC LIMIT 60")
            for log in cursor.fetchall():
                tag = "fraud" if "FRAUD" in str(log["action"]) else "ok"
                self.audit_tree.insert("", "end", values=(
                    log["log_id"], log["action"],
                    log["table_affected"] or "—",
                    log["record_id"] or "—",
                    (log["details"] or "")[:90],
                    str(log["log_time"])
                ), tags=(tag,))
            self.audit_tree.tag_configure("fraud", foreground=DANGER)
            self.audit_tree.tag_configure("ok",    foreground=SUCCESS)
            close_connection(conn, cursor)
        except Exception as e:
            self.status_var.set(f"Audit error: {e}")

    # ── SIMULATE ─────────────────────────────────────────────
    def _build_simulate_page(self):
        p = self.pages["simulate"]
        self._page_header(p, "Simulate", "Test fraud detection rules")

        grid = tk.Frame(p, bg=BG)
        grid.pack(padx=28, pady=10, fill="x")

        sims = [
            ("Normal Transactions (15)",   simulate_normal_transactions, SUCCESS),
            ("High Amount  Rs.85,000",     simulate_high_amount,         WARNING),
            ("Velocity Attack (5 rapid)",  simulate_velocity,            WARNING),
            ("Location Mismatch (Foreign)",simulate_location_mismatch,   DANGER),
            ("Rapid Repeat (same amount)", simulate_rapid_repeat,        DANGER),
            ("Multi-Rule (max risk)",      simulate_multi_rule,          DANGER),
        ]
        for i, (label, fn, color) in enumerate(sims):
            row, col = divmod(i, 2)
            f = tk.Frame(grid, bg=CARD, padx=20, pady=14)
            f.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
            grid.columnconfigure(col, weight=1)
            tk.Label(f, text=label, font=FONT_H2, bg=CARD, fg=TEXT).pack(anchor="w")
            tk.Button(f, text="Run", font=FONT_BODY, bg=color,
                      fg=WHITE, bd=0, padx=12, pady=5, cursor="hand2",
                      command=lambda fn=fn: self._run_sim(fn)).pack(anchor="w", pady=(8, 0))

        tk.Label(p, text="Output", font=FONT_H2, bg=BG, fg=TEXT).pack(
            anchor="w", padx=28, pady=(10, 4))
        self.sim_log = tk.Text(p, height=9, bg=CARD, fg=TEXT, font=FONT_MONO,
                               bd=0, padx=10, pady=8, state="disabled")
        self.sim_log.pack(fill="x", padx=28, pady=(0, 12))

    def _run_sim(self, fn):
        def task():
            import io, sys
            buf = io.StringIO()
            sys.stdout = buf
            try:
                fn()
            except Exception as e:
                print(f"Error: {e}")
            sys.stdout = sys.__stdout__
            output = buf.getvalue()
            self.sim_log.configure(state="normal")
            self.sim_log.insert("end", output + "\n")
            self.sim_log.see("end")
            self.sim_log.configure(state="disabled")
            self.status_var.set("Simulation done! Go to Overview and click Refresh.")
        threading.Thread(target=task, daemon=True).start()

    # ── ADD TRANSACTION ──────────────────────────────────────
    def _build_insert_page(self):
        p = self.pages["insert"]
        self._page_header(p, "Add Transaction", "Insert a transaction manually")

        form = tk.Frame(p, bg=CARD, padx=30, pady=24)
        form.pack(padx=28, pady=16, fill="x")

        fields = [
            ("User ID (1 to 10):", "user_id",  "1"),
            ("Amount (Rs.):",       "amount",   "5000"),
            ("Merchant:",          "merchant", "Amazon India"),
            ("Location:",          "location", "Mumbai, India"),
            ("IP Address:",        "ip",       "192.168.1.1"),
        ]
        self.form_vars = {}
        for i, (label, key, default) in enumerate(fields):
            tk.Label(form, text=label, font=FONT_BODY, bg=CARD,
                     fg=MUTED, anchor="w").grid(row=i, column=0, sticky="w",
                                                pady=7, padx=(0, 16))
            var   = tk.StringVar(value=default)
            entry = tk.Entry(form, textvariable=var, font=FONT_BODY,
                             bg=BG, fg=TEXT, bd=0, insertbackground=TEXT,
                             relief="flat", width=38)
            entry.grid(row=i, column=1, sticky="ew", pady=7, ipady=7, padx=4)
            form.columnconfigure(1, weight=1)
            self.form_vars[key] = var

        tk.Button(form, text="   Insert Transaction   ",
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg=WHITE, bd=0, padx=20, pady=10, cursor="hand2",
                  command=self._insert_txn).grid(
                      row=len(fields), column=1, sticky="w", pady=(18, 0))

        self.insert_result = tk.Label(p, text="", font=("Segoe UI", 12, "bold"),
                                      bg=BG, fg=TEXT)
        self.insert_result.pack(padx=28, pady=12, anchor="w")

    def _insert_txn(self):
        try:
            user_id  = int(self.form_vars["user_id"].get())
            amount   = float(self.form_vars["amount"].get())
            merchant = self.form_vars["merchant"].get()
            location = self.form_vars["location"].get()
            ip       = self.form_vars["ip"].get()

            txn_id = insert_transaction(user_id, amount, merchant, location, ip)
            if txn_id:
                result = get_transaction_status(txn_id)
                status = result["status"].upper() if result else "UNKNOWN"
                if status == "BLOCKED":
                    self.insert_result.configure(
                        text=f"BLOCKED  txn_id={txn_id} | Flagged by fraud detection!",
                        fg=DANGER)
                else:
                    self.insert_result.configure(
                        text=f"APPROVED  txn_id={txn_id} | Transaction successful.",
                        fg=SUCCESS)
        except ValueError:
            messagebox.showerror("Invalid Input", "Check User ID and Amount fields.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = FraudDashboard()
    app.mainloop()
