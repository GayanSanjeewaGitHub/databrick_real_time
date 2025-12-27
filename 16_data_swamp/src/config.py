"""
Configuration Module
Loads environment variables and provides configuration for the pipeline
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the data pipeline"""
    
    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "bank_db")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "bank_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "bank_pass123")
    
    @property
    def postgres_url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Hive Metastore Configuration
    HIVE_METASTORE_URI = os.getenv("HIVE_METASTORE_URI", "thrift://localhost:9083")
    
    # Hadoop Configuration
    HDFS_NAMENODE = os.getenv("HDFS_NAMENODE", "hdfs://localhost:9000")
    
    # Spark Configuration
    SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
    
    # Data Generation
    NUM_CUSTOMERS = int(os.getenv("NUM_CUSTOMERS", 1000))
    NUM_TRANSACTIONS = int(os.getenv("NUM_TRANSACTIONS", 50000))
    NUM_WEBLOGS = int(os.getenv("NUM_WEBLOGS", 20000))
    
    # Paths
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    
    # HDFS Paths
    HDFS_RAW_TRANSACTIONS = "/data/raw/transactions"
    HDFS_RAW_WEBLOGS = "/data/raw/weblogs"
    HDFS_PROCESSED_TRAVEL_SPEND = "/data/processed/travel_spend"
    HDFS_PROCESSED_TRAVEL_VISITS = "/data/processed/travel_visits"

config = Config()
