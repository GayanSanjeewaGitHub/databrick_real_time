# Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐        ┌──────────────┐      ┌──────────────┐    │
│  │ Core Banking │        │ Web Server   │      │ Mobile App   │    │
│  │   System     │        │    Logs      │      │    Logs      │    │
│  └──────┬───────┘        └──────┬───────┘      └──────┬───────┘    │
│         │                       │                      │             │
│         │ Transactions          │ Clickstream         │ Events      │
│         │ (CSV)                 │ (JSON)              │ (JSON)      │
│         │                       │                      │             │
└─────────┼───────────────────────┼──────────────────────┼─────────────┘
          │                       │                      │
          ▼                       ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│               Batch Upload / Streaming (Flume/Kafka)                 │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER (HDFS)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  /data/raw/                                                  │   │
│  │    ├── transactions/  (CSV files)                           │   │
│  │    └── weblogs/       (JSON files)                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   METADATA LAYER (Hive Metastore)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  Databases: raw_data, processed_data                       │     │
│  │  Tables:                                                   │     │
│  │    - raw_data.raw_transactions                            │     │
│  │    - raw_data.raw_weblogs                                 │     │
│  │    - processed_data.travel_spend_agg                      │     │
│  │    - processed_data.travel_page_visits                    │     │
│  │                                                            │     │
│  │  Metadata: Schema, Owner, Source, Description             │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER (Apache Spark)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐         ┌──────────────┐       ┌──────────────┐  │
│  │   Spark      │         │   Spark      │       │   Spark      │  │
│  │   Master     │◄────────┤   Worker 1   │       │   Worker 2   │  │
│  └──────────────┘         └──────────────┘       └──────────────┘  │
│                                                                       │
│  Jobs:                                                               │
│    1. Read from Hive tables                                         │
│    2. Aggregate travel spending                                     │
│    3. Calculate page visit metrics                                  │
│    4. Join with customer profiles                                   │
│    5. Apply propensity model                                        │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              OPERATIONAL DATABASE (PostgreSQL)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  Tables:                                                   │     │
│  │    - customers           (Master Data)                     │     │
│  │    - promo_eligibility  (Target List)                     │     │
│  │    - pipeline_audit      (Execution Log)                  │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CONSUMPTION LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐         ┌──────────────┐       ┌──────────────┐  │
│  │  Marketing   │         │   BI Tools   │       │   CRM        │  │
│  │  Dashboard   │         │  (Tableau)   │       │   System     │  │
│  └──────────────┘         └──────────────┘       └──────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Ingestion**: Transaction and web log data flow into HDFS
2. **Registration**: Hive Metastore stores schema and metadata
3. **Processing**: Spark reads from Hive, processes, and writes back
4. **Analytics**: Propensity model combines big data with operational data
5. **Activation**: Results stored in PostgreSQL for campaign execution

## Key Components

### Without HMS (Data Swamp)
- Files written directly to HDFS
- No central schema registry
- Knowledge lives in code only
- Not discoverable by others

### With HMS (Governed)
- All tables registered in Hive Metastore
- Schema and metadata persisted
- Discoverable via SQL queries
- Lineage and ownership tracked
