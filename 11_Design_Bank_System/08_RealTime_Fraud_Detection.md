# Real-Time Analysis Scenario: Fraud Detection

This notebook demonstrates a real-time fraud detection pipeline. It detects **"Velocity Fraud"** (high frequency of transactions in a short window) and **"Large Amount"** anomalies.

## Scenario
*   **Input:** Stream of transaction events from Kafka (simulated).
*   **Logic:** 
    1.  Filter transactions > $10,000 (Rule-based).
    2.  Calculate rolling count of transactions per account in the last 5 minutes.
    3.  Flag if count > 5 (Velocity Rule).
*   **Output:** Alert stream to a "Fraud Alerts" Delta table and a notification topic.

## 1. Setup & Configuration

```python
# Notebook Configuration
import dlt
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Define Schema for Incoming Data
txn_schema = StructType([
    StructField("txn_id", StringType(), True),
    StructField("account_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("merchant", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("location", StringType(), True)
])

# Path Config (Injected via Widgets or Config File)
INPUT_PATH = "/mnt/dbs_dev/bronze/transactions_stream/"
OUTPUT_PATH = "/mnt/dbs_dev/gold/fraud_alerts/"
CHECKPOINT_PATH = "/mnt/dbs_dev/checkpoints/fraud_pipeline/"
```

## 2. Bronze Layer: Ingest Stream

```python
@dlt.table(
    comment="Raw streaming transactions",
    table_properties={"quality": "bronze"}
)
def bronze_transactions():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .schema(txn_schema)
        .load(INPUT_PATH)
    )
```

## 3. Silver Layer: Feature Engineering (Windowing)

Here we calculate the velocity features in real-time.

```python
@dlt.table(
    comment="Transactions with velocity features",
    table_properties={"quality": "silver"}
)
def silver_features():
    # Read from Bronze
    stream_df = dlt.read_stream("bronze_transactions")
    
    # Define Window: 5 minutes sliding every 1 minute
    window_spec = window("timestamp", "5 minutes", "1 minute")
    
    return (
        stream_df.withWatermark("timestamp", "10 minutes")
        .groupBy(
            col("account_id"),
            window_spec
        )
        .agg(
            count("txn_id").alias("txn_count_5m"),
            sum("amount").alias("total_amount_5m"),
            collect_list("merchant").alias("merchant_list")
        )
        .select(
            col("account_id"),
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("txn_count_5m"),
            col("total_amount_5m"),
            col("merchant_list")
        )
    )
```

## 4. Gold Layer: Fraud Alerts (Business Logic)

Join the features back with the raw stream (or evaluate on the aggregated stream) to generate alerts.

```python
@dlt.table(
    comment="High priority fraud alerts",
    table_properties={"quality": "gold"}
)
def gold_fraud_alerts():
    features = dlt.read_stream("silver_features")
    
    # Fraud Rules
    # 1. Velocity: More than 5 transactions in 5 minutes
    # 2. High Value: Total amount > 50,000 in 5 minutes
    
    return (
        features.filter(
            (col("txn_count_5m") > 5) | 
            (col("total_amount_5m") > 50000)
        )
        .withColumn("alert_reason", 
            when(col("txn_count_5m") > 5, "High Velocity")
            .otherwise("High Cumulative Value")
        )
        .withColumn("alert_timestamp", current_timestamp())
        .select(
            "alert_timestamp",
            "account_id",
            "alert_reason",
            "txn_count_5m",
            "total_amount_5m",
            "merchant_list"
        )
    )
```

## 5. Output Action (Send to Notification System)

While DLT handles the table updates, we can use `foreachBatch` for external actions (e.g., sending to PagerDuty/SNS).

*Note: This part typically runs in a separate streaming job reading from the Gold table.*

```python
def send_notification(df, epoch_id):
    # Convert to Pandas for API call (only for small alert batches)
    alerts = df.collect()
    for alert in alerts:
        print(f"🚨 FRAUD ALERT: Account {alert['account_id']} - {alert['alert_reason']}")
        # requests.post("https://api.pagerduty.com/...", json=alert.asDict())

# Read from Gold Table Stream
spark.readStream.table("dbs_dev.risk.gold_fraud_alerts") \
    .writeStream \
    .foreachBatch(send_notification) \
    .start()
```
