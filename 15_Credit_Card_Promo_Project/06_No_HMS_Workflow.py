from pyspark.sql import SparkSession
import os
import shutil

def main():
    # 1. Initialize Spark WITHOUT Hive Support
    # This simulates a "Siloed" environment where developers just run Spark jobs
    # and don't connect to a central Metastore.
    spark = SparkSession.builder \
        .appName("No_HMS_Workflow") \
        .master("local[*]") \
        .getOrCreate()

    print("--- Spark Session Started (No Hive Support) ---")

    # Path to our raw data
    input_path = "generated_data/transactions.csv"
    
    # Path where we will write the "Swamp" data
    # This represents a folder that keeps growing, but nobody knows what's in it
    output_path = "swamp_data/processed_transactions"

    # Clean up previous run for demo purposes
    if os.path.exists("swamp_data"):
        shutil.rmtree("swamp_data")

    # 2. Read Data (Direct File Read)
    print(f"Reading raw data from: {input_path}")
    df = spark.read.csv(input_path, header=True, inferSchema=True)

    # 3. Process Data (e.g., filter high value transactions)
    high_value_df = df.filter("amount > 100")

    # 4. Write Data DIRECTLY to File System (The "Swamp" Creation)
    # NOTICE: We are NOT using saveAsTable(). We are just dumping files.
    # No schema is recorded in any catalog.
    print(f"Writing processed data to: {output_path}")
    high_value_df.write.parquet(output_path)

    # 5. Querying using SQL (The "Hive-like" experience without HMS)
    # We can still use SQL, but we have to manually point to the file every time.
    
    # Option A: Create a Temporary View
    # This "Table" exists ONLY in RAM for this script. 
    # As soon as the script finishes, this "table" definition vanishes.
    high_value_df.createOrReplaceTempView("temp_high_value_trans")
    
    print("--- Running SQL on Temporary View ---")
    spark.sql("""
        SELECT category, count(*) as count, avg(amount) as avg_spend
        FROM temp_high_value_trans
        GROUP BY category
    """).show()

    # Option B: Querying files directly (Spark SQL feature)
    print("--- Running SQL directly on Parquet files ---")
    # This is how you query without a Metastore, but it's brittle.
    # You have to know the exact path.
    spark.sql(f"""
        SELECT * FROM parquet.`{output_path}` LIMIT 5
    """).show()

    print("\n--- DEMO CONCLUSION ---")
    print("1. Data is saved in 'swamp_data/processed_transactions'.")
    print("2. SQL queries worked.")
    print("3. BUT: If you open a new terminal or new script, you cannot say 'SELECT * FROM temp_high_value_trans'.")
    print("4. The schema is locked inside the Parquet file headers, not in a central Hive Metastore.")

    spark.stop()

if __name__ == "__main__":
    main()
