# Phase A: Architecture Vision
## Commercial Bank of Sri Lanka – Data Platform Transformation

---

## 1. Introduction

### 1.1 Purpose
This document defines the Architecture Vision for Commercial Bank of Sri Lanka's Enterprise Data Lakehouse Platform. It establishes the business drivers, scope, stakeholders, and target architecture that will guide the transformation initiative.

### 1.2 Scope
This vision covers the design and implementation of a modern, cloud-based data platform on Azure Databricks to support:
- Real-time and batch analytics
- Regulatory compliance and reporting
- Customer 360° view
- Fraud detection and risk management
- Advanced analytics and ML capabilities

---

## 2. Business Context & Drivers

### 2.1 Current State Challenges

**Data Silos:**
- Customer data scattered across 12+ legacy systems
- No single view of customer relationships
- Reconciliation takes 48+ hours
- Duplicate and inconsistent data

**Technology Constraints:**
- On-premises data warehouse (Oracle) reaching capacity
- Limited real-time processing capabilities
- Manual ETL processes prone to failures
- High infrastructure maintenance costs

**Regulatory Pressure:**
- CBSL mandates for faster regulatory reporting
- PDPA compliance requirements for data privacy
- Need for comprehensive audit trails
- Material outsourcing guidelines for cloud adoption

**Business Limitations:**
- Fraud detection runs daily (not real-time) → losses LKR 150M/year
- Customer segmentation outdated (refreshed quarterly)
- Limited self-service analytics for business users
- Time-to-insight: 2-4 weeks for new reports

### 2.2 Strategic Business Drivers

| Driver | Description | Expected Benefit |
|--------|-------------|------------------|
| **Customer Experience** | Deliver personalized, real-time banking experiences | NPS increase +15 points, retention +8% |
| **Operational Efficiency** | Automate data pipelines, reduce manual work | Cost reduction 30%, time-to-insight from weeks to hours |
| **Risk Management** | Real-time fraud detection and credit risk analytics | Fraud losses reduction 60%, NPL ratio improvement |
| **Regulatory Compliance** | Automated CBSL reporting, audit trails, PDPA compliance | Zero regulatory penalties, faster approvals |
| **Revenue Growth** | Data-driven cross-sell, product innovation | Revenue increase 12-15% over 3 years |
| **Digital Transformation** | Foundation for AI/ML, real-time decisioning | Competitive advantage, future-ready platform |

### 2.3 Business Goals (3-Year Horizon)

1. **Customer Goal**: Achieve 360° customer view accessible in <2 seconds
2. **Risk Goal**: Detect and block fraudulent transactions in <500ms
3. **Compliance Goal**: Submit CBSL regulatory reports within 24 hours (currently 5 days)
4. **Analytics Goal**: Enable 80% of reports via self-service (currently 20%)
5. **Efficiency Goal**: Reduce data platform TCO by 25%
6. **Innovation Goal**: Launch 5+ ML-powered products (credit scoring, churn prediction, personalized offers)

---

## 3. Architecture Vision Statement

> **"To establish a secure, compliant, and high-performance enterprise data lakehouse on Azure Databricks that unifies Commercial Bank's data assets, enables real-time analytics, and supports data-driven decision-making across all business units—while maintaining complete data sovereignty and regulatory compliance."**

### 3.1 Vision Principles

1. **Unified Platform**: Single data platform for all analytics workloads
2. **Medallion Architecture**: Bronze (raw) → Silver (curated) → Gold (business-ready)
3. **Real-Time & Batch**: Support both streaming and batch processing
4. **Self-Service**: Empower business users with governed data access
5. **Cloud-Native**: Leverage Azure services with private connectivity
6. **Security First**: CMK encryption, Unity Catalog governance, private endpoints
7. **Scalable**: Handle 10x data growth over 5 years

---

