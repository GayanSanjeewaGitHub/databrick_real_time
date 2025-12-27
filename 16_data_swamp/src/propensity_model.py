"""
Final Propensity Model - Writes Results to PostgreSQL
Combines Hive/Spark analysis and writes target list to operational database
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit
import psycopg2
from config import config

def main():
    print("\n" + "="*70)
    print("PROPENSITY MODEL - Credit Card Campaign Targeting")
    print("="*70 + "\n")
    
    # Initialize Spark with Hive support
    print("Initializing Spark with Hive Metastore...")
    spark = SparkSession.builder \
        .appName("PropensityModel") \
        .master("local[*]") \
        .config("spark.sql.catalogImplementation", "hive") \
        .config("hive.metastore.uris", "thrift://localhost:9083") \
        .enableHiveSupport() \
        .getOrCreate()
    
    # Read customer data from PostgreSQL
    print("Loading customer data from PostgreSQL...")
    df_customers = spark.read.format("jdbc") \
        .option("url", f"jdbc:postgresql://{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}") \
        .option("dbtable", "customers") \
        .option("user", config.POSTGRES_USER) \
        .option("password", config.POSTGRES_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .load()
    
    print(f"✓ Loaded {df_customers.count()} customers from PostgreSQL\n")
    
    # Read processed data from Hive
    print("Loading processed data from Hive...")
    df_travel_spend = spark.table("processed_data.travel_spend_agg")
    df_travel_visits = spark.table("processed_data.travel_page_visits")
    
    # Join all data
    print("Joining customer profile with travel behavior...")
    enriched_df = df_customers \
        .join(df_travel_spend, "customer_id", "left") \
        .join(df_travel_visits, "customer_id", "left") \
        .fillna(0, subset=["total_travel_spend", "travel_page_visits"])
    
    # Apply propensity model
    print("Calculating propensity scores...")
    result_df = enriched_df.withColumn("propensity_score",
        when(
            (col("credit_score") > 650) &
            ((col("total_travel_spend") > 1000) | (col("travel_page_visits") > 3)),
            lit(0.9)
        ).when(
            (col("credit_score") > 550) &
            ((col("total_travel_spend") > 500) | (col("travel_page_visits") > 1)),
            lit(0.6)
        ).otherwise(lit(0.2))
    ).withColumn("promo_code", lit("PREMIUM_TRAVEL_2025"))
    
    # Filter eligible customers
    target_list = result_df.filter(col("propensity_score") >= 0.6) \
        .select(
            "customer_id",
            "name",
            "email",
            "credit_score",
            "promo_code",
            "propensity_score",
            col("total_travel_spend").cast("decimal(12,2)"),
            col("travel_page_visits").cast("int")
        )
    
    print(f"\n✓ Identified {target_list.count()} eligible customers\n")
    
    # Show sample
    print("--- Sample Target Customers ---")
    target_list.orderBy(col("propensity_score").desc(), col("total_travel_spend").desc()).show(10, truncate=False)
    
    # Write to PostgreSQL
    print("\nWriting results to PostgreSQL...")
    
    # Clear previous campaign results
    try:
        conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM promo_eligibility WHERE campaign_name = 'PREMIUM_TRAVEL_2025'")
        conn.commit()
        cursor.close()
        conn.close()
        print("✓ Cleared previous campaign data")
    except Exception as e:
        print(f"Warning: {str(e)}")
    
    # Write new results
    target_list_pd = target_list.toPandas()
    target_list_pd['campaign_name'] = 'PREMIUM_TRAVEL_2025'
    
    try:
        conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO promo_eligibility 
            (customer_id, promo_code, propensity_score, total_travel_spend, 
             travel_page_visits, campaign_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for _, row in target_list_pd.iterrows():
            cursor.execute(insert_query, (
                int(row['customer_id']),
                row['promo_code'],
                float(row['propensity_score']),
                float(row['total_travel_spend']) if row['total_travel_spend'] else 0,
                int(row['travel_page_visits']) if row['travel_page_visits'] else 0,
                row['campaign_name']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Successfully wrote {len(target_list_pd)} records to promo_eligibility table")
        print("\nMarketing team can now query: SELECT * FROM promo_eligibility WHERE campaign_name = 'PREMIUM_TRAVEL_2025'")
        
    except Exception as e:
        print(f"✗ Error writing to PostgreSQL: {str(e)}")
        raise
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70 + "\n")
    
    spark.stop()

if __name__ == "__main__":
    main()
