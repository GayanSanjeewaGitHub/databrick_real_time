import dlt
from pyspark.sql.functions import col, current_timestamp

RAW_TXN_PATH = "abfss://lake@cmbprodlake.dfs.core.windows.net/raw/core_banking/transactions"
SCHEMA_LOCATION = "abfss://lake@cmbprodlake.dfs.core.windows.net/_schemas/core_banking/transactions"

@dlt.table(
    name="bronze_retail_transactions",
    comment="Raw core banking transactions for Commercial Bank",
    table_properties={"quality": "bronze"}
)
def bronze_retail_transactions():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", SCHEMA_LOCATION)
            .load(RAW_TXN_PATH)
            .withColumn("_ingest_ts", current_timestamp())
    )

@dlt.table(
    name="silver_retail_transactions",
    comment="Cleaned Commercial Bank retail transactions",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_amount", "amount IS NOT NULL AND amount <> 0")
@dlt.expect("valid_currency", "currency IN ('LKR','USD','EUR','GBP')")
def silver_retail_transactions():
    bronze_df = dlt.read("bronze_retail_transactions")
    return (
        bronze_df
            .select(
                col("txn_id").cast("string"),
                col("account_id").cast("string"),
                col("amount").cast("decimal(18,2)"),
                col("currency").cast("string"),
                col("txn_type").cast("string"),
                col("txn_timestamp").cast("timestamp"),
                col("channel").cast("string"),
                col("branch_code").cast("string"),
                col("_ingest_ts")
            )
    )
