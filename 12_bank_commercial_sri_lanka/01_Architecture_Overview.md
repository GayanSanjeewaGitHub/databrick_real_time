# Commercial Bank – Azure Databricks Architecture Overview

## 1. High-Level Architecture

- **On-Prem DC (Colombo)** connected to Azure via **ExpressRoute**.
- **Azure vNet** with:
  - Azure Databricks workspace (Premium, Unity Catalog enabled)
  - Private Endpoints for ADLS Gen2 and Azure Key Vault
- **ADLS Gen2** as primary data lake (raw/bronze/silver/gold folders).
- **Azure Key Vault + HSM** for Customer-Managed Keys (CMK).
- **Unity Catalog** for centralized governance and lineage.

## 2. Data Flow

1. Core banking, card switch, ATM, and internet banking systems send data to the on-prem integration layer.
2. Data is landed into ADLS Gen2 `raw/` via secure connectors over ExpressRoute.
3. **Auto Loader / Structured Streaming** pulls from `raw/` into Bronze.
4. **Delta Live Tables / notebooks** transform Bronze → Silver → Gold.
5. BI tools (Power BI, reporting systems) query Gold via Databricks SQL Warehouse.
note vn otebook

## 3. Domains Covered

- **Retail Banking** (accounts, deposits, transactions)
- **Cards** (authorizations, settlements)
- **Loans** (personal, vehicle, housing)
- **Digital Channels** (mobile, internet, ATM)
