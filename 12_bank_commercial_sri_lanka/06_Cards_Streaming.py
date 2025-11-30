from pyspark.sql.functions import from_json, col, current_timestamp, when, lit
from pyspark.sql.types import *

KAFKA_BOOTSTRAP = dbutils.secrets.get("cmb-scope", "cards-kafka-bootstrap")
TOPIC = "cmb-card-auths"

auth_schema = StructType([
    StructField("auth_id", StringType()),
    StructField("card_token", StringType()),
    StructField("customer_id", StringType()),
    StructField("merchant_id", StringType()),
    StructField("amount", DoubleType()),
    StructField("currency", StringType()),
    StructField("auth_result", StringType()),
    StructField("auth_time", TimestampType()),
    StructField("channel", StringType()),
    StructField("country_code", StringType())
])

kafka_df = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "latest")
        .load()
)

parsed = (
    kafka_df
        .selectExpr("CAST(value AS STRING) AS json_str")
        .select(from_json(col("json_str"), auth_schema).alias("data"))
        .select("data.*")
        .withColumn("_ingest_ts", current_timestamp())
)

scored = (
    parsed
        .withColumn(
            "risk_score",
            when(col("country_code") != lit("LK"), lit(0.8)).otherwise(lit(0.2))
        )
        .withColumn("is_fraud_flag", col("risk_score") > 0.7)
)

query = (
    scored.writeStream
        .format("delta")
        .option("checkpointLocation",
                "abfss://lake@cmbprodlake.dfs.core.windows.net/_checkpoints/cards/auths")
        .outputMode("append")
        .toTable("cmb_cards.silver.card_authorizations")
)
