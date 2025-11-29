# Disaster Recovery & Backup Policy

To ensure business continuity and compliance with MAS guidelines, we implement a robust DR and Backup strategy.

## 1. Backup Policy (Time Travel & Cloning)

### 1.1 Operational Recovery (Time Travel)
Delta Lake automatically maintains version history.
*   **Retention:** 30 Days (Standard), 7 Years (Regulatory Tables).
*   **Mechanism:** `DEEP CLONE` for long-term archival.

```sql
-- Monthly Archival Job
CREATE OR REPLACE TABLE dbs_archive.transactions_2025_jan
DEEP CLONE dbs_retail.silver.transactions
VERSION AS OF '2025-02-01 00:00:00';
```

### 1.2 Off-Site Backup
*   **Frequency:** Daily.
*   **Destination:** Geo-Redundant Storage (GRS) in a secondary region (e.g., Hong Kong or Japan, subject to data residency approval).

## 2. Disaster Recovery (DR) Strategy

### 2.1 Active-Passive Architecture
*   **Primary Region:** Singapore (Azure Southeast Asia).
*   **Secondary Region:** Hong Kong (Azure East Asia) - *For critical systems only*.

### 2.2 Replication Strategy
1.  **Metadata:** Unity Catalog metastore replication enabled.
2.  **Data:** Azure GRS / AWS Cross-Region Replication (CRR) for underlying storage buckets.
3.  **Compute:** Infrastructure as Code (Terraform) to spin up Databricks workspaces in the secondary region within 4 hours (RTO).

### 2.3 RPO/RTO Targets
| Tier | Service | RPO (Data Loss) | RTO (Downtime) |
|------|---------|-----------------|----------------|
| **Tier 0** | Core Banking / Payments | < 5 mins | < 1 hour |
| **Tier 1** | Fraud Detection | < 15 mins | < 2 hours |
| **Tier 2** | Regulatory Reporting | < 24 hours | < 24 hours |
| **Tier 3** | Marketing Analytics | < 24 hours | < 48 hours |

## 3. GDPR/PDPA "Right to be Forgotten"
When a customer requests data deletion, we must remove them from all layers (Bronze, Silver, Gold) and history.

### Deletion Procedure
Delta Lake supports ACID deletes. We run a weekly "Purge Job".

```python
def purge_customer_data(customer_id):
    tables = [
        "dbs_retail.silver.customers",
        "dbs_retail.silver.accounts",
        "dbs_lending.silver.loans"
    ]
    
    for table in tables:
        spark.sql(f"""
            DELETE FROM {table} 
            WHERE customer_id = '{customer_id}'
        """)
        
    # VACUUM to remove physical files (GDPR requirement)
    # Note: This removes history, making time travel impossible for this period
    spark.sql(f"VACUUM {table} RETAIN 168 HOURS") 
```
