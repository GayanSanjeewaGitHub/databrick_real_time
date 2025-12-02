# Phase C: Data Architecture
## Commercial Bank of Sri Lanka – Enterprise Data Lakehouse

---

## 1. Introduction

### 1.1 Purpose
This document defines the target Data Architecture for Commercial Bank's enterprise data lakehouse on Azure Databricks. It covers data domains, logical and physical models, data flows, governance framework, and Unity Catalog implementation.

### 1.2 Scope
- Logical data models for all in-scope domains
- Physical storage layout (medallion architecture)
- Data governance framework (Unity Catalog)
- Data quality and lineage
- Master data management approach
- Data retention and archival policies

---

## 2. Data Architecture Principles

### 2.1 Core Principles

**Medallion Architecture:**
- **Bronze**: Raw, immutable copy of source data
- **Silver**: Validated, deduplicated, conformed data
- **Gold**: Business-aggregate, use-case-specific views

**Domain-Driven Design:**
- Data organized by business domains (Retail, Cards, Loans, Channels)
- Each domain has dedicated Unity Catalog catalogs
- Clear ownership and accountability

**Data Quality by Layer:**
- Bronze: No quality checks (capture everything)
- Silver: Schema enforcement, data quality expectations, deduplication
- Gold: Business rules, aggregations, dimensional models

---

## 3. Data Domains

### 3.1 Domain Overview

```
┌────────────────────────────────────────────────────────────┐
│                    DATA DOMAIN MAP                         │
├────────────────┬───────────────────────────────────────────┤
│ Domain         │ Description                               │
├────────────────┼───────────────────────────────────────────┤
│ RETAIL BANKING │ Customers, Accounts, Deposits,            │
│                │ Transactions, Branches                    │
├────────────────┼───────────────────────────────────────────┤
│ CARDS          │ Credit/Debit Cards, Authorizations,       │
│                │ Settlements, Disputes, Merchants          │
├────────────────┼───────────────────────────────────────────┤
│ LOANS          │ Loan Origination, Servicing, Collections, │
│                │ Collateral, Repayments                    │
├────────────────┼───────────────────────────────────────────┤
│ DIGITAL        │ Mobile Banking, Internet Banking, ATM     │
│ CHANNELS       │ Sessions, Chatbot Interactions            │
├────────────────┼───────────────────────────────────────────┤
│ REFERENCE DATA │ Products, Branches, Exchange Rates,       │
│                │ Holidays, GL Accounts                     │
├────────────────┼───────────────────────────────────────────┤
│ COMPLIANCE     │ KYC Documents, AML Alerts, CBSL Reports,  │
│                │ Audit Logs                                │
└────────────────┴───────────────────────────────────────────┘
```

### 3.2 Domain Details

#### 3.2.1 Retail Banking Domain

**Purpose**: Core retail banking operations and customer management

**Key Entities:**
- **Customers**: Individual and corporate customer master
- **Accounts**: Savings, Current, Fixed Deposits
- **Transactions**: Debits, credits, transfers, withdrawals
- **Relationships**: Customer-account linkages, joint accounts
- **Branches**: Branch information, regions, operational status

**Data Volume (Annual):**
- Customers: 2.5M active, 50K new/month
- Accounts: 4M active
- Transactions: 600M/year (~2M/day)

**Source Systems:**
- Core Banking (Finacle): Customers, Accounts, Transactions
- CRM: Customer segmentation, marketing preferences
- Relationship Manager System: Corporate customer relationships

**Critical Data Elements:**
- NIC (masked via Unity Catalog)
- Account balance (encrypted at rest)
- Transaction history (7 years retention)

#### 3.2.2 Cards Domain

**Purpose**: Credit and debit card operations, fraud detection

**Key Entities:**
- **Cards**: Card master (tokenized PAN)
- **Authorizations**: Real-time auth requests
- **Settlements**: Daily settlement batches
- **Disputes**: Chargeback management
- **Merchants**: Merchant profiles, MDRs

**Data Volume (Annual):**
- Active Cards: 1.8M
- Authorizations: 300M/year (~1M/day)
- Real-time peak: 500 TPS

**Source Systems:**
- Card Management System (Way4/UTS): Card issuance, limits
- Authorization Switch: Real-time auth decisions
- Settlement System: Clearing files from VISA/Mastercard

**Critical Requirements:**
- <500ms fraud detection latency
- Real-time streaming of authorizations
- PCI-DSS compliance (no raw PAN storage)

#### 3.2.3 Loans Domain

**Purpose**: Lending operations from origination through collections

