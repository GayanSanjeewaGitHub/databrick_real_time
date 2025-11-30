# Commercial Bank of Ceylon – Azure Databricks Lakehouse

This folder contains a reference implementation of a secure, governed Lakehouse for Commercial Bank of Ceylon on **Azure + Databricks**, designed for:

- Hybrid connectivity via **Azure ExpressRoute**
- **Customer Managed Keys (CMK)** in Azure Key Vault / HSM
- **Unity Catalog** with Row-Level Security and masking
- Product domains: Retail, Cards, Loans, Digital Channels

Structure:
- `01_Architecture_Overview.md`
- `02_Governance_and_Security.md`
- `03_Data_Models.md`
- `04_SQL_UnityCatalog_Setup.sql`
- `05_Retail_ETL.py`
- `06_Cards_Streaming.py`
- `07_Loans_Batch_ETL.py`
- `08_Channels_Streaming.py`
