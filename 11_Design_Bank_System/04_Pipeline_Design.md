# Pipeline Design (Delta Live Tables)

This document details the implementation of the data pipelines using **Delta Live Tables (DLT)**. DLT allows us to define the flow of data declaratively, handling dependencies, checkpoints, and retries automatically.

## Pipeline: Core Banking Transactions

### 1. Ingestion (Bronze)
Ingest raw JSON logs from Kafka (Payment Gateway) and Mainframe dumps (CDC) using Auto Loader.

```python
import dlt
from pyspark.sql.functions import *

# Bronze: Raw Ingestion from Kafka / Cloud Storage
@dlt.table(
    comment="Raw transaction logs from Payment Gateway",
    table_properties={"quality": "bronze"}
)
def bronze_transactions_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load("/mnt/dbs/source/transactions/")
    )
```

### 2. Transformation & Cleaning (Silver)
Clean data, enforce schema, and join with reference data.

```python
# Silver: Cleaned Transactions
@dlt.table(
    comment="Cleaned and standardized transactions",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_amount", "amount IS NOT NULL")
@dlt.expect("positive_amount", "amount > 0")
def silver_transactions():
    return (
        dlt.read_stream("bronze_transactions_raw")
        .select(
            col("txn_id"),
            col("account_id"),
            to_timestamp(col("timestamp")).alias("txn_timestamp"),
            col("amount").cast("decimal(18,2)"),
            col("currency"),
            col("merchant_code"),
            col("channel") # Mobile, Web, ATM
        )
        .withWatermark("txn_timestamp", "1 hour")
    )
```

### 3. Aggregation & Business Logic (Gold)
Create aggregated views for reporting and dashboards.

#### Use Case: Daily Branch Performance
```python
@dlt.table(
    comment="Daily transaction volume by branch",
    table_properties={"quality": "gold"}
)
def gold_branch_daily_stats():
    return (
        dlt.read("silver_transactions")
        .join(dlt.read("silver_accounts"), "account_id")
        .groupBy("branch_id", window("txn_timestamp", "1 day"))
        .agg(
            sum("amount").alias("total_volume"),
            count("txn_id").alias("txn_count")
        )
    )
```

#### Use Case: Fraud Detection Features (Real-Time)
```python
@dlt.table(
    comment="Features for Fraud ML Model",
    table_properties={"quality": "gold"}
)
def gold_fraud_features():
    return (
        dlt.read_stream("silver_transactions")
        .groupBy("account_id", window("txn_timestamp", "10 minutes"))
        .agg(
            count("txn_id").alias("velocity_10m"),
            sum("amount").alias("volume_10m"),
            collect_set("merchant_code").alias("distinct_merchants")
        )
    )
```
