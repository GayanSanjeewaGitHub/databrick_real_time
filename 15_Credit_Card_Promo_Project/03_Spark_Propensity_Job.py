from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, lit, when, desc

def main():
    # Initialize Spark Session
    # In a real cluster, this would be configured via spark-submit
    spark = SparkSession.builder \
        .appName("CreditCardPromoTargeting") \
        .master("local[*]") \
        .getOrCreate()

    print("Spark Session Created")

    # --- 1. Load Data (Simulating Reading from HDFS/Hive and Postgres) ---
    
    # Path to generated data
    data_dir = "generated_data"

    # Load Transactions (CSV)
    # In prod: spark.table("hive_db.raw_transactions")
    df_transactions = spark.read.csv(f"{data_dir}/transactions.csv", header=True, inferSchema=True)
    
    # Load Web Logs (JSON)
    # In prod: spark.table("hive_db.raw_weblogs")
    df_weblogs = spark.read.json(f"{data_dir}/weblogs.json")

    # Load Customers (CSV - Simulating Postgres JDBC read)
    # In prod: spark.read.format("jdbc").option("url", "jdbc:postgresql://...")...
    df_customers = spark.read.csv(f"{data_dir}/customers.csv", header=True, inferSchema=True)

    print("Data Loaded Successfully")

    # --- 2. Feature Engineering ---

    # Feature A: Total Spend on Travel in the last year
    travel_spend = df_transactions.filter(col("category") == "Travel") \
        .groupBy("customer_id") \
        .agg(_sum("amount").alias("total_travel_spend"))

    # Feature B: Number of visits to Travel related pages
    # Identifying travel pages
    travel_pages = ["/travel-rewards", "/flights-booking", "/hotels"]
    
    travel_visits = df_weblogs.filter(col("url_visited").isin(travel_pages)) \
        .groupBy("customer_id") \
        .agg(count("log_id").alias("travel_page_visits"))

    # --- 3. Join & Enriched Profile ---

    # Start with base customer list
    enriched_df = df_customers.join(travel_spend, "customer_id", "left") \
                              .join(travel_visits, "customer_id", "left") \
                              .fillna(0, subset=["total_travel_spend", "travel_page_visits"])

    # --- 4. Propensity Logic (Rule Based for Demo) ---
    
    # Rule: 
    # IF (Credit Score > 650) AND 
    #    (Total Travel Spend > $1000 OR Travel Page Visits > 3)
    # THEN High Propensity
    
    result_df = enriched_df.withColumn("propensity_score", 
        when(
            (col("credit_score") > 650) & 
            ((col("total_travel_spend") > 1000) | (col("travel_page_visits") > 3)),
            lit(0.9) # High probability
        ).otherwise(lit(0.1)) # Low probability
    )

    # Filter for eligible customers
    target_list = result_df.filter(col("propensity_score") > 0.5) \
                           .select("customer_id", "name", "email", "total_travel_spend", "travel_page_visits", "propensity_score") \
                           .orderBy(desc("propensity_score"), desc("total_travel_spend"))

    print("--- Target List for Promotion ---")
    target_list.show(20, truncate=False)

    # --- 5. Write Back (Simulating Write to Postgres) ---
    # In prod: target_list.write.format("jdbc")...
    
    # For demo, we write to a single CSV
    target_list.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{data_dir}/promo_target_list")
    print(f"Target list written to {data_dir}/promo_target_list")

    spark.stop()

if __name__ == "__main__":
    main()