## 4. Target Architecture Overview

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ON-PREMISES (Colombo DC)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Core Banking │  │  Card System │  │    Channels  │         │
│  │   (Finacle)  │  │   (Way4/UTS) │  │ (ComBank App)│         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
│                   ┌────────▼─────────┐                          │
│                   │  ExpressRoute    │                          │
│                   │  Private Circuit │                          │
│                   └────────┬─────────┘                          │
└────────────────────────────┼──────────────────────────────────┘
                             │
                             │ (Private Connectivity Only)
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                  AZURE (Southeast Asia Region)                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Virtual Network                        │ │
│  │  ┌─────────────────┐  ┌─────────────────┐               │ │
│  │  │ Private Endpoint│  │ Private Endpoint│               │ │
│  │  │   (Storage)     │  │  (Key Vault)    │               │ │
│  │  └────────┬────────┘  └────────┬────────┘               │ │
│  └───────────┼─────────────────────┼────────────────────────┘ │
│              │                     │                           │
│  ┌───────────▼─────────┐  ┌───────▼────────┐                 │
│  │   ADLS Gen2         │  │   Key Vault    │                 │
│  │  (cmbprodlake)      │  │   (CMK + HSM)  │                 │
│  │  ┌────────────────┐ │  │                │                 │
│  │  │ raw/           │ │  │  Customer      │                 │
│  │  │ bronze/        │ │  │  Managed Keys  │                 │
│  │  │ silver/        │ │  │                │                 │
│  │  │ gold/          │ │  └────────────────┘                 │
│  │  └────────────────┘ │                                      │
│  └─────────────────────┘                                      │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          Azure Databricks Premium Workspace              │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │            Unity Catalog Metastore                  │  │ │
│  │  │  Catalogs: cmb_retail, cmb_cards, cmb_loans, ...   │  │ │
│  │  │  Features: Masking, Row Filters, Lineage, Audit    │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │
│  │  │Delta Live    │  │ Streaming    │  │  SQL Warehouse│   │ │
│  │  │Tables (DLT)  │  │ Jobs         │  │  (Analytics)  │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │    Consumption Layer                                      │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │
│  │  │Power BI  │  │  Tableau │  │  Python  │               │ │
│  │  │Dashboards│  │  Reports │  │  Notebooks│               │ │
│  │  └──────────┘  └──────────┘  └──────────┘               │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Connectivity** | Azure ExpressRoute 1Gbps | Private, dedicated link from Colombo DC to Azure |
| **Storage** | ADLS Gen2 with CMK | Encrypted data lake with medallion architecture |
| **Key Management** | Azure Key Vault + HSM | Customer-managed encryption keys under bank control |
| **Data Platform** | Azure Databricks Premium | Unified analytics platform with Unity Catalog |
| **Governance** | Unity Catalog | Centralized metadata, access control, lineage |
| **Ingestion** | Auto Loader, Kafka, Event Hubs | Real-time and batch data ingestion |
| **Processing** | Delta Live Tables, Spark Streaming | ETL/ELT with data quality expectations |
| **Analytics** | SQL Warehouse, Notebooks | Interactive queries and ML development |
| **BI Layer** | Power BI, Tableau | Self-service dashboards and reports |

---

## 5. Stakeholder Analysis

### 5.1 Stakeholder Matrix

| Stakeholder | Role | Power | Interest | Engagement Strategy |
|-------------|------|-------|----------|---------------------|
| **CEO** | Strategic sponsor | High | High | Monthly steering committee |
| **CIO** | Executive owner | High | High | Bi-weekly reviews, decision authority |
| **CFO** | Budget approver | High | Medium | Quarterly ROI reviews |
| **Chief Risk Officer** | Compliance gatekeeper | High | High | Weekly risk reviews during implementation |
| **CISO** | Security approval | High | High | Security architecture review, pen-testing sign-off |
| **Head of Retail Banking** | Primary business sponsor | High | High | Use case prioritization, UAT sign-off |
| **Head of Cards** | Business unit sponsor | Medium | High | Fraud detection use case owner |
| **Chief Data Officer** | Platform owner post-launch | High | High | Design partner, transition planning |
| **Head of IT Infrastructure** | Implementation lead | Medium | High | Daily stand-ups, technical delivery |
| **Data Scientists** | End users | Low | High | Training, feedback sessions |
| **CBSL** | Regulator | High | Medium | Formal submission, periodic audits |
| **External Auditors** | Compliance validators | Medium | Medium | Annual audit, attestation reports |

