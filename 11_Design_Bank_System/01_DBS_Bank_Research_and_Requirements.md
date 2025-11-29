# DBS Bank Research & Data Lakehouse Requirements

## 1. DBS Bank Overview & Research

### 1.1 Key Banking Services and Products
DBS (Development Bank of Singapore) is a leading financial services group in Asia. Their core offerings include:
*   **Consumer Banking / Wealth Management:**
    *   **Deposits:** Savings accounts, Fixed Deposits, Multi-Currency Accounts.
    *   **Lending:** Home loans, renovation loans, car loans, personal loans.
    *   **Cards & Payments:** Credit/Debit cards, DBS PayLah! (mobile wallet).
    *   **Wealth:** DBS Treasures, DBS Vickers (trading), Unit Trusts, Bancassurance.
*   **Institutional Banking (Corporate / SME):**
    *   **Transaction Services:** Cash management, trade finance, securities services.
    *   **Treasury & Markets:** FX, interest rates, equities, derivatives.
    *   **SME Banking:** Working capital loans, business accounts, digital business solutions.

### 1.2 Digital Banking Strategy & Technology Focus
DBS is renowned as the "World's Best Digital Bank" with a strategy often summarized as **"Live more, Bank less"**.
*   **GANDALF Strategy:** DBS famously coined the term to benchmark themselves against tech giants: **G**oogle, **A**mazon, **N**etflix, **D**BS, **A**pple, **L**inkedIn, **F**acebook.
*   **Cloud-Native & Microservices:** Massive migration from legacy mainframes to cloud-native microservices architectures.
*   **API-First:** Extensive use of APIs (DBS Developers platform) to integrate with ecosystem partners (e.g., property, travel, retail).
*   **Data-Driven:** Heavy investment in AI/ML for hyper-personalization ("Nudge" engine), fraud detection, and credit risk modelling.

### 1.3 Key Regulatory Requirements
As a Singapore-headquartered bank with regional presence, DBS faces stringent regulations:
*   **MAS (Monetary Authority of Singapore):**
    *   **TRM Guidelines:** Technology Risk Management guidelines focusing on system reliability, security, and resiliency.
    *   **PS Notice 610:** Granular data reporting requirements for banks.
*   **Data Privacy:**
    *   **PDPA (Singapore):** Personal Data Protection Act.
    *   **GDPR:** Applicable for EU clients/operations.
    *   **Cross-border Data Transfer:** Strict rules on data residency and sovereignty (OBA - Outsourcing Banking Arrangements).
*   **Financial Standards:** Basel III (capital adequacy, liquidity risk), IFRS 9 (accounting standards).

### 1.4 Data Volume and Velocity Challenges
*   **High Velocity:**
    *   **Payments:** Millions of daily transactions via PayLah!, PayNow, and credit cards requiring near real-time processing for fraud checks.
    *   **Market Data:** Real-time FX and equity ticks for Treasury & Markets.
*   **High Volume:**
    *   **Historical Data:** Decades of customer transaction history for regulatory retention (7+ years).
    *   **Clickstream:** Massive logs from mobile and web banking apps for customer journey analysis.
*   **Variety:** Structured (core banking), Semi-structured (JSON logs, API payloads), Unstructured (customer support chats, documents).

### 1.5 Existing Tech Stack (Public Knowledge)
*   **Infrastructure:** Hybrid Cloud (Private Cloud + AWS/Azure/GCP).
*   **Big Data:** Heavy usage of Apache Spark, Hadoop (historically), and Kafka for streaming.
*   **Database:** PostgreSQL (moving away from commercial DBs like Oracle), MariaDB, Cassandra for high-throughput.
*   **DevOps:** Strong CI/CD culture, automated testing, chaos engineering.

---

## 2. Requirements for Databricks-based Data Lakehouse

Based on the research above, here are the synthesized requirements for designing a Data Lakehouse using Databricks.

### 2.1 Architectural Requirements
*   **Medallion Architecture:** Implement a Bronze (Raw), Silver (Cleaned/Conformed), and Gold (Aggregated/Business-level) layer pattern.
*   **Unified Platform:** Support both Data Engineering (ETL) and Data Science (ML) workloads on the same copy of data to eliminate silos.
*   **Multi-Cloud Support:** The architecture must be deployable across different cloud providers (Azure/AWS) to align with DBS's hybrid strategy.

### 2.2 Data Ingestion & Processing
*   **Real-Time Streaming (Velocity):**
    *   Integration with **Apache Kafka** or **Azure Event Hubs** for ingesting real-time payment and clickstream events.
    *   **Spark Structured Streaming** for low-latency processing (e.g., real-time fraud alerts).
*   **Batch Processing (Volume):**
    *   Scalable pipelines for End-of-Day (EOD) core banking reconciliation and regulatory reporting (MAS 610).
*   **Schema Enforcement:** Strict schema validation on ingestion (Delta Lake) to prevent bad data from corrupting downstream financial reports.

### 2.3 Storage & Management (Delta Lake)
*   **ACID Transactions:** Mandatory for financial data integrity (e.g., ensuring a debit and credit happen atomically).
*   **Time Travel:** Ability to query data "as of" a specific timestamp for auditing and reproducing regulatory reports.
*   **Upsert/Merge Capabilities:** Efficient handling of Change Data Capture (CDC) from core banking systems (updates to customer balances).

### 2.4 Security & Governance (Unity Catalog)
*   **Fine-Grained Access Control:** Row-level and Column-level security to mask PII (NRIC, Passport, Account Balances) based on user roles.
*   **Data Lineage:** End-to-end traceability of data from source to report to satisfy MAS audit requirements.
*   **Audit Logging:** Comprehensive logging of who accessed what data and when.
*   **Data Isolation:** Logical separation of data between different banking units (e.g., Retail vs. Investment Banking firewall).

### 2.5 Machine Learning & AI
*   **Feature Store:** Centralized repository of features (e.g., "avg_monthly_spend") for reuse across Credit Risk and Marketing models.
*   **Model Lifecycle (MLflow):** End-to-end tracking of model experiments, versioning, and deployment for governance.
*   **Explainability:** Requirement to explain AI decisions (e.g., why a loan was rejected) to regulators and customers.

### 2.6 Performance & Reliability
*   **High Availability:** Disaster Recovery (DR) setup with cross-region replication.
*   **SLA Guarantees:** Strict SLAs for critical reports (e.g., 99.9% availability for mobile banking balance updates).
*   **Photon Engine:** Utilization of Databricks Photon engine for high-concurrency SQL queries by business analysts.
