# ============================================================
# FILE: python/simulate_data.py
# ============================================================

import random
import time
from transaction_service import insert_transaction, get_transaction_status

MERCHANTS = [
    "Amazon India", "Flipkart", "Swiggy", "Zomato", "Myntra",
    "BigBasket", "Nykaa", "BookMyShow", "MakeMyTrip", "Paytm Mall"
]
INDIA_CITIES = [
    "Mumbai, India", "Delhi, India", "Bengaluru, India",
    "Hyderabad, India", "Chennai, India", "Pune, India"
]

def simulate_normal_transactions(count=15):
    print("\n[SIM] Inserting normal transactions...")
    for _ in range(count):
        user_id  = random.randint(1, 10)
        amount   = round(random.uniform(100, 8000), 2)
        merchant = random.choice(MERCHANTS)
        location = random.choice(INDIA_CITIES)
        insert_transaction(user_id, amount, merchant, location)
        time.sleep(0.05)

def simulate_high_amount(user_id=1):
    print("\n[SIM] Testing HIGH_AMOUNT rule...")
    txn_id = insert_transaction(user_id, 85000.00, "Luxury Electronics", "Mumbai, India")
    _print_result(txn_id)

def simulate_velocity(user_id=2):
    print("\n[SIM] Testing VELOCITY rule (5 rapid txns)...")
    txn_id = None
    for i in range(5):
        txn_id = insert_transaction(
            user_id, round(random.uniform(500, 2000), 2),
            random.choice(MERCHANTS), "Delhi, India"
        )
        time.sleep(0.1)
    _print_result(txn_id)

def simulate_location_mismatch(user_id=3):
    print("\n[SIM] Testing LOCATION_MISMATCH rule...")
    txn_id = insert_transaction(user_id, 12000.00, "Foreign Store", "New York, USA")
    _print_result(txn_id)

def simulate_rapid_repeat(user_id=4):
    print("\n[SIM] Testing RAPID_REPEAT rule...")
    for _ in range(2):
        txn_id = insert_transaction(user_id, 3333.00, "Online Store", "Bengaluru, India")
        time.sleep(0.3)
    _print_result(txn_id)

def simulate_multi_rule(user_id=5):
    print("\n[SIM] Testing MULTI-RULE transaction...")
    txn_id = insert_transaction(user_id, 99999.00, "International Luxury", "London, UK")
    _print_result(txn_id)

def _print_result(txn_id):
    if txn_id:
        result = get_transaction_status(txn_id)
        if result:
            status = result["status"].upper()
            icon   = "BLOCKED" if status == "BLOCKED" else "APPROVED"
            print(f"  --> txn_id={txn_id}  Rs.{result['amount']}  STATUS: {icon}")

if __name__ == "__main__":
    print("=" * 50)
    print("   FRAUD DETECTION — SIMULATION")
    print("=" * 50)
    simulate_normal_transactions(15)
    simulate_high_amount(user_id=1)
    simulate_velocity(user_id=2)
    simulate_location_mismatch(user_id=3)
    simulate_rapid_repeat(user_id=4)
    simulate_multi_rule(user_id=5)
    print("\n[DONE] Simulation complete. Now run: python gui_dashboard.py\n")