**Key Entities:**
- **Loans**: Loan master (personal, housing, vehicle)
- **Applications**: Loan origination workflow
- **Repayments**: Installment schedules and payments
- **Collateral**: Property, vehicle valuations
- **Collections**: NPL tracking, recovery actions

**Data Volume (Annual):**
- Active Loans: 450K
- Applications: 80K/year
- Repayments: 5.4M/year

**Source Systems:**
- Loan Origination System (Finacle): Applications, approvals
- Core Banking: Loan accounts, repayments
- Collateral Management: Property/vehicle registries

**Critical Data Elements:**
- Credit bureau scores
- Collateral valuations (refreshed quarterly)
- NPL classification (regulatory reporting)

#### 3.2.4 Digital Channels Domain

**Purpose**: Customer digital interactions and session analytics

**Key Entities:**
- **Mobile Sessions**: ComBank Digital app usage
- **Web Sessions**: Internet banking logins
- **ATM Transactions**: ATM withdrawal/deposit sessions
- **Chatbot Interactions**: AI assistant conversations

**Data Volume (Annual):**
- Mobile Sessions: 120M/year (~350K/day)
- Internet Banking: 40M/year
- ATM Transactions: 50M/year

**Source Systems:**
- Mobile Banking Platform: Session logs, API calls
- Internet Banking: Login events, transaction logs
- ATM Switch: Transaction records

**Critical Requirements:**
- Real-time session anomaly detection
- Customer journey analytics
- A/B testing data for feature releases

---

## 4. Logical Data Models

### 4.1 Retail Banking - Silver Layer

#### Customers Table
```
cmb_retail.silver.customers
├── customer_id         STRING (PK)
├── nic                 STRING (MASKED via Unity Catalog)
├── passport_no         STRING (MASKED)
├── full_name           STRING
├── dob                 DATE
├── gender              STRING
├── nationality         STRING
├── email               STRING (MASKED)
├── mobile_number       STRING (MASKED)
├── address_line1       STRING
├── address_line2       STRING
├── city                STRING
├── postal_code         STRING
├── segment             STRING (MASS, PREMIER, PRIVATE)
├── kyc_status          STRING (PENDING, VERIFIED, REJECTED, EXPIRED)
├── kyc_expiry_date     DATE
├── risk_rating         INT (1-5, AML risk)
├── cif_number          STRING
├── onboarding_date     TIMESTAMP
├── branch_code         STRING
├── relationship_mgr_id STRING
├── is_active           BOOLEAN
├── last_updated_ts     TIMESTAMP
└── _metadata           STRUCT (source_system, ingested_ts, pipeline_version)
```

**Row-Level Security:**
```sql
CREATE OR REPLACE ROW FILTER cmb_retail.silver.customers_branch_filter
ON cmb_retail.silver.customers
RETURN is_account_group_member('cmb_hq_staff')
    OR is_account_group_member('cmb_data_admins')
    OR branch_code = current_user();
```

#### Accounts Table
```
cmb_retail.silver.accounts
├── account_id          STRING (PK)
├── customer_id         STRING (FK → customers)
├── account_number      STRING (encrypted)
├── product_code        STRING
├── product_type        STRING (SAVINGS, CURRENT, FD, OD)
├── currency            STRING (LKR, USD, EUR, GBP)
├── balance             DECIMAL(18,2) (encrypted)
├── available_balance   DECIMAL(18,2)
├── status              STRING (ACTIVE, DORMANT, CLOSED, FROZEN)
├── open_date           DATE
├── maturity_date       DATE (for FD)
├── interest_rate       DECIMAL(5,4)
├── branch_code         STRING
├── account_officer_id  STRING
├── last_transaction_date DATE
├── is_joint_account    BOOLEAN
├── primary_owner_id    STRING
├── last_updated_ts     TIMESTAMP
└── _metadata           STRUCT
```

#### Transactions Table
```
cmb_retail.silver.transactions
├── txn_id              STRING (PK)
├── account_id          STRING (FK → accounts)
├── txn_timestamp       TIMESTAMP
├── txn_date            DATE (partition key)
├── txn_type            STRING (DEBIT, CREDIT, TRANSFER)
├── amount              DECIMAL(18,2)
├── currency            STRING
├── balance_after_txn   DECIMAL(18,2)
├── channel             STRING (BRANCH, ATM, MOBILE, WEB, POS)
├── sub_channel         STRING (specific ATM/branch/app)
├── description         STRING
├── reference_number    STRING
├── counterparty_account STRING
├── counterparty_bank   STRING
├── branch_code         STRING
├── teller_id           STRING (for branch txns)
├── device_id           STRING (for digital txns)
├── ip_address          STRING
├── location_lat        DOUBLE
├── location_lon        DOUBLE
├── is_suspicious       BOOLEAN (fraud flag)
├── fraud_score         DOUBLE
├── processed_timestamp TIMESTAMP
└── _metadata           STRUCT
```

