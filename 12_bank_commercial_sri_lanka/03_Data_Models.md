# Domain Data Models – Commercial Bank

## 1. Retail Customers (Silver)

Table: `cmb_retail.silver.customers`

- `customer_id` STRING – Internal unique ID (surrogate key)
- `nic` STRING – National Identity Card (masked for most users)
- `full_name` STRING – Legal customer name
- `dob` DATE – Date of birth
- `risk_rating` INT – AML/KYC risk score 1–5
- `kyc_status` STRING – `PENDING`, `VERIFIED`, `REJECTED`
- `segment` STRING – `MASS`, `PREMIER`, `PRIVATE`
- `branch_code` STRING – Home branch

## 2. Retail Accounts (Silver)

Table: `cmb_retail.silver.accounts`

- `account_id` STRING – Core banking account number
- `customer_id` STRING – FK to customers
- `product_type` STRING – `SAVINGS`, `CURRENT`, `FD`
- `currency` STRING – `LKR`, `USD`, etc.
- `balance` DECIMAL(18,2)
- `status` STRING – `ACTIVE`, `DORMANT`, `CLOSED`
- `open_date` TIMESTAMP

## 3. Retail Transactions (Silver)

Table: `cmb_retail.silver.transactions`

- `txn_id` STRING – Unique transaction ID
- `account_id` STRING – Source account
- `amount` DECIMAL(18,2)
- `currency` STRING
- `txn_type` STRING – `ATM`, `POS`, `ONLINE`, `BRANCH`
- `channel` STRING – `MOBILE`, `WEB`, `ATM`, `BRANCH`
- `txn_timestamp` TIMESTAMP
- `branch_code` STRING

## 4. Card Authorizations (Silver)

Table: `cmb_cards.silver.card_authorizations`

- `auth_id` STRING – Authorization ID
- `card_token` STRING – Tokenized PAN
- `customer_id` STRING – FK to customers
- `merchant_id` STRING
- `amount` DECIMAL(18,2)
- `currency` STRING
- `auth_result` STRING – `APPROVED`, `DECLINED`
- `auth_time` TIMESTAMP
- `channel` STRING – `POS`, `ECOM`, `ATM`
- `country_code` STRING – ISO country
- `risk_score` DOUBLE – Calculated risk
- `is_fraud_flag` BOOLEAN – ML output

## 5. Loans (Silver)

Table: `cmb_loans.silver.loans`

- `loan_id` STRING
- `customer_id` STRING
- `loan_type` STRING – `PERSONAL`, `VEHICLE`, `HOUSING`
- `principal_amount` DECIMAL(18,2)
- `interest_rate` DECIMAL(5,4)
- `tenure_months` INT
- `remaining_balance` DECIMAL(18,2)
- `status` STRING – `ACTIVE`, `CLOSED`, `DEFAULT`

## 6. Digital Channels – Mobile Sessions (Silver)

Table: `cmb_channels.silver.mobile_sessions`

- `session_id` STRING
- `customer_id` STRING
- `device_id` STRING
- `login_time` TIMESTAMP
- `logout_time` TIMESTAMP
- `ip_address` STRING
- `os_type` STRING
- `app_version` STRING
- `is_successful_login` BOOLEAN
