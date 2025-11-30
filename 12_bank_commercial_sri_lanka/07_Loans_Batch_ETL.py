from pyspark.sql.functions import col, current_timestamp

RAW_LOANS_PATH = "abfss://lake@cmbprodlake.dfs.core.windows.net/raw/core_banking/loans"

raw_loans_df = (
    spark.read
        .format("parquet")
        .load(RAW_LOANS_PATH)
)

silver_loans_df = (
    raw_loans_df
        .select(
            col("loan_id").cast("string"),
            col("customer_id").cast("string"),
            col("product_code").alias("loan_type"),
            col("principal_amount").cast("decimal(18,2)"),
            col("interest_rate").cast("decimal(5,4)"),
            col("tenure_months").cast("int"),
            col("remaining_balance").cast("decimal(18,2)"),
            col("status").cast("string"),
            col("branch_code").cast("string")
        )
        .withColumn("_ingest_ts", current_timestamp())
)

(
    silver_loans_df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable("cmb_loans.silver.loans")
)