**Data Quality Expectations (DLT):**
```python
@dlt.expect_or_drop("valid_amount", "amount IS NOT NULL AND amount <> 0")
@dlt.expect_or_drop("valid_currency", "currency IN ('LKR','USD','EUR','GBP')")
@dlt.expect("valid_channel", "channel IN ('BRANCH','ATM','MOBILE','WEB','POS')")
@dlt.expect_or_drop("valid_timestamp", "txn_timestamp IS NOT NULL")
```

### 4.2 Cards Domain - Silver Layer

#### Card Authorizations Table
```
cmb_cards.silver.card_authorizations
├── auth_id             STRING (PK)
├── card_token          STRING (tokenized PAN)
├── customer_id         STRING (FK → cmb_retail.silver.customers)
├── merchant_id         STRING
├── merchant_name       STRING
├── merchant_category_code STRING (MCC)
├── merchant_country    STRING (ISO 3166)
├── amount              DECIMAL(18,2)
├── currency            STRING
├── transaction_currency STRING
├── fx_rate             DECIMAL(10,6)
├── auth_result         STRING (APPROVED, DECLINED, REFERRAL)
├── decline_reason      STRING
├── auth_timestamp      TIMESTAMP
├── auth_date           DATE (partition key)
├── channel             STRING (POS, ECOM, ATM, CONTACTLESS)
├── pos_entry_mode      STRING (CHIP, SWIPE, CONTACTLESS, KEYED)
├── is_international    BOOLEAN
├── is_online           BOOLEAN
├── card_present        BOOLEAN
├── cvv_result          STRING
├── avs_result          STRING
├── three_ds_status     STRING
├── risk_score          DOUBLE (ML model output)
├── fraud_rules_triggered ARRAY<STRING>
├── is_fraud_flag       BOOLEAN
├── fraud_confirmed     BOOLEAN (post-investigation)
├── processing_time_ms  INT
├── acquirer_id         STRING
├── terminal_id         STRING
├── device_fingerprint  STRING
├── ip_address          STRING
├── customer_location   STRUCT(lat DOUBLE, lon DOUBLE)
├── merchant_location   STRUCT(lat DOUBLE, lon DOUBLE)
└── _metadata           STRUCT
```

**Real-Time Processing:**
- Ingested via Kafka topic: `cmb-card-auths`
- Enriched with customer profile in <50ms
- Fraud ML model inference <100ms
- Total latency budget: <500ms

### 4.3 Loans Domain - Silver Layer

#### Loans Table
```
cmb_loans.silver.loans
├── loan_id             STRING (PK)
├── customer_id         STRING (FK → cmb_retail.silver.customers)
├── account_id          STRING
├── application_id      STRING
├── loan_type           STRING (PERSONAL, HOUSING, VEHICLE, BUSINESS)
├── loan_product_code   STRING
├── principal_amount    DECIMAL(18,2)
├── approved_amount     DECIMAL(18,2)
├── disbursed_amount    DECIMAL(18,2)
├── outstanding_balance DECIMAL(18,2)
├── interest_rate       DECIMAL(5,4)
├── interest_type       STRING (FIXED, FLOATING)
├── tenure_months       INT
├── installment_amount  DECIMAL(18,2)
├── installment_frequency STRING (MONTHLY, QUARTERLY)
├── disbursement_date   DATE
├── maturity_date       DATE
├── first_installment_date DATE
├── next_installment_date DATE
├── status              STRING (PENDING, ACTIVE, CLOSED, WRITTEN_OFF, NPL)
├── npl_category        STRING (STANDARD, SMA, SUB, DBT, LOSS per CBSL)
├── days_past_due       INT
├── collateral_type     STRING (PROPERTY, VEHICLE, DEPOSIT, GUARANTOR)
├── collateral_value    DECIMAL(18,2)
├── ltv_ratio           DECIMAL(5,2) (Loan-to-Value %)
├── purpose             STRING
├── credit_score        INT
├── approval_date       DATE
├── approver_id         STRING
├── branch_code         STRING
├── relationship_mgr_id STRING
└── _metadata           STRUCT
```

### 4.4 Channels Domain - Silver Layer

