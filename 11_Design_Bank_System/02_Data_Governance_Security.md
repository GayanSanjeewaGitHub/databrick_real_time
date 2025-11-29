# Data Governance & Security Strategy (MAS & GDPR Compliant)

## 1. Governance Framework (Unity Catalog)
DBS operates in a highly regulated environment (MAS). We utilize **Unity Catalog** as the centralized governance layer to manage access, audit, and lineage across all workspaces.

### 1.1 Metastore Structure
*   **Metastore:** `dbs_prod_metastore` (Region: Singapore)
*   **Catalogs:**
    *   `dbs_retail` (Retail Banking)
    *   `dbs_wealth` (Wealth Management)
    *   `dbs_risk` (Risk & Compliance)
    *   `dbs_common` (Reference Data)

## 2. Data Privacy & Protection (PII)
Strict handling of Personally Identifiable Information (PII) like NRIC, Passport Numbers, and Phone Numbers is mandatory under PDPA/GDPR.

### 2.1 Dynamic View Masking
We implement **Row-Level Security (RLS)** and **Column-Level Masking** so that data analysts can query tables without seeing sensitive data, while automated systems (like fraud detection) can access full data.

#### Implementation Example (SQL):
```sql
-- Create a masking function for NRIC
CREATE OR REPLACE FUNCTION mask_nric(nric STRING)
RETURNS STRING
RETURN CASE 
  WHEN is_account_group_member('admin_group') THEN nric
  ELSE '*****' || RIGHT(nric, 4)
END;

-- Apply to Customer Table
ALTER TABLE dbs_retail.silver.customers 
ALTER COLUMN nric SET MASK mask_nric;

-- Row Level Security: Bankers only see customers in their branch
CREATE OR REPLACE ROW FILTER branch_filter ON dbs_retail.silver.customers
RETURN is_account_group_member('hq_staff') OR branch_id = current_user_branch();
```

## 3. Audit & Lineage
To satisfy MAS TRM (Technology Risk Management) guidelines, every data access and transformation must be logged.

*   **System Tables:** Enable `system.access.audit` to track who queried what data and when.
*   **Lineage:** Unity Catalog automatically captures lineage. If a regulatory report is incorrect, we can trace back to the specific ingestion job and source file.

## 4. Data Sovereignty
*   **Region Locking:** All data storage buckets are provisioned in the **Singapore Region** to comply with data residency laws.
*   **Encryption:**
    *   **At Rest:** Customer-Managed Keys (CMK) in Azure Key Vault / AWS KMS.
    *   **In Transit:** TLS 1.2+.

## 5. Data Quality (Expectations)
We use Delta Live Tables (DLT) expectations to enforce data quality at the ingestion point. Bad data is quarantined, not discarded.

```python
@dlt.table(
    comment="Cleaned customer transactions",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_amount", "amount IS NOT NULL AND amount != 0")
@dlt.expect("valid_currency", "currency_code IN ('SGD', 'USD', 'EUR', 'GBP')")
def silver_transactions():
    return dlt.read("bronze_transactions_stream")
```