### 5.2 Key Concerns by Stakeholder

**Executive Leadership:**
- ROI and payback period
- Risk of disruption to customer services
- Regulatory approval timeline

**Risk & Compliance:**
- Data sovereignty and CBSL compliance
- Encryption key control
- Audit trail completeness

**IT & Security:**
- Integration complexity with legacy systems
- Skills gap (Databricks, Python, Spark)
- Operational resilience and disaster recovery

**Business Units:**
- Time to value for their use cases
- User-friendliness of new tools
- Data accuracy and freshness

---

## 6. Scope Definition

### 6.1 In-Scope

**Data Domains:**
- ✅ Retail Banking (customers, accounts, deposits, transactions)
- ✅ Cards (credit/debit authorizations, settlements, disputes)
- ✅ Loans (personal, housing, vehicle – origination through collections)
- ✅ Digital Channels (mobile app, internet banking, ATM sessions)
- ✅ Reference Data (branches, products, exchange rates)

**Capabilities:**
- ✅ Batch ETL pipelines (daily/hourly)
- ✅ Real-time streaming (fraud detection, customer activity)
- ✅ Data governance (Unity Catalog, masking, row-level security)
- ✅ Self-service analytics (SQL Warehouse, Power BI)
- ✅ ML platform (feature store, model registry)
- ✅ Regulatory reporting (CBSL FSD, LCR, NSFR)

**Infrastructure:**
- ✅ Azure ExpressRoute setup
- ✅ ADLS Gen2 with CMK
- ✅ Databricks Premium workspace
- ✅ Unity Catalog metastore
- ✅ Event Hubs / Kafka for streaming

### 6.2 Out-of-Scope (Phase 1)

- ❌ Core Banking System replacement
- ❌ Treasury & Markets trading systems data (Phase 2)
- ❌ International branch operations
- ❌ Payment gateway or card issuing platform replacement
- ❌ Mobile/Internet Banking application redesign
- ❌ Data center decommissioning

### 6.3 Assumptions

1. ExpressRoute circuit will be operational by Month 2
2. CBSL approval for cloud data platform obtained by Month 3
3. Core Banking, Cards, and Channel systems will expose APIs/file feeds
4. Existing network security policies allow private endpoint traffic
5. Databricks team will have access to production-like dev environment by Month 1

### 6.4 Constraints

1. **Regulatory**: CBSL approval required before production deployment
2. **Budget**: LKR 750M cap (approx. USD 2.5M)
3. **Timeline**: Go-live Phase 1 within 18 months
4. **Data Residency**: All data processing in Southeast Asia region (Singapore)
5. **Connectivity**: No public internet access to data platform
6. **Skills**: Limited in-house Databricks/Spark expertise (training required)

---

## 7. Architecture Principles (Detailed)

### 7.1 Business Principles

**BP-01: Customer-Centric Design**
- Statement: Every architecture decision must enhance customer experience or enable better service.
- Rationale: Customer satisfaction is the primary business objective.
- Implications: 360° customer view, real-time personalization, faster service.

**BP-02: Compliance as Enabler**
- Statement: Regulatory compliance is not a blocker but an enabler of trust.
- Rationale: Strong compliance posture allows innovation with confidence.
- Implications: Built-in audit trails, PDPA-compliant data handling, CBSL reporting automation.

**BP-03: Data-Driven Decision Making**
- Statement: Business decisions should be based on timely, accurate data insights.
- Rationale: Reduce gut-feel decisions, increase predictability.
- Implications: Self-service analytics, data democratization with governance.

