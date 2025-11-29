# Sample Data Generators

Use these Python scripts to generate realistic dummy data for testing the pipelines. You can run these in a Databricks Notebook to populate the `bronze` landing zones.

## 1. Transaction Generator (JSON)

Generates a stream of JSON files simulating credit card transactions.

```python
import random
import json
import time
from datetime import datetime, timedelta
import uuid

# Configuration
OUTPUT_PATH = "/dbfs/mnt/dbs_dev/bronze/transactions_stream/"
RECORDS_PER_BATCH = 100
BATCH_INTERVAL_SEC = 5

# Reference Data
MERCHANTS = ["Amazon", "Grab", "Shopee", "FairPrice", "Starbucks", "MRT", "Lazada"]
LOCATIONS = ["Singapore", "Johor Bahru", "London", "Tokyo", "New York"]
ACCOUNTS = [f"ACC-{i:05d}" for i in range(1, 51)] # 50 Test Accounts

def generate_transaction():
    return {
        "txn_id": str(uuid.uuid4()),
        "account_id": random.choice(ACCOUNTS),
        "amount": round(random.uniform(5.0, 5000.0), 2),
        "merchant": random.choice(MERCHANTS),
        "timestamp": datetime.now().isoformat(),
        "location": random.choice(LOCATIONS),
        "currency": "SGD"
    }

def generate_fraud_spike(account_id):
    """Generates a burst of transactions for a specific account to test fraud logic"""
    burst = []
    for _ in range(10):
        txn = generate_transaction()
        txn['account_id'] = account_id
        txn['amount'] = round(random.uniform(1000.0, 10000.0), 2) # High value
        burst.append(txn)
    return burst

# Main Loop
print(f"Starting Data Generator writing to {OUTPUT_PATH}...")
try:
    while True:
        batch_data = [generate_transaction() for _ in range(RECORDS_PER_BATCH)]
        
        # Inject Fraud Scenario (Randomly every ~10 batches)
        if random.random() < 0.1:
            victim = random.choice(ACCOUNTS)
            print(f"⚠️ Injecting Fraud Spike for {victim}")
            batch_data.extend(generate_fraud_spike(victim))
            
        # Write to JSON file
        file_name = f"txn_batch_{int(time.time())}.json"
        with open(f"{OUTPUT_PATH}/{file_name}", "w") as f:
            for record in batch_data:
                f.write(json.dumps(record) + "\n")
                
        print(f"Written {len(batch_data)} records to {file_name}")
        time.sleep(BATCH_INTERVAL_SEC)
        
except KeyboardInterrupt:
    print("Generator Stopped.")
```

## 2. Customer Reference Data Generator (CSV)

Generates the static customer data for the Silver layer.

```python
import csv
from faker import Faker
fake = Faker()

OUTPUT_PATH = "/dbfs/mnt/dbs_dev/bronze/customers_load/"
NUM_CUSTOMERS = 1000

def generate_customers():
    file_name = f"{OUTPUT_PATH}/customers_snapshot.csv"
    
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = ['customer_id', 'nric_fin', 'full_name', 'dob', 'risk_rating', 'kyc_status', 'segment']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i in range(NUM_CUSTOMERS):
            writer.writerow({
                'customer_id': str(uuid.uuid4()),
                'nric_fin': f"S{random.randint(1000000, 9999999)}{random.choice('ABCDEF')}",
                'full_name': fake.name(),
                'dob': fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
                'risk_rating': random.randint(1, 5),
                'kyc_status': random.choice(['VERIFIED', 'PENDING', 'REJECTED']),
                'segment': random.choice(['RETAIL', 'TREASURES', 'PRIVATE'])
            })
            
    print(f"Generated {NUM_CUSTOMERS} customers at {file_name}")

# Run once
generate_customers()
```
