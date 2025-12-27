# Credit Card Promotion Targeting - Use Case & Architecture

## 1. Scenario: Intelligent Credit Card Promotion Targeting

**Business Context:**
A commercial bank wants to launch a targeted marketing campaign for a new "Premium Travel Credit Card". Instead of sending generic emails to all customers, the bank wants to identify customers who:
1.  Have high transaction volumes on existing debit/credit cards.
2.  Frequently visit travel-related websites or the travel section of the bank's mobile app.
3.  Have a stable balance history but don't currently hold a premium card.

**The Challenge:**
-   **Transaction Data**: Massive volume, stored in legacy formats or raw logs.
-   **Web/App Logs**: Unstructured clickstream data, very high velocity and volume.
-   **Customer Data**: Structured, relational data stored in a core banking system (PostgreSQL).

**The Solution:**
Use a **Hadoop/Spark/Hive** ecosystem to ingest and process the massive unstructured/semi-structured logs, and join them with the structured customer data from **PostgreSQL** to generate a "Propensity Score" for each customer.

---

## 2. Technology Stack

| Component | Technology | Role in Architecture |
| :--- | :--- | :--- |
| **Raw Storage** | **Hadoop HDFS** | Stores massive historical transaction logs (CSV/Avro) and web clickstream logs (JSON/Text). Cost-effective for petabytes of data. |
| **Data Warehousing** | **Apache Hive** | Provides a SQL-like interface over HDFS. Used to define schemas on the raw logs (e.g., mapping raw web logs to a `web_activity` table). |
| **Processing Engine** | **Apache Spark** | The compute engine. Reads data from Hive (logs) and PostgreSQL (customer profiles), performs joins, aggregations, and runs the propensity machine learning model. |
| **Operational DB** | **PostgreSQL** | 1. **Source**: Stores Customer Master Data (Profiles, Demographics).<br>2. **Sink**: Stores the final "Target List" of eligible customers for the Campaign Management System to consume. |

---

## 3. Data Flow & Pipeline Design

### Step 1: Data Ingestion (How data is coming)
1.  **Transaction Logs**: End-of-day batch files from the Core Banking System are pushed to an HDFS landing zone (`/data/raw/transactions/`).
2.  **Clickstream Data**: Web servers and Mobile App backends stream user activity logs via Flume or Kafka into HDFS (`/data/raw/weblogs/`).
3.  **Customer Data**: Resides in PostgreSQL (`customers` table).

### Step 2: Data Preparation (Hive)
-   **Hive External Tables** are created on top of the HDFS directories to structure the raw data.
    -   `hive_db.raw_transactions`
    -   `hive_db.raw_weblogs`

### Step 3: Processing & Analytics (Spark)
1.  **Read**: Spark reads `hive_db.raw_transactions` and `hive_db.raw_weblogs`.
2.  **Read**: Spark reads `public.customers` from PostgreSQL via JDBC.
3.  **Transform**:
    -   Aggregate transactions to calculate `monthly_spend_avg`.
    -   Filter web logs for `category = 'travel'`.
4.  **Join**: Join aggregated metrics with Customer Profile.
5.  **Logic/ML**: Apply rules (e.g., `spend > $2000` AND `travel_visits > 5`) or run a Propensity Model.
6.  **Write**: Save the resulting `customer_id` and `propensity_score` back to a PostgreSQL table `public.promo_eligibility`.

### Step 4: Activation
-   The Marketing Team's dashboard queries `public.promo_eligibility` in PostgreSQL to send out emails/SMS.

---

## 4. Data Schema Definitions

### PostgreSQL (Source & Sink)
```sql
-- Source: Customer Master
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    credit_score INT,
    current_balance DECIMAL(10, 2)
);

-- Sink: Promotion Targets
CREATE TABLE promo_eligibility (
    customer_id INT,
    promo_code VARCHAR(50),
    propensity_score FLOAT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

### Hive (HDFS Layer)
```sql
-- Raw Transactions
CREATE EXTERNAL TABLE raw_transactions (
    trans_id STRING,
    customer_id INT,
    amount DOUBLE,
    category STRING,
    trans_date STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
LOCATION '/data/raw/transactions';

-- Web Logs
CREATE EXTERNAL TABLE raw_weblogs (
    log_id STRING,
    customer_id INT,
    url_visited STRING,
    timestamp STRING
)
STORED AS JSONFILE
LOCATION '/data/raw/weblogs';
```
