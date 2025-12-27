import csv
import json
import random
import os
import datetime
import uuid

# Configuration
NUM_CUSTOMERS = 100
NUM_TRANSACTIONS = 5000
NUM_WEBLOGS = 2000
OUTPUT_DIR = "generated_data"

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- 1. Generate Customer Data (PostgreSQL) ---
print("Generating Customer Data...")
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    customer = {
        "customer_id": i,
        "name": f"Customer_{i}",
        "email": f"customer_{i}@example.com",
        "credit_score": random.randint(300, 850),
        "current_balance": round(random.uniform(100.0, 50000.0), 2)
    }
    customers.append(customer)

# Write to CSV (Simulating Postgres Export or Load File)
with open(f"{OUTPUT_DIR}/customers.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["customer_id", "name", "email", "credit_score", "current_balance"])
    writer.writeheader()
    writer.writerows(customers)


# --- 2. Generate Transaction Data (Hadoop/Hive - CSV) ---
print("Generating Transaction Data...")
categories = ["Groceries", "Travel", "Dining", "Utilities", "Entertainment", "Retail"]
transactions = []

start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2023, 12, 31)
delta = end_date - start_date

for _ in range(NUM_TRANSACTIONS):
    random_days = random.randrange(delta.days)
    trans_date = start_date + datetime.timedelta(days=random_days)
    
    # Skew logic: High spenders for Travel category
    category = random.choice(categories)
    amount = round(random.uniform(5.0, 500.0), 2)
    if category == "Travel":
        amount = round(random.uniform(100.0, 2000.0), 2)

    transaction = {
        "trans_id": str(uuid.uuid4()),
        "customer_id": random.randint(1, NUM_CUSTOMERS),
        "amount": amount,
        "category": category,
        "trans_date": trans_date.isoformat()
    }
    transactions.append(transaction)

# Write to CSV (Simulating HDFS File)
with open(f"{OUTPUT_DIR}/transactions.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["trans_id", "customer_id", "amount", "category", "trans_date"])
    # Hive often works well without headers or with them, we'll include header for clarity but in prod usually removed
    writer.writeheader() 
    writer.writerows(transactions)


# --- 3. Generate Web Logs (Hadoop/Hive - JSON) ---
print("Generating Web Logs...")
urls = [
    "/home", "/login", "/account/summary", 
    "/travel-rewards", "/flights-booking", "/hotels", # Travel related
    "/loans/personal", "/credit-cards/apply"
]

weblogs = []
for _ in range(NUM_WEBLOGS):
    random_days = random.randrange(delta.days)
    log_date = start_date + datetime.timedelta(days=random_days)
    
    log = {
        "log_id": str(uuid.uuid4()),
        "customer_id": random.randint(1, NUM_CUSTOMERS),
        "url_visited": random.choice(urls),
        "timestamp": log_date.isoformat() + "T" + datetime.time(random.randint(0, 23), random.randint(0, 59)).isoformat(),
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "session_id": str(uuid.uuid4())
    }
    weblogs.append(log)

# Write to JSON (Simulating HDFS File)
with open(f"{OUTPUT_DIR}/weblogs.json", "w") as f:
    for log in weblogs:
        f.write(json.dumps(log) + "\n") # NDJSON format is common for Spark/Hive

print(f"Data generation complete. Check the '{OUTPUT_DIR}' folder.")