#### Mobile Sessions Table
```
cmb_channels.silver.mobile_sessions
├── session_id          STRING (PK)
├── customer_id         STRING (FK → cmb_retail.silver.customers)
├── device_id           STRING
├── app_version         STRING
├── os_type             STRING (iOS, Android)
├── os_version          STRING
├── device_model        STRING
├── login_timestamp     TIMESTAMP
├── logout_timestamp    TIMESTAMP
├── session_duration_sec INT
├── session_date        DATE (partition key)
├── is_successful_login BOOLEAN
├── login_method        STRING (BIOMETRIC, PIN, OTP)
├── failed_attempts     INT
├── ip_address          STRING
├── ip_country          STRING
├── location_lat        DOUBLE
├── location_lon        DOUBLE
├── is_vpn_detected     BOOLEAN
├── is_rooted_device    BOOLEAN
├── actions_performed   ARRAY<STRING>
├── transactions_count  INT
├── transactions_value  DECIMAL(18,2)
├── screens_visited     ARRAY<STRING>
├── errors_encountered  ARRAY<STRING>
├── network_type        STRING (WIFI, 4G, 5G)
├── risk_score          DOUBLE
└── _metadata           STRUCT
```

---

## 5. Physical Data Architecture

### 5.1 Storage Layout (ADLS Gen2)

```
cmbprodlake (ADLS Gen2 Account)
└── lake (container)
    ├── raw/                          # Landing zone, immutable
    │   ├── core_banking/
    │   │   ├── customers/
    │   │   │   └── YYYY/MM/DD/HH/    # Hourly partitions
    │   │   ├── accounts/
    │   │   └── transactions/
    │   ├── cards/
    │   │   ├── authorizations/       # Real-time streaming
    │   │   └── settlements/          # Daily batches
    │   ├── loans/
    │   └── channels/
    │
    ├── bronze/                       # Raw Delta tables
    │   ├── retail/
    │   │   ├── customers_bronze/
    │   │   ├── accounts_bronze/
    │   │   └── transactions_bronze/
    │   ├── cards/
    │   ├── loans/
    │   └── channels/
    │
    ├── silver/                       # Curated, validated Delta tables
    │   ├── retail/
    │   │   ├── customers/            # Partitioned by branch_code
    │   │   ├── accounts/             # Partitioned by product_type
    │   │   └── transactions/         # Partitioned by txn_date
    │   ├── cards/
    │   │   └── card_authorizations/  # Partitioned by auth_date
    │   ├── loans/
    │   │   └── loans/                # Partitioned by loan_type
    │   └── channels/
    │       └── mobile_sessions/      # Partitioned by session_date
    │
    ├── gold/                         # Business-aggregate views
    │   ├── retail/
    │   │   ├── customer_360/         # Denormalized customer view
    │   │   ├── daily_balances/       # Account balance snapshots
    │   │   └── txn_summary_daily/    # Daily transaction aggregates
    │   ├── cards/
    │   │   ├── fraud_features/       # ML feature store
    │   │   └── merchant_analytics/   # Merchant performance
    │   ├── loans/
    │   │   ├── portfolio_summary/    # Loan book aggregates
    │   │   └── npl_trending/         # NPL analysis
    │   └── regulatory/
    │       ├── cbsl_fsd_returns/     # CBSL reporting
    │       ├── lcr_report/           # Liquidity Coverage Ratio
    │       └── nsfr_report/          # Net Stable Funding Ratio
    │
    ├── _schemas/                     # Auto Loader schema tracking
    │   ├── core_banking/
    │   ├── cards/
    │   └── channels/
    │
    └── _checkpoints/                 # Streaming checkpoints
        ├── cards_auth_stream/
        ├── retail_txn_stream/
        └── mobile_sessions_stream/
```

### 5.2 Unity Catalog Structure

```
cmb_prod_metastore (Unity Catalog Metastore)
├── cmb_retail (Catalog)
│   ├── bronze (Schema)
│   │   ├── customers_bronze (Table)
│   │   ├── accounts_bronze (Table)
│   │   └── transactions_bronze (Table)
│   ├── silver (Schema)
│   │   ├── customers (Table) ← NIC masked, row-filtered
│   │   ├── accounts (Table) ← Balance encrypted
│   │   └── transactions (Table) ← Partitioned by txn_date
│   └── gold (Schema)
│       ├── customer_360 (Table)
│       └── daily_balances (Table)
│
├── cmb_cards (Catalog)
│   ├── bronze (Schema)
│   ├── silver (Schema)
│   │   └── card_authorizations (Table) ← Streaming table
│   └── gold (Schema)
│       └── fraud_features (Table)
│
├── cmb_loans (Catalog)
│   ├── silver (Schema)
│   │   └── loans (Table)
│   └── gold (Schema)
│       └── portfolio_summary (Table)
│
├── cmb_channels (Catalog)
│   ├── silver (Schema)
│   │   ├── mobile_sessions (Table)
│   │   └── web_sessions (Table)
│   └── gold (Schema)
│       └── channel_analytics (Table)
│
└── cmb_common (Catalog)
    ├── security (Schema)
    │   ├── mask_nic (Function)
    │   ├── mask_email (Function)
    │   ├── mask_mobile (Function)
    │   ├── customers_branch_filter (Row Filter)
    │   └── accounts_branch_filter (Row Filter)
    └── reference (Schema)
        ├── branches (Table)
        ├── products (Table)
        ├── currencies (Table)
        └── holidays (Table)
```