### 7.2 Data Principles

**DP-01: Data Sovereignty**
- Statement: Bank retains full control over all customer and operational data.
- Rationale: CBSL requirement, risk mitigation.
- Implications: CMK in bank-controlled Key Vault, ExpressRoute connectivity, no public endpoints.

**DP-02: Single Source of Truth**
- Statement: Each data element has one authoritative source.
- Rationale: Eliminate reconciliation efforts, ensure consistency.
- Implications: Master data management for customers, accounts, products.

**DP-03: Data Quality by Design**
- Statement: Data quality checks are enforced at ingestion and transformation.
- Rationale: Poor quality data leads to poor decisions.
- Implications: DLT expectations, schema enforcement, lineage tracking.

**DP-04: Privacy by Design**
- Statement: PII is masked, encrypted, and access-controlled by default.
- Rationale: PDPA compliance, minimize breach impact.
- Implications: Unity Catalog masking functions, column-level encryption, audit logs.

### 7.3 Application Principles

**AP-01: API-First Integration**
- Statement: All system integrations use secure, versioned APIs.
- Rationale: Loose coupling, easier testing, reusability.
- Implications: API gateway for legacy systems, event-driven architecture.

**AP-02: Real-Time Capability**
- Statement: Platform must support both real-time streaming and batch processing.
- Rationale: Fraud detection and customer experience require real-time insights.
- Implications: Kafka/Event Hubs ingestion, Spark Structured Streaming, Delta Live Tables.

**AP-03: Modularity and Reusability**
- Statement: Data pipelines and models are modular, reusable components.
- Rationale: Faster time-to-market for new use cases, maintainability.
- Implications: Domain-driven design (retail, cards, loans as separate catalogs).

### 7.4 Technology Principles

**TP-01: Cloud-First, Hybrid Reality**
- Statement: Prefer cloud-native services, but maintain private connectivity.
- Rationale: Leverage Azure innovation while respecting on-prem investments.
- Implications: ExpressRoute, private endpoints, no public internet access.

**TP-02: Zero Trust Security**
- Statement: Never trust, always verify—every request authenticated and authorized.
- Rationale: Minimize breach radius, defense in depth.
- Implications: Azure AD integration, Unity Catalog RBAC, network segmentation.

**TP-03: Infrastructure as Code**
- Statement: All infrastructure defined in version-controlled code.
- Rationale: Repeatability, auditability, disaster recovery.
- Implications: Terraform/Bicep for Azure resources, CI/CD pipelines.

**TP-04: Observability and Monitoring**
- Statement: All systems instrumented for proactive monitoring and alerting.
- Rationale: Detect issues before they impact customers.
- Implications: Azure Monitor, Databricks system tables, SLA dashboards.

---

## 8. Business Case Summary

### 8.1 Investment

| Category | Cost (LKR Millions) | Cost (USD) | Notes |
|----------|---------------------|------------|-------|
| **Azure Infrastructure** | 180 | 600K | 3-year commitment, ExpressRoute, ADLS, networking |
| **Databricks Licenses** | 240 | 800K | Premium workspace, Unity Catalog, 3-year contract |
| **Professional Services** | 150 | 500K | Implementation partner (6 months) |
| **Training & Change Mgmt** | 45 | 150K | Staff training, documentation |
| **Contingency (15%)** | 92 | 307K | Risk buffer |
| **TOTAL** | **707** | **~2.36M** | 18-month project |

### 8.2 Benefits (3-Year NPV)

