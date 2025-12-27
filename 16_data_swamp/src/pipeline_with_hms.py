"""
Governed Workflow - WITH Hive Metastore
Demonstrates proper data governance using HMS
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, lit, when, desc, current_date
import os

def main():
    print("\n" + "="*70)
    print("GOVERNED WORKFLOW - With Hive Metastore")
    print("="*70 + "\n")
    
    # 1. Initialize Spark WITH Hive Support
    print("Step 1: Initializing Spark with Hive Metastore...")
    spark = SparkSession.builder \
        .appName("Governed_WithHMS") \
        .master("local[*]") \
        .config("spark.sql.catalogImplementation", "hive") \
        .config("hive.metastore.uris", "thrift://localhost:9083") \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .enableHiveSupport() \
        .getOrCreate()
    
    print("✓ Spark started WITH Hive Metastore support")
    print("  - Tables will be registered in central catalog")
    print("  - Schema is persistent and discoverable")
    print("  - Lineage can be tracked\n")
    
    # Define paths
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    raw_transactions = os.path.join(base_dir, "raw", "transactions", "transactions.csv")
    raw_weblogs = os.path.join(base_dir, "raw", "weblogs", "weblogs.json")
    
    # 2. Create Databases
    print("Step 2: Setting up Hive databases...")
    
    spark.sql("CREATE DATABASE IF NOT EXISTS raw_data COMMENT 'Raw data landing zone'")
    spark.sql("CREATE DATABASE IF NOT EXISTS processed_data COMMENT 'Curated datasets'")
    
    print("✓ Databases created: raw_data, processed_data\n")
    
    # 3. Register Raw Data as External Tables
    print("Step 3: Registering raw data in Hive Metastore...")
    
    # Read and register transactions
    df_transactions = spark.read.csv(raw_transactions, header=True, inferSchema=True)
    df_transactions.write.mode("overwrite").saveAsTable("raw_data.raw_transactions")
    
    # Add table properties for governance
    spark.sql("""
        ALTER TABLE raw_data.raw_transactions SET TBLPROPERTIES (
            'creator' = 'ETL_Service',
            'source_system' = 'Core_Banking_System',
            'classification' = 'Confidential',
            'retention_days' = '365'
        )
    """)
    
    # Register web logs
    df_weblogs = spark.read.json(raw_weblogs)
    df_weblogs.write.mode("overwrite").saveAsTable("raw_data.raw_weblogs")
    
    spark.sql("""
        ALTER TABLE raw_data.raw_weblogs SET TBLPROPERTIES (
            'creator' = 'Web_Analytics_Team',
            'source_system' = 'Web_Server_Logs',
            'classification' = 'Internal',
            'retention_days' = '90'
        )
    """)
    
    print("✓ Registered: raw_data.raw_transactions")
    print("✓ Registered: raw_data.raw_weblogs\n")
    
    # 4. Process and Create Curated Tables
    print("Step 4: Processing data and creating curated tables...")
    
    # Calculate travel spending
    travel_spend = spark.sql("""
        SELECT 
            customer_id,
            SUM(amount) as total_travel_spend,
            COUNT(*) as transaction_count,
            AVG(amount) as avg_transaction_amount,
            MAX(trans_date) as last_travel_purchase
        FROM raw_data.raw_transactions
        WHERE category = 'Travel'
        GROUP BY customer_id
    """)
    
    # Write as managed table with documentation
    travel_spend.withColumn("run_date", lit(current_date())) \
        .write.mode("overwrite") \
        .partitionBy("run_date") \
        .saveAsTable("processed_data.travel_spend_agg")
    
    spark.sql("""
        ALTER TABLE processed_data.travel_spend_agg SET TBLPROPERTIES (
            'creator' = 'Spark_Analytics_Job',
            'source_tables' = 'raw_data.raw_transactions',
            'update_frequency' = 'Daily',
            'owner' = 'Data_Science_Team',
            'description' = 'Aggregated travel spending per customer for marketing campaigns'
        )
    """)
    
    # Calculate travel page visits
    travel_visits = spark.sql("""
        SELECT 
            customer_id,
            COUNT(*) as travel_page_visits,
            MIN(timestamp) as first_visit_date,
            MAX(timestamp) as last_visit_date
        FROM raw_data.raw_weblogs
        WHERE url_visited IN (
            '/travel-rewards', '/flights-booking', '/hotels', 
            '/vacation-packages', '/insurance/travel'
        )
        GROUP BY customer_id
    """)
    
    travel_visits.withColumn("run_date", lit(current_date())) \
        .write.mode("overwrite") \
        .partitionBy("run_date") \
        .saveAsTable("processed_data.travel_page_visits")
    
    spark.sql("""
        ALTER TABLE processed_data.travel_page_visits SET TBLPROPERTIES (
            'creator' = 'Spark_Analytics_Job',
            'source_tables' = 'raw_data.raw_weblogs',
            'update_frequency' = 'Daily',
            'owner' = 'Marketing_Team',
            'description' = 'Travel-related web page visits for campaign targeting'
        )
    """)
    
    print("✓ Created: processed_data.travel_spend_agg")
    print("✓ Created: processed_data.travel_page_visits\n")
    
    # 5. Query Managed Tables
    print("Step 5: Querying registered tables (accessible by anyone)...")
    
    result = spark.sql("""
        SELECT 
            ts.customer_id,
            ts.total_travel_spend,
            ts.transaction_count,
            COALESCE(tv.travel_page_visits, 0) as travel_page_visits,
            CASE 
                WHEN ts.total_travel_spend > 1000 AND COALESCE(tv.travel_page_visits, 0) > 3 
                THEN 'High'
                WHEN ts.total_travel_spend > 500 OR COALESCE(tv.travel_page_visits, 0) > 1 
                THEN 'Medium'
                ELSE 'Low'
            END as propensity_segment
        FROM processed_data.travel_spend_agg ts
        LEFT JOIN processed_data.travel_page_visits tv 
            ON ts.customer_id = tv.customer_id
        WHERE ts.run_date = CURRENT_DATE
        ORDER BY ts.total_travel_spend DESC
        LIMIT 10
    """)
    
    print("\n--- Top 10 Travel Customers (From Governed Tables) ---")
    result.show(truncate=False)
    
    # 6. Demonstrate Discoverability
    print("\n" + "="*70)
    print("GOVERNANCE BENEFITS")
    print("="*70)
    
    print("\n1. ✓ All tables are discoverable:")
    spark.sql("SHOW DATABASES").show()
    
    print("\n2. ✓ View tables in each database:")
    print("\nRaw Data Tables:")
    spark.sql("SHOW TABLES IN raw_data").show()
    
    print("\nProcessed Data Tables:")
    spark.sql("SHOW TABLES IN processed_data").show()
    
    print("\n3. ✓ View table details and documentation:")
    print("\n--- Table: processed_data.travel_spend_agg ---")
    spark.sql("DESCRIBE EXTENDED processed_data.travel_spend_agg").show(50, truncate=False)
    
    print("\n4. ✓ Any user can now query:")
    print("   SELECT * FROM processed_data.travel_spend_agg")
    print("   No need to know file paths or schema!")
    
    print("\n5. ✓ Metadata is preserved:")
    print("   - Owner: Data_Science_Team")
    print("   - Source: raw_data.raw_transactions")
    print("   - Update Frequency: Daily")
    print("   - Classification: Documented in properties")
    
    print("\n" + "="*70)
    print("THIS IS PROPER DATA GOVERNANCE!")
    print("="*70 + "\n")
    
    spark.stop()

if __name__ == "__main__":
    main()