### 5.3 Partitioning Strategy

| Table | Partition Key | Rationale | Z-Ordering |
|-------|---------------|-----------|------------|
| `transactions` | `txn_date` (daily) | Query patterns typically date-range | `customer_id`, `account_id` |
| `card_authorizations` | `auth_date` (daily) | Real-time append, historical analysis by date | `card_token`, `merchant_id` |
| `mobile_sessions` | `session_date` (daily) | Session analytics by day/week/month | `customer_id` |
| `customers` | None (small dimension) | Broadcast join eligible | `customer_id`, `branch_code` |
| `accounts` | `product_type` | Separate perf for savings vs current vs FD | `customer_id` |
| `loans` | `loan_type` | Regulatory reporting by loan type | `customer_id`, `branch_code` |

### 5.4 Retention & Archival

| Layer | Hot Tier (Delta) | Cool Tier (Parquet) | Cold Tier (Archive) |
|-------|------------------|---------------------|---------------------|
| **Raw** | 90 days | 2 years | Forever (compliance) |
| **Bronze** | 1 year | 3 years | 7 years (CBSL requirement) |
| **Silver** | 2 years | 5 years | 7 years |
| **Gold** | 3 years | 7 years | 10 years (regulatory) |

**Archival Process:**
- Monthly job to move old partitions to cool/archive tiers
- Metadata retained in Unity Catalog for discovery
- Restore SLA: 24 hours for archived data

---

## 6. Data Governance Framework

### 6.1 Unity Catalog Governance Model

#### Access Control Hierarchy

```
Unity Catalog Metastore
  └─ Catalog (e.g., cmb_retail)
      ├─ Schema (e.g., silver)
      │   └─ Table (e.g., customers)
      │       ├─ Column-level masking
      │       └─ Row-level filtering
      └─ Functions (e.g., mask_nic)
```

#### User Groups & Permissions

| Group | Catalogs | Permissions | Use Case |
|-------|----------|-------------|----------|
| `cmb_data_admins` | ALL | ALL PRIVILEGES | Platform administration |
| `cmb_hq_staff` | ALL | SELECT (unmasked) | Executive reporting, audit |
| `cmb_retail_analysts` | cmb_retail | SELECT (masked PII) | Retail analytics |
| `cmb_cards_engineers` | cmb_cards, cmb_retail.gold | SELECT, MODIFY | Fraud model development |
| `cmb_loan_officers` | cmb_loans, cmb_retail.gold | SELECT | Loan underwriting support |
| `cmb_branch_staff` | cmb_retail | SELECT (row-filtered by branch) | Branch-level reporting |
| `cmb_data_scientists` | *.gold | SELECT | ML/AI development |
| `cmb_bi_developers` | *.gold | SELECT | Dashboard development |

#### Column Masking Functions

```sql
-- NIC Masking
CREATE OR REPLACE FUNCTION cmb_common.mask_nic(nic STRING)
RETURNS STRING
RETURN CASE
  WHEN is_account_group_member('cmb_data_admins') THEN nic
  WHEN is_account_group_member('cmb_hq_staff') THEN nic
  ELSE concat('*****', right(nic, 4))
END;

-- Email Masking
CREATE OR REPLACE FUNCTION cmb_common.mask_email(email STRING)
RETURNS STRING
RETURN CASE
  WHEN is_account_group_member('cmb_data_admins') THEN email
  ELSE regexp_replace(email, '^(.{2}).*(@.*)$', '\\1***\\2')
END;

-- Mobile Number Masking
CREATE OR REPLACE FUNCTION cmb_common.mask_mobile(mobile STRING)
RETURNS STRING
RETURN CASE
  WHEN is_account_group_member('cmb_data_admins') THEN mobile
  ELSE concat(substring(mobile, 1, 3), '****', right(mobile, 2))
END;

-- Account Balance Masking (for non-privileged users)
CREATE OR REPLACE FUNCTION cmb_common.mask_balance(balance DECIMAL(18,2))
RETURNS STRING
RETURN CASE
  WHEN is_account_group_member('cmb_data_admins') THEN CAST(balance AS STRING)
  WHEN is_account_group_member('cmb_finance_team') THEN CAST(balance AS STRING)
  ELSE '[RESTRICTED]'
END;
```

