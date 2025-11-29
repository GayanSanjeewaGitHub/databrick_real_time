# Domain Data Models

This document defines the core schemas for the DBS Data Lakehouse.

## 1. Customer Domain (Silver Layer)
**Table:** `dbs_retail.silver.customers`
*Single source of truth for customer identity.*

| Column | Type | Description | PII |
|--------|------|-------------|-----|
| `customer_id` | STRING | Unique UUID | No |
| `nric_fin` | STRING | National ID | **Yes** (Masked) |
| `full_name` | STRING | Legal Name | **Yes** |
| `dob` | DATE | Date of Birth | **Yes** |
| `risk_rating` | INT | AML Risk Score (1-5) | No |
| `kyc_status` | STRING | Verified/Pending | No |
| `segment` | STRING | Treasures/Private/Retail | No |

## 2. Accounts Domain (Silver Layer)
**Table:** `dbs_retail.silver.accounts`
*Holdings for Savings, Current, and Fixed Deposits.*

| Column | Type | Description |
|--------|------|-------------|
| `account_id` | STRING | Unique Account Number |
| `customer_id` | STRING | FK to Customers |
| `product_type` | STRING | 'SAVINGS', 'FIXED_DEP', 'MULTI_CURRENCY' |
| `currency` | STRING | SGD, USD, etc. |
| `balance` | DECIMAL(18,2) | Current Balance |
| `status` | STRING | Active, Dormant, Frozen |
| `open_date` | TIMESTAMP | Account opening date |

## 3. Lending Domain (Silver Layer)
**Table:** `dbs_lending.silver.credit_cards`

| Column | Type | Description |
|--------|------|-------------|
| `card_id` | STRING | Tokenized Card Number |
| `account_id` | STRING | Linked Account |
| `card_type` | STRING | 'Live Fresh', 'Altitude', 'Woman World' |
| `credit_limit` | DECIMAL(18,2) | Approved Limit |
| `expiry_date` | DATE | Card Expiry |

**Table:** `dbs_lending.silver.loans`

| Column | Type | Description |
|--------|------|-------------|
| `loan_id` | STRING | Unique Loan ID |
| `loan_type` | STRING | 'MORTGAGE', 'RENOVATION', 'CAR' |
| `principal_amount` | DECIMAL(18,2) | Original Loan Amount |
| `interest_rate` | DECIMAL(5,4) | Annual Interest Rate |
| `tenure_months` | INT | Loan Duration |
| `remaining_balance`| DECIMAL(18,2) | Outstanding Amount |

## 4. Transaction Domain (Bronze -> Silver)
**Table:** `dbs_retail.silver.transactions`
*High-volume transaction ledger.*

| Column | Type | Description |
|--------|------|-------------|
| `txn_id` | STRING | Unique Transaction ID |
| `account_id` | STRING | Source Account |
| `txn_type` | STRING | 'PAYNOW', 'FAST', 'GIRO', 'POS' |
| `amount` | DECIMAL(18,2) | Transaction Amount |
| `merchant_id` | STRING | If POS/Online |
| `txn_timestamp` | TIMESTAMP | Exact time of transaction |
| `location_lat` | DOUBLE | For Fraud Detection |
| `location_long` | DOUBLE | For Fraud Detection |
| `is_fraud_flag` | BOOLEAN | ML Model Output |

## 5. Wealth Domain (Silver Layer)
**Table:** `dbs_wealth.silver.fixed_deposits`

| Column | Type | Description |
|--------|------|-------------|
| `fd_id` | STRING | Deposit ID |
| `principal` | DECIMAL(18,2) | Deposit Amount |
| `rate` | DECIMAL(5,4) | Interest Rate (e.g., 3.20%) |
| `maturity_date` | DATE | When funds are released |
| `auto_renew` | BOOLEAN | Rollover instruction |
