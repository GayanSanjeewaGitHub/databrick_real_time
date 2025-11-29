# Environment & File Organization Strategy

This document visualizes the physical and logical organization of the DBS Data Lakehouse across Development, QA, and Production environments. We utilize **Unity Catalog** for logical separation and **ADLS Gen2 / S3** for physical separation.

## 1. Logical Organization (Unity Catalog)

We use a **3-Level Namespace**: `Catalog.Schema.Table`.

### Development Environment
*   **Catalog:** `dbs_dev`
*   **Schemas:** `retail`, `wealth`, `risk`, `common`
*   **Access:** Developers (Read/Write), Data Scientists (Read/Write)

### QA Environment
*   **Catalog:** `dbs_qa`
*   **Schemas:** `retail`, `wealth`, `risk`, `common`
*   **Access:** QA Team (Read/Write), Developers (Read Only)

### Production Environment
*   **Catalog:** `dbs_prod`
*   **Schemas:** `retail`, `wealth`, `risk`, `common`
*   **Access:** Service Principals (Write), BI Users (Read), Analysts (Read - Masked)

---

## 2. Physical Storage Structure (ADLS Gen2 / S3)

We maintain separate storage containers/buckets for each environment to ensure complete isolation.

### Visual Structure

```text
Azure Data Lake Storage Gen2 (dbs-datalake)
│
├── 📁 container-dev (Mounted as /mnt/dbs_dev or External Location)
│   ├── 📁 bronze (Raw Ingestion)
│   │   ├── 📁 transactions
│   │   │   ├── 📄 part-0001.json
│   │   │   └── 📁 _checkpoint
│   │   ├── 📁 kyc_docs
│   │   └── 📁 logs
│   │
│   ├── 📁 silver (Cleaned/Delta Tables)
│   │   ├── 📁 retail
│   │   │   ├── 📁 customers (Delta Table)
│   │   │   └── 📁 accounts (Delta Table)
│   │   └── 📁 wealth
│   │
│   └── 📁 gold (Aggregated/Business)
│       ├── 📁 reports
│       └── 📁 dashboards
│
├── 📁 container-qa (Mirror of Dev structure)
│   └── ...
│
└── 📁 container-prod (Strict Access Control)
    ├── 📁 bronze
    │   └── ... (Ingested from Prod Sources)
    ├── 📁 silver
    │   └── ...
    └── 📁 gold
        └── ...
```

---

## 3. Workspace File Organization (Repos)

We use **Databricks Repos** (Git Integration) for code management. Do not store code in Workspace root.

```text
Databricks Workspace
│
├── 📁 Repos (Git Synced)
│   ├── 📁 Production_Deploy (Read-Only, synced to Main branch)
│   │   └── 📁 dbs-lakehouse-repo
│   │       ├── 📁 pipelines (DLT definitions)
│   │       ├── 📁 notebooks (Analysis/ML)
│   │       └── 📄 databricks.yml (Asset Bundle Config)
│   │
│   └── 📁 User_Folders (Dev branches)
│       ├── 📁 alice@dbs.com
│       │   └── ...
│       └── 📁 bob@dbs.com
│           └── ...
│
├── 📁 Shared
│   ├── 📁 Common_Libs (Utility Wheels/Jars)
│   └── 📁 Onboarding_Docs
│
└── 📁 Users (Personal Workspace - Scratchpad only)
```

## 4. Configuration Management

Configuration is decoupled from code using **JSON/YAML** files loaded at runtime based on the environment.

**File:** `configs/env_config.json` (Stored in Repo)

```json
{
  "dev": {
    "storage_root": "abfss://container-dev@dbsdatalake.dfs.core.windows.net/",
    "catalog": "dbs_dev",
    "kafka_brokers": "dev-kafka.dbs.internal:9092"
  },
  "prod": {
    "storage_root": "abfss://container-prod@dbsdatalake.dfs.core.windows.net/",
    "catalog": "dbs_prod",
    "kafka_brokers": "prod-kafka.dbs.internal:9092"
  }
}
```
