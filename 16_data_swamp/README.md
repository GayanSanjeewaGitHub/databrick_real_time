# Credit Card Promotion Targeting - Full Stack Implementation

## 🎯 Project Overview

This is a complete end-to-end implementation of a **Credit Card Promotion Targeting System** for a commercial bank, demonstrating the difference between a **Data Swamp** (ungoverned) and a **Governed Data Architecture** using Hadoop, Spark, Hive, and PostgreSQL.

### Business Use Case
The bank wants to launch a targeted marketing campaign for a "Premium Travel Credit Card" by identifying customers who:
- Have high transaction volumes on travel-related purchases
- Frequently visit travel-related pages on the bank's website/app
- Have good credit scores but don't currently hold a premium card

### Architecture Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Operational Database** | PostgreSQL | Customer master data & campaign results |
| **Storage Layer** | Hadoop HDFS | Massive transaction logs & web clickstream data |
| **Metadata Catalog** | Hive Metastore | Central schema repository & data governance |
| **Processing Engine** | Apache Spark | ETL, analytics, and ML propensity modeling |
| **Orchestration** | Docker Compose | Local development environment |

---

## 📂 Project Structure

```
16_data_swamp/
├── config/                      # Configuration files
├── data/                        # Data directory (generated)
│   ├── raw/
│   │   ├── transactions/       # Transaction CSV files
│   │   └── weblogs/            # Web log JSON files
│   ├── processed/              # Curated Parquet files
│   └── swamp/                  # Ungoverned data (demo)
├── notebooks/                   # Jupyter notebooks (optional)
├── scripts/                     # Setup and utility scripts
│   ├── setup.sh               # Linux/Mac setup
│   └── setup.bat              # Windows setup
├── sql/                        # SQL scripts
│   ├── init_postgres.sql      # PostgreSQL initialization
│   └── hive_tables.sql        # Hive table definitions
├── src/                        # Python source code
│   ├── __init__.py
│   ├── config.py              # Configuration module
│   ├── data_generator.py      # Synthetic data generator
│   ├── pipeline_no_hms.py     # Data Swamp demo (No HMS)
│   ├── pipeline_with_hms.py   # Governed approach (With HMS)
│   └── propensity_model.py    # Full propensity model
├── docker-compose.yml          # Docker services definition
├── requirements.txt            # Python dependencies
├── setup.py                    # Python package setup
├── .env.example               # Environment variables template
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Python 3.8+ installed
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

### Step 1: Setup Environment

**Windows:**
```powershell
cd 16_data_swamp
.\scripts\setup.bat
```

**Linux/Mac:**
```bash
cd 16_data_swamp
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Create Python virtual environment
- Install dependencies
- Create `.env` file
- Set up data directories

### Step 2: Start Services

```bash
docker-compose up -d
```

**Wait 2-3 minutes** for all services to initialize. Monitor with:
```bash
docker-compose ps
```

All services should show `Up` status.

### Step 3: Verify Services

Access the web UIs:
- **Hadoop NameNode**: http://localhost:9870
- **Spark Master**: http://localhost:8080
- **PostgreSQL**: `localhost:5432` (user: `bank_user`, password: `bank_pass123`)

### Step 4: Generate Data

Activate the virtual environment:

**Windows:**
```powershell
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

Generate synthetic data:
```bash
python src/data_generator.py
```

This creates:
- 1,000 customers in PostgreSQL
- 50,000 transactions in `data/raw/transactions/`
- 20,000 web logs in `data/raw/weblogs/`

---

## 🎓 Demo Workflows

### Demo 1: Data Swamp (Without Hive Metastore)

```bash
python src/pipeline_no_hms.py
```

**What happens:**
- ✗ Spark writes data directly to files
- ✗ No schema registered in Hive Metastore
- ✗ Tables are temporary and not discoverable
- ✗ Other users cannot find this data
- ⚠️ **This creates a Data Swamp!**

**Output:** Processed data in `data/swamp/` that only this script knows about.

### Demo 2: Governed Approach (With Hive Metastore)

```bash
python src/pipeline_with_hms.py
```

**What happens:**
- ✓ Spark connects to Hive Metastore
- ✓ Tables are registered in central catalog
- ✓ Schema and metadata are documented
- ✓ Data is discoverable by all users
- ✓ **Proper Data Governance!**

**Output:** Tables visible in Hive:
- `raw_data.raw_transactions`
- `raw_data.raw_weblogs`
- `processed_data.travel_spend_agg`
- `processed_data.travel_page_visits`

### Demo 3: Full Propensity Model

```bash
python src/propensity_model.py
```

**What happens:**
1. Reads customer profiles from PostgreSQL
2. Reads processed data from Hive tables
3. Joins data and calculates propensity scores
4. Identifies high-value customers
5. Writes results back to PostgreSQL

**Output:** Target customer list in PostgreSQL `promo_eligibility` table.

---

## 📊 Verifying Results

### Query PostgreSQL Results

```bash
docker exec -it bank_postgres psql -U bank_user -d bank_db
```

```sql
-- View target customers
SELECT 
    c.name, 
    c.email, 
    c.credit_score,
    p.propensity_score, 
    p.total_travel_spend,
    p.travel_page_visits
