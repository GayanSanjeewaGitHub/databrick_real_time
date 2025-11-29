# Real-Time Streaming with Databricks

## Table of Contents
1. [Introduction to Structured Streaming](#introduction)
2. [Auto Loader](#auto-loader)
3. [Structured Streaming Basics](#structured-streaming)
4. [Delta Lake Streaming](#delta-streaming)
5. [Kafka Integration](#kafka)
6. [Event Hubs Integration](#event-hubs)
7. [Change Data Capture (CDC)](#cdc)
8. [Stateful Streaming](#stateful-streaming)
9. [Stream Monitoring](#monitoring)
10. [Production Considerations](#production)
11. [Practical Examples](#examples)

## Introduction to Structured Streaming

Structured Streaming is a scalable and fault-tolerant stream processing engine built on Spark SQL.

### Key Concepts
- **Micro-batch Processing**: Process data in small batches
- **Continuous Processing**: Low-latency event processing
- **Exactly-once Semantics**: Guaranteed processing
- **Fault Tolerance**: Automatic recovery from failures
- **Integration**: Works seamlessly with Delta Lake

### Architecture
```
Streaming Architecture:
┌────────────┐     ┌──────────────┐     ┌─────────────┐
│   Source   │────▶│   Spark      │────▶│    Sink     │
│  (Kafka,   │     │  Streaming   │     │ (Delta Lake)│
│  Files)    │     │   Engine     │     │             │
└────────────┘     └──────────────┘     └─────────────┘
                         │
                         ▼
                   ┌──────────────┐
                   │  Checkpoint  │
                   │   Location   │
                   └──────────────┘
```

## Auto Loader

Auto Loader incrementally and efficiently processes new files as they arrive in cloud storage.

### Basic Auto Loader
```python
from pyspark.sql.functions import col, current_timestamp

# Define file path
file_path = "/databricks-datasets/structured-streaming/events"
checkpoint_path = "/tmp/autoloader/_checkpoint"

# Read streaming data with Auto Loader 
#cloudFiles (Auto Loader) uses a notification system (like Azure Event Grid) or an incremental listing method to instantly find new files without scanning the whole directory.
raw_df = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", checkpoint_path)
    .load(file_path)
)

# Display schema
raw_df.printSchema()

# Add metadata columns
enriched_df = raw_df \
    .select("*", 
            col("_metadata.file_path").alias("source_file"),
            col("_metadata.file_name").alias("file_name"),
            current_timestamp().alias("processing_time"))

# Write to Delta Lake
(enriched_df.writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint_path)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)
    .table("bronze_events"))

print("Auto Loader streaming started!")
```

### Auto Loader with Schema Inference
```python
# Advanced Auto Loader configuration
auto_loader_df = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/tmp/schema/events")
    
    # Schema inference options
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    
    # File notification options
    .option("cloudFiles.useNotifications", "true")
    
    # Error handling
    .option("cloudFiles.maxFilesPerTrigger", "1000")
    .option("cloudFiles.includeExistingFiles", "true")
    
    .load(file_path)
)

# Write with schema evolution
(auto_loader_df.writeStream
    .format("delta")
    .option("checkpointLocation", "/tmp/checkpoints/events")
    .option("mergeSchema", "true")
    .trigger(processingTime="10 seconds")
    .table("events_raw"))
```

### Auto Loader for Different File Formats
```python
# CSV files
csv_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", "/tmp/schema/csv")
    .option("header", "true")
    .load("/mnt/data/csv/")
)

# Parquet files
parquet_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", "/tmp/schema/parquet")
    .load("/mnt/data/parquet/")
)

# Avro files
avro_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "avro")
    .option("cloudFiles.schemaLocation", "/tmp/schema/avro")
    .load("/mnt/data/avro/")
)

# Binary files (images, documents)
binary_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "binaryFile")
    .load("/mnt/data/images/")
)
```

## Structured Streaming Basics

### Reading Streams
```python
# Read from Delta table as stream
delta_stream = spark.readStream \
    .format("delta") \
    .table("source_table")

# Read from file path
file_stream = spark.readStream \
    .format("delta") \
    .load("/mnt/delta/events")

# Read with rate source (for testing)
rate_stream = spark.readStream \
    .format("rate") \
    .option("rowsPerSecond", 100) \
    .option("numPartitions", 10) \
    .load()

# Display rate stream
from pyspark.sql.functions import *

display_df = rate_stream \
    .withColumn("event_id", col("value")) \
    .withColumn("event_time", col("timestamp")) \
    .withColumn("random_value", rand(seed=42))

display(display_df)
```

### Writing Streams
```python
# Write to Delta Lake
(delta_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/output")
    .trigger(processingTime="30 seconds")
    .table("target_table"))

# Write to console (for debugging)
(delta_stream.writeStream
    .format("console")
    .outputMode("append")
    .trigger(processingTime="10 seconds")
    .start())

# Write to memory (for testing)
(delta_stream.writeStream
    .format("memory")
    .queryName("test_query")
    .outputMode("append")
    .start())

# Query in-memory table
spark.sql("SELECT * FROM test_query").show()
```

### Output Modes
```python
# Append mode - only new rows
(stream_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoint1")
    .table("append_table"))

# Complete mode - entire result table
aggregated_df = stream_df.groupBy("category").count()

(aggregated_df.writeStream
    .format("delta")
    .outputMode("complete")
    .option("checkpointLocation", "/tmp/checkpoint2")
    .table("complete_table"))

# Update mode - only updated rows
updated_df = stream_df.groupBy("category").count()

(updated_df.writeStream
    .format("delta")
    .outputMode("update")
    .option("checkpointLocation", "/tmp/checkpoint3")
    .table("update_table"))
```

## Delta Lake Streaming

### Stream from Delta Lake
```python
from pyspark.sql.functions import *

# Read Delta table as stream
events_stream = spark.readStream \
    .format("delta") \
    .table("events")

# Transform stream
transformed_stream = events_stream \
    .withColumn("processed_at", current_timestamp()) \
    .withColumn("date", to_date(col("timestamp"))) \
    .filter(col("status") == "active")

# Write to Delta Lake
(transformed_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/events_processed")
    .trigger(availableNow=True)
    .table("events_processed"))
```

### Stream Joins with Delta
```python
# Stream-static join
static_customers = spark.read.table("customers")

enriched_stream = (spark.readStream
    .table("orders")
    .join(static_customers, "customer_id", "left")
    .select("order_id", "customer_id", "customer_name", 
            "order_amount", "order_date"))

# Write enriched stream
(enriched_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/enriched_orders")
    .trigger(processingTime="1 minute")
    .table("enriched_orders"))
```

### Stream-Stream Join
```python
# Join two streams with watermarking
from pyspark.sql.functions import expr

# Stream 1: Orders
orders_stream = (spark.readStream
    .table("orders")
    .withWatermark("order_time", "10 minutes"))

# Stream 2: Payments
payments_stream = (spark.readStream
    .table("payments")
    .withWatermark("payment_time", "10 minutes"))

# Join streams
joined_stream = orders_stream.join(
    payments_stream,
    expr("""
        order_id = payment_order_id AND
        payment_time >= order_time AND
        payment_time <= order_time + interval 1 hour
    """),
    "inner"
)

# Write joined stream
(joined_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/orders_payments")
    .trigger(processingTime="30 seconds")
    .table("orders_with_payments"))
```

## Kafka Integration

### Read from Kafka
```python
# Kafka connection configuration
kafka_bootstrap_servers = "kafka-broker:9092"
kafka_topic = "events"

# Read from Kafka
kafka_df = (spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
    .option("subscribe", kafka_topic)
    .option("startingOffsets", "earliest")
    .load())

# Parse Kafka messages
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

# Define message schema
event_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("event_time", TimestampType(), True),
    StructField("properties", MapType(StringType(), StringType()), True)
])

# Parse JSON from Kafka
parsed_df = kafka_df \
    .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .select(
        col("key"),
        from_json(col("value"), event_schema).alias("data")
    ) \
    .select("key", "data.*")

# Write to Delta Lake
(parsed_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/kafka_events")
    .trigger(processingTime="10 seconds")
    .table("kafka_events"))
```

### Write to Kafka
```python
# Write stream to Kafka
from pyspark.sql.functions import struct, to_json

# Prepare data for Kafka
kafka_output = parsed_df \
    .select(
        col("event_id").cast("string").alias("key"),
        to_json(struct("*")).alias("value")
    )

# Write to Kafka
(kafka_output.writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
    .option("topic", "processed_events")
    .option("checkpointLocation", "/tmp/checkpoints/kafka_output")
    .trigger(processingTime="5 seconds")
    .start())
```

### Kafka to Delta to Kafka Pipeline
```python
# Complete Kafka pipeline
from pyspark.sql.functions import *

# Read from Kafka
input_stream = (spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
    .option("subscribe", "input_topic")
    .load())

# Parse and transform
parsed_stream = input_stream \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), event_schema).alias("event")) \
    .select("event.*") \
    .withColumn("processing_time", current_timestamp()) \
    .filter(col("event_type").isin(["click", "purchase", "view"]))

# Write to Delta Lake (for analytics)
delta_query = (parsed_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/kafka_to_delta")
    .trigger(processingTime="1 minute")
    .table("raw_events"))

# Aggregate and write back to Kafka
aggregated_stream = parsed_stream \
    .groupBy(
        window(col("event_time"), "5 minutes"),
        col("event_type")
    ) \
    .agg(count("*").alias("event_count"))

kafka_output_df = aggregated_stream \
    .select(
        col("event_type").cast("string").alias("key"),
        to_json(struct(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("event_type"),
            col("event_count")
        )).alias("value")
    )

kafka_query = (kafka_output_df.writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
    .option("topic", "aggregated_events")
    .option("checkpointLocation", "/tmp/checkpoints/delta_to_kafka")
    .trigger(processingTime="30 seconds")
    .start())
```

## Event Hubs Integration

### Read from Event Hubs
```python
# Event Hubs connection configuration
eh_namespace = "my-namespace"
eh_name = "my-eventhub"
eh_connection_string = dbutils.secrets.get("my-scope", "eh-connection-string")

# Event Hubs configuration
eh_conf = {
    "eventhubs.connectionString": sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(eh_connection_string),
    "eventhubs.consumerGroup": "$Default",
    "maxEventsPerTrigger": 5000
}

# Read from Event Hubs
eh_df = (spark.readStream
    .format("eventhubs")
    .options(**eh_conf)
    .load())

# Parse Event Hubs messages
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Define schema
message_schema = StructType([
    StructField("sensor_id", StringType(), False),
    StructField("temperature", DoubleType(), False),
    StructField("humidity", DoubleType(), False),
    StructField("timestamp", LongType(), False)
])

# Parse body
parsed_eh_df = eh_df \
    .withColumn("body_string", col("body").cast("string")) \
    .select(from_json("body_string", message_schema).alias("data")) \
    .select("data.*") \
    .withColumn("event_timestamp", from_unixtime(col("timestamp")))

# Write to Delta Lake
(parsed_eh_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/eventhubs")
    .trigger(processingTime="30 seconds")
    .table("sensor_data"))
```

### Write to Event Hubs
```python
# Write stream to Event Hubs
output_conf = {
    "eventhubs.connectionString": sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(eh_connection_string)
}

# Prepare data for Event Hubs
eh_output = parsed_eh_df \
    .withColumn("body", to_json(struct("*")))

# Write to Event Hubs
(eh_output.writeStream
    .format("eventhubs")
    .options(**output_conf)
    .option("checkpointLocation", "/tmp/checkpoints/eventhubs_output")
    .trigger(processingTime="1 minute")
    .start())
```

## Change Data Capture (CDC)

### CDC with Delta Lake
```python
from delta.tables import DeltaTable
from pyspark.sql.functions import *

# Enable CDC on table
spark.sql("""
    ALTER TABLE source_table 
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Read CDC stream
cdc_stream = (spark.readStream
    .format("delta")
    .option("readChangeDataFeed", "true")
    .option("startingVersion", 0)
    .table("source_table"))

# Process CDC events
processed_cdc = cdc_stream \
    .withColumn("cdc_type", 
        when(col("_change_type") == "insert", "I")
        .when(col("_change_type") == "update_preimage", "U_OLD")
        .when(col("_change_type") == "update_postimage", "U_NEW")
        .when(col("_change_type") == "delete", "D")
    ) \
    .withColumn("captured_at", current_timestamp())

# Write CDC log
(processed_cdc.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/cdc_log")
    .trigger(processingTime="1 minute")
    .table("cdc_log"))
```

### Apply CDC to Target Table
```python
# Read CDC stream
cdc_df = spark.readStream \
    .format("delta") \
    .option("readChangeDataFeed", "true") \
    .table("source_table")

# Function to apply CDC using foreachBatch
def apply_cdc_changes(batch_df, batch_id):
    """Apply CDC changes to target table"""
    
    if batch_df.count() == 0:
        return
    
    target_table = DeltaTable.forName(spark, "target_table")
    
    # Handle deletes
    deletes = batch_df.filter(col("_change_type") == "delete")
    if deletes.count() > 0:
        delete_keys = deletes.select("id").distinct()
        target_table.delete(col("id").isin([row.id for row in delete_keys.collect()]))
    
    # Handle updates and inserts
    upserts = batch_df.filter(col("_change_type").isin(["insert", "update_postimage"]))
    if upserts.count() > 0:
        target_table.alias("target").merge(
            upserts.alias("source"),
            "target.id = source.id"
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()

# Apply CDC using foreachBatch
(cdc_df.writeStream
    .foreachBatch(apply_cdc_changes)
    .option("checkpointLocation", "/tmp/checkpoints/apply_cdc")
    .trigger(processingTime="1 minute")
    .start())
```

## Stateful Streaming

### Windowed Aggregations
```python
from pyspark.sql.functions import window, col, count, sum as spark_sum, avg

# Read stream
events_stream = spark.readStream.table("events")

# Tumbling window aggregation
tumbling_agg = events_stream \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        window(col("event_time"), "5 minutes"),
        col("event_type")
    ) \
    .agg(
        count("*").alias("event_count"),
        spark_sum("amount").alias("total_amount"),
        avg("amount").alias("avg_amount")
    )

# Write aggregations
(tumbling_agg.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/tumbling_window")
    .trigger(processingTime="1 minute")
    .table("event_aggregations"))

# Sliding window aggregation
sliding_agg = events_stream \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        window(col("event_time"), "10 minutes", "5 minutes"),  # window size, slide interval
        col("event_type")
    ) \
    .agg(count("*").alias("event_count"))

(sliding_agg.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/sliding_window")
    .table("sliding_event_aggregations"))
```

### Session Windows
```python
from pyspark.sql.functions import session_window

# Session window aggregation (groups events within gap)
session_agg = events_stream \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        session_window(col("event_time"), "5 minutes"),  # session gap
        col("user_id")
    ) \
    .agg(
        count("*").alias("events_in_session"),
        min("event_time").alias("session_start"),
        max("event_time").alias("session_end")
    )

(session_agg.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/session_window")
    .table("user_sessions"))
```

### Arbitrary Stateful Operations
```python
from pyspark.sql.streaming import GroupState, GroupStateTimeout

# Define state schema
state_schema = StructType([
    StructField("user_id", StringType(), False),
    StructField("total_events", LongType(), False),
    StructField("last_event_time", TimestampType(), False)
])

# State update function
def update_user_state(key, values, state: GroupState):
    """Update user state based on new events"""
    
    # Get existing state or initialize
    if state.exists:
        existing_state = state.get
        total_events = existing_state["total_events"]
        last_event = existing_state["last_event_time"]
    else:
        total_events = 0
        last_event = None
    
    # Process new events
    new_events = 0
    latest_event = last_event
    
    for value in values:
        new_events += 1
        if latest_event is None or value.event_time > latest_event:
            latest_event = value.event_time
    
    # Update state
    updated_state = {
        "user_id": key[0],
        "total_events": total_events + new_events,
        "last_event_time": latest_event
    }
    
    state.update(updated_state)
    
    return updated_state

# Apply stateful operation
stateful_stream = events_stream \
    .groupByKey(lambda row: (row.user_id,)) \
    .flatMapGroupsWithState(
        outputMode="update",
        timeoutConf=GroupStateTimeout.ProcessingTimeTimeout,
        func=update_user_state
    )
```

## Stream Monitoring

### Monitor Streaming Queries
```python
# List active streams
active_streams = spark.streams.active

for stream in active_streams:
    print(f"Stream ID: {stream.id}")
    print(f"Name: {stream.name}")
    print(f"Status: {stream.status}")
    print("-" * 50)

# Get specific stream
stream = spark.streams.get(stream_id)

# Stream status
status = stream.status
print(f"Message: {status['message']}")
print(f"Is Data Available: {status['isDataAvailable']}")
print(f"Is Trigger Active: {status['isTriggerActive']}")

# Last progress
progress = stream.lastProgress
if progress:
    print(f"Batch ID: {progress['batchId']}")
    print(f"Input Rows: {progress['numInputRows']}")
    print(f"Duration: {progress['durationMs']}")
```

### Stream Metrics
```python
# Get recent progress
recent_progress = stream.recentProgress

for batch in recent_progress:
    print(f"Batch {batch['batchId']}:")
    print(f"  Input Rows: {batch['numInputRows']}")
    print(f"  Processed Rows/sec: {batch['processedRowsPerSecond']}")
    print(f"  Duration: {batch['durationMs']['triggerExecution']} ms")
    print()

# Monitor streaming metrics
def monitor_stream_metrics(stream, duration_minutes=5):
    """Monitor stream metrics for specified duration"""
    import time
    
    start_time = time.time()
    metrics = []
    
    while (time.time() - start_time) < duration_minutes * 60:
        progress = stream.lastProgress
        if progress:
            metrics.append({
                "timestamp": progress["timestamp"],
                "batch_id": progress["batchId"],
                "input_rows": progress["numInputRows"],
                "processing_rate": progress.get("processedRowsPerSecond", 0),
                "latency_ms": progress["durationMs"].get("triggerExecution", 0)
            })
        
        time.sleep(30)  # Check every 30 seconds
    
    return metrics

# Usage
# metrics = monitor_stream_metrics(stream, duration_minutes=10)
```

## Production Considerations

### Checkpoint Management
```python
# Proper checkpoint configuration
checkpoint_location = "/mnt/checkpoints/production_stream"

# Start stream with checkpoint
query = (stream_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_location)
    .trigger(processingTime="1 minute")
    .table("production_table"))

# Wait for termination with timeout
query.awaitTermination(timeout=3600)  # 1 hour

# Stop stream gracefully
query.stop()

# Check if stream is active
if query.isActive:
    print("Stream is running")
else:
    print("Stream has stopped")
```

### Error Handling
```python
# Implement error handling with foreachBatch
def process_batch_with_error_handling(batch_df, batch_id):
    """Process batch with comprehensive error handling"""
    
    try:
        # Validate batch
        if batch_df.count() == 0:
            print(f"Batch {batch_id}: No data to process")
            return
        
        # Process data
        processed_df = batch_df.transform(your_transformation_function)
        
        # Write to Delta Lake
        processed_df.write \
            .format("delta") \
            .mode("append") \
            .saveAsTable("processed_table")
        
        print(f"Batch {batch_id}: Successfully processed {batch_df.count()} rows")
        
    except Exception as e:
        # Log error
        error_log = spark.createDataFrame([{
            "batch_id": batch_id,
            "error_message": str(e),
            "timestamp": datetime.now(),
            "row_count": batch_df.count()
        }])
        
        error_log.write \
            .format("delta") \
            .mode("append") \
            .saveAsTable("stream_errors")
        
        # Optionally write failed batch to quarantine
        batch_df.write \
            .format("delta") \
            .mode("append") \
            .partitionBy("batch_id") \
            .save("/mnt/quarantine/failed_batches")
        
        print(f"Batch {batch_id}: Error - {str(e)}")
        raise  # Re-raise to fail the batch

# Use foreachBatch with error handling
(stream_df.writeStream
    .foreachBatch(process_batch_with_error_handling)
    .option("checkpointLocation", "/tmp/checkpoints/with_error_handling")
    .trigger(processingTime="1 minute")
    .start())
```

### Trigger Options
```python
# Processing time trigger
(stream_df.writeStream
    .trigger(processingTime="30 seconds")
    .format("delta")
    .option("checkpointLocation", "/tmp/checkpoint1")
    .table("table1"))

# Once trigger (process all available data once)
(stream_df.writeStream
    .trigger(once=True)
    .format("delta")
    .option("checkpointLocation", "/tmp/checkpoint2")
    .table("table2"))

# Available now trigger (process all available data and stop)
(stream_df.writeStream
    .trigger(availableNow=True)
    .format("delta")
    .option("checkpointLocation", "/tmp/checkpoint3")
    .table("table3"))

# Continuous trigger (experimental, low latency)
(stream_df.writeStream
    .trigger(continuous="1 second")
    .format("delta")
    .option("checkpointLocation", "/tmp/checkpoint4")
    .table("table4"))
```

## Practical Examples

### Example 1: End-to-End Streaming Pipeline
```python
from pyspark.sql.functions import *
from delta.tables import DeltaTable

# Step 1: Ingest with Auto Loader
raw_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/tmp/schema/iot")
    .load("/mnt/landing/iot_data/"))

# Step 2: Bronze layer (raw data)
(raw_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/bronze")
    .trigger(processingTime="1 minute")
    .table("bronze.iot_raw"))

# Step 3: Silver layer (cleaned and enriched)
silver_stream = (spark.readStream
    .table("bronze.iot_raw")
    .filter(col("sensor_id").isNotNull())
    .withColumn("temperature_c", (col("temperature_f") - 32) * 5/9)
    .withColumn("processing_timestamp", current_timestamp())
    .dropDuplicates(["sensor_id", "timestamp"]))

(silver_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/silver")
    .trigger(processingTime="1 minute")
    .table("silver.iot_clean"))

# Step 4: Gold layer (aggregated)
gold_stream = (spark.readStream
    .table("silver.iot_clean")
    .withWatermark("timestamp", "10 minutes")
    .groupBy(
        window(col("timestamp"), "5 minutes"),
        col("sensor_id")
    )
    .agg(
        avg("temperature_c").alias("avg_temp"),
        max("temperature_c").alias("max_temp"),
        min("temperature_c").alias("min_temp"),
        count("*").alias("reading_count")
    ))

(gold_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/gold")
    .trigger(processingTime="5 minutes")
    .table("gold.iot_aggregated"))
```

### Example 2: Real-Time Anomaly Detection
```python
from pyspark.sql.functions import *

# Read streaming data
sensor_stream = spark.readStream.table("silver.iot_clean")

# Calculate running statistics
stats_stream = sensor_stream \
    .withWatermark("timestamp", "1 hour") \
    .groupBy(
        window(col("timestamp"), "1 hour", "10 minutes"),
        col("sensor_id")
    ) \
    .agg(
        avg("temperature_c").alias("avg_temp"),
        stddev("temperature_c").alias("stddev_temp")
    )

# Detect anomalies (values > 3 standard deviations)
anomaly_stream = sensor_stream.alias("s") \
    .join(
        stats_stream.alias("st"),
        expr("""
            s.sensor_id = st.sensor_id AND
            s.timestamp >= st.window.start AND
            s.timestamp < st.window.end
        """),
        "left"
    ) \
    .where(
        (col("s.temperature_c") > col("st.avg_temp") + 3 * col("st.stddev_temp")) |
        (col("s.temperature_c") < col("st.avg_temp") - 3 * col("st.stddev_temp"))
    ) \
    .select("s.*", "st.avg_temp", "st.stddev_temp") \
    .withColumn("anomaly_detected_at", current_timestamp())

# Write anomalies
(anomaly_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/anomalies")
    .trigger(processingTime="30 seconds")
    .table("alerts.temperature_anomalies"))
```

### Example 3: Multi-Source Aggregation
```python
# Stream 1: Web clickstream
web_clicks = (spark.readStream
    .table("bronze.web_clicks")
    .select("user_id", "event_time", "page_url", "session_id"))

# Stream 2: Mobile app events
mobile_events = (spark.readStream
    .table("bronze.mobile_events")
    .select("user_id", "event_time", "screen_name", "session_id"))

# Unionize streams
unified_stream = web_clicks \
    .withColumn("source", lit("web")) \
    .withColumn("location", col("page_url")) \
    .drop("page_url") \
    .unionByName(
        mobile_events
            .withColumn("source", lit("mobile"))
            .withColumn("location", col("screen_name"))
            .drop("screen_name")
    )

# Aggregate across sources
user_activity = unified_stream \
    .withWatermark("event_time", "30 minutes") \
    .groupBy(
        window(col("event_time"), "15 minutes"),
        col("user_id"),
        col("source")
    ) \
    .agg(
        count("*").alias("event_count"),
        countDistinct("location").alias("unique_locations"),
        countDistinct("session_id").alias("session_count")
    )

# Write unified metrics
(user_activity.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/unified_activity")
    .trigger(processingTime="1 minute")
    .table("gold.user_activity_metrics"))
```

## Summary

Structured Streaming provides:

1. **Auto Loader**: Efficient file ingestion
2. **Delta Integration**: Reliable streaming storage
3. **Kafka/Event Hubs**: External system integration
4. **CDC**: Change data capture
5. **Stateful Processing**: Windowing and aggregations
6. **Monitoring**: Built-in metrics and observability

### Best Practices
- Use checkpoints for fault tolerance
- Implement proper error handling
- Monitor stream metrics continuously
- Use appropriate trigger intervals
- Enable watermarking for stateful operations
- Partition output tables appropriately

## Next Steps
- Learn Delta Live Tables (DLT)
- Explore Advanced Stateful Processing
- Study Production Deployment Patterns
