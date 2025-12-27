"""
Data Swamp Workflow - WITHOUT Hive Metastore
Demonstrates how data becomes ungoverned when not using HMS
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, lit, when, desc
import os
import shutil

def main():
    print("\n" + "="*70)
    print("DATA SWAMP WORKFLOW - Without Hive Metastore")
    print("="*70 + "\n")
    
    # 1. Initialize Spark WITHOUT Hive Support
    print("Step 1: Initializing Spark (No Hive Metastore)...")
    spark = SparkSession.builder \
        .appName("DataSwamp_NoHMS") \
        .master("local[*]") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    print("✓ Spark started WITHOUT Hive support")
    print("  - Tables created will NOT be visible to other users")
    print("  - Schema exists only in memory\n")
    
    # Define paths
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    raw_transactions = os.path.join(base_dir, "raw", "transactions", "transactions.csv")
    raw_weblogs = os.path.join(base_dir, "raw", "weblogs", "weblogs.json")
    swamp_dir = os.path.join(base_dir, "swamp")
    
    # Clean up previous runs
    if os.path.exists(swamp_dir):
        shutil.rmtree(swamp_dir)
    os.makedirs(swamp_dir, exist_ok=True)
    
    # 2. Read Raw Data
    print("Step 2: Reading raw data files...")
    df_transactions = spark.read.csv(raw_transactions, header=True, inferSchema=True)
    df_weblogs = spark.read.json(raw_weblogs)
    
    print(f"✓ Read {df_transactions.count()} transactions")
    print(f"✓ Read {df_weblogs.count()} web logs\n")
    
    # 3. Process Data
    print("Step 3: Processing data...")
    
    # Calculate travel spending
    travel_spend = df_transactions.filter(col("category") == "Travel") \
        .groupBy("customer_id") \
        .agg(_sum("amount").alias("total_travel_spend"))
    
    # Calculate travel page visits
    travel_pages = ["/travel-rewards", "/flights-booking", "/hotels", 
                    "/vacation-packages", "/insurance/travel"]
    
    travel_visits = df_weblogs.filter(col("url_visited").isin(travel_pages)) \
        .groupBy("customer_id") \
        .agg(count("log_id").alias("travel_page_visits"))
    
    print(f"✓ Calculated travel spending for {travel_spend.count()} customers")
    print(f"✓ Calculated travel visits for {travel_visits.count()} customers\n")
    
    # 4. Write to "Data Swamp" (Direct File Write)
    print("Step 4: Writing processed data (BYPASSING Hive Metastore)...")
    
    travel_spend_path = os.path.join(swamp_dir, "travel_spend")
    travel_visits_path = os.path.join(swamp_dir, "travel_visits")
    
    # THE PROBLEM: Direct file writes create orphaned data
    travel_spend.write.mode("overwrite").parquet(travel_spend_path)
    travel_visits.write.mode("overwrite").parquet(travel_visits_path)
    
    print(f"✗ Data written to: {travel_spend_path}")
    print(f"✗ Data written to: {travel_visits_path}")
    print("\n⚠️  WARNING: No schema registered in Hive Metastore!")
    print("⚠️  Other teams cannot discover this data!")
    print("⚠️  Schema knowledge is lost when this script ends!\n")
    
    # 5. Query using Temporary Views (In-Memory Only)
    print("Step 5: Creating temporary views (exist only in this session)...")
    
    travel_spend.createOrReplaceTempView("temp_travel_spend")
    travel_visits.createOrReplaceTempView("temp_travel_visits")
    
    result = spark.sql("""
        SELECT 
            ts.customer_id,
            ts.total_travel_spend,
            COALESCE(tv.travel_page_visits, 0) as travel_page_visits,
            CASE 
                WHEN ts.total_travel_spend > 1000 AND COALESCE(tv.travel_page_visits, 0) > 3 
                THEN 'High'
                WHEN ts.total_travel_spend > 500 OR COALESCE(tv.travel_page_visits, 0) > 1 
                THEN 'Medium'
                ELSE 'Low'
            END as propensity_segment
        FROM temp_travel_spend ts
        LEFT JOIN temp_travel_visits tv ON ts.customer_id = tv.customer_id
        ORDER BY ts.total_travel_spend DESC
        LIMIT 10
    """)
    
    print("\n--- Top 10 Customers by Travel Spend ---")
    result.show(truncate=False)
    
    # 6. Demonstrate direct file querying
    print("\nStep 6: Querying files directly (requires knowing exact path)...")
    
    direct_query = spark.sql(f"""
        SELECT customer_id, total_travel_spend 
        FROM parquet.`{travel_spend_path}`
        WHERE total_travel_spend > 500
        ORDER BY total_travel_spend DESC
        LIMIT 5
    """)
    
    print("\n--- High Value Travel Customers (Direct File Query) ---")
    direct_query.show()
    
    # 7. Show the problem
    print("\n" + "="*70)
    print("PROBLEM DEMONSTRATION")
    print("="*70)
    print("\n1. ✗ Run 'SHOW TABLES' - Result: Empty (No registered tables)")
    spark.sql("SHOW TABLES").show()
    
    print("2. ✗ Try to query 'SELECT * FROM travel_spend' - Will FAIL")
    print("   (Table doesn't exist in catalog)")
    
    print("\n3. ✗ Another user/script cannot access this data without:")
    print("   - Knowing the exact file path")
    print("   - Inferring the schema from file headers")
    print("   - Understanding what the columns mean")
    
    print("\n4. ✗ After 6 months, nobody remembers:")
    print("   - What this data represents")
    print("   - Which job created it")
    print("   - Whether it's still being used")
    
    print("\n" + "="*70)
    print("THIS IS HOW DATA SWAMPS ARE CREATED!")
    print("="*70 + "\n")
    
    spark.stop()

if __name__ == "__main__":
    main()
