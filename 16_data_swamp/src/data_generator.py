"""
Data Generator Module
Generates synthetic data for customers, transactions, and web logs
"""
import csv
import json
import random
import os
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from config import config

fake = Faker()

class DataGenerator:
    """Generates synthetic banking data"""
    
    def __init__(self):
        self.num_customers = config.NUM_CUSTOMERS
        self.num_transactions = config.NUM_TRANSACTIONS
        self.num_weblogs = config.NUM_WEBLOGS
        self.raw_data_dir = config.RAW_DATA_DIR
        
        # Create directories if they don't exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.raw_data_dir, "transactions"), exist_ok=True)
        os.makedirs(os.path.join(self.raw_data_dir, "weblogs"), exist_ok=True)
    
    def generate_customers(self):
        """Generate customer data and insert into PostgreSQL"""
        print(f"Generating {self.num_customers} customers...")
        
        customers = []
        segments = ["Premium", "Standard", "Basic", "Student"]
        cities = ["Colombo", "Kandy", "Galle", "Jaffna", "Negombo", "Matara", "Kurunegala"]
        
        for i in range(1, self.num_customers + 1):
            customer = {
                "name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number()[:20],
                "credit_score": random.randint(300, 850),
                "current_balance": round(random.uniform(100.0, 100000.0), 2),
                "account_opening_date": fake.date_between(start_date="-5y", end_date="today"),
                "customer_segment": random.choice(segments),
                "city": random.choice(cities),
                "country": "Sri Lanka"
            }
            customers.append(customer)
        
        # Insert into PostgreSQL
        try:
            conn = psycopg2.connect(
                host=config.POSTGRES_HOST,
                port=config.POSTGRES_PORT,
                database=config.POSTGRES_DB,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD
            )
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("TRUNCATE TABLE customers CASCADE")
            
            # Insert customers
            insert_query = """
                INSERT INTO customers (name, email, phone, credit_score, current_balance, 
                                      account_opening_date, customer_segment, city, country)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for customer in customers:
                cursor.execute(insert_query, (
                    customer["name"], customer["email"], customer["phone"],
                    customer["credit_score"], customer["current_balance"],
                    customer["account_opening_date"], customer["customer_segment"],
                    customer["city"], customer["country"]
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✓ Successfully inserted {len(customers)} customers into PostgreSQL")
            
        except Exception as e:
            print(f"✗ Error inserting customers into PostgreSQL: {str(e)}")
            raise
    
    def generate_transactions(self):
        """Generate transaction data as CSV files"""
        print(f"Generating {self.num_transactions} transactions...")
        
        categories = ["Groceries", "Travel", "Dining", "Utilities", "Entertainment", "Retail", "Healthcare"]
        transactions = []
        
        start_date = datetime.now() - timedelta(days=365)
        
        for _ in range(self.num_transactions):
            # Random date within the last year
            random_days = random.randint(0, 365)
            trans_date = start_date + timedelta(days=random_days)
            
            category = random.choice(categories)
            
            # Travel transactions tend to be higher value
            if category == "Travel":
                amount = round(random.uniform(100.0, 3000.0), 2)
            else:
                amount = round(random.uniform(5.0, 500.0), 2)
            
            transaction = {
                "trans_id": fake.uuid4(),
                "customer_id": random.randint(1, self.num_customers),
                "amount": amount,
                "category": category,
                "trans_date": trans_date.strftime("%Y-%m-%d")
            }
            transactions.append(transaction)
        
        # Write to CSV
        output_file = os.path.join(self.raw_data_dir, "transactions", "transactions.csv")
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["trans_id", "customer_id", "amount", "category", "trans_date"])
            writer.writeheader()
            writer.writerows(transactions)
        
        print(f"✓ Generated transactions saved to {output_file}")
    
    def generate_weblogs(self):
        """Generate web log data as JSON files"""
        print(f"Generating {self.num_weblogs} web logs...")
        
        urls = [
            "/home",
            "/login",
            "/account/summary",
            "/account/transactions",
            "/travel-rewards",
            "/flights-booking",
            "/hotels",
            "/vacation-packages",
            "/loans/personal",
            "/credit-cards/apply",
            "/credit-cards/premium-travel",
            "/investment/funds",
            "/insurance/travel"
        ]
        
        weblogs = []
        start_date = datetime.now() - timedelta(days=365)
        
        for _ in range(self.num_weblogs):
            random_days = random.randint(0, 365)
            log_date = start_date + timedelta(days=random_days)
            log_time = fake.time()
            
            log = {
                "log_id": fake.uuid4(),
                "customer_id": random.randint(1, self.num_customers),
                "url_visited": random.choice(urls),
                "timestamp": f"{log_date.strftime('%Y-%m-%d')}T{log_time}",
                "user_agent": fake.user_agent(),
                "session_id": fake.uuid4()
            }
            weblogs.append(log)
        
        # Write to NDJSON (newline-delimited JSON)
        output_file = os.path.join(self.raw_data_dir, "weblogs", "weblogs.json")
        with open(output_file, "w", encoding="utf-8") as f:
            for log in weblogs:
                f.write(json.dumps(log) + "\n")
        
        print(f"✓ Generated web logs saved to {output_file}")
    
    def generate_all(self):
        """Generate all synthetic data"""
        print("\n=== Starting Data Generation ===\n")
        self.generate_customers()
        self.generate_transactions()
        self.generate_weblogs()
        print("\n=== Data Generation Complete ===\n")

if __name__ == "__main__":
    generator = DataGenerator()
    generator.generate_all()