| Benefit Category | Annual Value (LKR M) | Cumulative (3Y) | Assumptions |
|------------------|----------------------|-----------------|-------------|
| **Fraud Loss Reduction** | 90 | 270 | 60% reduction in card fraud (baseline 150M/yr) |
| **Operational Efficiency** | 120 | 360 | 30% reduction in data team costs, automation |
| **Revenue Growth** | 200 | 600 | Cross-sell lift 10%, customer retention +5% |
| **Regulatory Fine Avoidance** | 50 | 150 | Avoid late filing penalties, compliance costs |
| **Infrastructure Cost Savings** | 40 | 120 | Decommission on-prem warehouse, reduce licenses |
| **TOTAL BENEFITS** | **500** | **1,500** | |
| **Net Benefit (3Y)** | | **793M** | 1,500M - 707M |
| **ROI** | | **112%** | (793 / 707) * 100 |
| **Payback Period** | | **~20 months** | |

### 8.3 Intangible Benefits

- Enhanced data-driven culture
- Improved employee productivity and morale
- Competitive advantage through faster innovation
- Foundation for AI/ML initiatives
- Improved customer trust and brand reputation

---

## 9. Risks & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **CBSL approval delayed** | Medium | High | Early engagement, pre-submission workshops, compliance mapping |
| **Legacy system integration complexity** | High | Medium | Proof of concept phase, contingency budget for custom connectors |
| **Skills gap in Databricks/Spark** | High | Medium | 3-month training program, hire 2-3 senior data engineers |
| **ExpressRoute setup delays** | Low | High | Parallel track, early procurement, vendor SLA commitments |
| **Data quality issues from source systems** | High | Medium | Robust bronze layer, data quality dashboard, source system owners accountable |
| **Scope creep** | Medium | Medium | Strict change control, phase-gate approvals |
| **Key personnel turnover** | Medium | Medium | Knowledge transfer sessions, documentation, cross-training |

---

## 10. Success Criteria

### 10.1 Technical Metrics

- ✅ Platform availability: 99.9% (< 9 hours downtime/year)
- ✅ Fraud detection latency: <500ms (P95)
- ✅ Customer 360° query response: <2 seconds
- ✅ Data freshness: Real-time for cards, <1 hour for retail
- ✅ Pipeline SLA: 95% of jobs complete within scheduled window

### 10.2 Business Metrics

- ✅ Self-service report adoption: 80% of users by Month 12 post-launch
- ✅ CBSL reporting time: <24 hours (from 5 days)
- ✅ Fraud loss reduction: 60% within 12 months
- ✅ Customer NPS: +15 points attributed to personalization
- ✅ Time-to-insight: From weeks to hours for new analysis requests

### 10.3 Compliance Metrics

- ✅ Zero regulatory penalties related to data platform
- ✅ 100% audit trail coverage
- ✅ PDPA compliance: 100% PII masked for non-privileged users
- ✅ Security incidents: Zero data breaches

---

## 11. Next Steps

### 11.1 Immediate Actions (Month 1-2)

1. **Steering Committee Formation**: Secure executive sponsors, schedule kickoff
2. **CBSL Engagement**: Submit material outsourcing application with architecture docs
3. **Vendor Selection**: Finalize Databricks contract, select implementation partner
4. **Team Formation**: Hire/assign core team (architect, 3 engineers, 1 analyst)
5. **Environment Setup**: Provision dev Azure subscription, ExpressRoute initiation

### 11.2 Phase A Deliverables Checklist

- [x] Architecture Vision document (this document)
- [ ] Stakeholder matrix with sign-offs
- [ ] Detailed business case presentation
- [ ] High-level architecture diagram (approved)
- [ ] Scope statement with stakeholder agreement
- [ ] Risk register (initial version)
- [ ] Executive presentation deck (for steering committee)

---

## 12. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **CIO (Sponsor)** | [Name] | | |
| **Chief Risk Officer** | [Name] | | |
| **Chief Data Officer** | [Name] | | |
| **Enterprise Architect** | [Name] | | |
| **Head of Retail Banking** | [Name] | | |

---

## 13. Document Control

- **Version**: 1.0
- **Status**: Draft for Review
- **Last Updated**: December 2025
- **Next Review**: After Steering Committee Approval
- **Classification**: Internal - Confidential
- **Owner**: Enterprise Architecture Team

---

**End of Phase A: Architecture Vision**