#### Row-Level Security Filters

```sql
-- Branch-based row filter for customers
CREATE OR REPLACE ROW FILTER cmb_retail.silver.customers_branch_filter
ON cmb_retail.silver.customers
RETURN 
  is_account_group_member('cmb_data_admins')
  OR is_account_group_member('cmb_hq_staff')
  OR branch_code = (
    SELECT branch_code FROM cmb_common.reference.user_branch_mapping 
    WHERE username = current_user()
  );

-- Product-based row filter for loans (personal loan officers can't see housing)
CREATE OR REPLACE ROW FILTER cmb_loans.silver.loans_product_filter
ON cmb_loans.silver.loans
RETURN
  is_account_group_member('cmb_data_admins')
  OR (
    is_account_group_member('cmb_personal_loan_officers') 
    AND loan_type = 'PERSONAL'
  )
  OR (
    is_account_group_member('cmb_housing_loan_officers')
    AND loan_type IN ('HOUSING', 'PROPERTY')
  );
```

### 6.2 Data Quality Framework

#### Quality Dimensions

| Dimension | Definition | Measurement | Target |
|-----------|------------|-------------|--------|
| **Completeness** | % of non-null required fields | `COUNT(*) - COUNT(col) / COUNT(*)` | >99% |
| **Accuracy** | % of data matching source | Reconciliation checks | >99.5% |
| **Consistency** | % of data conforming to rules | DLT expectations pass rate | >98% |
| **Timeliness** | Data freshness | `current_timestamp - _ingest_ts` | <1 hour (batch), <5 min (streaming) |
| **Uniqueness** | % of duplicate-free records | `COUNT(*) vs COUNT(DISTINCT pk)` | 100% |

#### DLT Expectation Patterns

**Bronze → Silver Transformations:**
```python
# Example: Retail Transactions
@dlt.table(
    name="silver_retail_transactions",
    comment="Validated retail transactions",
    table_properties={"quality": "silver", "retention_days": "730"}
)
@dlt.expect_all({
    "valid_txn_id": "txn_id IS NOT NULL",
    "valid_account": "account_id IS NOT NULL",
    "valid_amount": "amount IS NOT NULL AND amount <> 0",
    "valid_currency": "currency IN ('LKR','USD','EUR','GBP','AUD','CAD')",
    "valid_timestamp": "txn_timestamp IS NOT NULL AND txn_timestamp < current_timestamp()",
    "valid_channel": "channel IN ('BRANCH','ATM','MOBILE','WEB','POS')"
})
@dlt.expect_or_drop("no_future_dates", "txn_date <= current_date()")
def silver_retail_transactions():
    return (
        dlt.read("bronze_retail_transactions")
        .dropDuplicates(["txn_id"])
        .withColumn("txn_date", col("txn_timestamp").cast("date"))
        .withColumn("fraud_score", fraud_scoring_udf(col("amount"), col("channel")))
    )
```

#### Data Quality Dashboard

**Metrics Tracked:**
- DLT expectations: pass rate, failure count, trending
- Pipeline SLA: on-time completion %
- Data freshness: lag by domain
- Reconciliation: source vs lake row counts
- Schema drift: new columns detected

**Alerting:**
- Slack/email on expectation violations >5%
- PagerDuty for streaming pipeline failures
- Weekly quality scorecard to CDO

### 6.3 Data Lineage

**Unity Catalog Lineage Features:**
- Automatic capture: table → table, table → notebook, table → dashboard
- Column-level lineage (where supported)
- Upstream/downstream impact analysis
- Compliance audit trail

**Example Lineage Flow:**
```
[Core Banking Finacle]
    ↓ (SFTP file drop)
[raw/core_banking/customers/]
    ↓ (Auto Loader)
[cmb_retail.bronze.customers_bronze]
    ↓ (DLT Pipeline: Dedupe, Validate)
[cmb_retail.silver.customers] ← NIC masking applied
    ↓ (DLT Pipeline: Aggregate)
[cmb_retail.gold.customer_360]
    ↓ (SQL Warehouse query)
[Power BI Dashboard: "Customer Insights"]
    ↓ (viewed by)
[Retail Marketing Team]
```

---

## 7. Master Data Management

### 7.1 Master Data Domains

**Customer Master (Golden Record):**
- Source of Truth: Core Banking (Finacle CIF)
- Update Frequency: Real-time CDC
- Deduplication: Fuzzy matching on NIC + name + DOB
- Survivorship Rules: Latest non-null value wins, except for CIF (immutable)

