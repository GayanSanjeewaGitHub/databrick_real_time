# DBS Bank Data Lakehouse Architecture

## 1. Executive Summary
This document outlines the next-generation Data Lakehouse infrastructure for DBS Bank. Aligned with the "GANDALF" strategy (Google, Amazon, Netflix, Apple, LinkedIn, Facebook - transforming banking into a tech company), this architecture leverages **Databricks on Azure/AWS** to provide a unified, scalable, and secure platform for all banking services.

## 2. Architectural Principles
1.  **Cloud-Native & Serverless:** Utilizing Databricks Serverless SQL and Compute to minimize operational overhead.
2.  **Lakehouse Paradigm:** Unifying Data Warehousing (Regulatory Reporting) and AI (Fraud Detection, Personalization) on a single copy of data.
3.  **Data Sovereignty & Security:** Strict adherence to MAS (Monetary Authority of Singapore) TRM guidelines and PDPA/GDPR.
4.  **Real-Time First:** Prioritizing streaming ingestion for immediate fraud detection and customer notifications.

## 3. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Sources
        A[Core Banking (Mainframe)] -->|CDC| Ingest
        B[Payment Gateways (PayLah!)] -->|Kafka| Ingest
        C[Wealth Systems] -->|Batch| Ingest
        D[External APIs (Open Banking)] -->|API| Ingest
    end

    subgraph "Databricks Lakehouse (Unity Catalog)"
        direction TB
        
        subgraph "Bronze Layer (Raw)"
            B1[(Raw Transactions)]
            B2[(Raw Logs)]
            B3[(Raw KYC Docs)]
        end

        subgraph "Silver Layer (Clean/Conformed)"
            S1[(Customer 360)]
            S2[(Accounts & Balances)]
            S3[(Transaction History)]
            S4[(Credit Cards)]
        end

        subgraph "Gold Layer (Aggregated/Business)"
            G1[(Regulatory Reports)]
            G2[(Risk Models)]
            G3[(Marketing Segments)]
            G4[(Executive Dashboards)]
        end

        Ingest -->|Auto Loader / DLT| Bronze Layer
        Bronze Layer -->|Delta Live Tables| Silver Layer
        Silver Layer -->|Delta Live Tables| Gold Layer
    end

    subgraph Consumers
        BI[PowerBI / Tableau]
        ML[MLflow Models (Fraud/Credit)]
        App[Mobile App API]
    end

    Gold Layer --> BI
    Silver Layer --> ML
    Gold Layer --> App
```

## 4. Domain Driven Design
We organize data into domains to ensure ownership and scalability.

| Domain | Description | Key Entities |
|--------|-------------|--------------|
| **Customer** | Single view of customer (KYC, Demographics) | `customers`, `kyc_documents`, `beneficiaries` |
| **Retail** | Core banking products | `savings_accounts`, `fixed_deposits`, `transactions` |
| **Lending** | Credit and Loans | `credit_cards`, `loans`, `repayments`, `delinquency_history` |
| **Wealth** | Investment products | `portfolios`, `trades`, `market_data` |
| **Risk** | Compliance and Fraud | `fraud_alerts`, `aml_checks`, `credit_scores` |

## 5. Technology Stack
*   **Storage:** Azure Data Lake Gen2 / AWS S3 (Delta Lake Format)
*   **Compute:** Databricks Runtime (Photon Engine)
*   **Orchestration:** Databricks Workflows
*   **Governance:** Unity Catalog
*   **Ingestion:** Auto Loader, Spark Structured Streaming
*   **Transformation:** Delta Live Tables (DLT)
