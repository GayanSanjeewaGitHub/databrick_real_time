-- Unity Catalog setup for Commercial Bank

-- Catalogs
CREATE CATALOG IF NOT EXISTS cmb_retail
  MANAGED LOCATION 'abfss://lake@cmbprodlake.dfs.core.windows.net/silver/retail';

CREATE CATALOG IF NOT EXISTS cmb_cards
  MANAGED LOCATION 'abfss://lake@cmbprodlake.dfs.core.windows.net/silver/cards';

CREATE CATALOG IF NOT EXISTS cmb_loans
  MANAGED LOCATION 'abfss://lake@cmbprodlake.dfs.core.windows.net/silver/loans';

CREATE CATALOG IF NOT EXISTS cmb_channels
  MANAGED LOCATION 'abfss://lake@cmbprodlake.dfs.core.windows.net/silver/channels';

CREATE CATALOG IF NOT EXISTS cmb_common
  MANAGED LOCATION 'abfss://lake@cmbprodlake.dfs.core.windows.net/silver/common';

-- Schemas (bronze/silver/gold)
CREATE SCHEMA IF NOT EXISTS cmb_retail.bronze;
CREATE SCHEMA IF NOT EXISTS cmb_retail.silver;
CREATE SCHEMA IF NOT EXISTS cmb_retail.gold;

CREATE SCHEMA IF NOT EXISTS cmb_cards.bronze;
CREATE SCHEMA IF NOT EXISTS cmb_cards.silver;
CREATE SCHEMA IF NOT EXISTS cmb_cards.gold;

CREATE SCHEMA IF NOT EXISTS cmb_loans.bronze;
CREATE SCHEMA IF NOT EXISTS cmb_loans.silver;
CREATE SCHEMA IF NOT EXISTS cmb_loans.gold;

CREATE SCHEMA IF NOT EXISTS cmb_channels.bronze;
CREATE SCHEMA IF NOT EXISTS cmb_channels.silver;
CREATE SCHEMA IF NOT EXISTS cmb_channels.gold;

-- Masking function for NIC
CREATE OR REPLACE FUNCTION cmb_common.mask_nic(nic STRING)
RETURNS STRING
RETURN CASE
  WHEN is_account_group_member('cmb_data_admins') THEN nic
  ELSE concat('*****', right(nic, 4))
END;

-- Retail customers table with masking and row filter
CREATE TABLE IF NOT EXISTS cmb_retail.silver.customers (
  customer_id STRING,
  nic STRING,
  full_name STRING,
  dob DATE,
  risk_rating INT,
  kyc_status STRING,
  segment STRING,
  branch_code STRING
)
TBLPROPERTIES ('quality' = 'silver');

ALTER TABLE cmb_retail.silver.customers
  ALTER COLUMN nic SET MASK cmb_common.mask_nic;

CREATE OR REPLACE ROW FILTER cmb_retail.silver.customers_branch_filter
ON cmb_retail.silver.customers
RETURN is_account_group_member('cmb_hq_staff')
    OR branch_code = current_user();