**Product Master:**
- Source of Truth: Product Management System
- Update Frequency: Daily batch
- Versioning: SCD Type 2 (track product changes over time)

**Branch Master:**
- Source of Truth: HR/Admin system
- Update Frequency: Daily
- Attributes: Branch code, name, region, type, operational status

### 7.2 Reference Data Tables

| Table | Keys | Update Pattern | Retention |
|-------|------|----------------|-----------|
| `cmb_common.reference.branches` | `branch_code` (PK) | Daily full refresh | Forever (SCD Type 2) |
| `cmb_common.reference.products` | `product_code` (PK) | Daily CDC | Forever (SCD Type 2) |
| `cmb_common.reference.currencies` | `currency_code` (PK) | Daily (from CBSL feed) | Forever |
| `cmb_common.reference.exchange_rates` | `currency_pair, rate_date` (PK) | Daily | 10 years |
| `cmb_common.reference.holidays` | `holiday_date, country` (PK) | Annually | 10 years |
| `cmb_common.reference.merchants` | `merchant_id` (PK) | Daily CDC | Forever |

---

## 8. Data Integration Patterns

### 8.1 Batch Ingestion (Auto Loader)

**Use Case:** Core Banking daily extracts (customers, accounts, loans)

```python
# Pattern: File-based batch ingestion
raw_path = "abfss://lake@cmbprodlake.dfs.core.windows.net/raw/core_banking/customers"
schema_location = "abfss://lake@cmbprodlake.dfs.core.windows.net/_schemas/core_banking/customers"

@dlt.table(name="bronze_customers")
def bronze_customers():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")  # or "csv", "parquet"
            .option("cloudFiles.schemaLocation", schema_location)
            .option("cloudFiles.inferColumnTypes", "true")
            .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
            .load(raw_path)
            .withColumn("_ingest_ts", current_timestamp())
            .withColumn("_source_file", input_file_name())
    )
```

### 8.2 Streaming Ingestion (Kafka / Event Hubs)

**Use Case:** Real-time card authorizations, mobile app events

```python
# Pattern: Kafka streaming ingestion
KAFKA_BOOTSTRAP = dbutils.secrets.get("cmb-scope", "cards-kafka-bootstrap")
KAFKA_TOPIC = "cmb-card-auths"

@dlt.table(name="bronze_card_auths")
def bronze_card_auths():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
            .option("subscribe", KAFKA_TOPIC)
            .option("startingOffsets", "latest")
            .option("failOnDataLoss", "false")
            .load()
            .selectExpr("CAST(value AS STRING) as json_payload")
            .select(from_json(col("json_payload"), auth_schema).alias("data"))
            .select("data.*")
            .withColumn("_ingest_ts", current_timestamp())
    )
```

### 8.3 CDC (Change Data Capture)

**Use Case:** Real-time customer profile updates from Core Banking

```python
# Pattern: CDC using Debezium format
@dlt.table(name="bronze_customers_cdc")
def bronze_customers_cdc():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
            .option("subscribe", "finacle.cust.customers")
            .load()
            .selectExpr("CAST(value AS STRING) as cdc_payload")
            .select(from_json(col("cdc_payload"), cdc_schema).alias("cdc"))
            .select("cdc.after.*", "cdc.op")  # op: c=create, u=update, d=delete
    )

# Apply CDC to silver table (merge)
@dlt.view(name="customers_cdc_stream")
def customers_cdc_stream():
    return dlt.read_stream("bronze_customers_cdc")

dlt.create_streaming_table("silver_customers")

dlt.apply_changes(
    target="silver_customers",
    source="customers_cdc_stream",
    keys=["customer_id"],
    sequence_by=col("_ingest_ts"),
    apply_as_deletes=expr("op = 'd'"),
    except_column_list=["op"]
)
```

---

## 9. Data Security & Encryption

### 9.1 Encryption at Rest

**ADLS Gen2:**
- Customer-Managed Key (CMK) in Azure Key Vault
- AES-256 encryption
- Key rotation: Annually (automated)
- Key revocation: Immediate effect (data becomes unreadable)

**Databricks Managed Storage:**
- CMK for DBFS root storage
- Encrypted workspace notebooks

### 9.2 Encryption in Transit

- ExpressRoute: Private circuit (not encrypted by default, but isolated)
- TLS 1.3 for all Azure API calls
- Databricks cluster-to-cluster communication: AES-256

### 9.3 Column-Level Encryption (Application-Level)

