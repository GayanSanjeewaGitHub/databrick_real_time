from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import *

eh_conn_string = dbutils.secrets.get("cmb-scope", "eh-mobile-conn")

eh_conf = {
    "eventhubs.connectionString": sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(eh_conn_string),
    "maxEventsPerTrigger": 5000
}

schema = StructType([
    StructField("session_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("device_id", StringType()),
    StructField("login_time", TimestampType()),
    StructField("logout_time", TimestampType()),
    StructField("ip_address", StringType()),
    StructField("os_type", StringType()),
    StructField("app_version", StringType()),
    StructField("is_successful_login", BooleanType())
])

raw_eh = (
    spark.readStream
        .format("eventhubs")
        .options(**eh_conf)
        .load()
)

parsed = (
    raw_eh
        .withColumn("body_str", col("body").cast("string"))
        .select(from_json("body_str", schema).alias("data"))
        .select("data.*")
        .withColumn("_ingest_ts", current_timestamp())
)

(
    parsed.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation",
                "abfss://lake@cmbprodlake.dfs.core.windows.net/_checkpoints/channels/mobile_sessions")
        .toTable("cmb_channels.silver.mobile_sessions")
)
