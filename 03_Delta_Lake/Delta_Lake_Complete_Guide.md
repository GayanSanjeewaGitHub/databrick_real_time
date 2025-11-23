# Delta Lake - Complete Guide

## Table of Contents
1. [Introduction to Delta Lake](#introduction)
2. [ACID Transactions](#acid-transactions)
3. [Creating Delta Tables](#creating-delta-tables)
4. [Reading and Writing Data](#reading-and-writing-data)
5. [Time Travel and Versioning](#time-travel)
6. [MERGE Operations (Upserts)](#merge-operations)
7. [Delete and Update Operations](#delete-update)
8. [Optimization](#optimization)
9. [Schema Evolution](#schema-evolution)
10. [Change Data Feed](#change-data-feed)
11. [Practical Examples](#practical-examples)

## Introduction to Delta Lake

Delta Lake is an open-source storage layer that brings ACID transactions to Apache Spark and big data workloads. It is the default format for all operations on Azure Databricks.

### Key Features
- **ACID Transactions**: Serializable isolation levels
- **Scalable Metadata**: Handles billions of partitions and files
- **Time Travel**: Query historical versions
- **Schema Evolution**: Safe schema changes
- **Unified Batch and Streaming**: Single source of truth
- **Audit History**: Complete data lineage
- **Updates and Deletes**: Full DML support
- **Data Quality**: Expectations and constraints

### Architecture
```
Delta Lake Architecture:
┌─────────────────────────────────────┐
│       Spark DataFrame API           │
├─────────────────────────────────────┤
│       Delta Lake Protocol          │
│  ┌──────────────┬─────────────────┐│
│  │ Transaction  │   Optimized     ││
│  │    Log       │   Parquet Files ││
│  └──────────────┴─────────────────┘│
├─────────────────────────────────────┤
│       Cloud Storage (DBFS/S3/ADLS) │
└─────────────────────────────────────┘
```

## ACID Transactions

Delta Lake provides full ACID guarantees.

### Example: Concurrent Writes
```python
from pyspark.sql.functions import col, current_timestamp
from delta.tables import DeltaTable

# Create sample data
data1 = [(1, "Alice", 50000), (2, "Bob", 60000)]
data2 = [(3, "Charlie", 55000), (4, "Diana", 65000)]

df1 = spark.createDataFrame(data1, ["id", "name", "salary"])
df2 = spark.createDataFrame(data2, ["id", "name", "salary"])

# Both writes are atomic - either complete fully or not at all
df1.write.format("delta").mode("append").save("/mnt/delta/employees")
df2.write.format("delta").mode("append").save("/mnt/delta/employees")

# Read returns consistent view
result = spark.read.format("delta").load("/mnt/delta/employees")
display(result)
```

### Transaction Isolation
```python
# Serializable isolation - readers don't block writers
# Writer 1
df_update = spark.sql("""
    SELECT id, name, salary * 1.1 as salary 
    FROM delta.`/mnt/delta/employees`
""")
df_update.write.format("delta").mode("overwrite").save("/mnt/delta/employees")

# Concurrent Reader - sees consistent snapshot
df_read = spark.read.format("delta").load("/mnt/delta/employees")
display(df_read)
```

## Creating Delta Tables

### Method 1: Using DataFrame API
```python
from pyspark.sql.types import *

# Define schema
schema = StructType([
    StructField("customer_id", IntegerType(), False),
    StructField("customer_name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("registration_date", DateType(), True),
    StructField("total_purchases", DoubleType(), True),
    StructField("region", StringType(), True)
])

# Create sample data
data = [
    (1, "John Doe", "john@example.com", "2024-01-15", 1500.50, "North"),
    (2, "Jane Smith", "jane@example.com", "2024-01-20", 2300.75, "South"),
    (3, "Bob Johnson", "bob@example.com", "2024-02-01", 890.00, "East"),
    (4, "Alice Williams", "alice@example.com", "2024-02-10", 3200.25, "West")
]

df = spark.createDataFrame(data, schema)

# Write as Delta table
df.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("region") \
    .option("overwriteSchema", "true") \
    .save("/mnt/delta/customers")

print("Delta table created successfully!")
```

### Method 2: Using SQL
```sql
-- Create Delta table using SQL
CREATE TABLE customers_sql (
    customer_id INT NOT NULL,
    customer_name STRING,
    email STRING,
    registration_date DATE,
    total_purchases DOUBLE,
    region STRING
)
USING DELTA
PARTITIONED BY (region)
LOCATION '/mnt/delta/customers_sql';

-- Insert data
INSERT INTO customers_sql VALUES
    (1, 'John Doe', 'john@example.com', '2024-01-15', 1500.50, 'North'),
    (2, 'Jane Smith', 'jane@example.com', '2024-01-20', 2300.75, 'South'),
    (3, 'Bob Johnson', 'bob@example.com', '2024-02-01', 890.00, 'East'),
    (4, 'Alice Williams', 'alice@example.com', '2024-02-10', 3200.25, 'West');
```

### Method 3: Convert Parquet to Delta
```python
# Convert existing Parquet table to Delta
from delta.tables import DeltaTable

# First, create a Parquet table
parquet_path = "/mnt/data/parquet_customers"
df.write.format("parquet").mode("overwrite").save(parquet_path)

# Convert to Delta
DeltaTable.convertToDelta(spark, f"parquet.`{parquet_path}`")

print("Parquet converted to Delta!")

# Verify
delta_df = spark.read.format("delta").load(parquet_path)
display(delta_df)
```

### Method 4: Managed Table
```python
# Create managed table (Unity Catalog)
df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("catalog_name.schema_name.customers")

# Read from managed table
managed_df = spark.read.table("catalog_name.schema_name.customers")
display(managed_df)
```

## Reading and Writing Data

### Reading Delta Tables
```python
# Method 1: Using path
df_path = spark.read.format("delta").load("/mnt/delta/customers")

# Method 2: Using table name
df_table = spark.read.table("customers")

# Method 3: Using SQL
df_sql = spark.sql("SELECT * FROM customers WHERE region = 'North'")

# Method 4: With time travel
df_version = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .load("/mnt/delta/customers")

# Method 5: As of timestamp
df_timestamp = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-01") \
    .load("/mnt/delta/customers")

display(df_path)
```

### Writing Delta Tables
```python
from pyspark.sql.functions import current_date

# Create new data
new_customers = [
    (5, "Tom Brown", "tom@example.com", current_date(), 1200.00, "North"),
    (6, "Emma Davis", "emma@example.com", current_date(), 1800.50, "South")
]

new_df = spark.createDataFrame(new_customers, schema)

# Append mode
new_df.write.format("delta") \
    .mode("append") \
    .save("/mnt/delta/customers")

# Overwrite mode
new_df.write.format("delta") \
    .mode("overwrite") \
    .save("/mnt/delta/customers")

# Overwrite specific partition
new_df.write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", "region = 'North'") \
    .save("/mnt/delta/customers")

# Error if exists
new_df.write.format("delta") \
    .mode("errorifexists") \
    .save("/mnt/delta/new_customers")

# Ignore if exists
new_df.write.format("delta") \
    .mode("ignore") \
    .save("/mnt/delta/customers")
```

## Time Travel and Versioning

Delta Lake maintains a complete history of all changes.

### Query Historical Data
```python
from delta.tables import DeltaTable

# Get Delta table history
deltaTable = DeltaTable.forPath(spark, "/mnt/delta/customers")
history_df = deltaTable.history()
display(history_df)

# Query specific version
df_v0 = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .load("/mnt/delta/customers")

df_v1 = spark.read.format("delta") \
    .option("versionAsOf", 1) \
    .load("/mnt/delta/customers")

# Query as of timestamp
from datetime import datetime, timedelta

yesterday = datetime.now() - timedelta(days=1)
df_yesterday = spark.read.format("delta") \
    .option("timestampAsOf", yesterday.strftime("%Y-%m-%d")) \
    .load("/mnt/delta/customers")

# SQL time travel
df_sql_version = spark.sql("""
    SELECT * FROM customers VERSION AS OF 0
""")

df_sql_timestamp = spark.sql("""
    SELECT * FROM customers TIMESTAMP AS OF '2024-01-01'
""")

display(df_v0)
```

### Restore Previous Version
```python
# Restore table to previous version
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "/mnt/delta/customers")

# Restore to specific version
deltaTable.restoreToVersion(0)

# Restore to specific timestamp
deltaTable.restoreToTimestamp("2024-01-01")

# Using SQL
spark.sql("""
    RESTORE TABLE customers TO VERSION AS OF 0
""")

spark.sql("""
    RESTORE TABLE customers TO TIMESTAMP AS OF '2024-01-01'
""")
```

## MERGE Operations (Upserts)

MERGE allows you to upsert (update + insert) data based on conditions.

### Basic Merge
```python
from delta.tables import DeltaTable
from pyspark.sql.functions import *

# Target Delta table
target_table = DeltaTable.forPath(spark, "/mnt/delta/customers")

# Source data (updates and new records)
updates_data = [
    (2, "Jane Smith Updated", "jane.new@example.com", "2024-01-20", 2500.75, "South"),  # Update
    (7, "New Customer", "new@example.com", current_date(), 500.00, "West")  # Insert
]

source_df = spark.createDataFrame(updates_data, schema)

# Perform merge
target_table.alias("target") \
    .merge(
        source_df.alias("source"),
        "target.customer_id = source.customer_id"
    ) \
    .whenMatchedUpdate(set={
        "customer_name": "source.customer_name",
        "email": "source.email",
        "total_purchases": "source.total_purchases"
    }) \
    .whenNotMatchedInsert(values={
        "customer_id": "source.customer_id",
        "customer_name": "source.customer_name",
        "email": "source.email",
        "registration_date": "source.registration_date",
        "total_purchases": "source.total_purchases",
        "region": "source.region"
    }) \
    .execute()

print("Merge completed!")

# Verify results
result = spark.read.format("delta").load("/mnt/delta/customers")
display(result.orderBy("customer_id"))
```

### Advanced Merge with Conditions
```python
# Merge with additional conditions
target_table.alias("target") \
    .merge(
        source_df.alias("source"),
        "target.customer_id = source.customer_id"
    ) \
    .whenMatchedUpdate(
        condition="source.total_purchases > target.total_purchases",
        set={
            "customer_name": "source.customer_name",
            "email": "source.email",
            "total_purchases": "source.total_purchases"
        }
    ) \
    .whenMatchedDelete(
        condition="source.total_purchases < 100"
    ) \
    .whenNotMatchedInsert(
        condition="source.total_purchases >= 500",
        values={
            "customer_id": "source.customer_id",
            "customer_name": "source.customer_name",
            "email": "source.email",
            "registration_date": "source.registration_date",
            "total_purchases": "source.total_purchases",
            "region": "source.region"
        }
    ) \
    .execute()
```

### Merge with SQL
```sql
-- SQL MERGE syntax
MERGE INTO customers AS target
USING updates AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
    UPDATE SET 
        target.customer_name = source.customer_name,
        target.email = source.email,
        target.total_purchases = source.total_purchases
WHEN NOT MATCHED THEN
    INSERT (customer_id, customer_name, email, registration_date, total_purchases, region)
    VALUES (source.customer_id, source.customer_name, source.email, 
            source.registration_date, source.total_purchases, source.region);
```

### SCD Type 2 with Merge
```python
# Slowly Changing Dimension Type 2
from pyspark.sql.functions import lit, current_timestamp

# Add SCD columns to schema
scd_schema = schema.add("effective_date", DateType()) \
                   .add("end_date", DateType()) \
                   .add("is_current", BooleanType())

# Existing data with SCD fields
existing_data = [
    (1, "John Doe", "john@example.com", "2024-01-15", 1500.50, "North", 
     "2024-01-15", None, True)
]

existing_df = spark.createDataFrame(existing_data, scd_schema)
existing_df.write.format("delta").mode("overwrite").save("/mnt/delta/customers_scd")

# New/changed data
new_data = [
    (1, "John Doe Updated", "john.new@example.com", "2024-01-15", 1500.50, "North")
]
new_df = spark.createDataFrame(new_data, schema) \
    .withColumn("effective_date", current_date()) \
    .withColumn("end_date", lit(None).cast(DateType())) \
    .withColumn("is_current", lit(True))

# SCD Type 2 Merge
target = DeltaTable.forPath(spark, "/mnt/delta/customers_scd")

target.alias("target") \
    .merge(
        new_df.alias("source"),
        "target.customer_id = source.customer_id AND target.is_current = true"
    ) \
    .whenMatchedUpdate(
        condition="target.customer_name <> source.customer_name OR target.email <> source.email",
        set={
            "end_date": "source.effective_date",
            "is_current": "false"
        }
    ) \
    .execute()

# Insert new versions
new_records = new_df.join(
    existing_df.filter("is_current = true"),
    "customer_id",
    "left_anti"
)
new_records.write.format("delta").mode("append").save("/mnt/delta/customers_scd")
```

## Delete and Update Operations

### DELETE Operations
```python
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "/mnt/delta/customers")

# Delete with condition
deltaTable.delete("region = 'East'")

# Delete using column reference
from pyspark.sql.functions import col
deltaTable.delete(col("total_purchases") < 1000)

# SQL DELETE
spark.sql("""
    DELETE FROM customers
    WHERE registration_date < '2024-01-01'
""")
```

### UPDATE Operations
```python
# Update with Python API
deltaTable.update(
    condition="region = 'North'",
    set={"total_purchases": "total_purchases * 1.1"}
)

# Update with expressions
from pyspark.sql.functions import expr
deltaTable.update(
    condition=expr("region IN ('North', 'South')"),
    set={
        "total_purchases": expr("total_purchases + 100"),
        "customer_name": expr("upper(customer_name)")
    }
)

# SQL UPDATE
spark.sql("""
    UPDATE customers
    SET total_purchases = total_purchases * 1.05
    WHERE region = 'West' AND total_purchases > 2000
""")
```

## Optimization

### OPTIMIZE Command
```python
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "/mnt/delta/customers")

# Basic optimize (compacts small files)
deltaTable.optimize().executeCompaction()

# Optimize with Z-ordering (for faster queries)
deltaTable.optimize().executeZOrderBy("region", "registration_date")

# SQL OPTIMIZE
spark.sql("OPTIMIZE customers")
spark.sql("OPTIMIZE customers ZORDER BY (region, registration_date)")
```

### VACUUM Command
```python
# Remove old files (data older than retention period)
deltaTable.vacuum(168)  # 168 hours = 7 days (default retention)

# Shorter retention (for testing only!)
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", False)
deltaTable.vacuum(0)  # Delete all files not in latest version

# SQL VACUUM
spark.sql("VACUUM customers RETAIN 168 HOURS")
```

### Auto Optimize
```python
# Enable auto-optimize at write time
df.write.format("delta") \
    .mode("append") \
    .option("optimizeWrite", "true") \
    .option("autoCompact", "true") \
    .save("/mnt/delta/customers")

# Set as table property
spark.sql("""
    ALTER TABLE customers 
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")
```

## Schema Evolution

### Add Columns
```python
# Enable schema evolution
new_data = [
    (8, "Sarah Connor", "sarah@example.com", current_date(), 
     1500.00, "North", "Premium", 5)  # New columns: tier, years
]

new_schema = schema.add("tier", StringType()) \
                   .add("years_customer", IntegerType())

new_df = spark.createDataFrame(new_data, new_schema)

# Write with schema merge
new_df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/mnt/delta/customers")

# Verify new schema
result = spark.read.format("delta").load("/mnt/delta/customers")
result.printSchema()
display(result)
```

### Schema Enforcement
```python
# Delta Lake enforces schema by default
incompatible_data = [
    ("invalid_id", "Name", "email@test.com")  # Wrong types
]

try:
    bad_df = spark.createDataFrame(
        incompatible_data, 
        ["customer_id", "customer_name", "email"]
    )
    bad_df.write.format("delta").mode("append").save("/mnt/delta/customers")
except Exception as e:
    print(f"Schema enforcement error: {str(e)}")
```

### Column Mapping
```python
# Enable column mapping for column renames
spark.sql("""
    ALTER TABLE customers 
    SET TBLPROPERTIES (
        'delta.columnMapping.mode' = 'name',
        'delta.minReaderVersion' = '2',
        'delta.minWriterVersion' = '5'
    )
""")

# Rename column
spark.sql("ALTER TABLE customers RENAME COLUMN customer_name TO full_name")

# Drop column
spark.sql("ALTER TABLE customers DROP COLUMN email")
```

## Change Data Feed

Enable Change Data Feed to track all changes.

### Enable CDC
```python
# Enable at table creation
spark.sql("""
    CREATE TABLE customers_cdc (
        customer_id INT,
        customer_name STRING,
        email STRING,
        total_purchases DOUBLE
    )
    USING DELTA
    TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Enable on existing table
spark.sql("""
    ALTER TABLE customers 
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
```

### Read Change Feed
```python
# Read changes between versions
changes_df = spark.read.format("delta") \
    .option("readChangeDataFeed", "true") \
    .option("startingVersion", 0) \
    .option("endingVersion", 5) \
    .load("/mnt/delta/customers")

display(changes_df)

# Read changes by timestamp
from datetime import datetime, timedelta

start_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
end_time = datetime.now().strftime("%Y-%m-%d")

changes_time_df = spark.read.format("delta") \
    .option("readChangeDataFeed", "true") \
    .option("startingTimestamp", start_time) \
    .option("endingTimestamp", end_time) \
    .load("/mnt/delta/customers")

display(changes_time_df)
```

### Stream Change Feed
```python
# Stream all changes
stream_df = spark.readStream.format("delta") \
    .option("readChangeDataFeed", "true") \
    .option("startingVersion", 0) \
    .load("/mnt/delta/customers")

# Write to another Delta table
stream_df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/mnt/checkpoints/cdc") \
    .start("/mnt/delta/customers_audit")
```

## Practical Examples

### Example 1: Complete ETL Pipeline
```python
from pyspark.sql.functions import *
from delta.tables import DeltaTable

# Step 1: Extract - Read source data
source_df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/mnt/source/customers.csv")

# Step 2: Transform - Clean and enrich
transformed_df = source_df \
    .withColumn("email", lower(col("email"))) \
    .withColumn("customer_name", initcap(col("customer_name"))) \
    .withColumn("load_date", current_date()) \
    .withColumn("load_timestamp", current_timestamp()) \
    .filter(col("email").isNotNull()) \
    .dropDuplicates(["customer_id"])

# Step 3: Load - Upsert into Delta
target_path = "/mnt/delta/customers_final"

if DeltaTable.isDeltaTable(spark, target_path):
    target = DeltaTable.forPath(spark, target_path)
    
    target.alias("target").merge(
        transformed_df.alias("source"),
        "target.customer_id = source.customer_id"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
else:
    transformed_df.write.format("delta") \
        .mode("overwrite") \
        .save(target_path)

print("ETL pipeline completed!")
```

### Example 2: Real-time Aggregations
```python
# Maintain real-time aggregations in Delta
from pyspark.sql.functions import sum, count, avg, max as spark_max

# Source transactions
transactions = [
    (1, 1, 100.00, "2024-01-15"),
    (2, 1, 150.00, "2024-01-16"),
    (3, 2, 200.00, "2024-01-15"),
    (4, 2, 50.00, "2024-01-17")
]

trans_schema = ["transaction_id", "customer_id", "amount", "date"]
trans_df = spark.createDataFrame(transactions, trans_schema)

# Calculate aggregations
agg_df = trans_df.groupBy("customer_id").agg(
    count("*").alias("transaction_count"),
    sum("amount").alias("total_amount"),
    avg("amount").alias("avg_amount"),
    spark_max("date").alias("last_transaction_date")
)

# Upsert aggregations
agg_path = "/mnt/delta/customer_aggregations"

if DeltaTable.isDeltaTable(spark, agg_path):
    target = DeltaTable.forPath(spark, agg_path)
    
    target.alias("target").merge(
        agg_df.alias("source"),
        "target.customer_id = source.customer_id"
    ).whenMatchedUpdate(set={
        "transaction_count": "target.transaction_count + source.transaction_count",
        "total_amount": "target.total_amount + source.total_amount",
        "avg_amount": "(target.total_amount + source.total_amount) / (target.transaction_count + source.transaction_count)",
        "last_transaction_date": "CASE WHEN source.last_transaction_date > target.last_transaction_date THEN source.last_transaction_date ELSE target.last_transaction_date END"
    }).whenNotMatchedInsertAll().execute()
else:
    agg_df.write.format("delta").mode("overwrite").save(agg_path)
```

### Example 3: Data Quality Checks
```python
# Implement data quality checks with Delta
from pyspark.sql.functions import col, expr

def validate_and_load(df, table_path, rules):
    """
    Validate data quality and load to Delta
    
    Args:
        df: Source DataFrame
        table_path: Delta table path
        rules: Dictionary of validation rules
    """
    # Separate valid and invalid records
    valid_df = df
    invalid_records = []
    
    for rule_name, rule_expr in rules.items():
        # Filter valid records
        valid_df = valid_df.filter(rule_expr)
        
        # Collect invalid records
        invalid = df.filter(~expr(rule_expr)) \
            .withColumn("rule_failed", lit(rule_name)) \
            .withColumn("validation_time", current_timestamp())
        
        invalid_records.append(invalid)
    
    # Load valid records to Delta
    valid_df.write.format("delta") \
        .mode("append") \
        .save(table_path)
    
    # Log invalid records
    if invalid_records:
        invalid_df = invalid_records[0]
        for df in invalid_records[1:]:
            invalid_df = invalid_df.union(df)
        
        invalid_df.write.format("delta") \
            .mode("append") \
            .save(f"{table_path}_invalid")
    
    return valid_df.count(), sum(df.count() for df in invalid_records)

# Define quality rules
quality_rules = {
    "email_valid": "email LIKE '%@%.%'",
    "amount_positive": "total_purchases > 0",
    "name_not_null": "customer_name IS NOT NULL",
    "recent_registration": "registration_date >= '2020-01-01'"
}

# Validate and load
valid_count, invalid_count = validate_and_load(
    transformed_df,
    "/mnt/delta/customers_validated",
    quality_rules
)

print(f"Valid records: {valid_count}")
print(f"Invalid records: {invalid_count}")
```

## Summary

Delta Lake provides:

1. **ACID Guarantees**: Reliable transactions
2. **Time Travel**: Query historical data
3. **Schema Evolution**: Flexible schema changes
4. **Optimization**: File compaction and indexing
5. **CDC**: Track all changes
6. **MERGE**: Efficient upserts
7. **DML**: Full UPDATE/DELETE support

### Best Practices
- Enable auto-optimize for write-heavy workloads
- Use Z-ordering for frequently queried columns
- Partition large tables appropriately
- Regular VACUUM to clean up old files
- Enable Change Data Feed for audit trails
- Use MERGE for idempotent pipelines

## Next Steps
- Explore Structured Streaming with Delta
- Learn Delta Live Tables (DLT)
- Study Unity Catalog integration
- Master performance tuning