FROM promo_eligibility p
JOIN customers c ON p.customer_id = c.customer_id
WHERE p.campaign_name = 'PREMIUM_TRAVEL_2025'
ORDER BY p.propensity_score DESC, p.total_travel_spend DESC
LIMIT 10;
```

### Query Hive Tables

Access Spark SQL shell:
```bash
docker exec -it spark_master spark-sql \
  --conf spark.sql.catalogImplementation=hive \
  --conf hive.metastore.uris=thrift://hive-metastore:9083
```

```sql
-- Show all databases
SHOW DATABASES;

-- Show tables
SHOW TABLES IN processed_data;

-- Query aggregated data
SELECT * FROM processed_data.travel_spend_agg LIMIT 10;

-- View table metadata
DESCRIBE EXTENDED processed_data.travel_spend_agg;
```

---

## 🔍 Key Differences: Swamp vs Governed

| Aspect | Data Swamp (No HMS) | Governed (With HMS) |
|--------|---------------------|---------------------|
| **Write Command** | `df.write.parquet("/path")` | `df.write.saveAsTable("table")` |
| **Schema Storage** | File headers only | Hive Metastore Database |
| **Discoverability** | Requires file system search | `SHOW TABLES` |
| **Documentation** | None | Table properties & comments |
| **Lineage** | Unknown | Trackable via metadata |
| **Access** | Need exact file path | Standard SQL queries |
| **Persistence** | Files remain, meaning lost | Metadata persists forever |

---

## 🛠️ Configuration

Edit `.env` file to customize:

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Hive Metastore
HIVE_METASTORE_URI=thrift://localhost:9083

# Data Generation
NUM_CUSTOMERS=1000
NUM_TRANSACTIONS=50000
NUM_WEBLOGS=20000
```

---

## 🧹 Cleanup

Stop services:
```bash
docker-compose down
```

Remove all data and volumes:
```bash
docker-compose down -v
```

Clean generated data:
```bash
rm -rf data/raw/* data/processed/* data/swamp/*
```

---

## 📚 Learning Objectives

This project demonstrates:

1. **Data Swamp Problem**: How ungoverned data accumulates when Hive Metastore is bypassed
2. **Hive Metastore Benefits**: Central catalog for schema management and discovery
3. **Spark Integration**: Proper configuration to connect Spark to HMS
4. **Data Governance**: Using table properties, comments, and metadata
5. **End-to-End Pipeline**: From raw data → processing → analytics → operational database
6. **Hadoop Ecosystem**: HDFS, Hive, Spark working together
7. **Hybrid Architecture**: Combining big data storage with RDBMS for operations

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check Docker resources
docker stats

# View logs
docker-compose logs namenode
docker-compose logs hive-metastore
```

### Connection errors
- Ensure all services are healthy: `docker-compose ps`
- Wait 2-3 minutes after starting services
- Check firewall settings for ports 5432, 9000, 9083, 7077

### Hive Metastore connection failed
```bash
# Restart Hive Metastore
docker-compose restart hive-metastore

# Check Hive logs
docker-compose logs hive-metastore
```

### Python errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.8+
```

---

## 📖 Additional Resources

- [Apache Hive Documentation](https://hive.apache.org/)
- [Apache Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Hadoop HDFS Architecture](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- [Data Governance Best Practices](https://www.dataversioncontrol.com/blog/data-governance-best-practices)

---

## 👥 Contributing

This is a demonstration project for learning purposes. Feel free to:
- Modify the data generation parameters
- Add more processing steps
- Implement additional governance features
- Integrate with Apache Atlas for lineage tracking

---

## 📝 License

This project is provided as-is for educational purposes.

---

**Author**: Data Engineering Team  
**Date**: December 2025  
**Version**: 1.0.0