**Sensitive Columns:**
- Account numbers: Encrypted with bank's master key (not CMK)
- Credit card tokens: Already tokenized by card system
- Passwords/PINs: Never stored in lake

---

## 10. Compliance & Regulatory Mapping

### 10.1 CBSL Requirements

| CBSL Guideline | Implementation | Evidence |
|----------------|----------------|----------|
| **Material Outsourcing** | ExpressRoute + CMK = bank control | Architecture docs, key custody records |
| **Data Residency** | Southeast Asia region only | Azure policy, resource tags |
| **Audit Trail** | Unity Catalog system tables | `system.access.audit` lineage logs |
| **Retention (7 years)** | Lifecycle policies on ADLS | Retention tags, archival logs |
| **FSD Returns** | Automated pipelines | `cmb_common.regulatory.cbsl_fsd` table |

### 10.2 PDPA (Personal Data Protection Act)

| Requirement | Implementation | Notes |
|-------------|----------------|-------|
| **Consent Management** | `kyc_status`, `marketing_consent` flags | Tracked in `customers` table |
| **Right to Access** | Self-service query via customer portal | SQL Warehouse endpoint |
| **Right to Erasure** | `DELETE` from silver + `VACUUM` | Manual approval process |
| **Data Minimization** | Column masking, row filters | Only necessary data exposed |
| **Breach Notification** | Audit logs + alerting | 72-hour notification SLA |

### 10.3 Audit Trail Requirements

**Unity Catalog System Tables:**
```sql
-- Access audit: Who queried what, when
SELECT * FROM system.access.audit
WHERE table_name = 'cmb_retail.silver.customers'
  AND action_name = 'SELECT'
  AND event_date >= current_date() - INTERVAL 30 DAYS;

-- Data lineage: Upstream/downstream dependencies
SELECT * FROM system.access.table_lineage
WHERE source_table_full_name = 'cmb_retail.silver.customers';

-- Column lineage: Which columns flow where
SELECT * FROM system.access.column_lineage
WHERE source_table_full_name = 'cmb_retail.silver.customers'
  AND source_column_name = 'nic';
```

---

## 11. Performance Optimization

### 11.1 Optimization Techniques

**Partitioning:**
- Date-based for fact tables (transactions, authorizations)
- Categorical for dimensions (product_type, loan_type)

**Z-Ordering:**
```sql
OPTIMIZE cmb_retail.silver.transactions
ZORDER BY (customer_id, account_id);

OPTIMIZE cmb_cards.silver.card_authorizations
ZORDER BY (card_token, merchant_id);
```

**Auto-Optimize & Auto-Compaction:**
```sql
ALTER TABLE cmb_retail.silver.transactions
SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

**Liquid Clustering (Databricks 13.3+):**
```sql
-- For high-cardinality, evolving access patterns
CREATE TABLE cmb_retail.silver.transactions_v2
CLUSTER BY (txn_date, customer_id, channel);
```

### 11.2 Caching Strategy

**SQL Warehouse Result Caching:**
- Enabled by default (24-hour TTL)
- Accelerates repeated dashboard queries

**Photon Engine:**
- Enabled on all SQL Warehouse clusters
- 2-5x faster for aggregation queries

---

## 12. Next Steps

### 12.1 Phase C Deliverables Checklist

- [x] Logical data models for all domains
- [x] Physical storage layout (medallion + Unity Catalog)
- [x] Data governance framework (masking, row filters)
- [x] Data quality expectations (DLT)
- [ ] Entity-Relationship Diagrams (ERDs) for each domain
- [ ] Data dictionary (detailed field descriptions)
- [ ] Data flow diagrams (source → bronze → silver → gold)
- [ ] Sample data generation scripts for testing

### 12.2 Follow-On Activities

1. **Data Profiling**: Run profiling on bronze tables to validate assumptions
2. **Pilot Use Case**: Implement one end-to-end pipeline (e.g., fraud detection)
3. **Performance Baseline**: Benchmark query performance on sample data
4. **Security Testing**: Validate masking, row filters, access controls
5. **Regulatory Review**: Present data architecture to CBSL for pre-approval

---

## 13. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Chief Data Officer** | [Name] | | |
| **Chief Risk Officer** | [Name] | | |
| **CISO** | [Name] | | |
| **Head of Retail Banking** | [Name] | | |
| **Enterprise Architect** | [Name] | | |

---

## 14. Document Control

- **Version**: 1.0
- **Status**: Draft for Review
- **Last Updated**: December 2025
- **Next Review**: After stakeholder sign-off
- **Classification**: Internal - Confidential
- **Owner**: Data Architecture Team

---

**End of Phase C: Data Architecture**
